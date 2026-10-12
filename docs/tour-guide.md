# peforth Forth 新手快速導覽

這份導覽帶你用幾分鐘開始操作 peforth v2。不用先讀 VM 原始碼，也不用先學 Python；只要跟著輸入幾個例子，就能掌握 Forth 最重要的思考方式：**資料在 stack 上流動，word 依序取用 stack 上的資料並把結果放回去。**

> 本導覽以 `f` 載入 `base.f` 後的完整互動環境為準。peforth 共用 kernel 刻意保持精簡；像 `+`、`dup`、`:`、`if` 等常用 word 都是啟動時從 `base.f` 載入的擴充字典。

## 1. 啟動 Forth

先依 repository 根目錄 `README.md` 完成 editable install，之後可在任意工作目錄啟動 `f`：

```bash
f
```

看到 `peforth Forth REPL` 和 `>` 提示字元後，就可以輸入 Forth。離開請輸入 `bye`，或在 Linux / WSL 按 `Ctrl+D`。

不進互動介面也能直接執行一段程式：

```bash
f -e 10 20 + . cr
```

預期會印出 `30`。以下 Forth 範例請在 REPL 中逐段輸入（每個程式碼區塊視為一次輸入），或整理成 `.f` 檔再執行；用 `-e` 時，請將需解析行尾的 `py>>` 放在該次輸入的最後一行。

若想執行後繼續使用同一個 VM，可在 `-e` 前加 `-i`：`f -i -e 10 20 + . cr`。`-e` 後的所有參數會以單一空格連接成一份 TIB；`-h` 可查看命令列說明。

## 2. 關鍵觀念：Forth 使用後綴順序

一般數學寫法是 `10 + 20`；Forth 先放運算元，再呼叫運算 word：

```forth
10 20 +
```

可以把它想成一疊盤子：數字依序放上去，word 從頂端取需要的值。執行後，結果留在 stack 上。輸入 `.s` 檢視 stack（不會取走資料）；輸入 `.` 印出並取走最上面的值；`cr` 換行。

在 REPL 試試：

```forth
10 20 + .s
.
cr
```

結果先顯示 stack 中的 `[30]`，接著 `.` 印出 `30` 並將它移除。每次按 Enter 都會執行輸入，但資料 stack 會保留在同一個 VM 裡；所以實驗時可用 `drop` 移除一個值，或用 `dropall` 清空。

基本算術與比較：

```forth
8 3 - . cr       \ 5
8 3 * . cr       \ 24
8 2 / . cr       \ 4（兩個整數相除會做整數向下取整）
5 3 > . cr       \ True
```

Forth 的 `\` 是單行註解；它後面的內容到該行結束都會忽略。也可以用 `( ... )` 寫區塊註解。

## 3. 學會看懂 stack 與 Stack Effect

常見 stack 操作：

| Word | 效果 | 說明 |
| --- | --- | --- |
| `dup` | `( x -- x x )` | 複製頂端值 |
| `drop` | `( x -- )` | 丟掉頂端值 |
| `swap` | `( a b -- b a )` | 交換頂端兩值 |
| `over` | `( a b -- a b a )` | 複製倒數第二個值 |
| `rot` | `( a b c -- b c a )` | 將第三個值轉到頂端 |
| `nip` | `( a b -- b )` | 移除倒數第二個值 |

括號中的 `--` 左邊是執行前、右邊是執行後；最右邊的值在 stack 最頂端。例如：

```forth
10 3 swap .s
```

stack 會是 `[3, 10]`，因此 TOS（頂端值）是 `10`。理解每個 word 需要哪些輸入、留下哪些輸出，是讀懂 Forth 的最快方法。

## 4. 把一串操作命名：定義自己的 word

用 `: 名稱 ... ;` 建立新 word。下面定義平方：

```forth
: square ( n -- n² ) dup * ;
```

現在可像內建 word 一樣使用它：

```forth
9 square . cr
```

結果是 `81`。定義中的 `dup` 複製 n，`*` 取走兩份 n 並留下乘積。word 定義完成後會留在字典中，可在後續輸入重複使用，也能拿來組合更大的 word：

```forth
: fourth-power square square ;
3 fourth-power . cr
```

結果是 `81`。在定義後加註解可讓它被 `help` 搜尋：

```forth
: cube ( n -- n³ ) dup dup * * ; // 計算立方
/// 複製輸入兩次，再連乘三個相同的數。
```

`//` 為單行說明，`///` 可累積多行說明；兩者都要放在要說明的定義完成後。接著輸入 `help cube` 看說明，或 `see cube` 看定義、資訊與可還原的 Forth 內容。

> 小提醒：word 名稱大小寫有別；`square` 和 `Square` 是不同名稱。

## 5. 字串、輸出與互動探索

用 `s" ..."` 將字串放到 stack，再用 `.` 印出：

```forth
s" Hello, Forth!" . cr
```

如果字串內含雙引號，可改用其他定界字：`s' ...'`、`s`...``、`s|...|`、`s^...^`、`s/.../`。例如：

```forth
s' 她說 "你好"' . cr
```

探索字典的常用工具：

```forth
words              \ 列出所有 words
words stack        \ 搜尋名稱含 stack 的 words
help dup           \ 查 word 說明
see dup            \ 檢視 word 資訊與定義
```

`help` 與 `words` 可用多個關鍵字過濾；比起背下所有命令，遇到不熟的 word 時查詢它會更有效率。

## 6. 條件與迴圈

條件式使用 `if ... else ... then`。條件由比較 word 產生；真值走 `if` 區塊，假值走 `else` 區塊：

```forth
: abs-value ( n -- n )
    dup 0 < if
        0 swap -
    then ;

-7 abs-value . cr
```

結果是 `7`。若要兩種情況都處理：

```forth
: sign ( n -- text )
    dup 0 < if
        drop s" negative"
    else
        0 > if s" positive" else s" zero" then
    then ;
```

計數迴圈可用 `for ... next`。`r@` 讀取目前迴圈計數，不會將它從 return stack 移除：

```forth
: sum-down ( n -- sum )
    0 swap for r@ + next ;

5 sum-down . cr
```

結果是 `15`（5 + 4 + 3 + 2 + 1）。此實作的 `for` 依指定次數循環；迴圈計數器放在 return stack。一般初學時先熟悉 `if` 和 `for` 即可，之後再看 `begin ... until`、`begin ... while ... repeat`。

## 7. 命名資料：constant、variable、value

定義常數：

```forth
42 constant answer
answer . cr
```

定義可讀寫的變數：

```forth
variable counter
counter @ . cr       \ 初始值為 0
42 counter !         \ 將 42 存入 counter
counter @ . cr       \ 讀回 42
```

`@` 讀取、`!` 寫入，順序是「值、位置」：`42 counter !`。定義可重新指定的 `value`：

```forth
10 value total
total . cr
25 to total
total . cr
```

`constant` 不可用 `to` 改值；`value` 可以。初學階段可以先記：`variable` 放需要反覆更新的資料，`constant` 放固定值，`value` 放可替換的單一值。

## 8. 借用 Python：peforth 的 Host Bridge

peforth 的 stack 可以保存 Python 物件；Python 程式碼可直接使用目前 VM 提供的 host 環境。最簡單的 Python 表達式寫法是 `py>>`，它會讀取該行剩餘內容、求值並把結果放到 Forth stack：

```forth
py>> 2 + 3
.s
```

接著可用 `:>` 呼叫頂端 Python 物件的方法，並把回傳值放回 stack：

```forth
s" hello" :> upper() . cr
```

輸出 `HELLO`。也可以呼叫 Python 標準函式庫：

```forth
py>> __import__('math').sqrt(144)
. cr
```

輸出 `12.0`。`:>` 會消耗原本的物件並將呼叫結果推回 stack；`::` 則用於不需要回傳值的方法或操作。更大的 Python 程式可用 `<py> ... </py>`，要把 Python 表達式結果推上 stack 則用 `<py> ... </pyV>`。Python bridge 執行的是一般 Python 程式，具備目前程序的權限；只執行你信任的程式碼。

## 9. 暫停與恢復：進階的 Python Host 功能

Forth 的 `pause` 可讓目前 Task 暫停，之後由 Python host 呼叫同一個 Task 的 `resume()` 接續執行。它是協作式執行能力，不是一般 REPL 的 `resume` 指令；目前 `repl.py` 會顯示 `Task: paused`，但不提供互動式恢復該 Task 的命令。需要管理暫停 Task 時，請從 Python 程式呼叫 `create_vm()`，保存 `vm.dictate(...)` 回傳的 Task，再呼叫 `task.resume()`。未暫停的 Forth 初學練習不需要此功能。

## 10. 初學者練習路線

照順序完成以下練習，並用 `.s` 檢查每一步：

1. 計算 `(12 + 8) * 3`：先把兩個值相加，再乘以 3。
2. 定義 `double`，讓 `double` 將頂端數字乘以 2；用它計算 `21`。
3. 定義 `triple`，只用已經學會的 stack 操作與 `*`，計算 `7` 的三倍。
4. 建立 `variable visits`，將它設為 `1`，再寫一個 word 每次呼叫就加一，確認呼叫三次後是 `4`。
5. 搜尋 `words string`，再用 `help` 和 `see` 探索其中一個結果。

建議解題節奏：先把預期 stack 狀態寫下來，再選 word；遇到不確定的 word 就查 `help`。如果 stack 留有上一題的值，可先執行 `dropall`，讓下一題從乾淨狀態開始。

## 11. 出錯時怎麼辦

- `Unknown input` / `Unknown word`：檢查名稱拼字、大小寫，以及是否已用 `:` 定義。
- `Data stack is empty`：某個 word 需要的輸入不足；用 `.s` 檢查目前 stack。
- 定義未完成：確認 `:` 後有名稱，並以 `;` 結束。
- `!` 或 `@` 順序錯誤：記得 `!` 是 `value address !`，`@` 是 `address @`。
- 想重新開始一輪運算但不想重啟 REPL：輸入 `dropall` 清空資料 stack；已定義的 words 仍會保留。

更多啟動方式與環境設定請看 repository 根目錄的 `README.md`；深入核心設計請看 [`manual-py.md`](manual-py.md)。如果你想驗證整套 Python 實作，可在專案根目錄執行：

```bash
# Linux / WSL
python3 -m unittest discover -s tests -v

# Windows PowerShell / CMD
py -3 -m unittest discover -s tests -v
```
