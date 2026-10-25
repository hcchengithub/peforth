# peforth Input Box Tab Auto-completion 計劃書

**目標：**

在 peforth 互動式 Forth REPL 的 input box 中，按下 Tab 時，從目前 VM 的 live dictionary 提供所有 word names 的自動完成（auto-completion）。候選比對不分大小寫，但補回輸入的 word name 保留 dictionary 中的原始大小寫。

**範圍：**

本計劃只處理 REPL/editor 層的 word-name completion，不修改 Forth kernel、TIB、Task、tokenizer 或 word 定義機制。

---

## 一、已確定的行為

### 1. 候選來源

候選集合直接來自目前 VM 的 live dictionary：

```python
vm.words.keys()
```

因此會包含：

- `base.f` 載入的 words
- `auxiliary.f` 載入的 words
- `ai.f` 載入的 words
- Python runtime 動態加入的 words
- 使用者在 REPL 中新定義的 words
- 目前 dictionary 中的重新定義名稱

不建立第二份靜態 word registry，也不從 `.f` 檔案重新掃描名稱。

### 2. 啟用模式

只在 Forth mode 的 `> ` input box 啟用 completion。

Chat mode 的 `chat> ` input 不進行 Forth word completion。

### 3. 比對規則

- 採 prefix matching。
- 比對不分大小寫（case-insensitive）。
- dictionary 中的實際 word name 不被正規化或改寫。
- word names 可包含 Forth 特殊字元，例如：
  - `.`
  - `.s`
  - `[if]`
  - `ai:`
  - `py:`
- 不可套用 Python identifier 規則。
- 當游標位於一行中間時，只處理游標所在的目前 token。
- token 邊界以 whitespace 為主，符合現有 `Input.read()` 的基本 token 行為。

例如：

```text
> DUP<Tab>
```

可以匹配 dictionary 中的 `dup`，並補回原始名稱：

```text
> dup
```

### 4. 多候選行為

採用 `prompt_toolkit` 的標準 completion 行為：

- 零個候選：不改變輸入。
- 一個候選：補上完整 word name。
- 多個候選：顯示 completion menu。
- 重複按 Tab：由 prompt_toolkit 瀏覽候選。
- 若有共同 prefix，沿用 prompt_toolkit 的標準處理。

### 5. 純 UI 行為

Completion 必須是 read-only editor 行為：

- 不執行任何 Forth word。
- 不呼叫 `vm.dictate()`、`vm.execute()` 或 `vm.tick()` 來取得候選。
- 不修改 data stack、return stack、T-stack、TIB 或 Task 狀態。
- 不透過 `tib.append` 實作。
- Completion 期間不建立新 Task。

---

## 二、實作設計

### 1. 主要修改位置

修改：

```text
peforth/repl.py
```

在現有 `prompt_toolkit` import 區域加入 completion 相關元件，例如：

```python
from prompt_toolkit.completion import Completer, Completion
```

實作一個只依賴 VM 的 completer，例如：

```python
class ForthWordCompleter(Completer):
    ...
```

### 2. Completer 的責任

Completer 每次被 prompt_toolkit 呼叫時：

1. 取得游標前的目前 token。
2. 以不分大小寫的 prefix 比對 `vm.words.keys()`。
3. 以穩定順序產生 `Completion` 物件。
4. 將 candidate 的原始 word name 作為補回內容。
5. 將 start position 設為目前 token 長度的負值，使補完只替換目前 token。

概念形式：

```python
prefix = current_token_before_cursor
for name in vm.words:
    if name.casefold().startswith(prefix.casefold()):
        yield Completion(
            name,
            start_position=-len(prefix),
        )
```

實際 token 擷取必須正確處理：

- 空白後的新 token
- 多個 Forth token
- 游標不在行尾
- 特殊字元 word name
- 空 prefix

### 3. Candidate 順序

候選順序必須穩定，避免每次按 Tab 或每次 refresh 時跳動。

第一版採 dictionary insertion order；這保留目前 VM dictionary 的自然順序，不另外引入排序規則。

如果 prompt_toolkit 本身需要排序，應確保排序只影響顯示順序，不改變 candidate 的實際補回文字。

### 4. 動態 dictionary

Completer 不得在建立時永久快取 word names。

使用者完成下列定義後：

```forth
: hello ... ;
```

同一個 REPL session 內立即輸入：

```text
> hel<Tab>
```

必須可以找到 `hello`。

因此 completion provider 應持有 VM reference，並在 `get_completions()` 執行時讀取 `vm.words`。

### 5. PromptSession 整合

目前 `repl.py` 建立兩個 `PromptSession`：

- multiline 的主要 Forth/chat session
- 非 multiline 的 approval/cleanup session

應將 Forth completer 掛到主要 input session：

```python
PromptSession(
    multiline=True,
    key_bindings=_make_multiline_key_bindings(),
    completer=ForthWordCompleter(vm),
    prompt_continuation=...,
)
```

approval/cleanup prompt 不需要 Forth completion。

主要 session 仍由既有的 `repl_mode` 決定 prompt 顯示；若 completer API 無法直接依 mode 停用，completer 應在 `get_completions()` 內檢查 VM 的 `repl_mode`，chat mode 直接 yield 空結果。

---

## 三、測試計劃

### 1. 單元測試位置

優先新增或修改：

```text
tests/test_peforth.py
```

測試 completer 的邏輯時，使用最小 VM 或 mock VM；不需要啟動真正互動式 terminal。

### 2. 必測案例

#### Case A：大小寫不分

Dictionary：

```python
{"dup": ..., "DUPLICATE": ...}
```

輸入 prefix：

```text
dUp
```

預期匹配所有 `casefold().startswith("dup")` 的 names，並保留原始名稱。

#### Case B：prefix matching

`st` 只能匹配以 `st` 開頭的 names，不匹配中間才出現 `st` 的 names。

#### Case C：Forth 特殊字元

確認以下名稱不會被 Python identifier parsing 排除：

```text
.
.s
[if]
ai:
py:
```

#### Case D：目前 token

輸入：

```text
foo  DUP
```

游標在 `DUP` 後面時，只以 `DUP` 作為 prefix，不以整行作為 prefix。

#### Case E：游標不在行尾

確認 `start_position` 只替換游標所在 token 的已輸入部分，不破壞游標後文字。

#### Case F：空 prefix

空 token 的 completion 行為必須明確且可控。第一版可列出全部 words，但應避免因大型 dictionary 造成不必要的 UI 負擔；若 prompt_toolkit 對空 prefix 不呼叫 completer，則遵循其標準行為。

#### Case G：動態新增 word

在 completer 建立後新增 `vm.words["hello"]`，再取得 completion，必須能找到 `hello`。

#### Case H：Chat mode

當 `vm.host["repl_mode"] == "chat"` 時，completion 結果應為空。

#### Case I：空候選

沒有匹配 candidate 時，輸入與 VM 狀態不應被修改。

### 3. 回歸測試

執行完整既有測試：

```bash
pytest -q
```

並確認原有 Forth、TIB、Task、AI REPL 測試不受影響。

若環境缺少 `prompt_toolkit`，completion 單元測試應以清楚的 skip/requires 機制處理，不可讓非互動式 kernel 測試無故失敗。

---

## 四、驗收標準

功能完成必須同時符合：

1. 在 Forth `> ` input box 按 Tab 可以完成 live dictionary 中的 word name。
2. 候選比對不分大小寫。
3. 補回文字保留 dictionary 中的原始大小寫與特殊字元。
4. 只處理目前游標所在 token。
5. 支援 Forth 特殊 word names，不受 Python identifier 限制。
6. 新定義的 word 不需重啟 REPL 即可 completion。
7. Chat mode 不顯示 Forth word completion。
8. Completion 不執行 Forth、不修改 TIB、Task 或 stacks。
9. 零個、單個、多個候選均有可驗證的行為。
10. 完整既有測試通過。

---

## 五、實作順序

### Task 1：建立 completer 單元測試

**Files：**

- Modify: `tests/test_peforth.py`
- Test target: `ForthWordCompleter`

先加入大小寫不分、特殊字元、目前 token、動態 dictionary 與 chat mode 測試，確認測試在尚未實作時失敗。

### Task 2：在 `repl.py` 實作 live dictionary completer

**Files：**

- Modify: `peforth/repl.py`

加入 `ForthWordCompleter`，只讀取 `vm.words`，不引入新的 dictionary state。

### Task 3：掛接主要 PromptSession

**Files：**

- Modify: `peforth/repl.py`

將 completer 掛到主要 multiline `PromptSession`，approval/cleanup session 維持不變。

### Task 4：執行單元與完整回歸測試

執行：

```bash
pytest -q tests/test_peforth.py
pytest -q
```

另以實際 REPL 手動驗證：

```text
> du<Tab>
> : hello ... ;
> hel<Tab>
```

並確認 `chat` mode 不出現 Forth candidates。

### Task 5：更新文件與變更摘要

若實際行為與本計劃有差異，更新本文件的「已確定的行為」與驗收標準，避免文件和程式分歧。

---

## 六、明確不包含的工作

本次不做：

- fuzzy matching
- substring matching
- help/comment 顯示
- semantic suggestion
- word signature 或 stack-effect 顯示
- chat prompt 的 Forth completion
- 修改 `projectk.py` 的 dictionary API
- 修改 TIB 或 Task 的輸入流程
- completion history 或跨 session 的候選快取
- 另外建立 static word list
