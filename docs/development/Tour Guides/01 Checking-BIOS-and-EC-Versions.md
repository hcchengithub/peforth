# Tour Guide: Checking BIOS and EC Versions

This tour guide demonstrates a real peforth interaction: asking the AI to check BIOS and Embedded Controller (EC) versions, proposing a read-only system query, requesting approval for an unsafe word, and reporting the result. The conversation below is reproduced verbatim.

## Conversation

```text
chat> 檢查 BIOS 的版本以及 EC 的版本
╭─ 👋 user ────────────────────────────────────────────────────╮
  檢查 BIOS 的版本以及 EC 的版本
╰─────────────────────────────────────── 2026-11-26 02:54:18 ──╯

[AI Tool] Searching dictionary for: 'Windows system hardware BIOS version EC firmware version PowerShell WMI CIM'...

[AI Proposes Forth Code]
Purpose: 以唯讀 PowerShell/CIM 查詢目前 Windows 電腦的 BIOS 資訊，並嘗試從標準 PnP 裝置資訊辨識 EC firmware 版本。
Source:
s" $bios = Get-CimInstance Win32_BIOS | Select-Object Manufacturer, SMBIOSBIOSVersion, Version, ReleaseDate; $bios | Format-List; $ec = Get-CimInstance Win32_PnPEntity | Where-Object { $_.Name -match 'Embedded Controller|EC Firmware' }; if ($ec) { $ec | Select-Object Name, Manufacturer, PNPDeviceID | Format-List } else { 'EC firmware version: not exposed by standard PnP query' }" run_pwsh


[Security] Approval required — Word: run_pwsh
1. Allow Once
2. Trust this AI task
3. Deny this proposal
4. Cancel this AI task

Choose 1-4: 2

╭─ 🪄 peforth ────────────────────────── OpenAI │ gpt-6-luna ──╮
  查到的 BIOS 資訊：

  - **廠牌：** Predator
  - **BIOS 版本：** 1.06
  - **版本識別：** `ACRSYS - 1072009`
  - **發布日期：** 2025-12-26

  **EC 版本**無法透過這次查詢到的標準 Windows CIM／PnP 資訊確認；系統沒有公開可辨識的 EC firmware 版本欄位。
╰─────────────────────────────────────── 2026-11-26 02:54:32 ──╯
chat>
```

## What this demonstrates

- The AI searches the live Forth dictionary for relevant capabilities.
- It proposes Forth source that invokes a host PowerShell command through `run_pwsh`.
- Because `run_pwsh` is unsafe, peforth pauses and requests human approval before execution.
- The selected option, “Trust this AI task,” authorizes subsequent unsafe operations for that task.
- The query reports the BIOS details and clearly states that the EC firmware version was not available through the standard query.

The transcript above is kept verbatim; this explanatory section is tour-guide context.

## Try it

Ask peforth: `檢查 BIOS 的版本以及 EC 的版本`


---

# 產生以上教材的原始 prompt

```
p e f o r t h   v 2
2.1.0 - Runtime modified: 2026-11-26 02:24:32

Talk with our GitHub repo using Copilot for help, code samples, and the whys behind peforth.
Chat with AI directly. Type '/help' for instructions, '/forth' for Forth mode.

[Enter] submits / [Ctrl+J] adds a line / [Esc] interrupt.

chat> herdr: w5:pN 最後一輪問答是檢查 BIOS 和 EC 的版本，我
  要利用這個實際的場景來寫成 tour guide。你利用那段對話原原本本、都不要經過任何修改，把它改寫成 tour guide 存到這裡: 
  "%userprofile%\Documents\GitHub\peforth\docs\development\Tour Guides\<filename>.md" 
  其中 filename 你幫我想。我希望利用這個方式來示範給我們的 user 看，我們有哪些功能。
```  
  