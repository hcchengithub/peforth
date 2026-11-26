# Tour Guide: Reviewing Windows Event Logs

This tour guide demonstrates using peforth to review recent Windows Event Logs, inspect noteworthy errors in follow-up queries, and summarize findings with caveats. The transcript below is reproduced verbatim from the Herdr pane.

## Conversation

```text
chat> 檢查這台 Windows 電腦的 Event Log，看看有沒有什麼需要注
    意的問題。
╭─ 👋 user ────────────────────────────────────────────────────╮
  檢查這台 Windows 電腦的 Event Log，看看有沒有什麼需要注
    意的問題。
╰─────────────────────────────────────── 2026-11-26 03:20:50 ──╯

[AI Tool] Searching dictionary for: 'Windows Event Log Get-WinEvent read logs PowerShell run_pwsh safe'...

[AI Proposes Forth Code]
Purpose: 唯讀檢查最近 7 天 Windows System 與 Application event log 的 Critical/Error 事件，列出摘要與計數；不更改系統設定或清除日誌。
Source:
s" $since = (Get-Date).AddDays(-7); $logs = 'System','Application'; foreach ($log in $logs) { Get-WinEvent -FilterHashtable @{LogName=$log; Level=1,2; StartTime=$since} -MaxEvents 80 -ErrorAction SilentlyContinue | Select-Object @{N='Log';E={$log}}, TimeCreated, ProviderName, Id, LevelDisplayName, Message } | Format-List }; '--- Recent critical/error counts by System/Application for last 7 days ---'; foreach ($log in $logs) { $events = @(Get-WinEvent -FilterHashtable @{LogName=$log; Level=1,2; StartTime=$since} -ErrorAction SilentlyContinue); [pscustomobject]@{Log=$log; Critical=(@($events | Where-Object Level -eq 1)).Count; Error=(@($events | Where-Object Level -eq 2)).Count} } | Format-Table -AutoSize" run_pwsh


[Security] Approval required — Word: run_pwsh
1. Allow Once
2. Trust this AI task
3. Deny this proposal
4. Cancel this AI task

Choose 1-4: 2

[AI Proposes Forth Code]
Purpose: 修正 PowerShell 管線語法後，唯讀列出最近 7 天 System/Application 日誌中的 Critical 與 Error 事件及總數。
Source:
s" $since=(Get-Date).AddDays(-7); foreach($log in @('System','Application')) { Write-Output ('=== '+$log+' Critical/Error last 7 days ==='); Get-WinEvent -FilterHashtable @{LogName=$log; Level=1,2; StartTime=$since} -MaxEvents 30 -ErrorAction SilentlyContinue | ForEach-Object { [pscustomobject]@{Time=$_.TimeCreated; Provider=$_.ProviderName; Id=$_.Id; Level=$_.LevelDisplayName; Message=(($_.Message -replace '\s+',' ').Trim())} } | Format-Table -Wrap -AutoSize; $e=@(Get-WinEvent -FilterHashtable @{LogName=$log; Level=1,2; StartTime=$since} -ErrorAction SilentlyContinue); 'Total critical='+(@($e|Where-Object {$_.Level -eq 1}).Count)+' error='+(@($e|Where-Object {$_.Level -eq 2}).Count) }" run_pwsh


[AI Proposes Forth Code]
Purpose: 只讀取最近一週錯誤事件的詳細訊息，確認來源、錯誤內容與是否有反覆或需立即處理的項目。
Source:
s" $since=(Get-Date).AddDays(-7); foreach($log in @('System','Application')) { Write-Output ('=== '+$log+' recent Error details ==='); Get-WinEvent -FilterHashtable @{LogName=$log; Level=2; StartTime=$since} -MaxEvents 12 -ErrorAction SilentlyContinue | ForEach-Object { '--- '+$_.TimeCreated.ToString('s')+' | '+$_.ProviderName+' | ID '+$_.Id+' ---'; $_.Message } }" run_pwsh


[AI Proposes Forth Code]
Purpose: 核對反覆 Windows Update 錯誤及 System log 中錯誤事件的重複來源，補足是否只是更新時檔案被使用的暫時性問題。
Source:
s" $since=(Get-Date).AddDays(-7); $e=@(Get-WinEvent -FilterHashtable @{LogName='System'; Id=20; StartTime=$since} -ErrorAction SilentlyContinue | Where-Object ProviderName -eq 'Microsoft-Windows-WindowsUpdateClient' | Select-Object -First 10); foreach($x in $e){ '--- '+$x.TimeCreated+' ---'; $x.Message }; '--- Repeated IDs/counts ---'; Get-WinEvent -FilterHashtable @{LogName='System'; Level=2; StartTime=$since} -ErrorAction SilentlyContinue | Group-Object ProviderName,Id | Sort-Object Count -Descending | Select-Object -First 10 Count,Name | Format-Table -AutoSize" run_pwsh


[AI Proposes Forth Code]
Purpose: 釐清重複 BitLocker 事件是否只是非預期關機後的保護狀態警告，並查看目前磁碟保護狀態和近期更新事件；均為唯讀。
Source:
s" $since=(Get-Date).AddDays(-7); $events=Get-WinEvent -FilterHashtable @{LogName='System'; Id=24641; StartTime=$since} -ErrorAction SilentlyContinue | Select-Object -First 3; foreach($e in $events){'--- '+$e.TimeCreated+' ---'; $e.Message}; '--- Current BitLocker state ---'; Get-BitLockerVolume -ErrorAction SilentlyContinue | Select-Object MountPoint,VolumeStatus,ProtectionStatus,EncryptionPercentage | Format-Table -AutoSize; '--- Current update status ---'; Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-WindowsUpdateClient/Operational'; StartTime=(Get-Date).AddDays(-3)} -MaxEvents 5 -ErrorAction SilentlyContinue | Select-Object TimeCreated,Id,Message | Format-List" run_pwsh


╭─ 🪄 peforth ────────────────────────── OpenAI │ gpt-6-luna ──╮
  我檢查了最近 7 天的 **System** 和 **Application** 事件記錄；查詢是唯讀的，沒有更改系統或清除日誌。

  **值得留意的項目：**

  - **Acer Care Center 當機**：11 月 24 日，`ACCStd.exe` 發生未處理的 .NET `InvalidOperationException`，堆疊指向 Wi-Fi 裝置清單更新。若 Acer Care Center 常常當機，可考慮更新或修復它；若只有這一次，暫時不像系統層級故障。
  - **Windows Store app 更新曾遇到錯誤 `0x80073D02`**：事件指向 OpenAI Codex、Phone Link、Notepad 等 app；這通常表示更新時 app 檔案正在使用中。最新的 Windows Update Operational 記錄又顯示更新已下載，較像暫時性更新失敗，可先重新啟動後觀察是否重複。
  - **BitLocker 事件 24641**：11 月 24 日短時間內有多筆事件，訊息提到非預期關機時的保護行為。`Get-BitLockerVolume` 這次沒有回報磁碟狀態，因此我無法據此確認磁碟目前是否已加密或保護中；若這是公司或重要工作電腦，建議另外確認 BitLocker 狀態與復原金鑰備份。
  - 另有少量 **DistributedCOM、VSS、Steam／Maps Manager 服務**錯誤；從目前看到的紀錄，未能判斷它們代表持續性問題。

  **總結：**這 7 天查到 **0 筆 Critical**；System 有 **42 筆 Error**，Application 有 **12 筆 Error**。錯誤數量不等於有 54 個獨立故障，其中更新和服務類事件可能是暫時或背景事件。較明確值得追蹤的是 Acer Care Center 當機，以及確認 BitLocker 是否正常啟用。
╰─────────────────────────────────────── 2026-11-26 03:21:25 ──╯
chat>
```

## What this demonstrates

- The AI finds a relevant host capability and proposes PowerShell through the `run_pwsh` Forth word.
- `run_pwsh` is unsafe, so peforth requests human approval before the proposed system inspection runs.
- The investigation proceeds iteratively: a broad scan, corrected/query refinements, detailed event review, and targeted checks for Windows Update and BitLocker.
- The queries are described as read-only; the final answer distinguishes confirmed observations from items that could not be verified.
- The summary gives practical follow-up suggestions without treating every logged error as a separate system fault.

The conversation transcript is preserved as captured; the explanatory section is added as tour-guide context.

## Try it

Ask peforth: `檢查這台 Windows 電腦的 Event Log，看看有沒有什麼需要注意的問題。`
