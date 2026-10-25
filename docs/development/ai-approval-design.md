# AI Forth 批准與 Trust 設計

狀態：已實作；production approval flow 使用 `ai-approve`。

## 架構層與流程

<table align="center" border="1" cellpadding="8" cellspacing="0">
  <tr><th>層</th><th>職責／流程</th></tr>
  <tr><td><b>Host / Terminal</b></td><td>使用者輸入與畫面輸出</td></tr>
  <tr><td colspan="2" align="center">↓</td></tr>
  <tr><td><b>peforth application</b><br><code>repl.py</code>、<code>ai.f</code></td><td>proposal → Trust 檢查 → <code>ai-approve</code> → resume／cancel</td></tr>
  <tr><td colspan="2" align="center">↓ pause / resume</td></tr>
  <tr><td><b>Project K kernel</b><br>VM、Task</td><td>執行或暫停同一個 Task continuation</td></tr>
</table>

Task 不是架構層，而是 kernel 中的一個執行續接；Task Trust 由 application state 依 Task 物件識別，不要求 kernel 知道 AI Trust。

## Trust 範圍

| 授權 | 狀態位置 | 效期 |
|---|---|---|
| 單次批准 | 不保存 Trust | 僅此 proposal |
| Task Trust | REPL 的 application state，以目前 AI Task 物件識別；不放在 `vm.host` | 同一 AI Task 的 proposals；Task 結束、失敗或取消即失效 |
| Runtime Trust | `vm.host["ai_trusted"]` | 目前 VM/runtime；直到 `ai-confirm` 或 process 結束 |

Task Trust 必須跨越同一 Task 的 pause/resume，涵蓋該 AI 工作流程中的後續 Forth proposals；新 Task 不繼承它。這是 REPL/application 層的狀態，不在 `projectk.py` kernel 增加 AI 專用欄位或規則。Runtime Trust 是刻意長效的明確選項，不由 Task Trust 自動啟用。

## 批准流程

1. Proposal 到達時，先檢查 Runtime Trust，再檢查目前 Task 的 Trust。
2. 兩者皆未授權時，production REPL 呼叫可調整呈現方式的 Forth word `ai-approve`。
3. `ai-approve` 回傳 `allow_once`、`trust_task`、`deny` 或 `cancel`；它負責批准介面與決策，不執行 proposal，也不設定 Runtime Trust。Python 負責低階終端輸入、Task pause/resume 與遠端取消。
4. `trust_task` 只標記目前 Task；`allow_once` 只批准目前 proposal。執行前仍須確認遠端 action 尚未過期。
5. `ai-trust-runtime` 明確啟用 `vm.host["ai_trusted"]`；`ai-confirm` 撤銷 Runtime Trust，並透過 application 層清除目前 Task Trust。若 task 中途執行 `ai-confirm`，其後 proposal 必須重新批准。Task Trust 也會在 Task 結束、失敗或取消時清除。

Production flow 與測試共用同一個 Forth `ai-approve` word，讓應用程式可替換批准介面的呈現方式而不改 kernel。