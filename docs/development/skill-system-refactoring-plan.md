# Skills 系統架構重構計畫書（輕量 Manifest + 按需載入工具）

- **文件版本**：v1.0.0
- **日期**：2026-11-07
- **目標位置**：`docs/development/skill-system-refactoring-plan.md`
- **狀態**：審閱中（Pending Review）

---

## 1. 背景與重構動機

在目前的 `peforth v2.1.0` 架構中，`get_system_prompt(vm)` 透過 `load_all_skills()` 將所有 `skills/*/SKILL.md` 的完整說明文字一次性全部嵌入 System Prompt：

```python
# 現行架構 (ai.py:1404)
if combined_skills:
    instructions += "\n\n=== Available Skills ===\n\n" + combined_skills
```

### 現行架構的問題：
1. **Context 肥大與 Token 成本**：即使目前僅有 6 個 Skills，全文塞入也佔據了數萬字元。未來隨著 Skill 數量與參考資料增長，極易逼近 `100_000` bytes 的上限防線。
2. **注意力稀釋（Context Pollution）**：AI 在進行一般 Forth 計算或單純對話時，無需背負全部 Skill（例如 Windows 截圖、LINE Notify、Herdr 排程）的詳細步驟與範例。
3. **伴隨資源無法調用**：Skill 不只有 `SKILL.md`，許多 Skill 還包含附屬資源（例如 `peforth-forth` 的 `references/forth-reference.md`、`windows-msgbox` 的 `scripts/send_msgbox.ps1`）。在現行架構下，AI 根本無法在對話中閱讀這些伴隨文件與腳本。

---

## 2. 核心設計原則與約束

根據使用者明確指示與架構討論，本次重構必須嚴格遵守以下原則：

### 原則一：System Prompt 絕對不包含本機絕對路徑（Strict No Absolute Paths）
* **禁止項目**：System Prompt 中**嚴禁出現任何本機路徑**（如 `C:\Users\hcche\...`、`/home/user/...`、`~/.peforth/...`）。
* **原因**：
  1. **跨平台可移植性**：peforth 在 Windows (CMD/PowerShell)、WSL、Linux 皆可運行，System Prompt 應為純邏輯描述，不受本機環境干擾。
  2. **安全與隱私**：不向 AI 模型暴露本地使用者帳號名稱與目錄結構。
  3. **定位職責分離**：AI 僅需知道「技能名稱」與「用途簡述」；物理檔案的搜尋與定位（`get_skills_dir(vm)`）完全由本地 Python 工具在後端解析。

### 原則二：完整 Bundle 資源按需調用（Companion Files Support）
* AI 透過專屬工具 `peforth_read_skill` 不僅能讀取主說明檔 `SKILL.md`，還必須能讀取目錄下的 `references/`（參考手冊）與 `scripts/`（自動化腳本）等伴隨資源。

### 原則三：嚴格的安全沙盒（Path Traversal Guard）
* 本地工具必須防範路徑逃逸攻擊（Path Traversal）。任何傳入的子路徑（如 `../../etc/passwd` 或 `C:\Windows\...`）必須被強制攔截，解析後的路徑必須嚴格限制在該 Skill 目錄之內。

### 原則四：全系統相容與同步
* 修改範圍以 Repo（`OneDrive/Documents/GitHub/peforth`）為準，確保 `test_all.py` 100% 通過後，同步至執行時目錄（`~/.peforth`）並更新開發日誌（`peforth-devlog.txt`）。

---

## 3. 架構設計

```mermaid
flowchart TD
    subgraph System Prompt [System Prompt (瘦身後 < 500 bytes)]
        Manifest["=== Available Skills ===\n- herdr: Orchestrate multi-agent tasks...\n- peforth-forth: Forth guide... [companion: references/forth-reference.md]\n- windows-msgbox: Native msgbox... [companion: scripts/send_msgbox.ps1]"]
    end

    subgraph AI Model Decision
        NeedSkill{"是否需要使用特定技能？"}
    end

    subgraph Tool [peforth_read_skill 工具]
        ToolDispatch["peforth_read_skill(skill_name, file_path=None)"]
        SafeCheck{"Path Traversal 檢查\n(限制在 skill 目錄內)"}
        ReadSkillMD["讀取 SKILL.md\n+ 列出所有可用的 companion_files"]
        ReadSubFile["讀取特定 companion file\n(如 references/forth-reference.md)"]
    end

    System Prompt --> NeedSkill
    NeedSkill -- "需要" --> ToolDispatch
    NeedSkill -- "不需要" --> NormalFlow["直接回答或執行 Forth"]
    ToolDispatch --> SafeCheck
    SafeCheck -- "合法" --> Branch{"file_path 是否為空？"}
    Branch -- "空 / 未指定" --> ReadSkillMD
    Branch -- "指定相對路徑" --> ReadSubFile
    SafeCheck -- "非法路徑" --> Err["回傳安全錯誤訊息 (Blocked)"]
```

---

## 4. 詳細模組設計

### 4.1 System Prompt 清單生成器 (`load_skills_manifest`)

取代原先的 `load_all_skills()`。

1. **掃描目錄**：讀取 `get_skills_dir(vm)` 目錄下的所有子資料夾。
2. **解析 Frontmatter**：從每個 Skill 的 `SKILL.md` 開頭讀取 YAML Frontmatter（抽取 `name`、`description`）。若無 Frontmatter，則以目錄名為 name，取第一段文字為 description。
3. **掃描伴隨資源**：搜尋該 Skill 目錄下的所有檔案（排除 `SKILL.md`），以相對路徑列出（如 `references/forth-reference.md`、`scripts/send_msgbox.ps1`）。
4. **輸出格式（絕無本機路徑）**：
   ```text
   === Available Skills ===
   - herdr: Orchestrate multi-agent Forth tasks and monitor worker states.
   - peforth-forth: Comprehensive guide to Forth programming and peforth dialect. [companion: references/forth-reference.md]
   - windows-msgbox: Display native Windows message boxes. [companion: scripts/send_msgbox.ps1, scripts/send_msgbox.sh]
   - windows-screen-capture: Capture Windows screen or active window to image file.
   - line-notify: Send notifications and images via LINE Notify API. [companion: scripts/send_line_message.ps1, scripts/send_line_message.sh]
   - ai-diagnostics-log-inspector: Inspect and query peforth AI diagnostic log events.
   ```
   *整體長度預估約 400 ~ 500 bytes，遠低於先前數十 KB！*

---

### 4.2 `peforth_read_skill` 工具定義與 Schema

在 `TOOLS_DEFINITION` 與 `AGENTS_TOOLS_DEFINITION` 中註冊：

```python
{
    "type": "function",
    "function": {
        "name": "peforth_read_skill",
        "description": (
            "Read full documentation or companion files for an available skill. "
            "Call without file_path to read the main SKILL.md and discover companion files (references, scripts). "
            "Call with file_path (relative to the skill directory) to read a specific reference or script."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "description": "The logical name of the skill (e.g. 'peforth-forth', 'windows-msgbox').",
                },
                "file_path": {
                    "type": "string",
                    "description": "Optional relative path inside the skill directory (e.g. 'references/forth-reference.md', 'scripts/send_msgbox.ps1'). Defaults to 'SKILL.md'.",
                },
            },
            "required": ["skill_name"],
            "additionalProperties": False,
        },
    },
}
```

---

### 4.3 Python 實作邏輯 (`tool_read_skill`)

```python
def tool_read_skill(vm, skill_name: str, file_path: str = None) -> dict:
    """Read a skill's SKILL.md or companion reference/script file safely."""
    skills_root = get_skills_dir(vm)
    target_skill_dir = (skills_root / skill_name).resolve()

    # 1. 驗證 Skill 是否存在且落在 skills_root 內
    if not target_skill_dir.is_dir() or not target_skill_dir.is_relative_to(skills_root.resolve()):
        return {"error": f"Skill '{skill_name}' not found."}

    # 2. 收集 companion files 清單 (相對於 target_skill_dir)
    companion_files = []
    for f in sorted(target_skill_dir.rglob("*")):
        if f.is_file() and f.name != "SKILL.md":
            companion_files.append(str(f.relative_to(target_skill_dir)).replace("\\", "/"))

    # 3. 讀取指定檔案或預設 SKILL.md
    rel_path = (file_path or "SKILL.md").strip().replace("\\", "/")
    target_file = (target_skill_dir / rel_path).resolve()

    # 4. 安全檢查：防止 Path Traversal
    if not target_file.is_relative_to(target_skill_dir):
        return {"error": "Access denied: file_path escapes skill directory."}

    if not target_file.is_file():
        return {
            "error": f"File '{rel_path}' not found in skill '{skill_name}'.",
            "available_companion_files": companion_files,
        }

    try:
        content = target_file.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"error": f"Failed to read file: {e}"}

    return {
        "skill": skill_name,
        "file": rel_path,
        "content": content,
        "companion_files": companion_files if rel_path == "SKILL.md" else [],
    }
```

---

### 4.4 Tool 調度整合點

1. **Stateless 模式（OpenAI-compatible 迴圈）**：
   在 `ai.py` 的 tool 處理區塊加入 `elif fn_name == "peforth_read_skill":`，呼叫 `tool_read_skill` 並回傳 JSON。
2. **Stateful 模式（Copilot / Agents API 迴圈）**：
   在 Agents 端的 tool 處理區塊加入相應的分支。
3. **對話壓縮與清理 (`sanitize_compact_messages`)**：
   將 `peforth_read_skill` 納入清理規則，在對話壓縮時可適度去除大型 reference 的暫存輸出，避免舊的查詢塞爆歷史。

---

## 5. 預計修改與驗證計畫

### 5.1 程式碼異動檔案
* `ai.py`：
  - 更新 `load_all_skills()` / 新增 `load_skills_manifest()`
  - 更新 `get_system_prompt()` 組合邏輯（移除 100KB 大包裝，改用 Manifest）
  - 加入 `peforth_read_skill` 工具定義與 `tool_read_skill` 實作
  - 在 OpenAI 與 Agents 調度迴圈掛入工具處理
* `ai.f`：
  - 若有相關的 Forth 端輔助字詞，同步更新
* `test_all.py`：
  - 測試 1：`test_skills_manifest_generation`（驗證無絕對路徑、長度 < 1KB、正確解析描述與 companion files）。
  - 測試 2：`test_tool_read_skill_default`（讀取 `SKILL.md` 並包含 companion files 清單）。
  - 測試 3：`test_tool_read_skill_companion_file`（讀取 `references/forth-reference.md` 或 `scripts/...` 內容正確）。
  - 測試 4：`test_tool_read_skill_security_traversal`（測試 `../../ai.py` 或絕對路徑時正確被阻擋報錯）。

### 5.2 執行與同步步驟
1. 在 Repo `OneDrive/Documents/GitHub/peforth` 進行修改。
2. 執行全套單元測試：`python test_all.py`（確保 70+ 個測試全數 PASS）。
3. 同步至執行時目錄：`C:\Users\hcche\.peforth\`。
4. 更新開發日誌：`C:\Users\hcche\OneDrive\Documents\Docs\peforth-devlog.txt`。
5. 提交 Git Commit。
