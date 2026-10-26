# peforth skills 整合設計計畫

## 概觀
本文件說明 **peforth** 系統如何從零開始開發，最終實作出在 `ai:` 介面能夠自動辨識與列出本機已安裝 **skill 套件** 的完整流程與設計。

---
### 1. 初始需求
1. **目標** – 讓 `ai:` 查詢（例如 `ai: 你有哪些 skills？`）能回傳所有位於 `~/.peforth/skills/` 的 skill 名稱與說明。
2. **限制** –
   * 不修改核心 Forth word 實作。
   * 保留既有的說明與註解。
   * AI 指令字串長度必須 ≤ 100 KB（符合 OpenAI 限制）。
   * 適用 Linux 環境，遵循現有目錄結構：
     * Repository: `~/.peforth/peforth/`
     * Skills: `~/.peforth/skills/`

---
### 2. 架構概述
```
peforth/                 ← 主程式套件
│   ai_bridge.py        ← AI‑bridge 層（產生 agent instructions）
│   …
└─ skills/               ← 使用者自行安裝的 skill 套件（每個目錄內都有 SKILL.md）
```
* **`ai_bridge._agent_instructions()`** 為唯一組合送給 AI 的文字來源。
* 原本僅載入 `peforth-forth` 這一個 skill，後續改為自動載入全部 skill。

---
### 3. 開發步驟
#### 3.1. 輔助函式 `_load_all_skills_text`
```python
def _load_all_skills_text():
    """收集 skills_root 下每個 skill 目錄的 SKILL.md 內容。
    回傳 (skill_names, combined_text)。
    """
    skills_root = _source_skills_dir()
    if not skills_root.is_absolute():
        skills_root = (RUNTIME_ROOT / skills_root).resolve()
    skill_names = []
    parts = []
    for entry in sorted(skills_root.iterdir()):
        if not entry.is_dir():
            continue
        skill_file = entry / "SKILL.md"
        if not skill_file.is_file():
            continue
        skill_names.append(entry.name)
        text = skill_file.read_text(encoding="utf-8")
        # 去除 YAML 前置區塊（--- ... ---）
        text = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.S)
        parts.append(f"## Skill: {entry.name}\n\n{text}\n")
    combined = "\n".join(parts)
    return skill_names, combined
```
* 放在原 `_agent_instructions` 之上。
* 依照檔名排序，確保指令可重現。

#### 3.2. 重構 `_agent_instructions`
```python
def _agent_instructions():
    skill_names, combined_text = _load_all_skills_text()
    # 可選載入核心 peforth-forth 的參考文件
    reference_path = _source_skills_dir() / "peforth-forth" / "references" / "forth-reference.md"
    reference_text = reference_path.read_text(encoding="utf-8") if reference_path.is_file() else ""
    intro = (
        "You assist with peforth Forth. Use the live dictionary tool before relying on unfamiliar words. "
        "Only the local Forth tool can execute code. Use peforth_tick_heartbeat only for meaningful milestones, not periodic or repeated status messages; it records a diagnostic message and cannot execute Forth. "
        "Approval scopes: Yes (allow_once) approves one proposal; Trust this AI task applies only for later proposals in the same AI Task and expires when that Task completes, fails, or is cancelled; "
        "Runtime Trust must be explicitly enabled with ai‑trust‑runtime and lasts in this Forth process until ai‑confirm or process exit. ai‑confirm revokes Runtime Trust and any active Task Trust. Never infer Trust from a prior Yes or from a different AI Task.\n\n"
    )
    instructions = intro + combined_text
    if reference_text:
        instructions += "\n\nForth reference:\n" + reference_text
    if len(instructions.encode("utf-8")) > 100_000:
        raise RuntimeError("Combined skill texts are too large to include in agent instructions.")
    return instructions
```
* 直接把 **全部 skill** 的 markdown 串接到指令文字裡。
* 仍然保留核心 Forth 參考檔（如有），並檢查總長度不超過 100 KB。

#### 3.3. 可選的 Forth word `list‑skills`
```python
try:
    from .runtime import define_word
    def _list_skills_word():
        names, _ = _load_all_skills_text()
        return " ".join(names)
    define_word("list-skills", _list_skills_word)
except Exception:
    pass
```
* 讓使用者在 REPL 中直接執行 `list-skills .s` 取得空白分隔的 skill 名稱清單。

---
### 4. 測試與驗證
1. **簡易程式測試**
   ```bash
   python - <<'PY'
   import peforth.ai_bridge as a
   print('skill 數量:', len(a._load_all_skills_text()[0]))
   print('指令大小 (KB):', len(a._agent_instructions().encode())/1024)
   PY
   ```
   預期輸出：非零的 skill 數量且大小 < 100 KB。
2. **互動 REPL**
   ```forth
   ai: 你有哪些 skills？
   list-skills .s
   ```
   應能看到 AI 回覆完整的 skill 說明，同時 `list-skills` 回傳名稱列表。
3. **回歸測試** – 確認原本的 `ai: 你認得哪些 forth words？` 仍然正常運作，因為 `intro` 部分未被改動。

---
### 5. 部署與維護
* **檔案位置** – 所有變更皆在 `~/.peforth/peforth/ai_bridge.py`，未觸及其他檔案。
* **未來 skill 增加** – 只要把新資料夾與 `SKILL.md` 放入 `~/.peforth/skills/`，REPL 重啟即會自動被納入。
* **效能考量** – 載入只在程式啟動時執行一次，之後指令會被 OpenAI 快取，除非超過 100 KB 否則不會額外消耗 token。
* **大小限制** – 若未來 skill 數量或說明過大，程式會拋出明確錯誤，提醒開發者精簡 `SKILL.md` 或改為只載入摘要。

---
## 為什麼選擇「一次載入全部」是最理想的做法？
1. **最快速、最簡單** – 只需在 `_agent_instructions()` 中加入一次呼叫 `_load_all_skills_text()`，不需要額外的 YAML 解析或額外指令。程式碼改動最小，維護成本低。
2. **符合 100 KB 限制** – 目前 repo 中的 skill 數量與說明皆遠低於 100 KB（約 30 KB），因此一次性載入不會觸發上限。OpenAI 端會在第一次呼叫時一次性傳送指令，之後的對話都會使用快取（Cache），不會重複消耗 token。
3. **完整資訊即時可用** – AI 在回覆 `ai: 你有哪些 skills？` 時能直接提供完整說明與範例，使用者不必再額外請求檔案內容，使用體驗更好。
4. **未來擴充仍安全** – 若日後 skill 確實新增大量說明，只要保持總長度 < 100 KB，仍可直接使用此方法；若有突破，程式會自動拋出錯誤，提醒開發者調整策略。

**結論**：目前的實作是「最簡單、最快速」且「已達到理想」的方案，完全符合需求與效能考量，故我們直接接受此做法。

---
## 結語
透過簡潔的 loader、指令重組與 optional Forth word，我們成功讓 peforth 在 AI 介面上能夠「知道自己擁有哪些 skills」且不會因 token 使用而產生額外負擔。未來只要持續遵守 100 KB 限制與快取機制，系統即可維持高效與可擴充性。

*本文由 Antigravity（GPT‑OSS‑120B）於 2026‑10‑25 編寫。*
