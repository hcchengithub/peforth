# peforth v2 共用 Forth Kernel 技術手冊與架構設計理念

> **版本**：16:32 2026-10-08
> **適用環境**：Python 3.10+ / Linux, WSL, Windows  
> **核心代碼**：`peforth/projectk.py`, `peforth/repl.py`, `peforth/f/base.f`

---

## 序言：重構極簡主義的威力

在電腦科學的演進史中，Forth 代表著一種登峰造極的極簡美學：以 stack 為核心的虛擬機、零語法開銷、純粹的後綴表示法，以及完全開放編譯器內部狀態的 Metaprogramming 威力。然而，傳統 16-bit 與裸機 (Bare-metal) 時代的 Forth 體系，在現代軟體工程中卻逐漸陷入孤島困局——封閉的平坦位元組記憶體空間、薄弱的原生資料結構、缺乏現代型別系統，以及無法直接調用海量第三方軟體庫的窘境。

**peforth (Python Edition)** 的誕生，並非為了在現代作業系統中復刻一套 1980 年代的骨董模擬器，而是為了探索一個全新的架構範式：  
**當 Forth 的多 Stack 拓撲與 Metaprogramming 靈魂，直接運行於 Python 這種具備豐富物件生態與動態特性的 Host Language 之上，會帶來何種可能？**

本手冊是 peforth 的系統架構指南與設計理念記錄。本手冊**不做**傳統 Forth 語法的入門字典（各 Word 本身已內建 `help` 與 `comment` 自我文檔），而是深入剖析 peforth 如何用一個僅數百行程式碼的微核心，在動態物件世界中重建純粹的 Forth 哲學，並徹底解構傳統非同步編程的沉重枷鎖。

> [!TIP]
> **想直接動手跑起來？**  
若您希望立即在終端機操作、執行互動 REPL 或設定 checkout 的 `f` entry point，請參閱 repository 根目錄的 `README.md`（如何執行指南）。
> 本手冊（Manual）聚焦 peforth 的架構設計理念；安裝與環境配置請以 repository 根目錄的 `README.md` 為準。

---

## 第一章：設計理念與架構概述 (Design Philosophy & Architecture)

### 1.1 傳統 Forth 的困局與 peforth 的解方

傳統 Forth（如 FIG-Forth、Forth-79/83 與 ANS Forth）具備驚人的執行效率與自我延展性，但在現代計算環境中面臨三大根本瓶頸：

1. **Flat Memory 記憶體沙盒的局限**：傳統 Forth 假設全系統運作在一個線性位址空間（通常是 64KB 的 byte array）。這在裸機微控制器上十分自然，但在具備垃圾回收機制 (GC)、高階物件導向與虛擬記憶體的現代 Host 上，強行模擬 flat memory 只是在沙盒裡畫地為牢，無法直接共享 Host 的高階物件。
2. **型別系統與資料結構的匱乏**：傳統 Forth 的 stack 單元本質上只是單純的 cell（整數或指標）。處理多維陣列、雜湊表 (hash map)、多型物件或動態字串時，程式設計師必須從頭用記憶體位移自行實作，代碼難以維護。
3. **生態系割裂**：現代工程的生產力建立在第三方庫（科學計算、機器學習、網路協定、作業系統 API）之上。如果一個語言無法零成本地直接調用這些庫，就只能淪為玩具。

**peforth 的核心破局之道：共生微核心 (Symbiotic Micro-Kernel)**
* **拋棄沙盒，共享物件空間**：peforth 的 stack 上流轉的不再是單純的 16-bit/32-bit 位元組，而是**活生生的 Python 物件參照**（整數、浮點數、字串、清單、字典、生成器乃至自訂 class 實例）。
* **機制在 Forth，能力在 Host**：Forth 保留其無可匹敵的流程中樞控制力、自訂 DSL 能耐與 Metaprogramming factory；而重型運算、系統 API、字元編碼與巨量庫則直接由 Python 全權支撐。

---

### 1.2 多 Stack 虛擬機架構 (Multiple-Stack VM)

peforth 以多個 stack 分工保存運算資料與 Task-local 控制狀態：Data Stack 在 VM 間共享；Return Stack 與 T-stack 則各自屬於目前 Task。

```mermaid
flowchart TB
    subgraph VM ["VM Instance"]
        direction LR
        subgraph DS ["Data Stack (vm.stack)"]
            direction TB
            D1["TOS (Top of Stack)"]
            D2["..."]
            D3["Python Objects (運算元參照)"]
            D1 --- D2
            D2 --- D3
        end
        subgraph RS ["Return Stack (rstack)"]
            direction TB
            R1["TOR (Top of Return Stack)"]
            R2["Loop Counters (迴圈計數)"]
            R3["Task-local return values (Task 私有值)"]
            R1 --- R2
            R2 --- R3
        end
        subgraph TS ["T-stack (task.tstack)"]
            direction TB
            T1["TOS (Top of T-stack)"]
            T2["TIB offsets / Task-local values"]
            T1 --- T2
        end
    end
```

1. **Data Stack (`vm.stack`)**：
   * 運算元的流通中心與參數傳遞管線。
   * 物理實作為 Python 原生 `list`。所有的推入 (`push`) 與彈出 (`pop`) 均受到邊界保護；當 stack 為空而嘗試 pop 時，由 Python 層級直接拋出明確的 `ForthError("Data stack is empty")`，杜絕記憶體隨機損毀。
2. **Return Stack (`rstack`)**：
   * **Task Private 私有資源**：每個 Task 擁有專屬獨立的 `rstack`（物理存儲於 `Task.rstack`，透過 `vm.rstack` 代理動態路由至當前活躍 Task）。
   * 用於計數迴圈計數器暫存（如 `for ... next`）與程式流程的臨時中轉（`>r`, `r>`, `r@`, `rdrop`）。
   * 即使某個 Task 在迴圈內部呼叫 `pause` 暫停，其迴圈狀態與計數器仍安穩封裝於該 Task 的私有 `rstack` 中；其他 Task 擁有自己的 `rstack`，彼此不會踩踏。
3. **T-stack (`tstack`)**：
   * **Task Private 私有資源**：每個 Task 擁有自己的 `Task.tstack`，可存放 TIB 游標 offset 等一般值。
   * Forth words `>t`、`t@`、`t>` 分別將 Data Stack 頂端移入、複製 T-stack 頂端、及將 T-stack 頂端移回 Data Stack。

#### Stack Effect 標記慣例
在無型別語法的後綴世界中，Stack Effect 註釋是理解程式不變式的命脈。peforth 以標準形式標示各 stack 的輸入與輸出：
```forth
\ 單純操縱 Data stack
( a b -- c )

\ 跨越 Data stack 與 Return stack
( x -- ) ( R: -- x )

\ 操縱 Task-local T-stack
( x -- ) ( T: -- x )

\ 同時標示 Data 與 Return stack
( n1 n2 -- n3 | R: count -- count-1 )
```
* `--` 左側代表執行前的 stack 狀態；右側代表執行後的 stack 狀態。
* 頂端元素 (Top of Stack, TOS) 位於最右側。
* 常用約定符號：`n` (整數/數值), `flag` (布林值), `x` (任意物件), `str` (字串), `addr` (清單或索引位址)。

---

### 1.3 核心執行模型與生命週期

peforth 的 Outer Interpreter 擁有極致簡明的狀態循環：

```mermaid
flowchart TD
    In["Input Stream (Text / Tokens)"] --> Tokenizer["vm.input.read() Tokenizer"]
    Tokenizer --> CheckDict{"Word 存在於字典？"}
    
    CheckDict -- "是 (Yes)" --> CheckImm{"word.immediate?"}
    CheckImm -- "否 (編譯模式)" --> CompileWord["編譯 Word: vm.comma(word)"]
    CheckImm -- "是 (即時執行)" --> ExecWord["執行 Word: call(word)"]
    
    CheckDict -- "否 (No)" --> TryNum["嘗試數值解析 (int / float)"]
    TryNum --> CheckComp{"編譯狀態 vm.compiling?"}
    CheckComp -- "否 (直譯模式)" --> PushStack["推入 Data Stack: vm.push(val)"]
    CheckComp -- "是 (編譯模式)" --> CompileLit["編譯字面量: vm.literal(val)"]
    
    CompileWord --> NextToken["下一輪 Token 循環"]
    ExecWord --> NextToken
    PushStack --> NextToken
    CompileLit --> NextToken
```

* **直譯模式 (`vm.compiling = False`)**：
  遇到 Word 立即執行；遇到數值立即推入 Data stack。
* **編譯模式 (`vm.compiling = True`)**：
  遇到普通 Word，將其編譯至正在構建的 Word 指令列中 (`vm.comma(word)`)；
  遇到 `immediate` Word（如 `;`, `if`, `s"`），**打斷編譯直接執行該詞**，賦予其在編譯期操縱編譯器行為的 Metaprogramming 能力；
  遇到數值，自動包裝為字面量指令編譯進指令列 (`vm.literal(value)`)。

---

### 1.4 核心組件與工程架構

系統組件依職責分工如下：

| 組件檔案 | 定位 | 職責與邊界 |
| :--- | :--- | :--- |
| `peforth/projectk.py` | 共用 Forth Kernel | 包含 `Input` 串流解析器、`_Word` 核心結構、`Task` 狀態機、`VM` 容器，以及原生 Python 代碼塊 (`code ... end-code`) 的語彙編譯機制。不預載任何高階 Forth 詞彙，純粹、輕量且原生支援 Coroutines。 |
| `peforth/f/base.f` | Bootstrap 字典 | 以 Forth 撰寫的核心字典，包含控制結構、字串家族、Defining Words、`does>`、三階段 `see` 與 Python Host Bridge。 |
| `peforth/f/auxiliary.f` | 輔助字典 | Forth 優先的非核心工具 words，例如 `cls` 和 `stringify`。 |
| `peforth/f/ai.f` / `peforth/ai_bridge.py` / `peforth/ai_tools.py` | AI 擴充 | `ai.f` 以 Forth code words 與 colon words 實作 AI 介面、主要流程及本機工具 words；`ai_bridge.py` 保留 Agents API 傳輸與 session 檔案功能；`ai_tools.py` 提供程序執行及 HTTP 傳輸等 Python 專屬功能。 |
| `peforth/repl.py` | 執行期與 REPL | 負責環境裝配、啟動時偵測 host/System Info、載入 package resources、安裝 host primitives、載入輔助與 AI Forth 字典，以及 REPL 輸入處理。 |

---

## 第二章：串流解析、語彙分析與界定機制 (Stream Parsing & Lexical Architecture)

### 2.1 輸入串流模型 (Input Stream Architecture)

在 `peforth/projectk.py` 中，每個輸入上下文由單一 TIB 字串與字元 offset 表示：

```python
@dataclass
class Input:
    tib: str
    itib: int = 0
```
* `tib`：完整的 Terminal Input Buffer 字串；已讀文字保留在原處。
* `itib`：下一個要讀取字元的 offset。
* `append(text)`：將文字加到 TIB 尾端，不移動 `itib`；已有 Task 在暫停狀態時，可透過 `task.append_input(text)` 追加後再 `resume()`。
* `consume(count)`：由目前 offset 前進指定字元數並回傳消耗文字。
* `read()` / `read(until=delim)`：從目前 offset 讀取 token 或定界區域，並推進 offset。
* `rest()`：回傳目前 offset 到 TIB 尾端的文字，並將 offset 移至尾端。

Forth 的 `tib.append` 會把資料堆疊上的字串加到目前 TIB 尾端，前置一個空格作為 token 分隔；Task 到達 EOF 並完成後不會因追加文字而復活。

#### 註解的即時跳越
藉由 `Input` 的可塑性，註解 Word 均被標記為 `immediate`，在讀取當下即時消耗串流，完全不參與編譯：
* `\ `：單行註解，即時前進游標至下一行的開頭。
* `( ... )`：區塊註解，直接調用 `vm.input.read(until=")")` 吞沒內容。
* `//` 與 `///`：分別將行內說明與詳細多行註解直接附加於 `vm.last().help` 與 `vm.last().comment` 上，使 Word 具備原生自文檔能力。

---

### 2.2 為什麼 Host Tokenizer 能解決邊界模糊問題？

在 Forth 擴充原生代碼時，最危險的陷阱莫過於代碼塊定界符的混淆。在 `code ... end-code` 的設計中，我們必須判定「哪裡是代碼塊的真正終點」。

#### 傳統文字搜尋的致命漏洞
若使用單純的字串搜尋或正則表達式比對 `end-code`：
```python
code sample
    # 警告：這個註解包含 end-code 關鍵字！
    debug_msg = "這是一個字串常數，裡面也有 end-code 標記"
    print(debug_msg)
end-code
```
傳統的正則搜尋在掃描到第一行註解 `# ... end-code` 或字串常數時，就會**誤以為代碼塊已結束**，導致後半段程式碼被丟給 Forth 直譯器執行，瞬間引發不可收拾的語法崩潰！

#### Python 原生語彙分析器的降維打擊
peforth 的破局點在於：**讓 Host 的 Lexer 來審查 Host 的程式碼！**  
在 `VM._find_code_terminator` 中，核心直接引入 Python 標準庫的 `tokenize.generate_tokens`：

```python
for token in tokenize.generate_tokens(io.StringIO(text).readline):
    # 逐一檢視語彙 token
```
因為 `tokenize` 模組是 Python 編譯器本身的語彙前端，它原生就能識別：
* `tokenize.COMMENT`（註解內部文字）
* `tokenize.STRING`（字串常數內部文字）
* `tokenize.NAME` 與 `tokenize.OP`（真正的語法標記）

當且僅當 `end`、`-`、`code` 出現在頂層且非字串、非註解的代碼位置時，peforth 才確認找到真正的定界邊界！**這種直接借力 Host 語彙分析器的架構，徹底杜絕了代碼邊界判定失效的長年痛點。**

---

### 2.3 動態定界符與 Extensible Parsing 機制

在傳統語言中，字串遇到包含雙引號時往往必須寫成繁瑣的跳脫符號（如 `\"` 或 `\'`），這在編寫正則表達式或 JSON 時被稱為「跳脫字元地獄 (Escaping Hell)」。

peforth 在 `base.f` 中透過 Metaprogramming 打造了一整套字串定界符族群：

```forth
: string-quote ( delim <name> -- )
    create , immediate
does> ( -- string )
    @ (s) ;
```

利用這個 factory，系統一氣呵成定義了六種常用字串定界詞：
* `s"`：以 `"` 結尾。
* `s'`：以 `'` 結尾（適合內部包含雙引號的字串）。
* <code>s&grave;</code>：以反引號結尾。
* `s|`：以管線符 `|` 結尾（極度適合包含各種引號的正規表達式或 HTML 標籤）。
* `s^`：以脫字元 `^` 結尾。
* `s/`：以斜線 `/` 結尾（適合路徑字串）。

在直譯模式下，它們直接將字串物件推入 Data stack；在編譯模式下，自動生成字面量指令。這完美展現了「擴充解析器不需要改動編譯器核心，只需用 Forth 定義新 Word」的延展思路。

---

## 第三章：記憶體模型、動態串流與 PAD 架構 (Memory, Streams & The PAD Concept)

### 3.1 告別 Flat Memory：現代物件導向 Data Space

在傳統 Forth 系統中，`here` 是一個指向 RAM 位元組的整數指標，`,` (comma) 是將數值拷貝進實體記憶體。  
在 peforth 裡，這個概念被現代物件模型昇華：

1. **Word 的資料載體是 Python List**：  
   由 `create` 建立的 Word，其內部包含一個專屬的 `body = []` 清單。
2. **`@` (fetch) 與 `!` (store) 的現代多型語義**：
   ```python
   code !
       addr = vm.pop()
       val = vm.pop()
       if isinstance(addr, list):
           if not addr: addr.append(val)
           else: addr[0] = val
       elif isinstance(addr, int):
           if vm.compiling: vm._definition.body[addr] = val
   end-code
   ```
   * 當 `addr` 是一個 Python `list` 時（例如 Word 的 `body`），`!` 與 `@` 直接讀寫該 list 的第一個元素 `addr[0]`！
   * 這使得 `variable` 與自訂結構不需要計算實體位元組偏移量，直接享有 Python 原生垃圾回收機制維護物件生命週期。
   * **非首元素存取與切片 (Indexing & Slicing)**：  
     在傳統 Forth 中，連續存取陣列必須依賴指標算術（如 `addr 1 CELLS + @`）。但在 peforth 中，Word 的 `body` 是真實的 Python `list`，若強行使用數值加法運算（如 `xx 1+ @`）會直接被 Python 攔截型別錯誤。  
     正確且優雅的做法是直接透過 Host Bridge 的 `:>` 享受 Python 原生索引與切片：
     ```forth
     create xx 123 , 456 ,
     xx @ .         \ 輸出: 123 (取出首元素)
     xx :> [1] .    \ 輸出: 456 (直接索引第二項)
     xx :> [1:] @ . \ 輸出: 456 (切片產生子清單後，交由 @ 取出首項)
     ```
     這清晰展示了 Forth stack 資料流與 Python 切片運算式的混血之美。

---

### 3.2 編譯期位址概念與回填

在編譯期，`here` 被賦予了精準的架構意義：
* `here` 推入的是當前正在編譯的定義指令列長度：`len(vm._definition.body)`。
* 當 `,` 於直譯模式執行時，它將值附加到 `vm.last().body`；而於編譯模式執行時，則將指令追加進編譯陣列。
* 當 `!` 的目標是一個整數時，它專門用於**編譯期指令回填 (Backpatching)**，將跳轉目標索引寫入預留的空位。

---

### 3.3 TIB 尾端追加與 Task-private T-stack

每個 `Input` 以完整 TIB 字串 `tib` 和字元 offset `itib` 表示；讀取會推進 `itib`，不刪除已讀取內容。Forth word `tib.append` 把資料堆疊上的字串（前置一個空格）追加至目前 Task 的 TIB 尾端，保留目前游標。直譯器讀完原有未讀文字後，會繼續執行追加的文字。

Task 暫停時，Host 可呼叫 `task.append_input(text)` 追加原始文字，再呼叫 `task.resume()`。Task 若已讀到 EOF 並進入 `done`，追加文字不會重新啟動它。Task 執行是 cooperative；正在執行的 Forth word 可透過目前的 `vm.input.append(text)` 追加，Host 則可在暫停期間追加。REPL 暫存的使用者提交佇列屬於 Host/UI，不會自動併入已執行中的 Task TIB。

`Task.tstack` 是各 Task 獨立的 T-stack，`>t` 將資料堆疊頂端移入 T-stack，`t@` 複製 T-stack 頂端至資料堆疊，`t>` 則移出頂端至資料堆疊。這些 words 操作一般 stack 值；來源游標由 `Input.itib` 表示，Forth flow-control words 可按需保存或恢復其 offset。

---

## 第四章：流程控制結構的創新實現 (Control Structures: Classical Elegance on Modern VM)

### 4.1 現代結構下的經典優雅

在沒有底層組合語言、沒有平坦機器碼記憶體、指令是一串 Python 物件與 action tuple 的環境下，我們要如何實現經典的 `if else then`、`begin until` 與計數迴圈？

peforth 給出的答案是：**以編譯期 Control Stack 實現典雅的抽象回填。**  
在外表看來，Forth 代碼保持著純粹經典的書寫風格；但在幕後，直譯器精巧地利用 Control Stack（即編譯期的 Data stack）在指令清單的陣列索引上穿針引線。

---

### 4.2 條件分支與 Forward Branch 回填

> [!NOTE]
> 這套典雅的控制結構實作是照抄 FigTaiwan 陳爽（爽哥）的原始 source code。這是源自 Forth 前輩經典的結構設計，在現代 VM 的 Python list 索引結構上，原汁原味重現其優雅！

條件判斷依賴兩個底層基礎運算元：
* `branch`：無條件跳轉，將當前 frame 的 instruction pointer (`vm.frame.ip`) 變更為緊隨其後的單元數值。
* `0branch`：條件跳轉，彈出 TOS，若為 False 則跳轉；若為 True 則跳過目標位址單元繼續執行。

```forth
: if    ['] 0branch , here 0 , ; immediate
: then  here swap ! ; immediate
: else  [compile] ahead swap [compile] then ; immediate
: ahead ['] branch , here 0 , ; immediate
```

#### 執行期骨架剖析
當編譯 `: test if ." YES" else ." NO" then ;` 時：
1. `if` 編譯 `0branch`，並在指令列預留一個空位 `0`，將該空位的索引 `here` 留在 stack 上。
2. 編譯 True 區塊 (`." YES"`）。
3. `else` 編譯 `ahead`（無條件跳轉 `branch`），留下一號空位，並回填先前 `if` 的目標為當前位置。
4. 編譯 False 區塊 (`." NO"`）。
5. `then` 取得一號空位的索引，將當前最新位置 `here` 回填進去！

整個過程在 Python `list` 陣列索引上完成，既無組合語言的複雜性，又完全保留了 Forth 的極簡編譯對稱性。

---

### 4.3 不定次數迴圈體系

1. **`begin ... until` (後測試迴圈)**：
   ```forth
   : begin  here ; immediate
   : until  ['] 0branch , , ; immediate
   ```
   `begin` 在 stack 上留下起點索引；`until` 編譯 `0branch` 並將起點索引寫入，條件為 False 時回跳。
2. **`begin ... again` (無窮迴圈)**：
   直接編譯無條件跳轉 `branch` 回起點。
3. **`begin ... while ... repeat` (前測試迴圈)**：
   ```forth
   : while   [compile] if swap ; immediate
   : repeat  [compile] again [compile] then ; immediate
   ```
   `while` 調用 `if` 留下一處未結算的前向跳轉點；`repeat` 一方面將無條件回跳 `again` 導回起點，另一方面將 `while` 的出口回填至迴圈末端。

---

### 4.4 計數迴圈的精妙結構：`for ... next` 與 `aft`

除了條件迴圈，peforth 還實作了基於 Return stack 的高效計數迴圈：

* `for` `( count -- ) ( R: -- count )`：
  編譯 `>r` 將計數器推入 Return stack，並留下迴圈起點。
* `doNext`：
  執行期將 Return stack 頂端的計數減一；若仍大於 0 則跳回起點，若歸零則彈出計數器並離開。
* `next`：
  編譯 `doNext` 並閉合回跳位址。

#### `for ... aft ... then ... next` 的幾何奇蹟
若需要在迴圈第一輪跳過某些初始化邏輯，傳統語言往往必須設置旗標變數。而在 Forth 經典美學中，`aft` 利用編譯期 stack 的三次位址穿梭完成此一神技：
```forth
: aft  drop [compile] ahead [compile] begin swap ; immediate
```
首輪執行直接越過 `aft ... then` 之間的區塊，從次輪起方才進入循環。這種幾何般的結構美感，在 peforth 現代 VM 上得以 100% 完整重現！

---

## 第五章：字典、編譯器與 Factory 體系 (Dictionary, Compiler & Factory Architecture)

### 5.1 字典模型與 Word 結構

peforth 的字典是由 Word 物件組成的動態集合。每個 Word 均被封裝為 `peforth/projectk.py` 中的 `_Word` 資料類別：

```python
@dataclass
class _Word:
    name: str
    action: object
    immediate: bool = False
    source: str = ""
    help: str = ""
    comment: str = ""
    type: str = ""
    _value: object = None
    body: list = None
```

* `name`：Word 在字典中的鍵值（大小寫敏感）。
* `action`：Word 的執行主體。可以是原生 Python 可呼叫物件 (Callable)，也可以是由指令組成的 tuple（Colon 定義）。
* `immediate`：布林旗標，標記該詞是否在編譯狀態下即時執行。
* `source`：儲存原生 Python 代碼字串（針對 `code` 定義）。
* `help` 與 `comment`：分別由 `//` 與 `///` 註解填入的說明文檔。
* `body`：專屬的 Python 清單，用於存放 Word 實例的資料單元。
* `type`：**Word 的身份識別標記**（後述）。

#### 字典查詢與 Introspection
* `'` (tick)：在直譯模式下推入 Word 物件，在編譯模式下將該詞編譯為字面量。
* `[']`：強制作為編譯期字面量。
* `words`：列出字典中所有可用 Word，支援關鍵字過濾。
* `last`：取得最新定義的 Word 參照 (`vm.last()`)。

---

### 5.2 Colon 定義與編譯器控制

冒號定義 (`:`) 是 Forth 擴充詞彙的主要手段。其底層運作如下：
1. `:` 調用 `vm.begin(name)`：
   * 建立一個暫存的 `_Word(name, None)`。
   * 將系統狀態切換至編譯模式 (`vm.compiling = True`)。
   * 初始化編譯清單 `body = []`。
2. 逐一編譯指令：
   * 普通 Word 以 `vm.comma(word)` 追加至 body。
   * 數值以 `vm.literal(val)` 包裝追加。
   * Immediate Word 打斷編譯，即時執行。
   * 若需延遲 Immediate Word 的執行（強制將其編譯為指令），使用 `[compile] <name>`。
3. `;` 調用 `vm.finish()`：
   * 將暫存 body 固化為不可變的元組 `word.action = tuple(body)`。
   * 將新詞安裝進字典 `vm.words[name] = word`。
   * 將系統狀態還原為直譯模式 (`vm.compiling = False`)。

---

### 5.3 Defining Words 與 Custom Factory 機制

在 Forth 哲學中，最崇高的境界不是寫出功能強大的函數，而是寫出**「能製造新 Word 的 Word (Defining Words)」**。在現代架構中，這就是極致的 **Custom Factory 模式**。

peforth 透過 `create` 與 `(does>)` / `does>` 實現了完美的 factory 機制：

```forth
code create
    name = vm.input.read()
    if not name: raise ForthError("create expects a name")
    body = []
    def default_action(v, b=body):
        v.push(b)
    word = vm.define(name, default_action, type="created", body=body)
end-code
```
* **`create` 的 Compile-time**：從輸入串流讀取一個新名字，為其分配專屬的 `body = []`，並預設執行期行為是「將這個 body list 推入 Data stack」。

#### `does>` 的執行期黑魔法
`does>` 的任務是：**截斷 defining word 的後續指令，並將這段指令動態綁定為剛建立的子 Word (child word) 的執行體！**

在 `base.f` 中，`(does>)` 展現了令人驚嘆的動態 Metaprogramming 設計：
```python
code (does>)
    child = vm.last()
    frame = vm.frame
    steps = frame.action[frame.ip:]          # 截取 does> 之後的所有後續指令
    defining_word = getattr(frame, "word", None)
    if defining_word:
        child.type = defining_word.name      # 賦予子詞 factory 名稱！
    def child_action(v, w=child, s=steps):
        v.push(w.body)                       # 1. 先將子詞的 body list 推入 stack
        yield from v.call(s)                 # 2. 接著執行 does> 後方的指令體！
    child.action = child_action
    frame.ip = len(frame.action)             # 讓 defining word 提前結束返回
end-code
```

---

### 5.4 Word `type` 與 Factory 的類別身份 (Type as Factory Identity)

在物件導向程式設計 (OOP) 中，每個實例 (instance) 都有一個 Class 作為其類型歸屬。在傳統 Forth 裡，子 Word 往往只是無名的記憶體結構，缺乏型態 Introspection 能力。

**peforth 給出了一個極其典雅的解決方案：將 Factory 的名稱直接印刻在子 Word 的 `word.type` 上！**

1. **`constant` Factory**：
   ```forth
   : constant ( val <name> -- )
       create ,
   does> ( -- val )
       @ ;
   ```
   * 當執行 `10 constant ten` 時，`constant` 內部建立 `ten`。
   * `does>` 執行時，動態偵測當前 frame 的 Word 名為 `"constant"`，自動將 `ten.type` 設定為 `"constant"`！
2. **`variable` Factory**：
   ```forth
   : variable ( <name> -- )
       create 0 , ;
   ```
   * 建立子 Word，其 `body` 預設存放 `[0]`，執行時將此 list 推入 stack。
3. **`value` 與 `to` Factory**：
   ```forth
   : value ( val <name> -- )
       create ,
   does> ( -- val )
       @ ;
   ```
   * `value` 建立的 Word，執行時推入數值；當遇到 `to <name>` 時，`to` 會檢驗 `word.type == "value"`，並在執行期（或編譯期）動態修改該詞的 `word.value`。
4. **反編譯器 Introspection 整合**：
   正是因為 `word.type` 精準記錄了 Factory 身份，第三階段反編譯器 `see` 在面對 `ten` 時，不需要把內部指令還原成晦澀的 `create , does> @`，而是直接優雅反編譯出：
   ```text
   10 constant ten
   ```
   這讓 Factory 體系具備了與現代高階語言相媲美的 Reflection 與 Introspection 能力。

---

## 第六章：Host Bridge 深度互操作 (Python Interop)

### 6.1 嵌入式共生思路 (Symbiotic Design)

傳統語言通常把「呼叫其他語言」視為外部 FFI (Foreign Function Interface)，需要配置型別定義、記憶體封裝與序列化開銷。  
在 peforth 中，**Python 不是外部語言，Python 就是執行環境本身！**

Forth 扮演著靈巧、簡潔的宣告式 DSL 與流程編排大腦；Python 則作為運算能量的供應池。兩者在同一個進程、同一個記憶體空間內無縫共生。

---

### 6.2 內聯 Python 程式碼區塊

peforth 提供了四種粒度的 Python 代碼嵌入機制：

#### 1. Word 級嵌入：`code ... end-code`
用於在 Forth 字典中直接註冊高性能的原生 Python Word：
```forth
code double
    vm.push(vm.pop() * 2)
end-code
```
代碼內部自動享有 `vm`、`push`、`pop`、`tos`、`stack` 與 `rstack` 等上下文綁定。

#### 2. 多行區塊級嵌入：`<py> ... </py>` 與 `<py> ... </pyV>`
* `<py> ... </py>`：執行任意 Python 多行語句，不主動回傳值。
* `<py> ... </pyV>`：求值一段多行 Python 表達式，自動將運算結果推入 Data stack。

#### 3. 單行與 Token 級簡寫：
* `py:`：執行下一個 token 的 Python 程式碼。
* `py>`：求值下一個 token 的 Python 表達式並推入 stack。
* `py::`：執行直到該行結尾的所有 Python 代碼。
* `py>>`：求值直到該行結尾的 Python 表達式並推入 stack。

---

### 6.3 動態物件解析與調用：`::` 與 `:>`

要調用已存在於 stack 頂端之 Python 物件的方法或屬性，peforth 設計了一對極簡的操作符號：

#### `::`（無回傳值調用 / Procedure Invocation）
語法：`<object> :: <member_or_method>`  
* 彈出 stack 頂部的 Python 物件，並在其上執行屬性賦值或無返回值方法。
* 支援索引存取（`[key]`）與方法呼叫：
  ```forth
  s" data" py> {'data': []} :: ['data'].append(123)
  ```

#### `:>`（有回傳值查詢與調用 / Function Invocation）
語法：`<object> :> <member_or_method>`  
* 彈出 stack 頂部的 Python 物件，執行指定運算，**並自動將其返回值推回 Data stack**！
* 實例展示：
  ```forth
  \ 調用字串方法
  s" hello world" :> upper() .
  \ 輸出：HELLO WORLD

  \ 取得物件屬性或字典鍵值
  py> {'name': 'peforth', 'version': 2.0} :> ['name'] .
  \ 輸出：peforth

  \ 鏈式調用與數學計算
  py> __import__('math') :> sqrt(144) .
  \ 輸出：12.0
  ```

不需要手寫任何包裝膠水代碼，整個龐大的 Python 標準庫與第三方生產生態，在 peforth 中均可憑藉 `:>` 探囊取物。

---

## 第七章：任務架構、資源邊界與非同步調度 (Task, Pause & Concurrency Architecture)

### 7.1 主流非同步與並行編程的困局與批判 (Critique of Mainstream Concurrency Paradigms)

在深入 peforth 的 Coroutine 與多任務設計前，我們必須徹底審視現代主流語言在處理非同步 (Asynchronous) 與並行 (Concurrency) 問題時，積累了多少沉重、勉強而費工夫的歷史包袱。理解這些批判，能幫助我們清楚看見 peforth 所處的坐標，並深入體會其核心內涵：

#### 1. 盲目猜測的「Timeout」之痛
幾乎所有傳統系統在面臨等待時，第一反應都是引入 `timeout` 參數。但 Timeout 本質上是一場注定痛苦的猜測：
* **設太短？** 網路稍微抖動或伺服器負載微增，立即引發假超時錯誤 (False Failure)。
* **設太長？** 系統在真正出錯時只能無謂空等十幾秒甚至數分鐘，嚴重破壞互動體驗。
* 為了修補猜測的盲目性，工程師被迫在外部疊加指數退避 (Exponential Backoff)、隨機抖動 (Jitter) 與重試迴圈 (Retry Loop)。程式碼變得極其臃腫不堪。

#### 2. Callback 地獄與控制反轉 (Inversion of Control)
傳統非同步將後續代碼包裹進回呼函式交由他人執行。這直接將完整的 Call Stack 撕得粉碎：上下文遺失、除錯回溯 (Stack Trace) 支離破碎，錯誤捕獲必須層層手動 bubble up 傳遞。

#### 3. 惡名昭彰的「函數著色問題 (Function Coloring / Red-Blue Functions)」
現代語言為了解決 Callback 而發明了 `async / await`，卻引發了嚴重的架構分裂：
* 函數被硬生生染成兩種顏色：**同步函數（藍色）** 與 **非同步函數（紅色）**。
* 藍色函數可以呼叫藍色函數；但只要底層某個微小葉節點變成了紅色 (`async`)，所有直接或間接呼叫它的上層函數**必須全面染紅，且每一層呼叫前都必須強制加上 `await`**！
* 這在軟體工程中造成了極其嚴重的傳染性代碼重構，將同一個語言分裂為兩個平行宇宙。

#### 4. 重量級 OS Thread 與鎖的泥淖
為了避開非同步語法，另一派採用作業系統 thread (OS Threads)。但在多 thread 並行下，共享記憶體的幽靈如影隨形：資料競爭 (Race Conditions)、互斥鎖 (Mutex)、死鎖 (Deadlock) 與記憶體屏障，將程式複雜度推向毀滅邊緣。

#### 5. 「完全隔離 (Shared-Nothing)」與「完全全域 (Everything-Global)」的兩極迷思
在處理多任務狀態時，電腦科學界長期陷入兩極化的極端思維：
* **極端一：Erlang / Go 的完全隔離 (Shared-Nothing)**：
  Actor 模型與 CSP 模型主張任務之間絕不共享記憶體，所有資料必須透過信箱或通道傳遞。這保證了安全，代價卻是沉重的記憶體複製、序列化開銷，以及無法共享中央字典與資料管線的靈活性。
* **極端二：傳統 Forth 的完全全域 (Everything-Global)**：
  傳統 Forth 誕生於資源極度受限的單執行緒硬體時代，習慣將所有狀態視為全域：單一 Data stack、單一 Return stack、單一輸入指標。這種設計在單線執行時極致精簡，然而一旦邁入現代非同步 IO（例如等待 AI 回應或網路請求），只要一個任務暫停，另一個任務插隊就會立即造成致命的狀態覆蓋與踩踏。

---

### 7.2 peforth 的根本超越：機制與策略的徹底分離 (Mechanism vs. Policy)

面對上述亂象，peforth 選擇了一條回歸電腦科學純粹本質的道路：

#### `pause` 的極致純粹性
在 peforth 裡，`pause` **沒有任何參數、不接受 Timeout、不繫結 Event ID、不負責排程優先級**。它在核心中真的只有這三行代碼：
```python
code pause
    yield vm.pause()
end-code
```
它只做一件極致純粹的事：**「凍結當下執行的 Continuation，將主控權優雅讓渡回 Host」**。

#### 為什麼 peforth 根本沒有「函數著色問題」？
在 peforth 中，包含 `pause` 的 Word 依然是一個普通純粹的 Word！
* 呼叫一個會暫停的 Word，呼叫者**完全不需要改變語法**，不需要加 `async`，不需要加 `await`。
* 底層的 Continuation 透過 Python 生成器的 `yield from` 穿透機制，全自動、無感地在 call stack 向上委派凍結。整個 Forth 語言世界永遠保持統一、純粹。

#### Single-Thread 協作式的絕對安全
由於 VM 採用 single-thread 協作式模型，每一瞬間只有一個任務在走動，所有 stack 與記憶體狀態在切換時均完全受控，**徹底消滅了鎖、互斥量與 Race Condition**。

---

### 7.3 Task 的生命本質：每一次 `dictate()` 都是一個獨立 Task

在 peforth 的架構構想中，`Task` 不是外掛的附加品，它是**執行的最小生命單元**與 **Continuation 的具體承載者**。

#### 1. `dictate()` 的本質
當我們在 Host Python 或 REPL 中執行 `vm.dictate(text)` 時，底層執行的不是一段單純的同步直譯迴圈，而是立即孕育出一個新的 `Task` 實例：
```python
def dictate(self, text):
    return Task(self, self.evaluate(text)).resume()
```
每次敲下 Enter 送入一行指令，系統便啟動一個專屬的 Task，並立刻將其推進至第一個暫停點或完成狀態。

#### 2. Continuation 的具體承載
Task 持有最外層的 Generator（`self._steps`），它就像是這段尚未走完之路程的守護者：
* 凍結了目前執行到哪一個 Word 的哪一步（instruction pointer `ip`）；
* 保留了尚未返回的 Generator call stack 與區域變數；
* 封裝該 Task 的輸入上下文、Return Stack 與 T-stack。

#### 3. Task 狀態機
```mermaid
flowchart TD
    Ready["ready (初始就緒)"] -->|"resume()"| Running["running (執行中)"]
    Running -->|"yield vm.pause()"| Paused["paused (暫停讓出)"]
    Paused -->|"task.resume()"| Running
    Running -->|"正常執行完畢"| Done["done (完成)"]
    Running -->|"未捕捉例外 (Error)"| Failed["failed (失敗)"]
    Running -->|"vm.abort()"| Aborted["aborted (中止)"]
```

* `ready`：任務已配置，尚未踏出第一步。
* `running`：任務正在直譯迴圈或 Word 內部推進。
* `paused`：任務執行到 `pause`，主動釋放 CPU，狀態安穩凍結，等待外部事件喚醒。
* `done`：指令串流已完全消化，任務圓滿完成。
* `failed`：執行中拋出未捕獲的例外，已被隔離並記錄於 `task.error`。
* `aborted`：任務被 `vm.abort()` 或 Host `task.cancel()` 中途取消，未編譯完成的定義自動回滾。

---

### 7.4 資源全景哲學：全域共享 (Global) vs. 任務私有 (Task-Private)

peforth 既不盲從 Erlang/Go 的「全面隔離（Shared-Nothing）」，也不固守傳統 Forth 的「全面全域（Everything-Global）」，而是開闢了一條極其優雅的第三條路：

> **「各 Task 私有 continuation、輸入上下文、Return/T stacks；VM 共享 dictionary、Data Stack 與 Host。」**

```mermaid
flowchart TB
    subgraph VM_Space ["VM 全域共享空間 (Global Space)"]
        direction TB
        Words["字典 Dictionary (vm.words)<br/>共享詞彙與 Defining Words"]
        DStack["資料 Data Stack (vm.stack)<br/>共享運算管線與參數流轉"]
        HostCtx["Host 橋接環境 (vm.host)<br/>共享 Python API 與全域資源"]
        DefOwner["編譯擁有者鎖 (_definition.owner)"]
    end

    subgraph Task1 ["Task 1 私有領域 (Task Private)"]
        direction TB
        T1_Cont["Continuation (_steps)<br/>獨立 Generator 呼叫鏈"]
        T1_TIB["輸入上下文 (inputs)<br/>單一 TIB 字串 + 字元 offset"]
        T1_RS["Return Stack (task.rstack)<br/>私有迴圈指標與暫存"]
        T1_TS["T-stack (task.tstack)<br/>私有 TIB offset 暫存"]
        T1_Stat["生命狀態 (status / error)"]
    end

    subgraph Task2 ["Task 2 私有領域 (Task Private)"]
        direction TB
        T2_Cont["Continuation (_steps)<br/>獨立 Generator 呼叫鏈"]
        T2_TIB["輸入上下文 (inputs)<br/>單一 TIB 字串 + 字元 offset"]
        T2_RS["Return Stack (task.rstack)<br/>私有迴圈指標與暫存"]
        T2_TS["T-stack (task.tstack)<br/>私有 TIB offset 暫存"]
        T2_Stat["生命狀態 (status / error)"]
    end

    Task1 -.->|"共享存取與操縱"| VM_Space
    Task2 -.->|"共享存取與操縱"| VM_Space
```

#### 資源拓撲劃分矩陣

| 資源類別 | 實體屬性 | 歸屬範疇 | 設計思維與邊界理由 |
| :--- | :--- | :--- | :--- |
| **Continuation 鏈** | `task._steps` | **Task Private** | 保留尚未完成的呼叫鏈與 instruction pointer，各任務執行進度絕不混淆。 |
| **輸入串流緩衝區** | `task.inputs` (`tib`/`itib`) | **Task Private** | 各任務讀取自己的字符串流，獨立消費 Token，絕不互相搶字。 |
| **Return Stack** | `task.rstack` | **Task Private** | 保留私有迴圈計數器（`for...next`）與暫存變數（`>r`），防止跨任務踩踏。 |
| **T-stack** | `task.tstack` | **Task Private** | 供 `>t`、`t@`、`t>` 保存與取回來源游標等整數。 |
| **生命與錯誤狀態** | `task.status` / `task.error` | **Task Private** | 任務的成敗與中斷彼此隔離，單一任務崩潰不直接摧毀其他任務。 |
| **字典庫** | `vm.words` | **Global Shared** | 任務共享全體 Word 定義；Task 1 定義的新詞，Task 2 立即可用。 |
| **資料 Stack** | `vm.stack` | **Global Shared** | 承襲 Forth 中央暫存器哲學，提供最高自由度的資料流轉與任務間協同。 |
| **Host 橋接環境** | `vm.host` | **Global Shared** | 統一提供 Python 模組、原生函式與系統常數之橋接。 |
| **編譯定義鎖** | `vm._definition` | **Global (帶 Owner)** | 雖然掛在 VM 上，但標記 owner 屬於哪個 Task，避免並行編譯踩壞詞條。 |

---

### 7.5 從傳統誤區到 Task 境界：為什麼 Return Stack 必須是 Task Private？

在 peforth 的早期探索中，我們曾一度沿襲傳統 Forth 的慣性思維：既然 Data stack 放在全域，那麼 Return stack 似乎也理所當然地被放在全域（宣告為 `vm.host["rstack"] = []`）。

**然而，當 peforth 真正跨入 Task 的境界時，我們意識到了這是一個歷史遺留的重大錯誤！**

#### 1. 全域 Return Stack 的致命陷阱
考慮以下經典計數迴圈：
```forth
: pause-loop  2 for r@ pause next ;
```
在執行時，`for` 會將迴圈計數器壓入 Return Stack。當任務在迴圈內部執行 `pause` 暫停時，計數器正安靜地躺在 Return Stack 上。

如果 Return Stack 是全域共享的：
1. Task 1 在迴圈中 `pause` 讓出 CPU；
2. 此時使用者或 Host 啟動了 Task 2 執行另一個簡單迴圈：`0 5 for r@ + next`；
3. Task 2 的 `for` 與 `doNext` 會立即改寫甚至 pop 掉同一個全域 Return Stack！
4. 當 Task 1 稍後被 `resume()` 喚醒時，眼前的 Return Stack 早已被毀滅殆盡，迴圈指標完全錯亂。

#### 2. 架構躍升：物理私有化與智慧代理
認清這一點後，我們徹底打破了傳統束縛，確立了 **「Return Stack 必須是 Task Private」** 的鐵律：

* **物理私有**：直接將 `rstack` 綁定在 `Task` 實例身上（`task.rstack = []`）。
* **智慧代理 (`_RStackProxy`)**：在 `vm.host` 中注入動態代理物件，當 Forth 的 `>r`、`r>`、`r@`、`rdrop` 或 `doNext` 運行時，代理自動路由至當前活躍 Task 的私有 `rstack`：
  ```python
  class _RStackProxy:
      def append(self, item): self._vm.rstack.append(item)
      def pop(self, *args):
          try: return self._vm.rstack.pop(*args)
          except IndexError: raise ForthError("Return stack underflow")
  ```
* **多任務交錯安全保證**：
  Task 1 在迴圈中暫停時，其私有計數器安全封存於自身；Task 2 插隊執行任何迴圈均在自己的 `task2.rstack` 內進行，彼此秋毫無犯！

```mermaid
sequenceDiagram
    participant T1 as "Task 1 (pause-loop)"
    participant RS1 as "Task 1 rstack"
    participant H as "Python Host"
    participant T2 as "Task 2 (other-loop)"
    participant RS2 as "Task 2 rstack"

    H->>T1: dictate("pause-loop")
    T1->>RS1: 2 >r (計數器 2 壓入私有 rstack)
    T1-->>H: pause (暫停讓出)
    Note over T1,RS1: Task 1 凍結，RS1 保留 [2]

    H->>T2: dictate("0 3 for r@ + next")
    T2->>RS2: 3 >r (獨立壓入 RS2，絕不影響 RS1！)
    T2->>T2: 完成迴圈計算 6
    T2-->>H: done (Task 2 完成)

    H->>T1: task1.resume()
    Note over T1,RS1: Task 1 甦醒，RS1 依舊是 [2]！
    T1->>RS1: doNext (安全遞減為 1，繼續下次循環)
```

---

### 7.6 REPL 輸入與 Task TIB 的邊界

Task 暫停時會把控制權交回 Host。REPL 收到的使用者輸入屬於 Host/UI；一般提交的 Forth buffer 由 `vm.dictate()` 建立新 Task 執行。等待 AI approval 或 cleanup 確認期間暫存的輸入，也留在 REPL 自己的 queue，解除等待後再處理，不會併入暫停中的 Task TIB。

要讓同一 Task 繼續執行新增來源，須明確操作該 Task 的 TIB：正在執行的 Forth word 可呼叫 `tib.append`；Task 暫停後，Host 可呼叫 `task.append_input(text)`，再以 `task.resume()` 繼續。已完成的 Task 不會因追加文字而重新啟動。

---

### 7.7 深入理解 `pause`：兩個直觀模型

為了透徹理解 `pause` 在不同 Host 策略下的運作，我們回顧兩個極具代表性的直觀生活模型：

#### 模型一：無知的警衛 (The Unaware Guard / Polling Scheduler)
* **場景**：一棟大樓的夜間巡邏警衛，每隔一段時間巡邏房間，敲門確認狀況。警衛本身是「無知」的，不知道每個房間在等什麼。
* **運作機制**：
  1. Python Host 扮演警衛，定期輪巡任務清單：`task.resume()`；
  2. 任務被叫醒，自己檢查等待條件（例如檢查鍵盤緩衝區 `key?`）；
  3. 若條件尚未滿足，任務說一句 `pause`：「我還沒好，請去巡別間！」；
  4. 控制權交還警衛，警衛繼續巡邏下一個任務，直到某次條件滿足走出迴圈。
* **Forth 代碼視角**：
  ```forth
  : key ( -- char )
      begin key? 0= while pause repeat
      get-char ;
  ```

#### 模型二：震動號碼牌 (The Restaurant Buzzer / Event-driven Continuation)
* **場景**：在美食街點餐後拿到一個「震動號碼牌」。
* **運作機制**：
  1. 顧客拿到號碼牌後直接趴在桌上睡覺（執行 `pause`），完全不需要設鬧鐘或頻繁抬頭張望（無須 polling 迴圈）；
  2. Python Host 將 `Task` 參照掛鉤在非同步事件的回呼上，轉身處理其他事務；
  3. 餐點備妥時號碼牌震動，Host 喚醒顧客：`task.resume()`；
  4. 顧客睜開眼時餐點已在桌上，直接享用！
* **Forth 代碼視角**：
  ```forth
  : fetch-remote-data ( url -- response )
      start-async-request   \ 發起請求，掛上震動號碼牌
      pause                 \ 瀟灑趴下睡覺！無須迴圈！
      read-result ;         \ 甦醒瞬間，資料保證已在 stack 上！
  ```

**無論 Host 採行的是「巡邏警衛（Polling）」還是「震動號碼牌（Event-driven）」，peforth 內部的 `pause` 原力永遠純粹如一。**

---

## 第八章：Introspection、除錯與開發工具 (Introspection & Tooling)

### 8.1 Stack 檢視

* `.s` `( -- )`：
  非破壞性檢視當前 Data stack。直接印出當前 Python 清單的完整結構（例如 `[10, 'hello', {'status': 'ok'}]`），不消耗任何 stack 元素。

---

### 8.2 字典探索與自文檔系統

peforth 拒絕文檔與代碼分離。透過 `base.f` 內建的註解體系，字典本身就是一套即時互動文件庫：

* `words <filter>`：
  列出字典中所有 Word。若提供過濾字串，則執行不分大小寫的模糊過濾比對。
* `help <pattern>`：
  全方位文件檢索工具。自動搜尋匹配 Word 的 `name`、`help`（由 `//` 定義）與 `comment`（由 `///` 定義），並將說明文件格式化輸出至終端。

---

### 8.3 三階段反編譯器 `see` (Three-Stage Decompiler)

在傳統系統中，反編譯器要麼只能吐出位元組十六進位碼，要麼對動態產生的詞束手無策。  
peforth 設計了革命性的**三階段反編譯器 `see`**：

```text
使用者輸入：see ten
```

#### 階段一：文檔與註解呈現 (Documentation Header)
若該 Word 擁有 `//` 或 `///` 註解，率先以美觀的縮排印出其 Stack Effect 與架構說明。

#### 階段二：Word 物件中繼資料字典 (Object Metadata Inspection)
調用 `word.format_dict(collapse=True)`，印出該 Word 在 Python 層級的完整欄位：
```python
{
    'name': 'ten',
    'type': 'constant',
    'immediate': False,
    'action': <_Word @>,
    'body': [10],
    'help': '...',
    'comment': '...',
    'source': '',
}
```

#### 階段三：依 Type 與 Action 精準還原源碼 (Source Restoration)
根據 Word 的 `type` 與底層結構，還原出最符合人類可讀形式的定義源碼：
* 若為 `value`：還原為 `10 value ten`。
* 若為 `constant`：還原為 `10 constant ten`。
* 若為 `variable`：還原為 `variable v`。
* 若為 `string-quote`：還原為 `char " string-quote s"`。
* 若為 Colon 定義（tuple of steps）：還原為完整的 `: name ... ;` 指令鏈（包含分支跳轉與 does> 標記）。
* 若為 Host `code` 定義：還原出原始 Python 代碼區塊 `code name ... end-code`。

---

### 8.4 偵錯鉤子

* `*debug*` `( -- )`：
  在 Forth 代碼執行過程中隨時插入 `*debug*`。底層將直接調用 Python 3.7+ 原生的 `breakpoint()`，立刻掛起進程並切入 Python pdb 互動除錯模式，供工程師直接檢視 `vm` 內部變數與記憶體狀態。

---

## 第九章：工程架構、跨平台部署與驗證 (Engineering & Platform)

### 9.1 核心解耦與職責分離

peforth 的代碼組織貫徹高內聚、低耦合原則：

```text
       peforth/
       ├── peforth/
       │   ├── projectk.py      (共用 Forth Kernel)
       │   ├── repl.py          (REPL 與 f CLI)
       │   └── f/               (Forth source package 與 runtime resources)
       │       ├── __init__.py
       │       ├── base.f
       │       ├── auxiliary.f
       │       └── ai.f
       ├── tests/               (自動化測試)
       ├── docs/                (使用與開發文件)
       ├── skills/              (隨 source 提供，不自動全域安裝)
       └── plugins/             (隨 source 提供，不自動全域安裝)
```

> [!NOTE]
> 具體的最速啟動指令、`-e` 單行測試、全域 `f` 命令配置與常見排錯 SOP，均已收錄於獨立文檔 README.md。本章聚焦於背後的系統架構設計與跨平台路徑解析機制。

---

### 9.2 全域環境部署機制：動態路徑轉發

`f` 是 `pyproject.toml` 定義的 Python entry point；editable install 後由目前 checkout 的 venv 執行。開發安裝命令與 Windows/WSL 分開設定方式請見 README.md。

---
### 9.3 跨平台路徑與換行相容性

互動式 REPL 使用 `prompt_toolkit` 編輯完整輸入緩衝區。按 Enter 送出整個緩衝區；Ctrl+J 或 Esc 後再按 Enter 插入新行。多行貼上會保留在編輯器中，按 Enter 後作為一次輸入提交。`code ... end-code` 區塊也可跨行累積。

Shift+Enter 只有在終端提供可區分的按鍵序列時才能使用。部分終端會把 Ctrl+Enter 傳成 Ctrl+J，因此它也可能插入新行。

---
### 9.4 自動化驗證套件

系統品質由 `tests/` 中的自動化測試持續驗證，涵蓋：

* 基礎算術與大整數 / 浮點數精度
* Data Stack、Return Stack、T-stack 與 TIB 游標/尾端追加
* Stack underflow 與 Task-private stack isolation
* Colon 定義與 Immediate Word 編譯期行為
* `if else then`、`begin until/while` 與 `for next aft` 迴圈回填驗證
* `create does>` 與自訂 Factory 產物行為
* 多定界符字串家族解析
* Python Host Bridge（`::`、`:>`、`<py>` 代碼塊）雙向資料流
* `Task` 狀態機、`pause` 中斷與 `resume()` Coroutine 恢復
* 三階段 `see` 與自文檔 `help` 查詢

在 repo 根目錄執行 `python -m unittest discover -s tests -q` 可驗證目前測試結果。
