
[ ] 09:56 2026-10-29 我現在懷疑免批准去查看別的 pane 是有必要的，但寫出這麼多 words 可能沒有必要。
    應該用 herdr skill 就可以了，沒必要寫這麼多東西出來 :-( 

# GitHub copilot 介紹 peforth 'computer use'

> 網頁上來到 [GitHub peforth 的 master branch](https://github.com/hcchengithub/peforth) 即可用 GitHub Copilot 與 peforth 交談。以下是詢問 peforth 的 "computer use" 功能得到的回答。測試過都正確！
 
下面這份是最小、可直接試的 peforth computer-use 範例，重點是「在 Herdr-managed pane 裡讀/寫/執行」。[**Herdr** 是為了 AI 而生的下一代 Tmux](https://github.com/herdrdev/herdr) - 讓 Terminal、Shell、Bash、PowerShell 這些工作環境變得非常好用，而且很適合 AI.

先說前提：
- 你要在 [Herdr](https://github.com/herdrdev/herdr) 環境裡執行 peforth
- `herdr` CLI 必須可用
- 程式必須帶有 `HERDR_ENV=1` 和 `HERDR_PANE_ID`
- 你要明確知道目標 pane ID，例如 `w1:p2`

如果你已經在 Herdr 環境中啟動 peforth，這些範例可以直接貼進 `f` REPL：

1) 看當前 pane
```forth
herdr-current-pane .
```

2) 讀當前 pane 的可見畫面
```forth
herdr-current-pane
80 herdr-screen-read
```

如果你想指定 pane：
```forth
s" w1:p2" 80 herdr-screen-read
```

這會回傳一個 snapshot 結構，像是：
```forth
{ "pane_id": "w1:p2", "source": "visible", "text": "...", ... }
```

3) 讀最近輸出（tail）
```forth
s" w1:p2" 80 herdr-screen-tail
```

4) 往 pane 發送文字
```forth
s" w1:p2" s" echo hello from peforth" herdr-screen-send-text
```

5) 往 pane 發送鍵盤操作
例如 Ctrl+A 然後 Enter：
```forth
s" w1:p2" s" ctrl+a" herdr-screen-send-keys
s" w1:p2" s" enter" herdr-screen-send-keys
```

如果你要兩個鍵同時：
```forth
s" w1:p2" 2array
  s" ctrl+a"
  s" enter"
herdr-screen-send-keys
```

注意：repo 的註解裡有示例是使用 stack style：
```forth
char w2:p4 char ctrl+a char enter -2 slice herdr-screen-send-keys
```
這是更低階的 Forth 寫法；你先用字串版比較直覺。

6) 在 pane 裡執行命令
```forth
s" w1:p2" s" pwd && ls" herdr-screen-run
```

7) 直接用 AI tool 風格（如果你在 AI chat 模式）
```forth
ai: Read the visible text from pane w1:p2 and tell me what the app is showing
```

這時 peforth 會發現你用的是 `computer_read_screen` 這類工具，並且依規則請求 approval。

我給你一份更完整的「可執行」腳本版，直接貼進 REPL：

```forth
\ 先看現在的 pane
herdr-current-pane . cr

\ 讀畫面
s" w1:p2" 80 herdr-screen-read . cr

\ 讀尾巴
s" w1:p2" 80 herdr-screen-tail . cr

\ 傳文字
s" w1:p2" s" ls" herdr-screen-send-text . cr

\ 送鍵盤
s" w1:p2" s" ctrl+a" herdr-screen-send-keys . cr
s" w1:p2" s" enter" herdr-screen-send-keys . cr

\ 執行命令
s" w1:p2" s" echo hello-from-peforth" herdr-screen-run . cr
```

如果你要讓 AI 自動化，這是最像「computer use」的實際用法：
```forth
chat
ai: Read pane w1:p2 and tell me the current terminal output.
ai: In pane w1:p2, run `pwd && ls -la` and summarize the result.
```

一個實用提醒：
- `computer_read_screen` / `computer_operate` 需要「live Herdr-managed caller」
- 這不是桌面軟體自動點擊，而是 terminal pane 自動化
- 會要求 approval，這是 repo 設計
- `send_keys` / `run` 會比 `read` 更有風險，repo 明確要求更嚴格的 approval

如果你要，我下一步可以直接幫你做一份：
- 「在 WSL / Ubuntu 下跑 peforth + Herdr 的最小 setup」
- 或「一份從 shell 到 REPL 的完整測試清單」讓你一步步驗證這套功能是否真的在你機器上工作。
