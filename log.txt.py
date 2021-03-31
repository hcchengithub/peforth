
peforth

[x] 13:59 2017-07-31 找到 JavaScript eval() equivalent in Python
    https://stackoverflow.com/questions/701802/how-do-i-execute-a-string-containing-python-code-in-python
    成功了!!
    >>> mycode = 'print ("hello world")'
    >>> exec(mycode)
    hello world
    >>>

    The technique of returning a function from another function is known as currying:
    https://stackoverflow.com/questions/14261474/how-do-i-write-a-function-that-returns-another-function

    Python annoymous function lambda
    http://blog.csdn.net/majianfei1023/article/details/45269343
    https://www.zhihu.com/question/20125256

[x] review project-k , should project-k support python too?
    which will be peforth.py 10:04 2019/11/26 it's projectk.py now.

[x] 直接問 pyforth 的原作者的版權條件 ---> 用不著了.
[x] 實驗用 exec() 生成一個 function
        s = '''
        def show(s):
            print(s)
        '''
    exec(s)
    >>> show('abc')
    abc
    >>> 成功了!

[x] Try to define an python object
    s = '''
    class a():
        vm = None
        def b(self):  # self is must
            print(b)  # b unknown
            print(self)
            print(a)
            vm = self
    c = a()
    '''
    exec(s)
[x] peforth 可以引用的讀檔範例
    # average5 .py
    def main() :
        fileName = input ("What file are the numbers in? " )
        infile = open (fileName, ' r ')
        sum = 0
        count = 0
        for line in infile:
            sum = sum + eval (line)
            count = count + 1
        print ("\nThe average Of the numbers is", sum / count)
    main ( )

    # average6.py
    def main() :
    fileName = input ("What file are the numbers in? " )
    infile = open ( fileName
    sum = 0.0
    count = 0
    line = infile.readline()
    while line != ""
        sum = sum + eval(line)
        count = count + 1
        line = infile.readline()
    print("\nThe average Of the numbers is", sum / count)
    main()

[x] module 的用法搞懂了，很簡單。 peforth.py 就是 peforth VM.
    不需要像 javascript 用一個 function 把整個 vm 包起來, see
    GitHub\peforth\projectile.py
    python can redefine functions and methods. Function and methods are
    variables too.
    python objects, like javascript, can add properties and methods
    through simply assign a value to it.
        >>> type(show)  # show is an object
        <class 'projectile.Projectile'>
        >>> show
        <projectile.Projectile object at 0x000001C6260D0438>
        >>> show.x = 0   # assign new property to show
        >>> show.y = 11
        >>> show.p = 22
        >>> dir(show)    # check it out
        ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__',
        '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__',
        '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__',
        '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__',
        '__str__', '__subclasshook__', '__weakref__', 'getHere', 'getX', 'getY', 'p',
        'update', 'x', 'xpos', 'xvel', 'y', 'ypos', 'yvel']
        >>>
[x] python 也可以 see function 的 source code
    https://stackoverflow.com/questions/427453/how-can-i-get-the-source-code-of-a-python-function

    def foo(a):
    x = 2 # how about a comment?
    return x + a

    import inspect

    # inspect.getsource(foo)
    # u'def foo(a):\n    x = 2\n    return x + a\n'

    print (inspect.getsource(foo))
    ==> 結果完全成功, 連 comment 也被顯示出來。
    ==> 但是 py> py: 組合出來的 function 不行
            py> tick('test').cfa ==> 1
            py> dictionary[1:] ==> [.s, <function <lambda> at 0x0000024CE15810D0>,
            .s, <function <lambda> at 0x0000024CE1581158>, .s, None, None]
            OK py> inspect.getsource(dictionary[2]) .
            could not get source code  <------------------- error message
            Debug? [y/N]

    同一篇 stackoverflow 介紹的 dis module 也真的可行!
    >>> import dis
    >>> def func(x):
    ...     print(x+1)
    ...
    >>> func(123)
    124
    >>> dis.dis(func)
      2           0 LOAD_GLOBAL              0 (print)
                  2 LOAD_FAST                0 (x)
                  4 LOAD_CONST               1 (1)
                  6 BINARY_ADD
                  8 CALL_FUNCTION            1
                 10 POP_TOP
                 12 LOAD_CONST               0 (None)
                 14 RETURN_VALUE
    >>>    哇! 顯示出 function 的機械碼, 太正點了!!

[x] Python equivalent of:
    Word.prototype.toString = function(){return this.name + " " + this.help}; // every word introduces itself
    --> 有了, 就是去定義 __str__ prototype of the class

    #------- ex2.py ---------------
    class d():
        def __str__(self):
            return "a __str__"
        def __repr__(self):
            return "a __repr__"

    class x():
        name = 'stella'
        feet = 'splender'
    #------------------------------

    >>> import ex2
    >>> x = ex2.x()
    >>> x
    <ex2.x object at 0x00000170D77202B0>  <---- default __repr__ 打印
    >>> print(x)
    <ex2.x object at 0x00000170D77202B0> <---- default __str__ 傳回值

    >>> d = ex2.d()
    >>> d   # <--------- 執行該 obj 時, 打印 __repr__() 的傳回值
    a __repr__         # 應該讓它執行該 word
    >>> print(d)  # <---- obj 本身的傳回值是 __str__() 的傳回值
    a __str__
    >>>

[x] 進一步刺探未來的 peforth.py kernel module 的特性
    Ynote: 搞懂 python 的 module files globals() locals().note

[x] docode() 要組裝 function 需參考 anonymous function 的定義方法:
    https://stackoverflow.com/questions/6629876/how-to-make-an-anonymous-function-in-python-without-christening-it
    Study built-in function exec() https://docs.python.org/3/library/functions.html#exec
    Study build-in function compile() https://docs.python.org/3/library/functions.html#compile
    [x] genxt() 成功了
[x] IDLE path working directory working folder
    import sys
    sys.path.append('c:/Users/hcche/Documents/GitHub/peforth')
[x] 12:50 2017/08/12 已經跑起來了, debugging compiling == 'code' 的問題
    --> 可能是 end-code 裡面 Word(newname,newxt) 失敗的關係 --> no, it can't fail
    --> 應該是 docode 裡面, 結構不太好, 萬一 reDef 或 genxt() 失敗了會怎樣?
        很多都會半途結束, 留下 compiling == 'code' 的問題。 --> all tested, behavior acceptable now
[x] "import re" in peforth.py kernel is not a good choice.
    Simply letting the main program to do that. The main program is eforth.3py
    --> Yeah! it works.
        c:\Users\hcche\Documents\GitHub\peforth>python eforth.3py
        hello eforth!!
    --> 錯了, 每個 .py 檔都自己 import re, import pdb 反而是對的, see:
        https://stackoverflow.com/questions/8957859/python-child-cannot-use-a-module-the-parent-imported
        ... Generally if you're doing simple obvious things like importing a standard module,
        you should do it the simple and obvious way......
[x] reproduce the problem:
        import peforth as vm
        vm.dictate('code test end-code') # Try this first
        vm.words['forth']
    這樣是成功的,但是進入 forth command line 之後, 同樣的工作... 還是成功的。
    --> 改試 vm.dictate('code test3 print("hello test3!!") end-code')
        >>> vm.execute('test3') --> hello test3!!  很成功
    --> 進 forth command line
            >>> vm.peforth()
            OK code test4 print("hello test4") end-code
            OK test4
            hello test4
            OK
        還是很成功
    --> 好像要出過 error e.g. word unknown 之類才能複製問題
        >>> code test5 end-code
          File "<stdin>", line 1
            code test5 end-code
                     ^
        SyntaxError: invalid syntax
        >>>
        的確是這樣!!! now I've got the SRP
    --> 似乎是 w.xt(w) 執行 end-code 時出問題, 檢查此時的 end-code
        RI, outer() 裡面分辨 token 是否 [int, float] 用 eval(token) 會有 exception
        必須要用 try - except 處理才行。 --> Fixed !!!
[x] why after OK type 'words' no response <--- should be : Error! words unknown.
    --> 結果發現, 所有的 dir(vm) attributes 都這樣!!
        (Pdb) eval('pop') ==> <function pop at 0x00000178A534A730>
        (Pdb) eval('dictionary') ==> [0]
        (Pdb) eval('stack') ==> [{'forth': [0, code, end-code, //, stop, *debug*]}, {'forth': [0, code, end-code, //, stop, *debug*]}, {'forth': [0, code, end-code, //, stop, *debug*]}, <class 'peforth.Word'>, <function phaseA at 0x00000178A534A0D0>, <function phaseB at 0x00000178A534A158>]
        所以, outer() 還要再改良。
    --> eval() 的結果 + 0 就可以保證他是 number 了
[x] kernel project-k.py instead of peforth.py
[X] code word's help, not easy, keep the record.
    # stack diagram
    ntibwas, s = ntib, nextstring("\\(")
    if s['flag']:  # stack diagram is existing
        pdb.set_trace()
        newhelp = '( ' + nexttoken('\\)') + nexttoken() + ' '
    else: # return s to tib
        ntib = ntibwas
    # word description
    ntibwas, s = ntib, nextstring("\\")
    if s['flag']:  # description is existing
        newhelp += nexttoken('\n|\r')
    else: # return s to tib
        ntib = ntibwas
    code \ last().help += nexttoken('\n|\r'); end-code immediate
         // ( <comment> -- ) Give help message to the new word.
    code ( last().help = '( ' + nexttoken('\\)') + nexttoken() + ' ' end-code immediate
         // ( -- ) Get stack diagram to the last's help.
    --> v1.23 code words 可以用 # 下 help 了。 

[x] In jeforth, window.colonxt is dynamicly created by definition of ':'.
    Can peforth.f do that too in python? Yes!!!
        >>> def test():
        ...     globals()['cc'] = 123
        ...
        >>> cc
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        NameError: name 'cc' is not defined
        >>> test()
        >>> cc
        123
        >>>
[/] : test ;
    'module' object does not support item assignment
    Debug? [y/N] y
    RI: last().xt = xt # also vm['colonxt'] <------ [/] easy, deal with this later
[x] After the above error probably, after colon definition the compiling is still True!!!
    --> because forgot declare it a global.
    B i n g o ! ! colon definition works now
[x] literal needs to use closure
    def gen(n): # function generator
        def f(): # literal run time function
            print(n)
        f.description = "{} {}".format(type(n),n)
        return f
    f = gen([11,22,33])
    f()
    >>> f.description
    "<class 'list'> [11, 22, 33]"
    # functions are not shown by __str__ and __repr__ like dict
    # def str(self):    # return help message
    #     return f.description
    # def repr(self):   # execute xt and return help message
    #     return f.description
    # str.desc = "I am str"
    # repr.desc = "I am repr"
    # f.__str__  = str
    # f.__repr__ = repr
[x] py> py: 都應該改用 compile(code,"")
    compile CN http://www.th7.cn/Program/Python/201608/923063.shtml
    用到 lambda 就不能用來【賦值】, 安全理由. 故 py: 不能用 lambda. 要的話就必須用 compile 的。
    https://stackoverflow.com/questions/20695745/why-use-lambdas-vs-1-line-function-declarations
    --> [x] 已經發現 py: tick('//').immediate=True 行不通了!!!
            --> 用 <py> </py> </pyV> 分別改寫了 py: py> , ok now
    [x] pyExec pyEval 是多餘的 --> 去除
[x] (Pdb) execute("sdfsdf")
    (Pdb)
    沒半點錯誤訊息, 有問題看不出來!!
    --> fixed, now it's a panic.
[x] compiling 未定義怎麼不觸發 unknown?
    --> outer() 用 eval(token) 想判斷 token 是否 number 不行,
        當 token='compiling' 時不會觸發 exception 反而傳回其值 True or False !!
    --> 改用 complex(token) 很完美!
[x] t> >t t@
    >>> line = 'Cats are smarter than dogs\n\\ 1234\n\\ 2233'
    >>> matchObj = re.search( r'\n\\ (\d*)$', line)
    >>> matchObj.group()
    '\n\\ 2233'
    >>> matchObj.group(1)
    '2233'
    >>> len(matchObj.group())
    7
    >>> line[:-7]
    'Cats are smarter than dogs\n\\ 1234'
    >>>
[x] [/py] [/pyV] 只分別取得 exec-code 與 eval-code 不執行, 可以用 execute 執行嗎?
    [x] execute 也要能執行 exec-code 或 eval-code ---> done
    [x] 這兩個都不要，應該是個 compyle ( 'source' -- code object ) \ python compiler 指令
[x] 讓 execute() 認得 code object
    --> OK ' compyle .
        compyle ( "source" -- exec-code ) Python compile source to exec-code object __str__ OK
        OK char print('hi') compyle
        OK execute
        hi
        OK 一次就成功了!!
[x] colon definition 裡看能不能用 comma 塞入一個 code object ?
    --> : test char print('hi') compyle execute ;  成功
        : test2 [ char print('hi') compyle , ] ; 也成功
        : cfa ' py> dictionary[pop().cfa:] . cr ;
        OK cfa test2
        [ /* test2 */ <code object <module> at 0x0000019B24E1F8A0, file "", line 1>, None,
          /* cfa */ ', <function xt.<locals>.<lambda> at 0x0000019B24E29C80>, ., cr, None,
        None]
        OK
[x] 有了 compyle 要不要改寫 <py> </py> </pyV> 等?
    --> 只簡化了 </py> 一點點
[x] debug :: --> root cause 又是 branch 裡 assignment to ip 忘了加 vm.ip
    OK 11 22 ' + :: xt() .s ==> [33] OK 表示 :: interpret mode 功能 ok
    OK : test :: xt() ;
    --Return--
    > <string>(2)xt()->None
    (Pdb) c
    OK see-cfa test
    [<code object <module> at 0x000001F1364F68A0, file "", line 1>, None, None]
    OK 22 33 ' + test
    OK .s
    [55]
    OK
[x] constant 要用到 vm.forth['varname'] 複習一下 python 語法
    constant 要做的事 --> 'push(vm["forth"]["x"])'
    一開始 word-list 都沒有自己的空間
        (Pdb) vm['forth']
        *** TypeError: 'module' object is not subscriptable
        (Pdb) vm.forth
        *** AttributeError: module 'projectk' has no attribute 'forth'
    不能這樣 init :
        (Pdb) vm['forth']={}
        *** TypeError: 'module' object does not support item assignment
    要這樣 init :
        (Pdb) setattr(vm,'forth',{})
    Object 的 attribute 不能這樣 access :
        (Pdb) vm['forth']  <--- 這是 dict 的方式
        *** TypeError: 'module' object is not subscriptable
    要這樣 access :
        (Pdb) vm.forth
        {}
        (Pdb) getattr(vm,'forth')
        {}
        (Pdb)
[x] colon definition 失敗還是會佔一個位置
    OK 123 constant x
    OK 345 to x
    Error! Assigning to a none-value.
    Debug? [y/N]
    OK : test 44445555 to x ;
    Error! Assigning to a none-value. <--- 馬上觸發錯誤,好。
    Debug? [y/N]
    OK words
    0 code end-code // ...snip... to x test  <--- test 佔了位置
    OK : ttt ;
    OK words
    0 code end-code // ...snip... to x test ttt <--- 確實佔了位置
    OK test
    Error! test unknown. <---- colon definition 失敗, 只是沒有 reveal 而已
    Debug? [y/N]
    OK rescan-word-hash <---- rescan 之後它就會出現!!
    OK test
    OK .s
    [44445555]
    OK
    --> jeforth 也一樣, 算了, 有警告就可以了。
    --> (forget) 一下可以把它消除掉

[x] tib 平時有被 corrupted
    OK char $ . rewind
    OK 11 22 33 *debug*  # <---- 最簡單的
    (Pdb) tib
    '112233*debug*' # <----- 就已經有問題了 !!!
    (Pdb)
    問題在 kernel nexttoken() 裡面
    --> Root cause 1 : nexttoken() <--- skip leading white spaces 改寫
        Root cause 2 : tib and ntib are strange <-- ntib 太大先排除
[x] writeTextFile  實驗
    OK <py> open("pathname.txt", "wt")</pyV> constant f
    reDef f
    OK f .
    <_io.TextIOWrapper name='pathname.txt' mode='wt' encoding='cp950'> OK f :> name
    --> pathname.txt OK
    OK f :: write("abc")
    OK f :: write("123")
    OK f :: write("中文")
    OK f :: close()
    encoding='utf-8'
[x] refill works now. Use refill to improve <text> first. Let it accept
    multiple lines. ---> 最後是簡單地引進 accept2 用 Ctrl-D 切換 multiple-line mode 即可. 保留以下研究過程。
    : <text>.interpret ( <multi-lines> -- "string" ) // get multi-lines string from ternimal
        CR word ( s )
        begin
            accept if ( s line )
                \ get string to s, leave </text> and the rests in tib by adjusting ntib
                py> re.search("(.*)</text>(.*)",tos()) ( s line re )
                py> bool(tos()) if  \ line has </text> ?
                    ( s line re )
                    py: vm.tib="</text>"+tos().group(2);vm.ntib=0;
                    \ s += re.group(1)
                    nip ( s re ) :> group(1) + ( s )
                    exit
                else  ( s line re )
                    \ s += line
                    drop + ( s )
            else ( s )
                \ s += '\n'
                py> pop()+'\n'
            then
            refill
        again ;
    我發現, bool(regEx) 可以看出 re.search 的結果是否 found
    [x] See MetaMoji 討論如何適當分割以上複雜的 <text>.interpret 成簡單的 一行成功; 多行輸入 兩段。
        其中多行輸入是個公用 routine
    [x] 實驗後綴法是否有簡化功效? 使 group(1) 成為共同的結果
        \ regular expression 實例
        OK <py> re.search("(.*?)</text>(.*)","aa </text>bb</text>")</pyV> ( re ) constant re
        OK re bool . cr                                   ^^^^^^ 故意加上後綴讓 re.search 總是成功
        True <--- 總是成功
        OK re :> group() . cr
        aa </text>bb</text>
        OK re :> group(1) . cr
        aa <----------------------------- group(1) 為所求
        OK re :> group(2) . cr
        bb</text>  <-------------------- group(2) 去掉後綴之後還給 tib
        OK <py> re.search("(.*?)</text>(.*)","aa bb</text>")</pyV> ( re ) constant re
        OK re bool . cr
        True
        OK re :> group() . cr
        aa bb</text>
        OK re :> group(1) . cr
        aa bb  <------------ 當 bool group(2) False 時 group(1) 仍為所求, 故確有簡化功效
        OK re :> group(2) . cr
        OK re :> group(2)=="" . cr
        True
        OK re :> group(2) bool .
        False OK
    [x] 多行輸入公用 routine
        [x] 19:46 2020/10/04 複習需要 ^D 多行輸入 multiple lines inpue 的原因：如果是 colon definition 本來
            就可以在 compiling state 多行輸入，問題出在 code ... end-code 期間需要 ^D multiple lines input.
             
        : accepts ( "deli" <multiple lines> -- "string" ) // Get multiple lines from tib up to delimiter
            ( deli )
            begin
                accept if ( s line )
                    \ get string to s, leave </text> and the rests in tib by adjusting ntib
                    py> re.search("(.*)</text>(.*)",tos()) ( s line re )
                    py> bool(tos()) if  \ line has </text> ?
                        ( s line re )
                        py: vm.tib="</text>"+tos().group(2);vm.ntib=0;
                        \ s += re.group(1)
                        nip ( s re ) :> group(1) + ( s )
                        exit
                    else  ( s line re )
                        \ s += line
                        drop + ( s )
                else ( s )
                    \ s += '\n'
                    py> pop()+'\n'
                then
                refill
            again ;
        code accept2 # use Ctrl-D at the end to terminate the input. py> chr(4)=='^D' --> True
            result, s = "", input()
            while not chr(4) in s:
                result += s
                s = input()
            result += s.replace(chr(4),'\n')  # all ^D become \n
            push(result)
            push(True)
            end-code // ( -- str T|F ) Read a line from terminal.
[x] accept can be single line accept1 or multiple lines accept2 , switch by Ctrl-D
    8: [EOT] (<class 'str'>) <---- the Ctrl-D from input()
    OK py> ord(tos()[0]) . cr
    4
    OK
    示範 <accept> ... </accept> 的用法
        ------- clipboard ---------
        dropall
        <accept>
        11
        22
        33
        44
        55
        </accept>
        66
        77
        88
        99
        ----------------------------
        OK dropall      # paste 之後的樣子
        OK <accept>
        11
        22
        33
        44
        55
        </accept>66   # 這是最後一行，注意！66 可以往前緊貼, delimiter 會整個被忽略掉。
        OK 77
        OK 88
        OK 99
        ----------------------------
        OK .s      # 看看結果 .......
              0: 11
        22
        33
        44
        55
        66
         (<class 'str'>)
              1: True (<class 'bool'>)
              2:          77          4Dh (<class 'int'>)
              3:          88          58h (<class 'int'>)
              4:          99          63h (<class 'int'>)
        OK

[x] .s in trouble when cell is False, None ... etc
[x] peforth.py 可以直接執行 : python peforth.py
    也可以由 python interpreter 執行: >>> peforth.main() 此時 exit 回到 python interpreter
    bye 則會傳回 errorlevel 回到 DOS.

    # 從 python interpreter 就可以看到 peforth.py module 裡的 globals
    >>> dir(peforth)
    ['__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__',
    '__package__', '__spec__', 'greeting', 'main', 'panic', 'readTextFile',
    'vm', 'writeTextFile']

    # 從 python interpreter 更可以看到 project-k vm 裡的 globals
    >>> dir(peforth.vm)
    ['EXIT', 'RET', 'Word', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__',
    '__name__', '__package__', '__spec__', 'code', 'colonxt', 'comma', 'compiling', 'context',
    'context_word_list', 'current', 'current_word_list', 'debug', 'dictate', 'dictionary',
    'dis', 'docode', 'doendcode', 'endcode', 'execute', 'forth', 'genxt', 'greeting',
    'here', 'inner', 'inspect', 'ip', 'isReDef', 'json', 'last', 'major_version', 'multiple',
    'name', 'newhelp', 'newname', 'newxt', 'nextstring', 'nexttoken', 'ntib', 'order', 'os',
    'outer', 'panic', 'pdb', 'phaseA', 'phaseB', 'pop', 'push', 're', 'readTextFile', 'reset',
    'rstack', 'rtos', 'stack', 'stop', 'tib', 'tick', 'tos', 'version', 'vm', 'vocs', 'wordhash',
    'words', 'writeTextFile']

    # 從 python interpreter 也可以執行 peforth
    >>> peforth.vm.dictate
    <function dictate at 0x000001D1368E2510>
    >>> peforth.vm.dictate('version')
    p e f o r t h    v1.01
    source code http://github.com/hcchengithub/peforth

    # 在 peforth 裡面定義的東西, 回到 python interpreter 取用:
    >>> peforth.main()
    OK 123 constant x
    OK exit
    >>> peforth.vm.forth
    {'obj2dict': <function object2dict at 0x000001D136934510>, 'x': 123}
    >>> peforth.vm.forth['x'] --> 123

    # 用 obj2dict() 把 Word 轉成 dict, 這是 see 的準備
    >>> peforth.vm.forth['obj2dict'](peforth.vm.tick('+'))
    {'__class__': 'Word', '__module__': 'projectk', 'name': '+', 'xt': <function xt at 0x000001D1368F28C8>, 'immediate': False, 'help': '( a b -- a+b) Add two numbers or concatenate two strings.', 'comment': '', 'vid': 'forth', 'wid': 51, 'type': 'code'}

[x] see code words

    # json 需要先給它 obj2dict() function 才能處理我們的 object
    OK py> json.dumps(tick('+'),indent=4) .
    Failed to run <Word '</pyV>'>: Object of type 'Word' is not JSON serializable
    Continue, Debug, or Abort? [C/d/a] a          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    # 從 peforth 裡面定義轉換 function
    <py>
    def object2dict(obj):
        #convert object to a dict
        d = {}
        d['__class__'] = obj.__class__.__name__
        d['__module__'] = obj.__module__
        d.update(obj.__dict__)
        return d
    push(object2dict)
    </py>
    ^D
    OK .s
          0: <function object2dict at 0x000001D136934510> (<class 'function'>)
    OK constant obj2dict
    OK exit

    # 有了轉換 function 就可以讓 json 完成工作
    >>> import json
    >>> print(json.dumps(peforth.vm.tick('+'),default=peforth.vm.forth['obj2dict'],indent=4))
    {
        "__class__": "Word",
        "__module__": "projectk",
        "name": "+",
        "xt": {
            "__class__": "function",
            "__module__": "projectk",
            "source": "def xt(_me=None): ### + ###\n    push(pop(1)+pop()) \n",
            "name": "+"
        },
        "immediate": false,
        "help": "( a b -- a+b) Add two numbers or concatenate two strings.",
        "comment": "",
        "vid": "forth",
        "wid": 51,
        "type": "code"
    }
    >>>

[x] code object 希望能帶 source code 以供 see
    OK 45 @ dir .
    ['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__',
    '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__',
    '__le__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__',
    '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'co_argcount', 'co_cellvars',
    'co_code', 'co_consts', 'co_filename', 'co_firstlineno', 'co_flags', 'co_freevars',
    'co_kwonlyargcount', 'co_lnotab', 'co_name', 'co_names', 'co_nlocals', 'co_stacksize',
    'co_varnames'] OK
    OK    --> 不行, code object 裡面不能新增 attribute 也不能改裡面的

    若不行, 只好模仿 Word 弄成一個 class 來裝 code object 就可以帶上 source code
    或用 closure , 也就是 genxt() 的方法也是現成已經成功的辦法。也不見得比 compyle 差。
    或用 dis.dis(func) 也好, 更具視覺效果
    [x] 想到給 code object 加上 source code 顯示的辦法了, 引進 class Comment, 類似 class Word
        但是 do nothing (由 phaseA phaseB 實現) 只帶著 comment comma(Comment('lalalal')) 進
        dictionary 裡去躺著,等 see command 來利用。

        OK py: comma(Comment("lalala"))
        OK here
        OK .
        637 OK 636 @ .
        lalala OK 636 @ type . --> <class 'projectk.Comment'>
        OK 636 @ .
        lalala
        OK 636 @ execute -->
            Failed to run <Word 'execute'>: must be str, not Comment
            Continue, Debug, or Abort? [C/d/a] a
    [x] modify phaseA phaseB to support Comment class
        --> done!
    [x] modify ::, :>, </py>, and </pyV> to add comment
    [x] 目前 literal 仍被當一般 function 用 dis.dis() 顯示 --> 改成顯示 literal
        OK 339 @ .  # 已知 339 處是個 literal function
        <function xt.<locals>.f.<locals>.literal at 0x000001ED9B6579D8> OK 339 @ :> __name__ .
        OK 339 @ :> str . # 印出 readable 的方法
        Literal: pop(). <class 'str'> OK
        --> 可以修改 toString 了
    ==> see 終於完成了!!!
[x] 其實 __doc__ attribute 就是用來放說明文字的 . . .
    --> 錯!
        Failed to run <Word '</py>'>: 'code' object attribute '__doc__' is read-only
        Continue, Debug, or Abort? [C/d/a]
    可是我試過了呀!? 如下:
        00035: RET  (<class 'NoneType'>)
        00036: Literal: \\n|\\r <class 'str'>
        00037: RET  (<class 'NoneType'>)
        00038: lambda:push(eval(vm.greeting()))  (<class 'projectk.Comment'>)
        00039: (<class 'function'>)
          7           0 LOAD_GLOBAL              0 (push)
                      2 LOAD_GLOBAL              1 (eval)
                      4 LOAD_DEREF               0 (eval_code)
                      6 CALL_FUNCTION            1
                      8 CALL_FUNCTION            1
                     10 RETURN_VALUE
        OK 39 @ .
        <function xt.<locals>.<lambda> at 0x0000017E8D269598> OK
        OK 39 @ dir .
        ['__annotations__', '__call__', '__class__', '__closure__',
        '__code__', '__defaults__', '__delattr__', '__dict__',
        '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__get__',
        ...snip...]
        OK 39 @ :> __doc__ .
        None
        OK 39 @ :: __doc__="abc"
        OK 39 @ :> __doc__ .
        abc OK
    這是 : version py> vm.greeting() ; // ( -- revision ) print the greeting message and return the revision code
    compile() 出來的 eval_code, exec_code 的 __doc__ 都是 read-only, 但是
    包過一層 lambda 之後就可以編寫了。  <------ 真相大白！！
    --> </py> 直接 comma(exec_code) 實在沒有好處, 犧牲了 __doc__ 又
        迫使 phaseB 無謂地變得複雜。
    --> [x] 改掉!
[x] these lines are strange,
        "" value description     ( private ) // ( -- "text" ) description of a selftest section
        [] value expected_rstack ( private ) // ( -- [..] ) an array to compare rstack in selftest
        [] value expected_stack  ( private ) // ( -- [..] ) an array to compare data stack in selftest
        0  value test-result     ( private ) // ( -- boolean ) selftest result from [d .. d]
        [] value [all-pass]      ( private ) // ( -- ["words"] ) array of words for all-pass in selftest
    the "( private )" become prefix of their word.help !
    --> value command gets stack diagram ?
    --> ( command 看到 last 沒有 help 就把後續的 (...) comment 加進去了! 應該限制
        compiling state 才這麼做。
[x] *** debugging, OK now. RI: constant and value were in trouble due to that I
    changed the Comment word and the way to compile code objects.
[x] python shell and eforth 互相參考手上的資料
    >>> peforth.main()
    OK 0 constant shell  # peforth 定義的變量
    OK exit

    # 從外面把 globals() 給它
    >>> getattr(peforth.vm,'forth')['shell']=globals()
    >>> peforth.vm.forth
    {'obj2dict': <function obj2dict at 0x000002C8D8F5B1E0>,
    'description': '', 'expected_rstack': [], 'expected_stack': [],
    'test-result': 0, '[all-pass]': [],
    'shell': {'__name__': '__main__', '__doc__': None, '__package__': None,
    '__loader__': <class '_frozen_importlib.BuiltinImporter'>,
    '__spec__': None, '__annotations__': {}, '__builtins__': <module 'builtins' (built-in)>,
    'peforth': <module 'peforth' from 'c:\\Users\\hcche\\Documents\\GitHub\\peforth\\peforth.py'>}}

    >>> peforth.main()
    OK shell .
    {'__name__': '__main__', '__doc__': None, '__package__': None,
    '__loader__': <class '_frozen_importlib.BuiltinImporter'>,
    '__spec__': None, '__annotations__': {},
    '__builtins__': <module 'builtins' (built-in)>,
    'peforth': <module 'peforth' from 'c:\\Users\\hcche\\Documents\\GitHub\\peforth\\peforth.py'>}
    OK

    # 從外面 DOS copy-paste 進來，一氣呵成 (不要 indent, 用 block mode)
    python
import peforth
peforth.vm.dictate('0 constant shell')
peforth.vm.dictate('// ( -- dict ) 最外層 python interpreter 的 globals()')
getattr(peforth.vm,'forth')['shell']=globals()
peforth.main() # 從 python interpreter 切換進入 peforth
    \ 進入了 peforth interpret state
    <accept> \ 從 terminal 收取跨行 input lines
    <py>
    import sys
    push(sys)</py> constant sys
    // ( -- sys ) The sys module. Try: sys py: help(pop())
    </accept> \ ( -- string T|f ) 從 terminal copy-paste 進來的 string
    [if] tib.insert help sys [then]
[x] examples tools utilities goodies 範例 栗子 例子
    \ 列出所有的 code words
        <py> [w.name for w in words['forth'][1:] if 'code' in w.type] </pyV>
    \ 列出所有的 selftest passed words
        <py> [w.name for w in words['forth'][1:] if 'pass'==getattr(w,'selftest',False)] </pyV> . cr
    \ 列出所有 immediate words
        <py> [w.name for w in words['forth'] if getattr(w,'immediate',False) ] </pyV> . cr
    \ 把尾巴 2 個 TOS 切出來成為單獨的 list (array)
        ( -2 ) >r py: t,vm.stack=stack[rtos(1):],stack[:rpop(1)];push(t)
        --> slice
    \ Execute DOS command
        OK <py> exec('import os',globals(),globals())</py>  # import the os module
        OK py: os.system('dir')
            Volume in drive C is Windows
            Volume Serial Number is 2EA4-3202
            Directory of c:\Users\hcche\Documents\GitHub\peforth
            2017-08-23  09:31    <DIR>          .
            2017-08-23  09:31    <DIR>          ..
            2017-07-31  20:35                65 .gitattributes
            2017-06-25  13:31            18,226 voc.f
            2017-08-25  13:03    <DIR>          __pycache__
                        10 File(s)        178,951 bytes
                        3 Dir(s)  264,579,960,832 bytes free
            OK
        # But after <py> os.system(r"cd c:\Users\hcche\Documents\GitHub\ML\WH300")</py>
          the peforth working directory is not changed. It changes only the temperary shell.
    \ copy 以下 comment (用 np++ column mode) 從 DOS box Ctrl-V 一路跑起來
        <comment>
        python
        import peforth
        peforth.vm.dictate('0 constant shell')
        peforth.vm.dictate('// ( -- dict ) 最外層 python interpreter 的 globals()')
        getattr(peforth.vm,'forth')['shell']=globals()
        peforth.main() # 從 python interpreter 切換進入 peforth
        \ 進入了 peforth interpret state
        <accept> \ 從 terminal 收取跨行 input lines
        <py>
        import sys
        push(sys)</py> constant sys
        // ( -- sys ) The sys module. Try: sys py: help(pop())
        </accept> \ ( -- string T|f ) 從 terminal copy-paste 進來的 string
        [if] tib.insert help sys [then]
        </comment>
    \ DOS command line one-liner to print the path environment variable
        c:\Users\hcche\Desktop>python -m peforth s' push(os.get_exec_path())' compyle execute (see) bye

[x] <accept> <py> does not work when unless putting <py> to next line <---- problem
    --> rest of the line after <accept> should be the first line of the multiple lines
[x] OK include c:\Users\hcche\Documents\GitHub\ML\WH300\wh300.f
    C:\Users\hcche\AppData\Local\Programs\Python\Python36\lib\site-packages\sklearn\cross_validation.py:44: DeprecationWarning: This module was deprecated in version 0.18 in favor of the model_selection module into which all the refactored classes and functions are moved. Also note that the interface of the new CV iterators are different from that of this module. This module will be removed in 0.20.
      "This module will be removed in 0.20.", DeprecationWarning)
    Failed to run <Word 'sinclude'>: pop from empty list
    Continue, Debug, or Abort? [C/d/a] a
    OK
    --> possibly because rstack are to be used to return while reset() ( stop command )
        clears the rstack. --> 應該是猜對了。 stop command 只能中斷 outer loop 不能把 rstack 清掉!!
[x] let <accept> <text> auto indent. Use spaces before </accept> </text> as the common strip.
    --> study <text> </text> 直接用 BL word 把 </text> 之前的 spaces 都忽略掉了, 這裡要改一下。
    --> code test push(nextstring('[^ ]')) end-code test   123 得到:
            0: {'str': '   ', 'flag': True} (<class 'dict'>)
            1:         123          7Bh (<class 'int'>)
        用來取得 </text> 之前的 spaces --> 這只是一法,也不太好。
    --> 不如取所有 lines 的 leading spaces 之最大公因數,一律刪除就對了。
        1. 切成 lines in an array
            </text> :> splitlines() ( [lines] )
        2. 算出每行的前導 spaces 個數
            len - lstrip
            OK s"     abc" py> len(pop()) tib.
            s"     abc" py> len(pop()) \ ==> 7 (<class 'int'>)
            OK s"     abc" :> lstrip() py> len(pop()) tib.
            s"     abc" :> lstrip() py> len(pop()) \ ==> 3 (<class 'int'>)
            OK
        3. 取最小值,
            OK py> min([1,2,3]) tib.
            py> min([1,2,3]) \ ==> 1 (<class 'int'>)
            OK
        4. 每行都去除這麼多前導 spaces
            [ e for e in m]
        cls dropall <accept>
        <text>
            line1
                line2
                line3
                line4
                line5
        </text> constant lines
        </accept>
        drop tib.insert
        lines :> splitlines() constant [lines]
        <py> map(lambda x:len(x)-len(x.lstrip()),vm.forth['[lines]'])</pyV>
        constant leading-spaces // ( -- map ) 只能用一次!
        \ 檢查 leading-spaces 有兩種方法,後者才漂亮
        \ <py> [i for i in vm.forth['leading-spaces']]</pyV> tib. \ check leading-spaces
        \ leading-spaces py> list(pop()) .
            \ OK leading-spaces py> list(pop()) . # 如果 map 不大這個可以考慮
            \ [12, 16, 16, 16, 16, 8] OK
            \ OK leading-spaces py> list(pop()) . # map 之類的 iterator 都不能 rewind/reset
            \ [] OK
        leading-spaces py> min(pop()) constant common-indent
        [lines] common-indent <py> [i[tos():] for i in pop(1)]</pyV> nip constant [result]
        result py> "\n".join(pop()) constant result // ( -- string ) the cooked multi-lines string

    : -indent ( multi-lines -- cooked ) // Remove common indent of the string
        :> splitlines() ( [lines] )
        <py> map(lambda x:len(x)-len(x.lstrip()),tos())</pyV> ( [lines] map[^spaces] )
        py> min(pop()) ( [lines] indent )
        <py> [i[tos():] for i in pop(1)]</pyV> nip ( [result] )
        py> "\n".join(pop()) ;

    code -indent
        lines = pop()
        array = lines.splitlines() # [lines]
        spaces = map(lambda x:len(x)-len(x.lstrip()),array) # [spaces]
        indent = min(spaces) # number of common indent
        cut = [i[indent:] for i in array]  # [cuted lines]
        push("\n".join(cut)) end-code
        // ( multi-lines -- cooked ) Remove common indent of the string

    bingo! it works!
    [x] don't need to use map in -indent, use [f(i) for i in lines.splitlines()]
        should be enough --> Yes! The following two lines are equivalent:
        spaces = map(lambda x:len(x)-len(x.lstrip()),array) # iterator
        spaces = [len(x)-len(x.lstrip()) for x in array] # list
[x] Start to use peforth for the wh300 project . . .
    用 peforth 來實現 wh300
    第一個好消息就是 import module 變成 forth word 成功了!!
    <py>
    import numpy as np
    push(np)
    </py> constant np // ( -- numpy ) The numpy module
    OK np .
    <module 'numpy' from 'C:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36\\lib\\site-packages\\numpy\\__init__.py'> OK
    OK
    --> import to globals() is the best way. The above method is interesting but not the best.
    --> Done ! wh300.f works fine now.
[x] -indent 很聰明地 " "*100 的花招把 </text> 之前的線索給毀了!!! 目前變成過度 indent.
    --> 過度 indent 修好了， constant 的 runtime 又出問題。因為是 runtime, root cause 很難找。
        Root cause : 下面 lambda 的 code 內縮了，應該不要。所以是 -indent 有問題。
        str__', '__subclasshook__'] OK py> dictionary[456].__doc__ .
        lambda:exec(
           source = '\tpush(getattr(vm,"{}")["{}"])'.format(current, last().name)
           last().xt = genxt('constant',source)
           if not getattr(vm,current,False): setattr(vm,current,{})
           exec('getattr(vm,"{}")["{}"]=pop()'.format(current, last().name))
        ) OK 123 constant x
        Failed to run <function xt.<locals>.<lambda> at 0x000001C0C39B61E0>: unexpected indent (<string>, line 2)
        Continue, Debug, or Abort? [C/d/a] a
        OK
    --> 對照 ok of 'see constant' 可見得上面問題版的 lambda source code 裡有多的 indent
        ------------ Definition in dictionary ------------
        00456: lambda:exec(
        source = '\tpush(getattr(vm,"{}")["{}"])'.format(current, last().name)
        last().xt = genxt('constant',source)
        if not getattr(vm,current,False): setattr(vm,current,{})
        exec('getattr(vm,"{}")["{}"]=pop()'.format(current, last().name))
        )
    --> 先用醜版面過關取得完整功能, 再來對付它。
    --> interpret state ok, try compile --> ok too --> so what's the problem..it's clear
        當 <py> 之後跟著兩個 space 時其實這個實驗就已經複製到問題了, 厲害的是要到 test 的
        runtime 才會執行 lambda 從而觸發到 unexpected indent ... 難怪這麼難抓!!
            : test
            <py>
            a=1
            b=2
            c=3
            </py> ;
    --> breakpoint 在 -indent 當 last==constant 時
            code -indent
                if debug and last().name=='constant': pdb.set_trace() <--- 斷到了
                ...snip....
    --> constant 改到有問題的 <py>..</py> 版本 --> 看看這時 -indent 收到啥
        |(Pdb) p lines
        |' \n    source = \'\\tpush(getattr(vm,"{}")["{}"])...snip...
          ^---- 這個 space 就是問題所在了 ！！！！ 真難找。
    --> Root cause: in constant source code, after the <py> an extra space was there!
    --> See Ynote : "peforth -indent command indent 問題探討-- 成功了！ 扫描_20170828180311 _peforth_"

[X] reset() 能不能強一點? panic() 好幾次很煩....也許有意義?
[x] compyle 裡用到 lambda 來產生 function 有問題！
    # 這個可以!
        >>> s = '''
        ... dd = {'a':123,'b':456}
        ... print(dd)
        ... v = [dd[i] for i in dd] # 取得所有的 value of a dict
        ... print(v)
        ... '''
        >>> exec(s)  # <----------- 直接執行 exec() 很好,沒問題
        {'a': 123, 'b': 456}
        [123, 456]
        --
    # 經過 lambda 之後 local name space 就有怪現象了
    # 如下不行了, 這是經過 lambda 之後產生的結果。 compyle command 不要用 lambda . . . .
        ... s = '''
        ... dd = {'a':123,'b':456}
        ... print(dd)
        ... v = [dd[i] for i in dd] # 取得所有的 value of a dict
        ... print(v)
        ... '''
        >>> f = lambda:exec(s)
        >>> f()
        {'a': 123, 'b': 456}
        NameError: name 'dd' is not defined
        >>>
    --> compyle 裡改用 genfunc(source) 來產生 function

    ----- this snippet works fine ------------
    <py>
    # python does not support annoymous function. But it supports closure,
    # so we can recover it. genfunc("body","args") returns a function which
    # is composed by the given source code and arguments.
    def genfunc(body,args):
        local = {}
        source = "def func({}):".format(args)
        # args is something like "", or 'x, y=123,z=None'
        if body.strip()=="":
            source = source+"\n    pass\n";
        else:
            source = (source+'\n{}').format(body)
        try:
            exec(source,globals(),local)
        except Exception as err:
            panic("Failed in genfunc(body,{}): {}\nBody:\n{}".format(args,err,body))
        local['func'].__doc__ = source
        return local['func']
    push(genfunc)
    </py> constant genfunc // ( -- func ) function generater genfunc(body,args)
    genfunc <py> pop()('    print("hi")',"")</pyV> :: ()
    \ ==> hi
    ( arguments ) s" x,y"
    ( body ) <text>
        result = x**2 + y**2
        print(result)
    </text> -indent
    genfunc :> (pop(),pop()) constant f // ( -- func ) f(3,4) prints 25 which is 3^2+4^2
    f :: (3,4)
    \ ==> 25
    ----- this snippet works fine ------------
    結果：
        ^D
        hi  <--- 正確,正確
        25
        Multiple-line mode is on, Ctrl-D switches it off.
        OK
    --- genfunc() 進了 project-k kernel -----------
    ( name ) s" lalala"
    ( arguments ) s" x,y"
    ( body ) <text>
        result = x**3 + y**3
        print(result)
    </text> -indent
    py> genfunc(pop(),pop(),pop()) constant f f :: (3,4)
    # it works fine !!

    --- 有問題要到 runtime 才會發現, 故 selftest 很重要 -----------
    ( name ) s" lalala"
    ( arguments ) s" x,y"
    ( body ) <text>
        result = x*y
        print(resultttttttt)
    </text> -indent
    py> genfunc(pop(),pop(),pop()) constant f
    \ 到這裡都沒問題, 以下執行了才發現問題，而且 error message 線索差很遠
    OK f :: (1,2)
    Failed in </py> command: name 'resultttttttt' is not defined
    Body:
    pop()(1,2)
    Continue, Debug, or Abort? [C/d/a]
    ----- it works fine --------------
    [x] 改用 genfunc() 取代 lambda 之後, indent 習慣又全變了, 因為 function body
        一定要 indent 而與原來的 exec(body) 相反。 共有 <py> py> py: :: :> 這些
        東西受影響, 剩下 :: :> 要改 --> all done.
    [x] Now without lambda (genfunc instead) test the original problem:
        <py>
        dd = {'a':123,'b':456}
        print(dd)
        v = [dd[i] for i in dd] # 取得所有的 value of a dict
        print(v)
        </py>
        results:
        {'a': 123, 'b': 456}
        [123, 456]  <---------------- Pass!!

[x] code compyle
        execute('-indent');execute('indent')
    若用 dictate('-indent indent') 則無效, 何故?
    --> 以下實驗卻又都 ok !
    --> RI: 因為當時在 compiling state !! 用 dictate() 的結果是把兩個 words
        compile 進去了，既沒效果又出別的問題。
    ==> 用 dictate() 問題比較多，不能放心亂用。

    這兩行 debug trick 技巧留作紀念：
        if tos().find('vm.greeting')!=-1: pdb.set_trace()
        dictate('-indent indent')  # 奇怪, dictate 就不行???

[x] (forget) in trouble now
    OK (forget)
    Failed to run <function compyle_anonymous at 0x0000018230B22400>: 'Word' object has no attribute 'cfa'
    --> 這問題自動好了
[x] improve the greeting when imported from python interpreter
    OK py> sys.argv .
    ['peforth.py'] <------- run from DOS box
    >>> import peforth
    OK py> sys.argv .
    [''] <----------------- run from python interpreter, need more help messages
[x] 整理 try - exception in peforth.f
    # 從 python interpreter 裡用 genfunc() 產生 function
        >>> f = peforth.vm.genfunc(" 1/0",'','test2')
        >>> f
        <function test2 at 0x000001B42DB13E18>

        # 測試看看，確實會出錯
        >>> f()
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "<string>", line 2, in test2
        ZeroDivisionError: division by zero
        >>> f
        <function test2 at 0x000001B42DB13E18>

        # 直接 compile 進 peforth 的字典
        >>> peforth.vm.comma(f)

    # 進到 peforth 一執行 error message 又是 </py> 發的！
        >>> peforth.main()
        OK here 1- @ :: ()
        Failed in </py> (compiling=False): division by zero
        Body:
        pop()()
        Continue, Debug, or Abort? [C/d/a] a

    # 檢查看看，他確實是 test2
        OK here 1- @ :> __doc__ .
        def test2():
         1/0 OK

    --> 探討原因，似乎「誰執行的，error message 就打給誰」，這樣應該資訊比較充分。
        :: 裡面 interpret state 是 </py>, compiling state 則是 compyle --> 試試看

        OK here 1- @ constant f \ 取得 test2 function
        OK : test f :: () ;  \ 故意讓 :: 的 compiling state 表演
        OK test \ 一執行，報錯的變成 phaseB()
        Callable in phaseB <function compyle_anonymous at 0x000001CC3771D1E0>: division by zero
        Body:
        def compyle_anonymous():
            pop()()
        Continue, Debug, or Abort? [C/d/a] a
        --> ^^^^^^^--- 這個 Body information 似乎沒啥用，好像錯了？其實沒錯。
        --> 如下，這是 f :: () 這種寫法的結果，沒錯，它的 Body 當然顯示不出 f 的 source code
            ------------ Definition in dictionary ------------
            00711: f  __str__  (<class 'projectk.Word'>)
            00712: def compyle_anonymous():
                pop()() (<class 'function'>)
              2           0 LOAD_GLOBAL              0 (pop)
                          2 CALL_FUNCTION            0
                          4 CALL_FUNCTION            0
                          6 POP_TOP
                          8 LOAD_CONST               0 (None)
                         10 RETURN_VALUE
            00713: RET  (<class 'NoneType'>)
            ------------ End of the difinition ---------------

        --> 正確的寫法是 :

            OK : test2 [ f , ] ;
            OK test2
            Callable in phaseB <function test2 at 0x000001CC35113E18>: division by zero
            Body:
            def test2():   <------------------ 果然顯示出了 除0 的 source code
             1/0
            Continue, Debug, or Abort? [C/d/a] a

            OK see test2
            {
                ... snip...
                "cfa": 715
            }
            ------------ Definition in dictionary ------------
            00715: def test2():
             1/0 (<class 'function'>)
              2           0 LOAD_CONST               1 (1)
                          2 LOAD_CONST               2 (0)
                          4 BINARY_TRUE_DIVIDE
                          6 POP_TOP
                          8 LOAD_CONST               0 (None)
                         10 RETURN_VALUE
            00716: RET  (<class 'NoneType'>)
            ------------ End of the difinition ---------------
            OK
    --> 即使在 interpret state 也不一定讓 </py> 來報錯（描述不精確），如下：
        OK f py: execute(pop())
        Callable in phaseB <function test2 at 0x000001CC35113E18>: division by zero
        Body:
        def test2():  <----------------- 直接就看到真正的 source code
         1/0
        Continue, Debug, or Abort? [C/d/a]
    --> try: exception: 以後繼續改進。。。。。。
[x] multiple lines of tib. are not showing correctly.
    --> try test.f
        111 tib.
        222 tib.
        333 tib.
    --> I've got it. From clipboard is ok, from accept2 is not.
        OK ^D
                111 tib.
                222 tib.
                333 tib.
        ^D
        111 \ ==> 111 (<class 'int'>)
        111 \ ==> 222 (<class 'int'>)
        111 \ ==> 333 (<class 'int'>)
        OK
    --> fixed
[x] RET at end of dictionary is expected but missing <--- problem!!
    --> improve (dump) d dump --> ok now
[x] Oh, my God! peforth can be a debugger or 內視鏡 of python:
    <py>
    any python code; peforth is available e.g. push()
    push(123);import peforth;peforth.main() # enter peforth break point, wonderful !!
    </py>
    --> The way to enter peforth interpreter is not very good, though it's clear.
    --> ok now, the breakpoint usage is :
            push(locals());ok('111>>')
    ==> python -i 本來就可以回到 phthon interpreter 以便進行靜態分析執行結果。
        寫就 endo.py ( see my ynote) 當作 pdb 的另一選擇，在斷點上查看程式當時狀態。
[x] 手動 install peforth 的方法 see my ynote
    [x] peforth package 裡面 __init__.py 就是 peforth.py 也就是 __main__.py
    [x] 這時候要解決的是 peforth.f , quit.f 的 path , 用 __path__[0] 即可。
    [x] import projectk.py as vm 要改成 from . import projectk.py as vm 把 path 指定清楚
    [x] projectk.py 裡面用 vm = __import__(__name__) 在 package 裡不適用
        改由 __init__.py 來填 vm.vm = vm 即可。
    ==> 成功了 ！
        手動安裝
        ========
        1. 把本 project 的四個檔案 projectk.py quit.f peforth.f __main__.py 全部 copy 到如下新創建的 folder: c:\Users\yourname\AppData\Local\Programs\Python\Python36\Lib\site-packages\peforth
        2. 把其中 __main__.py 多 copy 一份成 __init__.py 即可。

        執行 peforth 有四個方式
        =======================
        1. 從 project folder 下執行 python __main__.py OK 後打 : test .’ hello world!’ cr ; test 印出 hello world! 打 bye 離開。
        2. 從 project folder 外面執行 python peforth OK 後打 : test .’ hello world!’ cr ; test 印出 hello world! 打 bye 離開。
        3. 安裝好 peforth package 之後,任意 folder 下執行 python -m peforth 後同上。
        4. 安裝好 peforth package 之後,任意 folder 下執行 python 然後 import peforth 然後按照指示打 peforth.main() 進入 peforth 後同上。

[x] why peforth? why endo.py? 一個 object 用來保存被觀察的 locals 不就好了？
        1. indent 自由
        2. 現成的 tool, forth 可以記住很多命令, 複雜的 command 可以臨時組合而成

[x] peforth 既然可以是個 python debug 學習工具，拿 peforth 來當 breakpoint 就要盡量簡單。
    --> The REPL, peforth.main(), renamed to peforth.ok()
        REPL, or Read-Eval-Print-Loop.
    --> peforth.ok(prompt='OK ',loc={}) for user to specify the prompt and giving the locals
        at the moment.
    --> at the point ok() started, TOS is the tuple with information from the caller.
        The data stack was supposed to be empty, here after it won't be.
    --> The TOS provides the prompt, the locals
[x] debug command 不要了, 會跟 py> debug which is vm.debug 撞名,沒必要增加這個問題。

[X] I found a python problem!!
    False==0 is True, False<=0 is True, False<=0.1 is True
    False<0.0001 is True, False<-0.1 is False
    這是在引用 debug 來篩選哪些 breakpoint 做不做用時遇到的問題。debug 初值為 False 結果
    debug<=33 竟然是成立的! 
    2019/11/25 10:26:06 
[x] ." a" prints an extra space <--- problem
    RI: dot . command 早期為了 debug 好看，有多印一個 space 可以不要了。
[x] peforth.path to indicates the home directory where peforth.f is
[x] IDLE generates keyboardinterrupts
    try-except can fix it http://effbot.org/zone/stupid-exceptions-keyboardinterrupt.htm
    --> 改寫 accept 加上了 try-except 檢查避免被 IDLE resize window 時的 KeyboardInterrupt
        意外甩出。
    --> resize window 的 KeyboardInterrupt 好了，但是 Ctrl-D 不能用，要輸入 multi-lines 可
        改用 <accept> ... </accept> tib.insert 代替。
[x] peforth 的 version 在 whl 打包時要如何統一定義來源？
    本文 "Single sourcing the version" 提供多種選擇。
    https://packaging.python.org/guides/single-sourcing-package-version/#single-sourcing-the-version
    我選用了 version.txt 檔案的方法，好像與 jeforth.3we 類似。
    peforth/version.txt 只有一行 python statement 讓相關的單位都來參考它。
    [X] 因此今後 projectk.major_version 就留在 projectk.py 裡沒有直接用到了。

        __version__ = "1.02"

    試出適合 setup.py 使用的 experiments 如下:

        dropall cls
        <accept>
        <py>
        loc = {} # locals
        with open(v('package-directory')+"peforth\\"+"version.txt") as fp:
            exec(fp.read(),{},loc )
            # later on we use: loc['__version__']
        push(loc)
        print('loc[\'__version__\'] is ',loc['__version__'])
        </py>
        </accept>
        tib.insert
        .s

    實際在 setup.py 裡的程式：

        loc = {} # locals
        with open("peforth/version.txt") as fp:
            exec(fp.read(),{},loc ) # later on we use: loc['__version__']

        version=loc['__version__'] # Refered in setup(...) as an argument

    在 peforth/__main__.py 裡的程式：

        # Get version code from peforth/version.txt for whl package
        # to see the single source of version code.
        exec(readTextFile(path + "version.txt"),{},locals())
        vm.version = __version__

[x] Improve (see) to see source code from project-k
    OK py> reset (see) <--- no good so far
        {
            "__class__": "function",
            "__module__": "peforth.projectk"
        }
    py> reset.__doc__ tib. \ ==> None (<class 'NoneType'>)
    py> reset.__code__ tib. \ ==> <code object reset at 0x000001CE712C2810, file "C:\Users\hcche\AppData\Local\Programs\Python\Python36\lib\site-packages\peforth\projectk.py", line 42> (<class 'code'>)
    __code__ is the chance to improve.
    [x] (see) only sees class and module, that can be improved to include some more e.g. __code__
    ==> circular reference detected 無法解決, 暫用 .members .source 應付。
[x] 決心用 3hta 寫一個 pykb.f 專門用來給 peforth 當 keyboard input to support multiple lines
    find the process ID of peforth for sendkey
    s" where name like '%python%'" see-process
    --> 已經完成 include pykb.f 之後，用 {F7} 把 inputbox 下給 python
    [x] T550 上 activate-shell 無效，sendkeys 還好。但是 git.f 卻又好好的。
        --> 似乎從 __main__.py 直接執行的 python 是切不過去的，經由 DOS Box 跑起來的才可以。
            > include git.f \ 對照看看為何人家可以？
            > s" where name like '%python%'" list-them
            python.exe:8212 \ 查出 python (直接 double click __main__.py 起來的)
            > WshShell :: appActivate(8212)
            > launch-git-shell
            > shellId . ==>  1608 \ 查出 git shell
            > WshShell :: appActivate(1608)  \ 這個可以切過去
            > WshShell :: appActivate(8212)  \ 這個就不行
        --> 如果退出 python 則該 DOS Box 能 activate 嗎？
            > s" where name like '%cmd%'" list-them
                TOTALCMD64.EXE:20780
                cmd.exe:22848
                cmd.exe:9556
            > WshShell :: appActivate(20780) 可以切到 total commander
            > WshShell :: appActivate(22848) 可以切到剛退出 peforth 的 DOS Box
            > WshShell :: appActivate(9556) 這個不知是啥，切不過去！
                用 see-process 看進去，竟然可能是 Google Chrome 的東西
                string   Name;                       cmd.exe
                uint32   ProcessId;                  9556
                string   Caption;                    cmd.exe
                string   CommandLine;                C:\WINDOWS\system32\cmd.exe /d /c "C:\Users\hcche\AppData\Local\youdao\Dict\Application\stable\text_extractor_host.exe" chrome-extension://aohddidmgooofkgohkbkaohadkolgejj/ --parent-window=0 < \\.\pipe\chrome.nativeMessaging.in.53dc641bdd08e0c9 > \\.\pipe\chrome.nativeMessaging.out.53dc641bdd08e0c9
                string   CreationClassName;          Win32_Process
        --> 所以切不到某些 process 是有的，何解？
            進一步研究發現，這個 python 是從 Anaconda3 run 起來的
            > s" where name like '%python%'" list-them
                python.exe:20092
            > WshShell :: appActivate(20092)
                string   Name;                       python.exe
                uint32   ProcessId;                  20092
                string   CommandLine;                C:\ProgramData\Anaconda3\python.exe "C:\Users\hcche\Documents\GitHub\peforth\__main__.py"
            --> Not root cause. 即使 Anaconda 的 python 也能切過去，只要。。。
        --> 把 Title 改成 peforth 吧！看看是否改得到所在的 cmd or powershell
            DOS command c:\> title titlename can change the doxbox title but it's not
            a process attribute so it doen't help.
        --> 所以答案是： 直接跑 __main__.py 或經過 dosbox 都可能行或不行，
            process ID 可以用 nnnn to processid 指定的，就算了吧！
        --> 多印些 info 讓 user 自己手動設 processid, Done!

[x] improve .members --> __class__ attribute can easily be circularly deep and long
    m py> inspect.getmembers(pop()) py> str(pop()) tib.
    [x] try to str(obj) then json.loads(string) and then json.dumps
        --> str() generates non-json 不行！
    --> 暫時放棄了

[x] C:\Users\hcche\Documents\GitHub\Morvan\tutorials\tensorflowTUT\tensorflow6_session.f
    如何一口氣把所有的 python section variables 都變成 forth values?
    l :> keys() tib. \ ==> dict_keys(
        ['result2', 'result', 'sess', 'product', 'matrix2', 'matrix1', 'tf']
    ) (<class 'dict_keys'>)

    --> 要能 programmatically 產生 constant --> 改寫 constant 得 (constant)
        : (constant)  ( n "name" -- ) // Create a constnat
            (create) <py>
            source = '    push(getattr(vm,"{}")["{}"])'.format(current, last().name)
            last().xt = genxt('constant',source)
            if not getattr(vm,current,False): setattr(vm,current,{})
            exec('getattr(vm,"{}")["{}"]=pop()'.format(current, last().name))
            </py>
            reveal ;
        OK 123 char x (constant)
        OK x . ==> 123 OK
        --> 一把就成功了！ 能不能用在 colon definition 裡面？
        : test 234 char y (constant) ;
        test
        y . ==> 234 成功！
    --> 有了 (constant) 應該就可以自動產生所有的 locals() 了
    ==> ok now! vm.outport(loc) defined in quit.f

[x] Install peforth from source 
    ---- 早期 (1.22 版以前) 不懂得用 python setup.py install 時的替代方法 ---- 
    a command to update the peforth module
    @ c:\Users\...\Python36\Lib\site-packages\peforth\..
    Get the path
        import os.path as ospath
        # py> pdb :> __file__ tib. \ ==> C:\Users\hcche\AppData\Local\Programs\Python\Python36\lib\pdb.py (<class 'str'>)
        # py> ospath.dirname(pdb.__file__) tib. \ ==> C:\Users\hcche\AppData\Local\Programs\Python\Python36\lib (<class 'str'>)
        # py> ospath.split(pdb.__file__) tib. \ ==> ('C:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36\\lib', 'pdb.py') (<class 'tuple'>)
        # py> ospath.splitdrive(pdb.__file__) tib. \ ==> ('C:', '\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36\\lib\\pdb.py') (<class 'tuple'>)
        # py> ospath.splitext(pdb.__file__) tib. \ ==> ('C:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36\\lib\\pdb', '.py') (<class 'tuple'>)
        # py> ospath.splitunc(pdb.__file__) tib. \ ==> ('', 'C:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36\\lib\\pdb.py') (<class 'tuple'>)
        py> ospath.dirname(pdb.__file__)+"\\site-packages\\peforth\\" ( targetPath )
    getenv(key, default=None)
        Get an environment variable, return None if it doesn't exist.
        The optional second argument can specify an alternate default.
        key, default and the result are str.
    getenv compare with py> ospath.dirname(pdb.__file__)
    if same then proceed the patch program to copy all files
    if not then warning and stop
    算了，直接 copy 就好了

    ------ update.bat ------
    set pythonlib=C:\Users\hcche\AppData\Local\Programs\Python\Python36\lib
    copy -y version.txt %pythonlib%\site-packages\peforth
    copy -y projectk.py %pythonlib%\site-packages\peforth
    copy -y __main__.py %pythonlib%\site-packages\peforth
    copy -y __init__.py %pythonlib%\site-packages\peforth
    copy -y peforth.f   %pythonlib%\site-packages\peforth
    copy -y quit.f      %pythonlib%\site-packages\peforth
    ------ ------ ------ ------ ------
    
    [x] 發現 pip help install 列出了 pip install 的種種用法。
        update.bat 直接從 project directly update peforth package 到
        lib\site-packages\peforth 的方式太暴力了。
        --> Try this example from pip help install : 
                pip install [options] [-e] <local project path> ...
        [X] 有待研究 14:33 18/05/21 v1.16 試用結果,失敗：    
        c:\Users\hcche\Documents\GitHub>pip install -e peforth
        Obtaining file:///C:/Users/hcche/Documents/GitHub/peforth
          Missing build time requirements in pyproject.toml for file:///C:/Users/hcche/Documents/GitHub/peforth: 'setuptools' and 'wheel'.
          This version of pip does not implement PEP 517 so it cannot build a wheel without 'setuptools' and 'wheel'.
          Installing build dependencies ... done
            Complete output from command python setup.py egg_info:
            Traceback (most recent call last):
              File "<string>", line 1, in <module>
              File "C:\Users\hcche\Documents\GitHub\peforth\setup.py", line 9, in <module>
                with open("peforth/version.txt") as fp:
            FileNotFoundError: [Errno 2] No such file or directory: 'peforth/version.txt'
            ----------------------------------------
        Command "python setup.py egg_info" failed with error code 1 in C:\Users\hcche\Documents\GitHub\peforth\
        c:\Users\hcche\Documents\GitHub>
    [x] Ynote: "研究 install peforth from source 的方法" 已經成功。
    [/] jump to 遙遠的下面 "---- 2018.12.15 懂得用 python setup.py install 需要修改 ----" 
-

[/] 螢幕編輯器
    os.get_terminal_size(...)
            Return the size of the terminal window as (columns, lines).
[x] (forget) 有 error
    'Word' object has no attribute 'cfa' <-- 用 getattr(obj,name,None) 即可。

[x] peforth 1.3 uploaded to pypi. 準備來寫 wiki 介紹怎麼
    應用 peforth 來學習 TensorFlow.
    --> Done https://github.com/hcchengithub/peforth/wiki/Example-4-Examine-a-Machine-Learning-exercise

[x] 繼續完成 peforth.f 的 selftest 元件
    --> string 轉譯成 array [d ... d] [r ... r] 要用到
    : test2 char 123,456 s" [{}]" :> format(pop()) py> eval(pop()) ;
    --> String.indexOf 改成 String.find

    \ Selftest 要 redirect print() 方便取得並檢查螢幕輸出的內容。
    \ 這是個 redirect print() 的有效範例

    \ Selftest 要 redirect print() 方便取得並檢查螢幕輸出的內容。
    \ 改寫成輸出到 buffer. See http://www.cnblogs.com/turtle-fly/p/3280519.html
        <accept>
        py> [""] value screen-buffer // ( -- 'string' ) Selftest screen buffer
        <py>
        class Screenbuffer:
            def __init__(self,buf):
                self.stdoutwas=sys.stdout
                self.buffer=buf

            def write(self, output_stream):
                self.buffer[0] += output_stream

            def view(self):
                self.stdoutwas.write(self.buffer[0])

            def reset(self):
                sys.stdout=self.stdoutwas
        vm.Screenbuffer=Screenbuffer

        # redirection
        sys.stdout=Screenbuffer(vm.forth['screen-buffer'])

        # print to screen buffer
        sys.stdout.stdoutwas.write("-------1111-----\n")
        print( 'hello')
        print( 'world')
        sys.stdout.stdoutwas.write("-------2222-----\n")

        # view screen buffer
        sys.stdout.view()

        # reset
        sys.stdout.reset()
        outport(locals())
        </py>
        </accept>
        tib.insert
[x] 探討，整理，討論幾種產生 function 或執行 inline python code 的方法
    1. projectk.py genxt() 有 __doc__ 專為 code word xt 硬性 _me argument
    2. projectk.py genfunc() 有 __doc__ 一般用途 name args body
    3. peforth.f compyle 產生一般用途的 annonymous function 沒有 args
    4. <py>...</py> 前後都是 immediate 正常使用沒問題。但若想先組合好 source code 再讓
       </py> or </pyV> 去執行，就有變化了。以下 try, try2 兩個都是有意義的、可以的
           OK : try char 123 [compile] </pyV> ;
           OK try .
           123OK
           OK : try2 [ char 123 ] </pyV> ;
           OK try2 .
           123OK
       但是下面這個其實是不知所云的：
           OK : try3 char 123 </pyV> ;
       其結果也是莫名其妙的：
           Error! try3 unknown.
           OK
    5. 直接用 exec(), eval() 執行臨時組合出來的 string, e.g. [r [d [p 的定義。
    6. 直接用 compile(), genfunc() 可能不會有，吧？

[x] 有很嚴重的 bug
    OK : test <py> 123 </pyV> ;
    OK see test
    ...snip...
    ------------ Definition in dictionary ------------
    00784: def compyle_anonymous():
        push(123 ) (<class 'function'>)
      2           0 LOAD_GLOBAL              0 (push)
                  2 LOAD_CONST               1 (123)
                  4 CALL_FUNCTION            1
                  6 POP_TOP
                  8 LOAD_CONST               0 (None)
                 10 RETURN_VALUE
    00785: RET  (<class 'NoneType'>)
    ------------ End of the difinition ---------------
    OK
    OK : test py> "abc" ;
    reDef test
    OK see test <----------- 沒反應！
    OK ' test (see)  <----------- 沒反應！
    OK ' test .  <----------- 沒反應！
    --> 順序倒過來怎樣？ 先試 : test py> "abc" ;
        --> OK 一切正常
        --> 再一個空的東西 : nothing ; --> 也正常！
        --> 就是不能有 inline python? : test2 py> 1234 ;
            --> OK 一切正常
    --> 整個重來，那這樣呢？
        : test <py> 123 </pyV> ; : test2 py> "abc" ;
        --> 都 OK, 算了，不了了之。可能是寫 selftest 捅出來的哈哈題。


[x] python or javascript can't access by address then how to
    access by reference instead of access by value? (call by name call by address call by reference)
    昨天寫 selftest 為了取得 screenbuffer 就是得定義成
        py> [""] value screen-buffer // ( -- ['string'] ) Selftest screen buffer
    而非
        py> "" value screen-buffer // ( -- 'string' ) Selftest screen buffer
    否則會 access 不到這個特定的 string.

[x] 照著 MetaMoji 2017-9-17 15:15 的討論, 研究把 <selftest> sections 都 dump 出來的辦法。
    --> 從 quit.f 裡一查即知, 應該是一行解決：
        py> tick('<selftest>').buffer char peforth-selftest.f writeTextFile stop
    --> 成功！
    --> 此後就是改寫 peforth-selftest.f 而已。
[x] (constant) 遇到 reDef writeTextFile 會議常中止 --> 不能用 panic 警告，用 print 即可。
[x] About to release peforth v1.4
    1. py:~ py>~ ::~ :>~ are so good to have.
    2. selftest not completed yet but nice to have some
    Release steps see Ynote: "Pack peforth to peforth.whl" > 打包步驟。

[x] v1.4 released, from now on v1.5

[x] 有了 argv 就不要有 greeting 也不要 reDef warnings.
    --> 所以要提早取得 command line, quit.f 太晚了。
    --> Done!
[x] PyPI README.rst 有辦法了 可查看 rst2html 也可以 convert from markdown
    https://stackoverflow.com/questions/26737222/pypi-description-markdown-doesnt-work
    --> 先用 pypandoc module 用轉的看看
        py:~ import pypandoc; push(pypandoc)
        constant pypandoc // ( -- module )
        pypandoc :: convert('README.md','rst')
        Failed in </py> (compiling=False): No pandoc was found:
        either install pandoc and add it to your PATH or or call
        pypandoc.download_pandoc(...) or install pypandoc wheels
        with included pandoc.
    --> OK pypandoc :> download_pandoc py: help(pop())
        Help on function download_pandoc in module pypandoc.pandoc_download:

        download_pandoc(url=None, targetfolder=None, version='latest')
            Download and unpack pandoc

            Downloads prebuild binaries for pandoc from `url` and unpacks it into
            `targetfolder`.

            :param str url: URL for the to be downloaded pandoc binary distribution for
                the platform under which this python runs. If no `url` is give, uses
                the latest available release at the time pypandoc was released.

            :param str targetfolder: directory, where the binaries should be installed
                to. If no `targetfolder` is give, uses a platform specific user
                location: `~/bin` on Linux, `~/Applications/pandoc` on Mac OS X, and
                `~\AppData\Local\Pandoc` on Windows.

        OK pypandoc :: download_pandoc()
        * Downloading pandoc from https://github.com/jgm/pandoc/releases/download/1.19.2.1/pandoc-1.19.2.1-windows.msi ...
        --> download 半天下不來。。。很煩
    --> http://pandoc.org/ 有 online converter , 分小段手動把 README.md 轉成 README.rst 吧！
        pandoc.org 專門做各種文檔格式轉換。
    --> Online reStructuredText editor http://rst.ninjs.org/
    --> Yes!!
[x] Release v1.5
[x] 把 update.bat setup.bat setup.py 等等統一起來
    --> 抄 3we 的 setup.bat
    --> done!
[x] Example in comment of the "words" command needs improvement
    --> 整個改良了，如今可以接受 pattern
[x] alias 要繼承原來的 help & comment 嗎？ 整個檢查看看。。。
    --> 要，但是 // 改成只有現有的 help 是 "(...)" 才用尾綴的，否則都用取代的。
[x] Bug: (see) unexpectedly leaves the given tos on the data stack if it's not a Word.
[x] 發現 python 應該也能執行 WshShell 因此可能不用靠 jeforth.3hta pykb.f
[x] 錄 elearning 介紹 peforth
[ ] wiki 介紹 py: help(genxt) py> genxt .source ' + . members 等好用的東西
    --> 唉，當時的層次真是，不好說啊！好是好，推薦自己的好東西，沒有照
        顧 user 的需求。
[X] 把網頁或至少 3hta 變成 peforth 的 input box, 解決 multiple line input 的問題。
    --> 從 peforth 去 launch 3hta include pykb.f
    --> python 能不能知道自己是誰 run 的？如果知道，就可以解決 Wsh.sendkey() 不知往哪 send
        的問題。
    --> 有 ^D, ipython, jupyter notebook 等方法了。
[x] peforth.f selftest almost done, still many to go:
    <py> [w.name for w in words['forth'][1:] if 'pass'!=getattr(w,'selftest',False)] </pyV> cr . cr
[x] 最進新發現的 bug 特別要加進 selftest
    --> (see) none Word 之後 stack 沒清乾淨 --> 有兩條路的 words 都可疑！
    --> 甚至，例如 words 最後有多印一個 print() 也是測試的重點。
[/] readTextFile, writeTextFile 好像都還不能用 -- haha bug 被 inport 取代掉的
[x] display-off 之後 on 不回來，突然發生，很奇怪。沒了 display 不好 debug.
    display-off 之內如果是 ." hello world" 就沒問題。
    是 words help 才有問題,而且是卡在 words 裡面了 <== 因為 words 出錯，導致 display-on
    沒 run 到。只要在 words 後面加上 e 就好了。表示是 nexttoken() 又出問題了，從
    檔案裡執行（而非console command line）時它會繞過 CRLF 往下抓到下一個 token 因此
    程式都亂了，特別是被他抓走的正好就是 display-on 螢幕都沒了，所以難搞。
    這類 nexttoken 可有可無的命令在 selftest 時都可能有問題。
    應該都會被挑出來。
    [x] review 所有用到 word 以及 nexttoken() 的地方。。。
[x] python -i -m peforth version
    exit 之後會有 error ---> 不見了！可能是 WshShell win32 package
    --> 又來了！！！
        c:\Users\hcche\Documents\GitHub\peforth>python -i __main__.py
        p e f o r t h    v1.07
        source code http://github.com/hcchengithub/peforth

        *** Start self-test
        *** End of peforth.f self-test ... pass
        OK bye
        Traceback (most recent call last):
          File "__main__.py", line 129, in <module>
            ok()
          .... snip ......
          File "C:\Users\hcche\AppData\Local\Programs\Python\Python36\lib\_sitebuiltins.py", line 26, in __call__
            raise SystemExit(code)
        SystemExit: None
        >>>
    --> can repro? python -i __main__.py and bye ... Yes, repro'ed
    --> OK py: exit() <--- can repro
        OK py: exit(0) <--- repro too!!!
    --> can it repro on a simplified ~.py instead of peforth?
        --> Yes!! as simple as only one statement in test.py :
            c:\Users\hcche\Downloads>type test.py
            exit()

            c:\Users\hcche\Downloads>python -i test.py
            Traceback (most recent call last):
              File "test.py", line 1, in <module>
                exit()
              File "C:\Users\hcche\AppData\Local\Programs\Python\Python36\lib\_sitebuiltins.py", line 26, in __call__
                raise SystemExit(code)
            SystemExit: None
            >>> exit()
            c:\Users\hcche\Downloads>
    --> It's not a problem. -i switch in command line normal behavior.
    --> bye to use os._exit(0) instead of exit() can fix the problem.

[x] exit command to set vm.exit=True to stop the ok() in __main__.py
[/] add bp('prompt') in addition to ok() to avoid the unnecesary awkward
    breakpoint instruction
    --> Listen to users, don't assume. ok(prompt,loc,cmd) arguments are
        all very useful.
[x] how to get vm's parent? so as to show greeting message differently
    for different situations. i.e. ok() or peforth.ok() to enter peforth
    interpreter
    --> 本來的目的不知能不能達到，有 parent 的 data 總是好的。

[x] Bug found
    c:\Users\hcche\Documents\GitHub\peforth>python -i -m peforth exit
    OK
    OK <=== python interpreter prompte expected
    --> 因為 vm.exit 有兩個！！！！
    peforth module __init__.py __main__.py 的關係不是一個！！！
    module 裡面的 __main__.py 專供 -m 執行用，改寫看看。。。。
    ==> 簡化整個執行方式，決心放棄從 project folder 執行。  ---> 2019-05-11 重新 study 有成
        只保留 import peforth 或 python -m peforth 兩種。
    --> Since commit c3d7677 on Oct 8, 2017
[x] 因應新檔案配置，setup.bat 的自動化晚點再做 --> Done
[x] Tests before a Release  v1.07
    [x] 所有 run 法帶 selftest 跑一遍
        [x] Run setup.bat 做出有 selftest 的 wheel
        [x] pip uninstall peforth
        [x] pip install peforth  <==== 啊！不行，會上網抓。
            pip install 剛做好的 wheel
        [x] 1. __main__.py [/] selfttest [/] greeting [/] exit [/] bye
        [x] 2. python __main__.py version drop [/] .s words [/] exit [/] bye
        [x] 3. python -i __main__.py [/] selfttest [/] greeting [/] exit [/] bye
        [x] 4. python -i __main__.py version drop [/] .s [/] exit [/] bye
        [x] 5. python -i -m peforth [/] selftest .s words exit
        [x] 6. python -i -m peforth version drop
        [x] 7. python import peforth
                [/] selftest peforth.ok() .s words <--- no parent
                [/] 1234 bye check echo %errorlevel%
    [x] 所有 run 不帶 selftest 再跑一遍
        [x] Run setup.bat 做出取消 selftest 的 wheel
        [x] pip uninstall peforth
        [x] pip install peforth  <==== 啊！不行，會上網抓。
            pip install 剛做好的 wheel
        [x] 1. __main__.py [/] selfttest [/] greeting [/] exit [/] bye
        [x] 2. python -i -m peforth [/] selftest .s words exit bye
        [x] 3. python -i -m peforth .' Hello World!!' cr bye
        [x] 4. python import peforth
        [x] 考慮 README.rst 改良
            --> GitHub 版的先弄好
                [x] hello world
                    Ynote: 草稿 peforth wiki article hello world  _wiki_
                [x] README.md --> README.rst by http://rst.ninjs.org
[x] These words should be moved into selftest section
        'description', 'expected_rstack', 'expected_stack', 'test-result',
        '[all-pass]', '***', 'all-pass', '[r', 'r]', '[d', 'd]']
    [x] while display-off dispaly-on should be moved out!
[x] a new word to include python file directly -- pyclude
    supports commands after #__peforth__ comment by simply removing
    all #__peforth__
    Also comment out "from __future__ import print_function" lines

    1. read the file
    2. find all #__peforth__ replace with null
    3. find "from __future__ import print_function" comment it out.
    4. -indent indent
    5. add <py> and </py>
    6. tib.insert the string

    : pyclude ( <pathname.py> -- ... ) // Run the .py file in a <PY>..</PY> space
        CR word readTextFile py> re.sub("#__peforth__","",pop())
        py> re.sub(r"(from\s+__future__\s+import\s+print_function)",r"#\1",pop())
        -indent indent <py> "    <p" + "y>\n" + pop() + "\n    </p" + "y>\n" </pyV>
        tib.insert ;
        /// Auto-remove all #__peforth__ marks so we can add debug
        /// statements what are only visible when debugging.
        /// Auto comment out "from __future__ import print_function"
        /// that is not allowed when in a <PY>..</PY> space.
[x] tib.insert is dictate now, an alias.
[x] Tests before a Release  v1.08
    [x] 所有 run 法帶 selftest 跑一遍
        [x] Run setup.bat 做出有 selftest 的 wheel
        [x] pip uninstall peforth
        [x] pip install peforth  <==== 啊！不行，會上網抓。
            pip install 剛做好的 wheel
        [x] 1. python -i -m peforth [/] selftest .s words exit
        [x] 2. python -i -m peforth version drop
        [x] 3. python import peforth
                [x] selftest peforth.ok() .s words <--- no parent
                [x] 1234 bye check echo %errorlevel%
    [x] 所有 run 不帶 selftest 再跑一遍
        [x] Run setup.bat 做出取消 selftest 的 wheel <-- 注意！改的是 site-packages\peforth
        [x] pip uninstall peforth
        [x] pip install peforth  <==== 啊！不行，會上網抓。
            pip install 剛做好的 wheel
        [x] 1. python -i -m peforth [/] selftest .s words exit bye
        [x] 2. python -i -m peforth .' Hello World!!' cr bye
        [x] 3. python import peforth
        [x] 考慮 README.rst 改良
[x] version.txt advanced to v1.09
[x] the way I get the path is not good, data files are in a separated folder
    in ubuntu. I have to manually copy data files to lib/python3.5
    Copy : none .py files are in ~/.local/lib/site-packages/peforth
        peforth.f  peforth.selftest  quit.f  version.txt
    To : .py files are in ~/.local/lib/python3.5/site-packages/peforth
        __init__.py  __main__.py  projectk.py
    Solutions I found on Stackoverflow are bad, do it manually is fine.
    [x] A wiki page discusses this. done.
    [/] 有機會解掉了。Search my Ynote: "2018/01/17 16:39 插曲，意外發現查出 python
        的東西都放哪裡的方法了！peforth 在 Ubuntu 上跑可能有救了。_peforth_
        _ubuntu_"
        [/] Study this :
        c:\Users\hcche\Documents\GitHub\DeepSpeech>py -m site
        sys.path = [
            'c:\\Users\\hcche\\Documents\\GitHub\\DeepSpeech',
            'C:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36\\python36.zip',
            'C:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36\\DLLs',
            'C:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36\\lib',
            'C:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36',
            'C:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36\\lib\\site-packages',
            'C:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36\\lib\\site-packages\\win32',
            'C:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36\\lib\\site-packages\\win32\\lib',
            'C:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36\\lib\\site-packages\\Pythonwin',
        ]
        USER_BASE: 'C:\\Users\\hcche\\AppData\\Roaming\\Python' (doesn't exist)
        USER_SITE: 'C:\\Users\\hcche\\AppData\\Roaming\\Python\\Python36\\site-packages' (doesn't exist)
        ENABLE_USER_SITE: True
        c:\Users\hcche\Documents\GitHub\DeepSpeech>

[/] 從 c:\Users\hcche\Documents\GitHub\Morvan\tutorials\tensorflowTUT\tf17_dropout\full_code-2.py
    裡，開發 harry_port() 的經驗看來，有了這麼強大的工具之後，用它臨時定義出來的
    words 不希望隨著 breakpoint 結束而被 --- marker --- 清除。怎麼辦？
    1.  要保留的東西放到 tutorial 的前面，或先 include 另一個 tool kit
        --> 這個好！
    2.  如果不用 marker (因為我的 marker 太強了，跨 vocabulary 全清！）
        就是要有 forget 能單清本 current vocabulary 的 words 到 ─── 為止。
    3.  而且要有 vocabulary, 把要保留的 words 定義到 root 去，平時在 tutorial
        vocabulary 工作。

[x] 這個 interpreter for loop 有何問題？
    OK 3 [for] t@ 100 + int digit [next]

    Failed in </py> (compiling=False): pop from empty list
    Body:
    push(pop().data[pop()])
    OK
    ==> 問題可能是出在 digit 裡面用到 <text>...</text> dictate 的 macro 形式
        證實了，因為不用該 macro 就好了

[/] harry_port() 的使用技巧，要寫進 help 裡！像這個例子，不能用 <py>...</py> block
    因為它會先 compile 而這個應用不能先被 compile :

    OK <text> locals().update(harry_port());
    batch_X, batch_Y = mnist.train.next_batch(100); outport(locals()) </text>
    py: exec(pop())

[x] exit 不夠力，會往下做。要再補個 stop 才行。
    code stop reset() end-code // ( -- ) Stop the TIB loop
    code exit
        if compiling: comma(EXIT)
        else: vm.exit=True ; reset() <---- 補 reset() 即 stop
        end-code immediate
        // ( -- ) Exit this colon word.
    靠！意外發現這個 bug !! 其實早就看到 exit 之後會暴衝，沒太在意。
[x] <accept> nop </accept> 同一行不行，要改良嗎？ ---> Done!
[x] Tests before a Release  v1.09
    [x] 所有 run 法帶 selftest 跑一遍
        [x] Run setup.bat 做出有 selftest 的 wheel
        [x] pip uninstall peforth
        [x] pip install peforth-xxxx.whl  <== 注意！用剛做好的 wheel 否則會上網抓。
        [x] 1. python -i -m peforth [/] selftest .s words exit
        [x] 2. python -i -m peforth version drop
        [x] 3. python import peforth
                [x] selftest peforth.ok() .s words <--- no parent
                [x] 1234 bye check echo %errorlevel%
    [x] 所有 run 不帶 selftest 再跑一遍
        [x] 注意！改的是 site-packages\peforth\quit.f 所以要
            在 setup.bat 做 wheel 以前插入這個動作！！！！！
            Run setup.bat 做出取消 selftest 的 wheel
        [x] pip uninstall peforth
        [x] pip install peforth-xxxx.whl  <== 注意！用剛做好的 wheel 否則會上網抓。
        [x] 1. python -i -m peforth [x] selftest .s words exit bye
        [x] 2. python -i -m peforth .' Hello World!!' cr bye
        [x] 3. python import peforth
        [x] 考慮 README.rst 改良
    [x] version 改成 1.11  (必須跳過 1.10 會變成 1.1）
[/] -indent 可以更聰明一點，目的讓 <text>...</text> 內部更自由。
    當 </text> 所在行是 blank line 時，就用它的長度當作 -indent 的最小值，這
    麼一來 <text> 之後就可以接著放東西。那它的 space 數比 </text> 之前小，就
    會被「加長」到「最小值」。這樣更自由。

[x] exit stop 之外，還需要一個中止 including 的方法。或者是仔細定義 stop, exit
    的差別或者合併。vm.exit 是給 ok() 看的，很明顯它用來回到 python interpreter
    這已經有點頭痛了，因為 exit 同時也是給 inner loop 看的 instruction 跟 RET
    等效。意思是，如果 exit 再有別的意思，恐怕連我自己都糊塗了。那只剩 stop 了，
    stop 用來打斷 outer loop 也很明確。所以，需要新的 word ... break-include
    因為 sinclude 是用 dictate 來處理 .f file 的，可能把 ntib 改一下就有 break-include
    的效果了，試試看，把斷點斷在 xray.f 裡查看半路的 tib 含不含 tutrial 。。。
    ---> Bingo!!

    : break-include ( -- ) // Break including .f file
        py: vm.ntib=len(tib) ;
    stop 就是 reset()
    exit 在 comiling 時是 EXIT==RET; 否則就是 vm.exit=True 而已，把 ok() 停下來。
    2020/06/03 10:34:10 該為 proeforth 寫了個 skip2 更有彈性。

[x] peforth 可以用來幫 .py import modules
        py> os.getcwd() constant working-directory // ( -- "path" ) Tutorial home directory saved copy
        \ my MNIST_data directory is there
        cd c:\Users\hcche\Downloads
        py:~ from tensorflow.examples.tutorials.mnist import input_data as mnist_data; push(mnist_data)
        parent :: ['mnist_data']=pop(1) \ pop(1) 很傷腦筋， in-line 要還原成 python 才看得懂。

[x] *debug* 改寫, 不要用 pdb.set_trace() 了
    不用 import 就使用 pdb 的方法
    py: sys.modules['pdb'].set_trace()
    : *debug* ( <prompt> -- ... ) // FORTH breakpoint
        BL word ( prompt ) py: ok(pop(),cmd="cr") ;
        /// How to invoke pdb:
        /// py: sys.modules['pdb'].set_trace()
    [x] now 11 *debug* >> 22 <== but 22 got skipped ! <----- problem
        --> fixed
[x] *debug* can not be used in compiling mode (colon definition) yet
    because the following prompt needs to read tib immediatedly
[x] Bug found,
        OK help a
        Word in phaseB <Word 'help'>: 'int' object has no attribute 'help'
    help improved
[x] new word "import" works fine
[x] new word __main__ works fine
    s" dos title " __main__ :> __file__ + CRLF + dictate drop
    Note! 如果沒有 CRLF 則 dos 會抓到 dictate 之後去，連 drop 都當成 command line 的一部份
[x] release 1.11
    new words import, __main__, break_include, and improved *debug* and help

[X] ( ... ) comment nested  v1.23 
[x] CRLF leaves '\r\n' on TOS
[x] Ignore command line when running in jupyter notebook
    (Pdb) vm.commandline
    '-f C:\\Users\\hcche\\AppData\\Roaming\\jupyter\\runtime\\kernel-be1c3297-f7a9-4cb2-a7aa-b06e29f158ea.json'
    (Pdb) sys.argv
    ['c:\\users\\hcche\\appdata\\local\\programs\\python\\python36\\lib\\site-packages\\ipykernel_launcher.py', '-f', 'C:\\Users\\hcche\\AppData\\Roaming\\jupyter\\runtime\\kernel-be1c3297-f7a9-4cb2-a7aa-b06e29f158ea.json']
    (Pdb) sys.argv[0]
    'c:\\users\\hcche\\appdata\\local\\programs\\python\\python36\\lib\\site-packages\\ipykernel_launcher.py'
    (Pdb) sys.argv[0].endswith('ipykernel_launcher.py') --> True , the key to know about the case

    跑 jupyter notebook 又發生 Error! -f unknown. 的問題。先前是因為
    jupyter notebook 下 import peforth 會有 unexpected command line 如上。
    這不是改好了嗎？ --> 光排除 py> sys.argv[0].endswith('.py') 不夠
    py> sys.argv[0].endswith(('.py','.ipy','.ipynb'))

[x] itchat 執行中，常有這個問題發生：
    Traceback (most recent call last):
      File "C:\Users\hcche\AppData\Local\Programs\Python\Python36\lib\site-packages\peforth\projectk.py", line 342, in outerExecute
        f = float(token) # triggers exception if token is malformed
    ValueError: could not convert string to float: '<mmreader><category'
    為何 try: exception: 攔不住它？

    Reproducing steps (at home on my desktop) :
        c:\Users\hcche\Documents\GitHub\ibrainfuck\bfinterpreter>python  v1.12 at home
        >>> import peforth
        >>> peforth.ok()
        OK sys . cr
        Traceback (most recent call last):
          File "C:\Users\hcche\AppData\Local\Programs\Python\Python36\lib\site-packages\peforth\projectk.py", line 342, in outerExecute
            f = float(token) # triggers exception if token is malformed
        ValueError: could not convert string to float: 'sys'
    終於找到複製方法了。。。。
    --> 改寫 projectk.py > outer() 之後好了。

[x] study how to run brainfuck interpreter
    c:\Users\hcche\Documents\GitHub\ibrainfuck
    --> See Ynote __brainfuck_
[x] 因 bug 發現 harry_port() 的更佳用法  （quit.f updated）
    \ Study 三寶
    \ 1. DOS Box title
        import peforth; peforth.ok(loc=locals(),cmd="include xray.f")
    \ 2. Breakpoint
        peforth.ok('11> ',cmd="parent inport")
    \ 3. Lab of copy-paste
        <accept> <text>
        # ---------------------------------------------------------------------------
        all locals() can use
        # ---------------------------------------------------------------------------
        </text> -indent py: exec(pop(),harry_port()) # If only globals is given, locals defaults to it.
        </accept> dictate

[x] msg is a forth value and also a peforth global.
    blabla bla something wrong.
    --> 不是因為繼承 JavaScript 的想法，object 與 dict 不分所造成的混淆。
         (::) (:>) 都是中性的 obj :: methed 或 obj :: ['property'] 隨人自己
         的認知而定，語法並無問題。
[x] Ipeforth kernel for Jupyter is ok now. Bring peforth to
    http://nbviewer.jupyter.org/
    How to install Ipeforth kernel for jupyter notebook :
    Copy kernel.json to here:
        %USERPROFILE%\AppData\Roaming\jupyter\kernels\peforth\kernel.json
        c:\Users\hcche\AppData\Roaming\jupyter\kernels\peforth\kernel.json
    manually create the directory if
        %USERPROFILE%\AppData\Roaming\jupyter\kernels\
    is not existing.

[x] Tests before a Release  v1.13
    [x] 所有 run 法不帶 selftest 跑一遍，準備要 release 的版本：
        [x] 改 %USERPROFILE%\Documents\GitHub\peforth\quit.f
            ' <selftest> :: enabled=False
            Run setup.bat 做出取消 selftest 的 wheel
        [x] pip uninstall peforth
        [x] pip install peforth-xxxx.whl  <== 注意！用剛做好的 wheel 否則會上網抓。
        [x] 1. python -i -m peforth [/] no-selftest .s words exit
        [x] 2. python -i -m peforth version drop
        [x] 3. python import peforth
               [x] selftest peforth.ok() .s words <--- no parent
               [x] 1234 bye check echo %errorlevel%
        [x] 4. jupyter notebook --> .s cd help bye .s cd help exit
        [x] 考慮 README.rst 改良
            [x] 若有改過 README.rst 則 wheel 就要重做
                --> quit.f selftest=False --> 重來
    [x] 所有 run 法帶 selftest：
        [x] 改 %USERPROFILE%\Documents\GitHub\peforth\quit.f
            ' <selftest> :: enabled=True
            Run setup.bat 更新本地版本以供測試
        [x] 1. python -i -m peforth [/] with-selftest .s words exit bye
        [x] 2. ipython -i -m peforth .' Hello World!!' cr bye
        [x] 3. ipython import peforth .s words
               [x] selftest peforth.ok() .s words <--- w/parent
               [x] 1234 bye check echo %errorlevel%
        [x] 4. jupyter notebook --> .s cd help bye .s cd help exit
        [x] 考慮 README.rst 改良
            [x] 若有改過 README.rst 則 wheel 就要重做
                --> quit.f selftest=False --> 重來
    [x] version 改成 1.14  (必須跳過 1.10 會變成 1.1）
    [x] Make a master release up to GitHub --> 用 GitHub Windows 很簡單。
[x] 讓 jupyter feature peforth --> 已經加進 jupyter 的 kernel list:
        https://github.com/jupyter/jupyter/wiki/Jupyter-kernels


[ ] Like harry_port that brings all wanted variables to projectk
    How to make it easier?
    [ ] Study when deep in a certain module, how peforth find and bring in
        specified variables?
        1. debug the toy.. keras exercise, breakpoint deep in a keras module
        2. instead of using the trick of loc={**locals(),**{'foo':foo,'bar':bar}}
           try to find foo,bar actual parent
        3. access volatile variables out of their scope may not be a good idea
           but being able to access them at a peforth breakpoint is necessary.

        tensor_shape is imported in C:\Users\hcche\AppData\Local\Programs\Python\Python36\Lib\site-packages\tensorflow\python\keras\_impl\keras\layers\wrappers.py

    char input_shape <text> \ local variable
    locals :> ['{0}'] constant {0}
    __main__ :: peforth.projectk.{0}=v('{0}')
    </text> :> format(pop()) dictate

    char tf <text> \ global variable
    __main__ :> {0} constant {0}
    __main__ :: peforth.projectk.{0}=v('{0}')
    </text> :> format(pop()) dictate

  * 1. char foobar module ( module )
    2. py: setattr(sys.modules['foobar'].projectk,'foobar',v('foobar')) \ add to peforth

  * 1. import numpy constant np // ( -- numpy ) module object, method #1
       py> sys.modules['numpy'] constant np // ( -- numpy ) method #2
       __main__ :> np constant np // ( -- numpy ) method #3
    2. np __main__ :: peforth.projectk.np=pop(1) \ peforth global
       np __main__ :: np=pop(1) \ __main__ global, see 'help __main__'
  * 3. py: setattr(sys.modules['peforth'].projectk,'np',v('np')) \ alt method

    char child_input_shape <text> \ local variable
    locals :> ['{0}'] constant {0}
    __main__ :: peforth.projectk.{0}=v('{0}')
    </text> :> format(pop()) dictate

    \ make librosa a global in peforth
    char librosa py> tick(tos()) execute py: globals()[pop()]=pop()

    \ even simpler way
    import librosa constant librosa char librosa librosa py: globals()[pop()]=pop()

    char input_shape <text> \ local variable
    locals :> ['{0}'] constant {0}
    __main__ :: peforth.projectk.{0}=v('{0}')
    </text> :> format(pop()) dictate

    char tensor_shape <text> \ local variable
    locals :> ['{0}'] constant {0}
    __main__ :: peforth.projectk.{0}=v('{0}')
    </text> :> format(pop()) dictate

    char selfLayer <text> \ local variable
    locals :> ['{0}'] constant {0}
    __main__ :: peforth.projectk.{0}=v('{0}')
    </text> :> format(pop()) dictate

    import peforth # [ ] _debug_
    peforth.ok(cmd='''
      0 value Count
      none value child_output_shape
      exit
      ''')

    try:
        child_output_shape = child_output_shape.as_list()
    except Exception as err:
        peforth.ok('33> ',loc={**locals(),**{'tensor_shape':tensor_shape,'self.layer':self.layer,'err':err}})

    locals :: pop('peforth') locals inport
    tensor_shape :> TensorShape(v('input_shape')).as_list() constant input_shape2
    tensor_shape :> TensorShape([v('input_shape2')[0]]+v('input_shape2')[2:])
        constant child_input_shape
    self.layer :> _compute_output_shape(v('child_input_shape')) tib. \ ==> (?, 2048) (<class 'tensorflow.python.framework.tensor_shape.TensorShape'>)
    self.layer :> _compute_output_shape(v('child_input_shape')) tib. \ ==> (?, 2048) (<class 'tensorflow.python.framework.tensor_shape.TensorShape'>)
    self.layer :> _compute_output_shape(v('child_input_shape')) tib. \ ==> None (<class 'NoneType'>)
    self.layer :> _compute_output_shape(v('child_input_shape')) tib. \ ==> None (<class 'NoneType'>)

[x] jupyter notebook 裡無法 exit , 每次 exit 都會留下一個東西在 stack 裡，出不去。
    load>   exit
    load> .s
          0: <IPython.core.autocall.ZMQExitAutocall object at 0x0000020577BF5EF0> (<class 'IPython.core.autocall.ZMQExitAutocall'>)
    load>
    --> 用 .py 比較看看 --> 沒這問題。
    --> 直接進去，直接出來看看 --> 馬上卡住了。
    --> 簡化 the peforth cell, 比較結果 ... 在 locals inport 之後多出一個 exit
        看起來還是原來的 exit 但多出來就是不對，而且 --- marker clean up 之後好了！
        充分證明就是它。
    --> 怎麼發生的？--> ipython case 下，當時的 locals() 就是有 exit quit 等一堆東西
        正好 exit 撞上了，而 locals :> ['exit'] . cr --> <IPython.core.autocall.ZMQExitAutocall object at 0x000001DBB24B5EF0>
        正是那個怪東西。
        RI

[ ] 最好 inport 能用挑的。程序如下：

    load2> locals keys . cr
        dict_keys(['__name__', '__doc__', '__package__', '__loader__', '__spec__', '__builtin__', '__builtins__', '_ih', '_oh', '_dh', 'In', 'Out', 'get_ipython', 'exit', 'quit', '_', '__', '___', '_i', '_ii', '_iii', '_i1', 'tf', '_i2', 'tflearn', '_i3', 'speech_data', '_i4', 'time', 'peforth', 'epoch_count', 'learning_rate', 'training_iters', 'batch_size', 'width', 'height', 'classes', '_i5', 'batch', 'word_batch', '_i6', 'net', 'model', 'x', '_i7'])
    \ 從上表裡面挑要用的東西
        <py> ['get_ipython', 'tflearn', 'speech_data', 'time', 'epoch_count',
         'learning_rate', 'training_iters', 'batch_size', 'width', 'height',
         'classes', 'batch', 'word_batch', 'net', 'model', 'x']
        </pyV> ( [挑過的keys] )
    \ 從 locals 裡面挑這些東西出來
        <py> dict([(k,v) for k,v in v('locals').items() if k in tos()])
        </pyV> nip ( {挑過的locals} )
    \ 可以放心地 inport 成 peforth words 了
        inport

[ ] python virtualenv http://docs.python-guide.org/en/latest/dev/virtualenvs/
    解決的問題也是 FORTH 的問題，參考人家怎麼解的，可以想想怎麼沿用，看如何只 include 必要的東西。
[x] Ubuntu 的問題好像有解了,
    --> Ubuntu 之下
    OK site :> USER_BASE . cr  不存在！
    /home/hcchen5600/.local
    OK site :> USER_SITE . cr  不存在！
    /home/hcchen5600/.local/lib/python3.6/site-packages
    OK site :> PREFIXES . cr
    ['/usr', '/usr']
    實際東西放在
    site.PREFIXES[0] + /local/lib/site-packages/peforth/

    --> windows
    OK site :> USER_BASE . cr  不存在！
    C:\Users\hcche\AppData\Roaming\Python
    OK site :> USER_SITE . cr  不存在！
    C:\Users\hcche\AppData\Roaming\Python\Python36\site-packages
    OK site :> PREFIXES . cr
    ['C:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36', 'C:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36']
    實際東西放在
    site.PREFIXES[0] + /lib/site-packages/peforth/

    --> Ubuntu virtualenv
    >>> import site
    >>> site.PREFIXES
    ['/home/hcchen5600/GitHub/DeepSpeech', '/home/hcchen5600/GitHub/DeepSpeech']
    >>> site.USER_BASE
    '/home/hcchen5600/.local'
    >>> site.USER_SITE
    '/home/hcchen5600/.local/lib/python3.6/site-packages'
    實際東西放在
    site.PREFIXES[0] + /lib/site-packages/peforth/
    也就是
    \rootfs\home\hcchen5600\GitHub\DeepSpeech\lib\site-packages\peforth\..

    \ Windows 下可 normalize the path
    照上面實施， windows 下變成
    OK py> path . cr
    C:\Users\hcche\AppData\Local\Programs\Python\Python36/lib/site-packages/peforth/
    \ 這可以用 ntpath.normpath() 解決
    OK import ntpath
    OK constant ntpath
    OK ntpath dir . cr
    ['__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', '_get_bothseps', '_getfinalpathname', '_getfullpathname', '_getvolumepathname', 'abspath', 'altsep', 'basename', 'commonpath', 'commonprefix', 'curdir', 'defpath', 'devnull', 'dirname', 'exists', 'expanduser', 'expandvars', 'extsep', 'genericpath', 'getatime', 'getctime', 'getmtime', 'getsize', 'isabs', 'isdir', 'isfile', 'islink', 'ismount', 'join', 'lexists', 'normcase', 'normpath', 'os', 'pardir', 'pathsep', 'realpath', 'relpath', 'samefile', 'sameopenfile', 'samestat', 'sep', 'split', 'splitdrive', 'splitext', 'splitunc', 'stat', 'supports_unicode_filenames', 'sys']
    OK ntpath :> normpath . cr
    <function normpath at 0x000001C511337E18>
    OK ntpath :> normpath py: help(pop())
    Help on function normpath in module ntpath:

    normpath(path)
        Normalize path, eliminating double slashes, etc.

    OK py> path ntpath :> normpath(pop()) . cr
    C:\Users\hcche\AppData\Local\Programs\Python\Python36\lib\site-packages\peforth
    OK
    \ 或者檢查看是否 Windows
    In [8]: sys.modules.get('nt') <--- None 就是沒有，就不是 windows
    In [9]: sys.modules.get('sys')
    Out[9]: <module 'sys' (built-in)>
    In [10]:
    \ 更好的方法, yeah! this is it.
    -- ubuntu --
    In [12]: os.name
    Out[12]: 'posix'
    -- windows --
    OK os :> name . cr
    nt
    [/] 有了這個 solution 連 jupyter peforth kernel 的 install 都可以自動化了。
[x] Ubuntu 的問題應該已經解決了，要推廣 peforth 必須趕快 release
    Tests before a Release  v1.14
    [x] 所有 run 法不帶 selftest 跑一遍，準備要 release 的版本：
        [x] 改 %USERPROFILE%\Documents\GitHub\peforth\quit.f
            ' <selftest> :: enabled=False
            Run setup.bat 做出取消 selftest 的 wheel
        [x] pip uninstall peforth
        [x] pip install peforth-xxxx.whl  <== 注意！用剛做好的 wheel 否則會上網抓。
        [x] 1. python -i -m peforth [x] no-selftest .s words exit
        [x] 2. python -i -m peforth version drop
        [x] 3. python import peforth
               [x] selftest peforth.ok() .s words <--- no parent
               [x] 1234 bye check echo %errorlevel%
        [x] 4. jupyter notebook --> .s cd help bye .s cd help exit
        [x] 5. repeat 以上 in ubuntu
               --> copy the wheel to WSL ubuntu
               --> use virtualenv is fine
        [/] 考慮 README.rst 改良
            [/] 若有改過 README.rst 則 wheel 就要重做
                --> quit.f selftest=False --> 重來
    [x] 所有 run 法帶 selftest：
        [x] 改 %USERPROFILE%\Documents\GitHub\peforth\quit.f
            ' <selftest> :: enabled=True
            Run setup.bat 更新本地版本以供測試
        [x] 1. python -i -m peforth [x] with-selftest .s words exit bye
        [x] 2. ipython -i -m peforth .' Hello World!!' cr bye
        [x] 3. ipython import peforth .s words
               [x] selftest peforth.ok() .s words <--- w/parent
               [x] 1234 bye check echo %errorlevel%
        [x] 4. jupyter notebook --> .s cd help bye .s cd help exit
        [x] 考慮 README.rst 改良
            [x] 若有改過 README.rst 則 wheel 就要重做
                --> quit.f selftest=False --> 重來
    [x] version 改成 1.15  (必須跳過 1.10 會變成 1.1）
    [x] 直接用測過的 wheel update Pypi
    [x] Make a master release up to GitHub --> 用 GitHub Windows 很簡單。

[x] WSL Ubuntu virtualenv weired experience
    when pip install peforth in a virtualenv --> permission denied
    --> so I use sudo and this will success but peforth will be installed
        to global instead of the virtualenv! see https://stackoverflow.com/questions/14665330/pip-requirement-already-satisfied
    --> The reason why permission denied was peforth-1.14-py3-none-any.whl which
        was copied by windows and it needs chmod 777
        \ see the correct example below:
        (DeepSpeech) hcchen5600@31ENB667:~/GitHub/DeepSpeech$ chmod 777 peforth-1.14-py3-none-any.whl
        (DeepSpeech) hcchen5600@31ENB667:~/GitHub/DeepSpeech$ pip install peforth-1.14-py3-none-any.whl
        Processing ./peforth-1.14-py3-none-any.whl
        Installing collected packages: peforth
        Successfully installed peforth-1.14
        (DeepSpeech) hcchen5600@31ENB667:~/GitHub/DeepSpeech$
[x] peforth.vm.things 的 peforth.things alias
    14:59 2018/03/11 讓 vm.execute() vm.dictate() peforth.ok() 都傳回 vm 以便 support function cascade
    19:22 2018/03/11 除了以上，連 stack, push, words, ... etc 都加上去了。
[x] %f magic command 暫無 auto-load, 必須 import peforth 才有 --> 解決了，雖然這樣也好。
    "c:\Users\hcche\OneDrive\文件\Jupyter Notebooks\Creating an IPython extension with custom magic commands.ipynb"
    討論複製過來如下:
    [x] 如上述加上 c.InteractiveShellApp.extensions = ["c:\\Users\\hcche\\Downloads\\csvmagic.py"] 之後，無效。參考 [stackoverflow](https://stackoverflow.com/questions/27483637/auto-reload-extension-not-reloading-on-change) 學到用 '%load_ext c:\\Users\\hcche\\Downloads\\csvmagic.py' 在 jupyter notebook 或 ipython 中試試看 . . . 果然是 path 寫法的問題。照以上範例, csvmagic.py 位在 current directory 直接 '%load_ext csvmagic' 就可以了。如果不在 crrent directory 那就是要 importable 則手動放到 site-packages 去亦可，討論如下。
    [x] 又或者必須是個 -m 搆得著的 module? 對了！上述的 importable 就是這個意思。--> 手動放進 site-packages (檔名改成 __init__.py) 就 importable 了，試試看 --> 成功！但是必須跑過 '%load_ext csvmagic' 之後才有 %%csv 不會自動 load。
        [x] 而且 import csvmagic 也無效；然而經過以下正確安排之後 import peforth 有效，不知何故？
    [x] 如何自動 load 應該跟 peforth 的 install 方式類似，這表示 csvmagic.py 所做的工作要由 `GitHub\peforth\peforthkernel.py` 來完成 (錯！要由 peforth 的 `__init__.py` 來負責)。其中 peforth %f 具有 line magic 與 cell magic 雙重腳色，該怎麼寫？看這裡：http://ipython.readthedocs.io/en/stable/config/custommagics.html
        # from IPython.core.magic import (register_line_magic, register_cell_magic)
        # @register_line_magic
        # def f(line):
        #     peforth.vm.dictate(line)
        #
        # @register_cell_magic
        # def f(line, cell):
        #     peforth.vm.dictate(cell)

        from IPython.core.magic import register_line_cell_magic
        @register_line_cell_magic
        def f(line, cell=None):
            if cell is None:
                peforth.vm.dictate(line)
            else:
                peforth.vm.dictate(cell)

        def load_ipython_extension(ipython):
            ipython.register_magic_function(f, 'line_cell')
            # see http://ipython.readthedocs.io/en/stable/api/generated/IPython.core.interactiveshell.html?highlight=register_magic_function

    [x] (錯!) 放進 GitHub\peforth\peforthkernel.py
    [x] (錯!) copy 到 c:\Users\hcche\AppData\Roaming\jupyter\kernels\peforth\kernel.json 所指到的位置："c:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36\\Lib\\site-packages\\peforth\\peforthkernel.py"
    [x] 重新啟動 jupyter notebook --> 結果無效, 這表示上面這段 code 沒有被執行到。可能放在 GitHub\peforth\peforthkernel.py 不對(確定不對)，也可能另有某個 .json 要指對地方。看 document 吧! --> 已知！c.InteractiveShellApp.extensions = ['peforth'] 就這行，所以上面這段要放在 peforth 的 __init__.py 才對 (對了)--> 再試試看 ... 還是無效，必須 import peforth 才行。目前這樣可以滿意了。
    [x] 我猜是 c.InteractiveShellApp.extensions = ['csvmagic','peforth'] 所在的
        profile_default\ipython_config.py 整個都無效之故。先前嘗試 "28 Jupyter
        Notebook tips, tricks and shortcuts" 該檔的另一個設定也是無效。從 path 裡
        有個 /test/ 看來，可能不是正確的檔案。--> 由 %f get_ipython :> ().ipython_dir
        . cr 得知正確的位置是：`C:\Users\hcche\.ipython` 才對，也就是
        `C:\Users\hcche\.ipython\profile_default\ipython_config.py` --> 試試看，
        有沒有自動 load_ext . . . 有了！剛改好 `profile_default\ipython_config.py`
        就馬上對新開的 jupyter notebook 有效。
[x] ipython 的 magic initialization in __init__.py 要防呆，避免從 python (none ipython)
    執行時出問題。判斷有沒有 ipython 的方法要看在哪裡判斷的， peforth __init__.py 裡
    好像太早，結果這兩個方法都 always false 而無效，不能自動 load_ext ：
        if 'get_ipython' in globals():
        if '__IPYTHON__' in dir(__builtins__):
    我看就算了，需要先 import peforth 有它的好處，例如 greeting 會出現在 import 的時候。
    [x] 從 jupyter notebook 裡面 debug peforth 的 __init__.py 很方便！用 pdb.set_trace()
        設個斷點在 ipython 判斷式前，查看以上兩個式子 --> 在當時都是 false !! 但我找到
        這個可以：
        '__IPYTHON__' in __builtins__.keys()
        B i n g o ! ! 果然成功了，我發現 __builtins__ 的定義再那之後會變，而
        __builtin__ 在那時甚至都還不存在。

[x] Tests before a Release  v1.15
    [x] 所有 run 法不帶 selftest 跑一遍，準備要 release 的版本：
        [x] 改 %USERPROFILE%\Documents\GitHub\peforth\quit.f
            ' <selftest> :: enabled=False
            Run setup.bat 做出取消 selftest 的 wheel
        [x] pip uninstall peforth
        [x] pip install peforth-xxxx.whl  <== 注意！用剛做好的 wheel 否則會上網抓。
        [x] 1. python -i -m peforth [x] no-selftest .s words exit
        [x] 2. python -i -m peforth version 12345 bye --> check errorlevel
        [x] 3. python import peforth
               [x] selftest peforth.ok() .s words <--- no parent
               [x] 1234 bye check echo %errorlevel%
        [x] 4. jupyter notebook --> .s cd help bye .s cd help exit
               %f %%f magic command
        [x] 5. repeat 以上 in ubuntu
               --> pip3 install (/mnt/...the wheel) to WSL ubuntu
               --> use virtualenv is fine
        [/] 考慮 README.rst 改良
            [/] 若有改過 README.rst 則 wheel 就要重做
                --> quit.f selftest=False --> 重來
    [x] 所有 run 法帶 selftest：
        [x] 改 %USERPROFILE%\Documents\GitHub\peforth\quit.f
            ' <selftest> :: enabled=True
            Run setup.bat 更新本地版本以供測試
        [x] 1. python -i -m peforth [x] with-selftest .s words exit bye
        [x] 2. ipython -i -m peforth .' Hello World!!' cr bye
        [x] 3. ipython import peforth .s words
               [x] selftest peforth.ok() .s words <--- w/parent
               [x] 1234 bye check echo %errorlevel%
        [x] 4. jupyter notebook --> .s cd help bye .s cd help exit
        [/] 考慮 README.rst 改良
            [/] 若有改過 README.rst 則 wheel 就要重做
                --> quit.f selftest=False --> 重來
    [x] 直接用測過的 wheel update Pypi
    [x] version 改成 1.16  (必須跳過 1.10 會變成 1.1）
    [x] Make a master release up to GitHub --> 用 GitHub Windows 很簡單。

[x] README.md needs to improve the installation guide for jupyter notebook support
    Install peforth kernel for Jupyter Notebook

    If you have ipython and jupyter installed, do following steps to add peforth
    as a kernel of Jupyter Notebook,
    Install peforth kernel for Jupyter Notebook
    1. install peforth
        pip install peforth
    2. copy
          c:\Users\yourname\AppData\Local\Programs\Python\Python36\Lib\site-packages\peforth\kernel.json
       到
          c:\Users\yourname\AppData\Roaming\jupyter\kernels\peforth\kernel.json
       如果上面的 target 目錄 kernels\ 或 peforth\ 不存在，則請手動建立這些目錄

    3. 編輯剛才這個檔案
          c:\Users\yourname\AppData\Roaming\jupyter\kernels\peforth\kernel.json
       照您的電腦實際情況，訂正其中的這個 path
          c:\Users\yourname\AppData\Local\Programs\Python\Python36\Lib\site-packages\peforth\peforthkernel.py
       以上是我的電腦的範例
    [/] 希望這個 installation 能自動化
        refer to Ynote : "怎麼加 javascript kernel 進 jupyter notebook" _ijavascript_

[x] setup.bat update 上 Pypi 成功之後，有個 error :batch not found 之類。
    upload v1.15 時發現的。應該是因為把 bye comment 掉了，往下看到 batch 的東西了。
    
[/] v1.15 %f 也發生了 comment 之後如果沒有 whitespace 會被下一行看到的問題
    %f __main__ :> census_train['age'].head(2) . cr \ 奇怪，它怎知這 dtype 是 int64?
    13:34 18/05/22 複製不出來, 上面這法都忘了怎來的了。
            
[x] 不認得的 words 自動到 __main__ 裡去找找看 <-- 成功了! v1.16
    不認得的 words 自動到 locals 裡去找找看            
    不認得的 words 自動到 globals 裡去找找看
    似乎 project-k 或看怎麼外掛一個序列 methods 用來處理 unknown workds
    --> 執行一個 word 就叫做 unknown ( 'token' -- thing Y|n) 
        傳回 True 就表示處理過了，轉回 False 就表示沒處理 (default) 然則顯示
        unknown 訊息。
    --> 先做 __main__ 的比較簡單
        : unknown py> getattr(sys.modules['__main__'],pop(),"Ûnknôwn") 
          py> str(tos())=='Ûnknôwn' if drop false else true then ; 
          // ( token -- thing Y|N) Try to find the unknown in __main__

[x] 開始 support jupyter magics 之後冒出問題，直接跑 ipython -m peforth 出 error 如下。
    先進 ipython 之後再 import peforth 就沒問題。
    
    c:\Users\hcche\Documents\GitHub>ipython -i -m peforth
    Python 3.6.0 (v3.6.0:41df79263a11, Dec 23 2016, 08:06:12) [MSC v.1900 64 bit (AMD64)]
    Type 'copyright', 'credits' or 'license' for more information
    IPython 6.2.1 -- An enhanced Interactive Python. Type '?' for help.
    p e f o r t h    v1.16
    source code http://github.com/hcchengithub/peforth
    Type 'peforth.ok()' to enter forth interpreter, 'exit' to come back.

    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)
    c:\users\hcche\appdata\local\programs\python\python36\lib\runpy.py in run_module(mod_name, init_globals, run_name, alter_sys)
        199        Returns the resulting top level namespace dictionary
        200     """
    --> 201     mod_name, mod_spec, code = _get_module_details(mod_name)
        202     if run_name is None:
        203         run_name = mod_name

    c:\users\hcche\appdata\local\programs\python\python36\lib\runpy.py in _get_module_details(mod_name, error)
        140         try:
        141             pkg_main_name = mod_name + ".__main__"
    --> 142             return _get_module_details(pkg_main_name, error)
        143         except error as e:
        144             if mod_name not in sys.modules:

    c:\users\hcche\appdata\local\programs\python\python36\lib\runpy.py in _get_module_details(mod_name, error)
        107         # Try importing the parent to avoid catching initialization errors
        108         try:
    --> 109             __import__(pkg_name)
        110         except ImportError as e:
        111             # If the parent or higher ancestor package is missing, let the

    c:\Users\hcche\Documents\GitHub\peforth\__init__.py in <module>()
        166     # Define peforth magic command, %f.
        167     @register_line_cell_magic
    --> 168     def f(line, cell=None):
        169         if cell is None:
        170             vm.dictate(line)

    c:\users\hcche\appdata\local\programs\python\python36\lib\site-packages\IPython\core\magic.py in magic_deco(arg)
        227                 break
        228         else:
    --> 229             raise NameError('Decorator can only run in context where '
        230                             '`get_ipython` exists')
        231

    NameError: Decorator can only run in context where `get_ipython` exists
    c:\users\hcche\appdata\local\programs\python\python36\lib\site-packages\IPython\core\interactiveshell.py:2598: UserWarning: Unknown failure executing module: <peforth>
      warn('Unknown failure executing module: <%s>' % mod_name)

    [x] ipython -m peforth 會出問題，可能是因為 get_ipython 當時還沒有 ready <-- 對
        NameError: Decorator can only run in context where `get_ipython` exists
        c:\users\hcche\appdata\local\programs\python\python36\lib\site-packages\IPython\core\interactiveshell.py:2598: UserWarning: Unknown failure executing module: <peforth>
          warn('Unknown failure executing module: <%s>' % mod_name)
        只要進了 ipython command prompt or jupyter notebook 都沒問題  
            In [2]: 'get_ipython' in globals()
            Out[2]: True    
        --> 用對的方法檢查 ipython magic 存不存在即可，以上 error message 提供了線索
            查看 python token 是否 defined 必須用 try-except:
            try:
                flag = "InteractiveShell" in str(get_ipython)
            except:
                flag = False

            if flag:
                from IPython.core.magic import register_line_cell_magic
                ... snip ....
                
        注意, 解掉問題之後，如今：
            1. jupyter notebook 完全沒問題。
            2. 用 ipython -i -m peforth 跑起來的，exit 到 ipython 不認得 magic commands:
                In [1]: %f
                UsageError: Line magic function `%f` not found.        
            3. 先進 ipython 然後 import peforth 的才認得 magic commands.
        
[x] Tests before releasing v1.16
    [x] 所有 run 法帶 selftest：
        [x] 改 %USERPROFILE%\Documents\GitHub\peforth\quit.f
            ' <selftest> :: enabled=True
            [x] 直接從 GitHub folder 執行 python peforth --> .s cd help exit
        [x] Run setup.bat 更新本地 pip installed 版本以供測試
        [x] 1. python -i -m peforth [x] with-selftest .s words exit bye
        [/] 2. ipython -i -m peforth .' Hello World!!' cr bye --> 目前有問題
        [x] 3. ipython import peforth .s words
               [x] selftest peforth.ok() .s words <--- w/parent
               [x] 1234 bye check echo %errorlevel% <-- 從 ipython 下直接出來也無誤。
        [x] 4. jupyter notebook 
               import peforth
               %f ." Hello FORTH!"
               %%f  Now we redefine the 'unknown' command that was doing nothing
                    : unknown ( token -- thing Y|N) // Try to find the unknown token in __main__
                      py> getattr(sys.modules['__main__'],pop(),"Ûnknôwn") 
                      py> str(tos())=="Ûnknôwn" if drop false else true then ;
                        
                    \ here after, when FORTH come accross an unknown token, instead of an error 
                    \ message, it try to find the token in python __main__ module name space.
                    y = 'abc'
                    %f y . cr
                    %f yy . cr
        [x] 考慮 README.rst 改良
            [x] 若有改過 README.rst 則 wheel 就要重做
                --> quit.f selftest=False --> 重來
    [x] 所有 run 法不帶 selftest 跑一遍，準備要 release 的版本：
        [x] 改 %USERPROFILE%\Documents\GitHub\peforth\quit.f
            ' <selftest> :: enabled=False
        [x] Run setup.bat 直接從 GitHub folder 執行 python peforth 先確定一把 --> .s cd help exit
        [x] Run setup.bat 做出取消 selftest 的 wheel
        [x] pip uninstall peforth
        [x] pip install peforth-xxxx.whl  <== 注意！用剛做好的 wheel 否則會上網抓。
        [x] 1. python -i -m peforth [x] no-selftest .s words exit
        [x] 2. python -i -m peforth version 12345 bye --> echo %errorlevel%
        [x] 3. python import peforth
               [x] selftest peforth.ok() .s words <--- no parent
               [x] 1234 bye check echo %errorlevel%
        [x] 4. jupyter notebook --> .s cd help exit
               %f %%f magic command
        [/] 5. repeat 以上 in ubuntu
           --> pip3 install (/mnt/...the wheel) to WSL ubuntu
           --> use virtualenv is fine
        [/] 考慮 README.rst 改良
            [/] 若有改過 README.rst 則 wheel 就要重做
                --> quit.f selftest=False --> 重來
    [x] 直接用測過的 wheel update Pypi
        twine upload dist/*
        ID, password search my Ynote with pypi _account_
    [x] version 改成 1.17  (必須跳過 1.10 會變成 1.1）
    [x] test mybinder.org to view peforth > notebook > *.ipynb
        不行, 猜測還是 _the_path_issue_ 的問題 <--- no, setup.py issue, see below.
    [x] Make a master release up to GitHub --> 用 GitHub Windows 很簡單。
[x] v1.16 released           

[x] (create) in peforth.f 認為當有 command line 時就不要有 reDef 警告，讓畫面清爽
    且 reDef 是常態。但是到了 jupyter notebook 底下, 他一定有 command line 

        jupyter notebook 下 
        %f py> commandline.strip() tib. ==> -f C:\Users\hcche\AppData\Roaming\jupyter\runtime\kernel-17e1c697-6363-49d3-b3af-81708a468835.json (<class 'str'>)
    
    因此 reDef 警告就都消失了也不對。因為 jupyter notebook 之下 command line 完全
    無用，因此原來的判斷方法可以保持，但是要排除 jupyter notebook 的場合。
    
    結論是 --> ('jupyter' in str(sys.modules) or not commandline.strip())
    
[x] Tests before releasing v1.17
    [x] 所有 run 法帶 selftest：
        [x] 改 %USERPROFILE%\Documents\GitHub\peforth\quit.f
            ' <selftest> :: enabled=True
            [x] 直接從 GitHub folder 執行 python peforth --> .s cd help exit
        [x] Run setup.bat 更新本地 pip installed 版本以供測試
        [x] 1.  python -i -m peforth [x] with-selftest .s words exit bye
        [x] 2.  ipython -i -m peforth .' Hello World!!' cr bye
        [x] 3.  ipython import peforth .s words
                [x] selftest peforth.ok() .s words <--- w/parent
                [x] 1234 bye check echo %errorlevel% <-- 從 ipython 下直接出來也無誤。
        [x] 4.  jupyter notebook 
                kernel > restart and clear outputs 
                import peforth
                    %%f 擴充、修訂一下 peforth 的行為模式，讓它認得 jupyter notebook 下的 globals. Dot . 也改寫了，適合 jupyter notebook 學習環境使用。
                    : unknown ( token -- thing Y|N) // Try to find the unknown token in __main__
                    py> getattr(sys.modules['__main__'],pop(),"Ûnknôwn") 
                    py> str(tos())=="Ûnknôwn" if drop false else true then ;
                    /// here after, when FORTH come accross an unknown token, instead of alerting 
                    /// it try to find the token in python __main__ module name space.
                    : . tib. ; // ( tos -- ) A better dot that also prints the entire command line
                    /// For experiments that need to show both question and result.
                    /// "" . prints the command line only, w/o the TOS.
                    : path-to-find-modules ( <path> -- ) // Add path to sys.path so "import module-name" can find the module
                        CR word trim ( "path" ) py: sys.path.append(pop()) ;
                    code \ print(nexttoken('\n')) end-code // Redefine \ command to print the comment line 
                x = 123
                %f x .     
                x . \ ==> 123 (<class 'int'>)
        [/] 考慮 README.rst 改良
            [/] 若有改過 README.rst 則 wheel 就要重做
                --> quit.f selftest=False --> 重來
    [x] 所有 run 法不帶 selftest 跑一遍，準備要 release 的版本：
        [x] 改 %USERPROFILE%\Documents\GitHub\peforth\quit.f
            ' <selftest> :: enabled=False
        [x] Run setup.bat 直接從 GitHub folder 執行 python peforth 先確定一把 --> .s cd help exit
        [x] Run setup.bat 做出取消 selftest 的 wheel
        [x] pip uninstall peforth
        [x] pip install peforth-xxxx.whl  <== 注意！用剛做好的 wheel 否則會上網抓。
        [x] 1. python -i -m peforth [x] no-selftest .s words exit
        [x] 2. python -i -m peforth version 12345 bye --> echo %errorlevel%
        [x] 3. python import peforth
               [x] no selftest, peforth.ok() .s words <--- no parent
               [x] 1234 bye check echo %errorlevel%
        [x] 4. jupyter notebook --> *debug* ok> .s cd help exit
               %f %%f magic command
        [x] 5. repeat 以上 in ubuntu
                [x] pip uninstall peforth
                [x] pip install (/mnt/...the wheel) to WSL ubuntu
                [x] ipython -m peforth
                [x] ipython , import peforth , magic commands 
    [x] 直接用測過的 wheel update Pypi
        繼續剛才的 setup.bat 即可，必要時： twine upload dist/*
        ID, password search my Ynote with pypi _account_
        --> 出錯! GFW?
            HTTPError: 403 Client Error: Invalid or non-existent authentication information. for url: https://upload.pypi.org/legacy/
        --> retry 看看 ... 這次就成功了!
            c:\Users\hcche\Desktop\peforth-master>twine upload dist/*
            Uploading distributions to https://upload.pypi.org/legacy/
            Enter your username: hcchen5600
            Enter your password:
            Uploading peforth-1.17-py3-none-any.whl
             12%|...snip....
            c:\Users\hcche\Desktop\peforth-master>
        --> 很奇怪，pypi.org 網頁上已經 upgraded 到 1.17 版了, WSL Ubuntu 下試過
            pip uninstall peforth -> pip install peforth 也到 1.17 版了，就是 
            Windows DOS 下怎麼試都還是 1.16 ! 不管了，晚點再看 --> 真的過幾分鐘就好了!!
    [x] version 改成 1.18  (必須跳過 1.10 會變成 1.1）
    [x] test mybinder.org 
        [http://github.com/hcchengithub/peforth][master][notebook]
        不行, 看來是 setup.py 的問題 --> see Ynote: "mybinder.org FileNotFoundErErrorno 2 No such file or directory"
        --> RI: 不是 bug, setup.py 改名不要讓 mybinder.org 看到即可。 
            2018.12.15 這可能是為何名為 setup.py.whl 的原因，我正在研究 command line:
                python setup.py install
            也許就是 peforth 的 install from source 的正解。
    [x] Make a master release up to GitHub --> 用 GitHub Windows 很簡單。
[x] v1.17 released --> verion.txt 跳成 v1.18 
    
[x] v1.14 v1.15 v1.16 on WSL Ubuntu, virtualenv , _the_path_issue_
    ipython still failed, message:
    ...snip...
    ~/tmp/deepspeech-venv/lib/python3.6/site-packages/peforth/__init__.py in readTextFile(pathname)
         33
         34 def readTextFile(pathname):
    ---> 35     f = open(pathname,'r',encoding='utf-8')
         36     # for line in f:
         37     s = f.read()
    FileNotFoundError: [Errno 2] No such file or directory:
    '/usr/local/lib/site-packages/peforth/version.txt'  <--- 因為 .py 與其他 files 被分開放了
    ...snip...

    [x] https://stackoverflow.com/questions/122327/how-do-i-find-the-location-of-my-python-site-packages-directory
    [x] v1.17 還是用 site.getsitepackages() 加上一點暴力    
        deli = '\\' if os.name == 'nt' else '/'
        path = "something wrong peforth path not found"
        for p in (pp for pp in site.getsitepackages() if pp.endswith("site-packages")):
            dirs = p.split(deli)
            if dirs[-2] != 'lib':  # expecting 'lib'
                dirs = dirs[:-2] + [dirs[-1]];  # if -2 is not 'lib' then remove it (pythonM.N or the likes)
            if 'lib' in dirs:  # extra check, may not be necessary
                path = deli.join(dirs) + deli + "peforth" + deli
        [x] test with WSL Ubuntu virtualenv --> failed
    [x] v1.17 failed for WSL Ubuntu in both with and without virtualenv. <-- v1.21 FP
        問題點：
            When without virtualenv:
                hcchen5600@WKS-4AEN0404:~$ python -m peforth
                Traceback (most recent call last):
                  ...snip...   
                  File "/home/hcchen5600/.local/lib/python3.6/site-packages/peforth/__init__.py", line 67, in <module>
                    exec(readTextFile(path + "version.txt"),{},locals())
                  File "/home/hcchen5600/.local/lib/python3.6/site-packages/peforth/__init__.py", line 35, in readTextFile
                    f = open(pathname,'r',encoding='utf-8')
                FileNotFoundError: [Errno 2] No such file or directory: 'something wrong peforth path not foundversion.txt'    
            When with virtualenv:
                (playground) hcchen5600@WKS-4AEN0404:~$ python -m peforth
                Traceback (most recent call last):
                  ...snip...  
                  File "/home/hcchen5600/playground/lib/python3.6/site-packages/peforth/__init__.py", line 57, in <module>
                    for p in (pp for pp in site.getsitepackages() if pp.endswith("site-packages")):
                AttributeError: module 'site' has no attribute 'getsitepackages'
        答案：
            還是這篇文章：https://stackoverflow.com/questions/122327/how-do-i-find-the-location-of-my-python-site-packages-directory
        
        [x] 正確答案先直接列出來
            w/o virtualenv  /home/hcchen5600/.local/lib/site-packages/peforth/version.txt
            with virtualenv /home/hcchen5600/playground/lib/site-packages/peforth/version.txt
            w/o virtualenv  C:\Users\hcche\AppData\Local\Programs\Python\Python36\Lib\site-packages\peforth\version.txt

        [x] 方法一、 sys.path 終極答案
            Ubuntu with virtualenv 可用(要剃除"python3.6")
                >>> import sys
                >>> [f for f in sys.path if f.endswith('site-packages')]
                ['/home/hcchen5600/playground/lib/python3.6/site-packages']
            Ubuntu w/o virtualenv 可用(要剃除"python3.6")
                >>> import sys
                >>> [f for f in sys.path if f.endswith('site-packages')]
                ['/home/hcchen5600/.local/lib/python3.6/site-packages']
            Windows w/o virtualenv 正確
                >>> [f for f in sys.path if f.endswith('site-packages')]
                ['C:\\Users\\hcche\\AppData\\Roaming\\Python\\Python36\\site-packages', 
                 'C:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36\\lib\\site-packages']
            --> 用這個方法只要把 v1.17 的 __init__.py 原來 "site.getsitepackages()" 
                改成 "sys.path" 即可，真是的！ 
        [x] 方法二、 site.getsitepackages() <--- v1.16 失敗，三個中最差的，我的媽！
            python -c "import site; print([f for f in site.getsitepackages() if f.endswith('site-packages')])" 
            Windows w/o virtualenv 正確
                python -c "import site; print([f for f in site.getsitepackages() if f.endswith('site-packages')])"
                ['C:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36\\lib\\site-packages']
            Ubuntu w/o virtualenv 錯誤！
                hcchen5600@WKS-4AEN0404:~$ python
                Python 3.6.5 (default, May  3 2018, 10:08:28)
                [GCC 5.4.0 20160609] on linux
                Type "help", "copyright", "credits" or "license" for more information.
                >>> import site
                >>> site.getsitepackages()
                ['/usr/local/lib/python3.6/dist-packages', '/usr/lib/python3/dist-packages', '/usr/lib/python3.6/dist-packages']
            Ubuntu with virtualenv 直接陣亡，根本不 support 這個命令！
                (playground) hcchen5600@WKS-4AEN0404:~/playground/bin$ python -c "import site; print([f for f in site.getsitepackages() if f.endswith('site-packages')])"
                Traceback (most recent call last):
                  File "<string>", line 1, in <module>
                AttributeError: module 'site' has no attribute 'getsitepackages'
        [x] 方法三、 不行！ <--- python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())" 
            Windows w/o virtualenv 正確
                c:\Users\hcche\Downloads>python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"
                C:\Users\hcche\AppData\Local\Programs\Python\Python36\Lib\site-packages
            Ubuntu w/o virtualenv 錯誤！
                hcchen5600@WKS-4AEN0404:~$ python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"
                /usr/lib/python3/dist-packages <--- 錯了，不能用。
            Ubuntu with virtualenv 可用(要剃除"python3.6")
                (playground) hcchen5600@WKS-4AEN0404:~/playground/bin$ python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"
                /home/hcchen5600/playground/lib/python3.6/site-packages
            
[x] 意外發現 python -m peforth include 1.f 時, 1.f 裡面不認得 ok() vm.ok()             
    RI: the recent __init__.py "run once" section that runs quit.f that runs command line
        arguments is *before* the definition of ok()! --> I move it down to the bottom
        then problem is gone. This solution will be released with v1.18.

[x] mybinder.org 跑不起來, peforth/version.txt file not found <--- RI: setup.py 改名就好了， expecting v1.18 
    See my Ynote: "mybinder.org FileNotFoundErErrorno 2 No such file or directory"
    --> 我猜是 setup.py 的檔案結構,在 Desktop\peforth-master\ 處多用了一個 peforth 
        folder 如此一來, 從 project 本身的 setup.py 所在之處來看 version.txt 就不在
        peforth/version.txt 而直接在 version.txt 才對。 v1.16 先直接修改
            Desktop\peforth-master\setup.py 
        做一版 wheel 在 local 看成不成功, 若成功就證明研究生的檔案結構多一個 peforth
        是沒必要的了，改掉就有機會了。
    --> 真的做成了, 把 peforth/ 裡的東西都移上來, setup.py 改掉,不要 peforth/, 
        如下從 working directory 執行, 成功了！
        c:\Users\hcche\Desktop\peforth-master>pip wheel --wheel-dir=dist .
        Processing c:\users\hcche\desktop\peforth-master
        Building wheels for collected packages: peforth
          Running setup.py bdist_wheel for peforth ... done
          Stored in directory: c:\users\hcche\desktop\peforth-master\dist
        Successfully built peforth
        c:\Users\hcche\Desktop\peforth-master>    
    --> 這表示根本不必搞到 Desktop\peforth-master 直接用 local GitHub repo 就可以
        了 --> 錯錯錯! Desktop\peforth-master\peforth folder 是必須的
    --> peforth/version.txt file not found 應該還是 _the_path_issue_
    [x] 做成 1.17 release 以便查看 mybinder.org 解了沒? --> failed !!
        see also : Ynote : "研究 peforth 的 path 到底正確該如何"
    [x] setup.py 是研究生為了做出 peforth 的 whl 而設。既然 mybinder.org 也要來
        看，就一定要更講究一點，我想就是這個原因....
        --> 可能要兩個 setup.py, 一個 at peforth folder, the other is for building .whl.
            when building .whl, the setup.py is at parent folder and is that a must ?
        --> anywhere>pip wheel --wheel-dir=dist c:\Users\hcche\Desktop\peforth-master 
            c:\Users\hcche\Desktop\peforth-master>pip wheel --wheel-dir=dist peforth
            以上都可以 build 出 peforthxxxxx.whl 
        --> peforth/setup.py 被 mybinder.org 看到了才出的問題, 把它改名成 setup.py.disabled 看看...
            RI: 把 setup.py 名字改掉就好了!!! 不要讓 mybinder.org 看到 setup.py 即可。
        --> 如前述，我們的 setup.py 是用來做 .whl 的，要給 pip 看的，不是要給 mybinder.org
            看的。
    [x] Merge 到 master 但可以不必急著 release, 純粹是 setup.py 的問題，跟程式無關。
        只要讓 mybinder.org 能跑，改 github 上的 setup.py 成 setup.py.whl 即可。
        --> expecting v1.18
[x] Tests before a Release v1.18 <--- on pypi.org already
    [x] 所有 run 法帶 selftest：
        [x] 改 %USERPROFILE%\Documents\GitHub\peforth\quit.f
            ' <selftest> :: enabled=True
            [取消] 直接從 GitHub folder 執行 python peforth --> 等於是 -m peforth
        [x] Run setup.bat 更新本地 pip installed 版本以供測試
        [x] 1.  python -i -m peforth [x] with-selftest .s words exit bye
        [x] 2.  ipython -i -m peforth .' Hello World!!' cr bye
        [x] 3.  ipython import peforth .s words
                [x] selftest peforth.ok() .s words <--- w/parent
                [x] 1234 bye check echo %errorlevel% <-- 從 ipython 下直接出來也無誤。
        [x] 4.  jupyter notebook 
                kernel > restart and clear outputs 
                import peforth
                    %%f 擴充、修訂一下 peforth 的行為模式，讓它認得 jupyter notebook 下的 globals. Dot . 也改寫了，適合 jupyter notebook 學習環境使用。
                    : unknown ( token -- thing Y|N) // Try to find the unknown token in __main__
                    py> getattr(sys.modules['__main__'],pop(),"Ûnknôwn") 
                    py> str(tos())=="Ûnknôwn" if drop false else true then ;
                    /// here after, when FORTH come accross an unknown token, instead of alerting 
                    /// it try to find the token in python __main__ module name space.
                    : . tib. ; // ( tos -- ) A better dot that also prints the entire command line
                    /// For experiments that need to show both question and result.
                    /// "" . prints the command line only, w/o the TOS.
                    : path-to-find-modules ( <path> -- ) // Add path to sys.path so "import module-name" can find the module
                        CR word trim ( "path" ) py: sys.path.append(pop()) ;
                    code \ print(nexttoken('\n')) end-code // Redefine \ command to print the comment line 
                x = 123
                %f x .     
                x . \ ==> 123 (<class 'int'>)
        [x] 5.  jupyter notebook --> peforth kernel 
        [/] 考慮 README.rst 改良
            [/] 若有改過 README.rst 則 wheel 就要重做
                --> quit.f selftest=False --> 重來
    [x] 所有 run 法不帶 selftest 跑一遍，準備要 release 的版本：
        [x] 改 %USERPROFILE%\Documents\GitHub\peforth\quit.f
            ' <selftest> :: enabled=False
        [x] Run setup.bat 做出取消 selftest 的 wheel
        [x] pip uninstall peforth
        [x] pip install peforth-xxxx.whl  <== 注意！用剛做好的 wheel 否則會上網抓。
        [x] 1. python -i -m peforth [x] no-selftest .s words exit
        [/] 2. python -i -m peforth version 12345 bye --> echo %errorlevel%
        [/] 3. python import peforth
               [/] no selftest, peforth.ok() .s words <--- no parent
               [/] 1234 bye check echo %errorlevel%
        [x] 4. jupyter notebook --> *debug* ok> .s cd help exit
               %f %%f magic command
        [x] 5. repeat 以上 in ubuntu
                [x] pip uninstall peforth
                [x] pip install (/mnt/...the wheel) to WSL ubuntu
                [x] ipython -m peforth
                [x] ipython , import peforth , magic commands 
    [x] 直接用測過的 wheel update Pypi
        繼續剛才的 setup.bat 即可，必要時： twine upload dist/*
        ID, password search my Ynote with pypi _account_
    [x] test mybinder.org @ [http://github.com/hcchengithub/peforth][develop][notebook]
        這個跟 pypi.org 無關，只要 github 有 push 上去馬上生效。
    [x] pypi.org 網頁上已經 upgraded 到 1.18 版了, WSL Ubuntu 下試過
            pip uninstall peforth -> pip install peforth 也到 1.17 版了，就是 
            Windows DOS 下怎麼試都還是 1.16 ! 不管了，晚點再看 --> 真的過幾分鐘就好了!!
    [x] WSL Ubuntu w/o virtualenv --> python -m peforth ... ok        
    [x] WSL Ubuntu with virtualenv --> python -m peforth ... ok        
    [/] test colab --> v1.18 還是 failed 還是 path 的問題 :-( 
    [x] version 改成 1.19  (必須跳過 1.10 會變成 1.1）
    [x] Make a master release up to GitHub --> 用 GitHub Windows 很簡單。
        
[x] test colab --> v1.18 還是 failed 還是 path 的問題 :-( 
    v1.18 is failed on colab, the chance is that v1.16 works fine on colab.
    [x] use v1.16 (pip install peforth==1.16 on colab) to check sys.path & site.getsitepackages()
        ---- from collab with peforth v1.16 ----
        import site
            site.getsitepackages()
                ['/usr/local/lib/python3.6/dist-packages',
                 '/usr/lib/python3/dist-packages',
                 '/usr/lib/python3.6/dist-packages']
        import sys
            sys.path
                ['',
                 '/env/python',
                 '/usr/lib/python36.zip',
                 '/usr/lib/python3.6',
                 '/usr/lib/python3.6/lib-dynload',
                 '/usr/local/lib/python3.6/dist-packages',
                 '/usr/lib/python3/dist-packages',
                 '/usr/local/lib/python3.6/dist-packages/IPython/extensions',
                 '/content/.ipython']
        -------- actual peforth path on Google colab ---------------         
        !ls /usr/local/lib/python3.6/dist-packages/peforth
            __init__.py  __main__.py  peforthkernel.py  projectk.py  __pycache__  setup.py
        !ls /usr/local/lib/site-packages/peforth
            kernel.json  peforthkernel.py  __pycache__  version.txt
            peforth.f    peforth.selftest  quit.f
    [/] So, the answer is clear here . . . try all possible directories with some 
        guess to find /peforth/version.txt that's doable 
    [x] can be setup.py's problem. I don't think all modules are facing the same
        annoying problem. --> try to simplify setup.py.whl 
        --> RTFD : https://packaging.python.org/guides/distributing-packages-using-setuptools/?highlight=data_files#data-files
        [x] testing c:\Users\hcche\Desktop\peforth-master\setup.py.improved that uses 
            package_data={...} instead of data_files=[...] in sety.py
            --> 用改過的 setup.py 重作 wheel  
                很奇怪，必須用 github\peforth\setup.bat 做否則 pip wheel 根本不 build 總之有個辦法可行做出了 v1.19
                See Ynote: "Pack peforth to peforth.whl" > "2018/07/02 13:06" 的討論。
            --> 直接看 ~.whl (zip檔)就知道成功了！
    [x] v1.18 用 sys.path 的加工不對了 --> 改掉 
        [x] path="" 只有 setup.bat 要看才出錯，真的不行嗎？ 
            --> 真的不行，讀 version.txt 時的 os.getcwd() 真的就是當時的 working directory，這樣不行。
            --> 所以用 sys.path 的方法還是要用 --> windows 本來就沒錯了呀! 
        [x] 改掉 setup.py 的好處是 data files 與 .py 都在一起了，但是 path 如何取得
            還是個問題 -- Ubuntu and colab 不能兩全 --> 用 sys.path 去 serch peforth/version.txt 
            還是唯一的辦法 ... 不難：
            
                path = "something wrong peforth path not found"
                for p in (pp for pp in sys.path if pp.endswith("site-packages")):
                    if os.path.isfile(p + deli + 'peforth' + deli + 'version.txt'):
                        path = p + deli + 'peforth' + deli
                        break
                vm.path = path
                pdb.set_trace()  # *debug*
        [x] windows (none anaconda virtualenv), WSL Ubuntu w/o virtualenv, with virtualenv
            --> all pass!

[x] Tests before a Release v1.19 --> v1.21 actually 
    [x] 所有 run 法帶 selftest：
        [x] 改 GitHub\peforth\quit.f
            ' <selftest> :: enabled=True
        [x] Run setup.bat 更新本地 pip installed 版本以供測試
        [x] 1.  python -i -m peforth [x] with-selftest .s words exit bye
        [x] 2.  ipython -i -m peforth .' Hello World!!' cr bye
        [x] 3.  ipython import peforth .s words
                [x] selftest peforth.ok() .s words <--- w/parent
                [x] 1234 bye check echo %errorlevel% <-- 從 ipython 下直接出來也無誤。
        [x] 4.  jupyter notebook 
                kernel > restart and clear outputs 
                import peforth
                    %%f 擴充、修訂一下 peforth 的行為模式，讓它認得 jupyter notebook 下的 globals. Dot . 也改寫了，適合 jupyter notebook 學習環境使用。
                    : unknown ( token -- thing Y|N) // Try to find the unknown token in __main__
                    py> getattr(sys.modules['__main__'],pop(),"Ûnknôwn") 
                    py> str(tos())=="Ûnknôwn" if drop false else true then ;
                    /// here after, when FORTH come accross an unknown token, instead of alerting 
                    /// it try to find the token in python __main__ module name space.
                    : . tib. ; // ( tos -- ) A better dot that also prints the entire command line
                    /// For experiments that need to show both question and result.
                    /// "" . prints the command line only, w/o the TOS.
                    : path-to-find-modules ( <path> -- ) // Add path to sys.path so "import module-name" can find the module
                        CR word trim ( "path" ) py: sys.path.append(pop()) ;
                    code \ print(nexttoken('\n')) end-code // Redefine \ command to print the comment line 
                x = 123
                %f x .     
                x . \ ==> 123 (<class 'int'>)
        [x] 5.  jupyter notebook --> peforth kernel --> .s words 
        [/] 考慮 README.rst 改良
            [/] 若有改過 README.rst 則 wheel 就要重做
                --> quit.f selftest=False --> 重來
    [x] 所有 run 法不帶 selftest 跑一遍，準備要 release 的版本：
        [x] 改 GitHub\peforth\quit.f
            ' <selftest> :: enabled=False
        [x] Run setup.bat 做出取消 selftest 的 wheel
        [x] pip uninstall peforth
        [x] pip install peforth-xxxx.whl  <== 注意！用剛做好的 wheel 否則會上網抓。
        [x] 1. python -i -m peforth [x] no-selftest .s words exit
        [x] 2. python -i -m peforth version 12345 bye --> echo %errorlevel%
        [x] 3. python import peforth
               [x] no selftest, peforth.ok() .s words <--- no parent
               [x] 1234 bye check echo %errorlevel%
        [x] 4. jupyter notebook --> *debug* ok> .s cd help exit
               %f %%f magic command
        [x] 5. repeat 以上 in ubuntu
                [x] pip uninstall peforth
                [x] pip install (/mnt/...the wheel) to WSL ubuntu
                [/] ipython -m peforth
                [/] ipython , import peforth , magic commands 
    [x] 直接用測過的 wheel update Pypi
        繼續剛才的 setup.bat 即可，必要時： twine upload dist/*
        ID, password search my Ynote with pypi _account_
    [x] pypi.org 網頁上已經 upgraded 到 1.19 版了, 
        若不行，晚點再看，過幾分鐘就好。
        [x] WSL Ubuntu 下試 pip uninstall peforth -> pip install peforth
            [x] WSL Ubuntu with and w/o w/o virtualenv --> python -m peforth
        [x] Windows DOS 下試
    [x] test mybinder.org @ [http://github.com/hcchengithub/peforth][develop][notebook]
        這個跟 pypi.org 無關，只要 github 有 push 上去馬上生效。
    [x] test colab --> v1.19 --> shit, 又錯了! 不能限定要 site-packages, dist-packages 也要接受
            deli = '\\' if os.name == 'nt' else '/'
            path = "wrong"
            for p in sys.path:
                if os.path.isfile(p + deli + 'peforth' + deli + 'version.txt'):
                    path = p + deli + 'peforth' + deli
                    break
        以上這改就對了，出 v1.21 版吧! Shit shit . . . 
        [x] __init__.py 
        [x] rebuild setup.bat 
        [x] release v1.21 to pypi.org 
        [x] test colab ... !pip install peforth==1.21 要等一等。。。 v1.21 成功了！ 嗚嗚嗚
    [x] Make a master release up to GitHub --> 用 GitHub Windows 很簡單。
    [x] version 改成 1.22  (必須跳過 1.20 會變成 1.2）
[x] 14:48 2018-12-09 python object (attributes -> values) and hash table or 
    dictionary (keys --> values) are confusing me especially when JavaScript sees 
    both the samething. The python 'dir' function lists an object's attributes and
    JSON can stringify a hash table to a readable string. Let's make an experient:

    \ o1 is a dict     
    py> {'a':11,'b':22} constant o1
    OK o1 tib. --> {'a': 11, 'b': 22}                \ it's a dict so it's shown as a dict
    OK o1 :> keys() . cr --> dict_keys(['a', 'b'])   \ dict has keys
    OK o1 :> values() . cr --> dict_values([11, 22]) \ dict has values 
    \ it's also an ojbect
    OK o1 dir . cr \ so it has attributes 
    --> ['clear', 'copy', 'fromkeys', 'get', 'items', 'keys', 'pop', 'popitem', 'setdefault', 'update', 'values']
    OK o1 stringify . cr
    {
        "a": 11,
        "b": 22
    }
    OK 
    這樣看來，dict 與 object 的混淆是 JavaScript user 的問題。 任何東西都是 object 而只有 dict 才有 hash table.
    用 (see) dir .members 查看 object 的 attributes, 用 (see) keys values 查看 dict. 用 stringify 查看 dict'fy 之後的
    任何東西。
    --> 結論是在 help (see) 裡講清楚就好了。 來自 jeforth 的 obj>keys 與 dir 或 keys 重複所以很少用了。
    
[x] Install peforth from source 
    ---- 2018.12.15 懂得用 python setup.py install 需要修改 ---- 
    [x] Ynote: "研究 install peforth from source 的方法" 已經成功。
    [x] 結論是： peforth/ 目錄結構要遷就研究生的安排，改變原先其實不太自然的執行方式: 
            C:\Users\hcche\Documents\GitHub\>python peforth
        變成從 peforth 目錄裡面執行，這很好哇！ [X] v1.22 1.23 __main__.py 還是用 import peforth 的，沒意思 --> 有 support test.py 取代 __main__.py 供 developing debugging 用
    [x] pywinio repo 裡面也是又有一個 pywinio/ folder, 將來 peforth 也是這樣。
    [x] 照研究生的目錄結構改 GitHub/peforth 
        c:\Users\hcche\Documents\GitHub\peforth\.. 
        Directories             Files
        --------------------    ---------------------------
        .git\                   .gitattributes
        .ipynb_checkpoints\     LICENCE
        __pycache__\            admin.bat
        notebook\               requirements.txt
        peforth\                LICENSE
        peforth.egg-info\       README.md
        playground\             README.rst
                                setup.bat
                                setup.py
                                setup.py.whl
                                log.txt
                                .gitignore
        c:\Users\hcche\Documents\GitHub\peforth\peforth\.. 
        Directories             Files
        --------------------    ---------------------------
                                __main__.py
                                kernel.json
                                peforthkernel.py
                                projectk.py
                                peforth.selftest
                                version.txt
                                __init__.py
                                quit.f
                                peforth.f       
    [x] remove existing peforth so aso to try setup.py install
        Python on my computer at home is anaconda, so though that I have to remove it
        by "conda uninstall" command. That was wrong. Do it by pip as usual works fine.
        see Ynote:"研究 install peforth from source 的方法" for the log.
    [x] now try "python setup.py install"
        it works !!!! 
        如何查看 setup.py 的 help: c:\Users\hcche\Documents\GitHub\peforth>python setup.py --help
[x] setup.bat 可以大簡化了。
    [V1.22之後的新版] 打包步驟  2018/12/16 11:02 
    See my Ynote: "Pack peforth to peforth.whl"
    1.  檢查 ~\GitHub\peforth\setup.py 看有沒有漏掉新檔案，有沒有要去掉的檔案。
    2.  跑 c:\Users\hcche\Documents\GitHub\peforth>python setup.py sdist bdist_wheel
        得到 peforth.whl in c:\Users\hcche\Documents\GitHub\peforth\dist
    3.  執行 c:\Users\hcche\Documents\GitHub\peforth>twine upload dist/* 
        需要帳號密碼，看這裡 Ynote: "python pypi 研究 -- upload to PyPI ok now.note"
    4.  pip uninstall peforth 然後再 pip install peforth 試驗看看。
    5.  完成！
        
[x] 13:27 2019-03-06 code ... end-code 可以取 xt.__doc__ 2nd line 當作 help
    code txt2json # ( txt -- dict ) Convert given string to dictionary
        push(json.loads("".join([ c if c != "'" else '"' for c in pop()])))
        end-code
    ' txt2json :> xt :> __doc__ --> def xt(_me=None): ### txt2json ###
        # ( txt -- dict ) Convert given string to dictionary
           push(json.loads("".join([ c if c != "'" else '"' for c in pop()]))) (<class 'str'>)
    18:04 2019-05-09 寫好了：
        # projectk.py 裡面
        # The basic FORTH word 'end-code's run time. 
        def doendcode(_me=None):
            global compiling
            if compiling!="code":
                panic("Error! 'end-code' a none code word.")
            current_word_list().append(Word(newname,newxt))
            last().vid = current;
            last().wid = len(current_word_list())-1;
            last().type = 'code';
            # ---------
            mm = re.match(r"^.*?#\s*(.*)$", last().xt.__doc__.split('\n')[1])
            last().help = mm.groups()[0] if mm and mm.groups()[0] else ""
            # ---------
            wordhash[last().name] = last();
            compiling = False; 
    --> py> doendcode .source <---- 看到對的 source code 了
    [x] 試驗定義一個 code word 查看他的 help 果然第一行的 # foo bar 有被抓進去當 help 了。
            
[X] unkown debug locals() 的說明 copy 過來                
    older unsync'ed notes on my LRV2
    v1.22 既然 peforth 主要都是用來配合 jupyter notebook trace code, set breakpoints, ... etc.
    unknown and ... and # should be added into the built-in words, plus the ability to 
    view local variables.
    [x] I remember that I have done making 'unknown' predefined . . . no.
        16:51 2019-01-12 I am now working on making 'unknown' to try locals. __main__ is
        an object so global variables are accessed by getattr() however locals and globals
        are dictionary that should be accessed by dict.get(key,default) instead.
            see https://stackoverflow.com/questions/3089186/python-getattr-equivalent-for-dictionaries
    [x] done an example @
        http://localhost:8888/notebooks/OneDrive/%E6%96%87%E4%BB%B6/Jupyter%20Notebooks/Siraj%20make_a_neural_net_live_demo.ipynb

    Source Code 
    ===========
        none value _locals_ // ( -- dict ) locals passed down from ok()
        false value debug // ( -- flag ) enable/disable the ok() breakpoint
        : unknown ( token -- thing Y|N) // Try to find the unknown token in __main__ or _locals_
          _locals_ if \ in a function
            ( token ) _locals_ :> get(tos(),"Ûnknôwn") ( token, local )
            py> str(tos())!="Ûnknôwn" ( token, local, unknown? ) 
            if ( token, local ) nip true exit ( return local Y ) else drop ( token ) then   
          then   
          ( token ) py> getattr(sys.modules['__main__'],pop(),"Ûnknôwn") ( thing ) 
          py> str(tos())=="Ûnknôwn" if ( thing ) drop false else true then ; 
          /// Example: Set a breakpoint in python code like this: 
          ///   if peforth.execute('debug').pop() : peforth.push(locals()).ok("bp>",cmd='to _locals_')
          /// Example: Save locals for investigations:
          ///   if peforth.execute('debug').pop() : peforth.push(locals()).dictate('to _locals_')
          /// That enters peforth that knows variables in __main__ and locals at the breakpoint.
          /// 'exit' to leave the breakpoint and forget locals.
        : exit ( -- ) // ( -- ) Exit the breakpoint forget locals and continue the process
          none to _locals_ py: vm.exit=True ;  
        code # print(nexttoken('\n')+'\n') end-code // print the comment line after #  
        : --> ( result -- ) // Print the result with the command line.
          py> tib[:ntib].rfind("\n") py> tib[max(pop(),0):ntib].strip() ( result cmd-line )
          s" {} {} ({})" :> format(pop(),tos(),type(pop())) . cr ;
          /// Good for experiments that need to show command line and the result.

[X] 10:48 2019-05-11 older note
    開發中，不要動到 pip'ed peforth 出錯很麻煩，所以想要從 working folder 執行
    不要每次都得先 pip install 改入 site-packages
    [x] __main__.py 當初為何他媽 import peforth 有屁用？就是要跑本地版本試驗改過的東西才有意義呀！
        --> 15:48 2019-05-11 應該是 path 搞不定，簡化問題 (Since commit c3d7677 on Oct 8, 2017)。 
            __main__.py 是用 python -m peforth 執行時的 entry，必須照顧。
            11:26 2019-05-11 while __init.py__ is 'import peforth' entry point.
        --> 11:24 2019-05-11 __main__.py 就是 run 
                c:\Users\hcche\Documents\GitHub\peforth>python peforth
                and
                c:\Users\hcche\Documents>python -m peforth
                時被執行的入口
            see https://www.tuicool.com/articles/iYRfe2
                https://stackoverflow.com/questions/44977227/how-to-configure-main-py-init-py-and-setup-py-for-a-basic-package
    --> 11:51 2019-05-11 how about to have test.py that does what __main__.py is supposed to do when
        running ~GitHub\peforth>python peforth? 
        --> this is a good idea, but the path in __init__.py will be wrong, deal with it!!
            --> 從 __init__.py 裡面處理 path 處添加可能找到 version.txt 的地方即可。 成功。
    --> 成功了，能直接執行就好，不一定要堅持像早期一樣執行 peforth 目錄。
        執行方法： c:\Users\hcche\Documents\GitHub\peforth\peforth>python test.py
        __run__.py --> 最終命名為 test.py 最自然
        # 各種方法都試過，最後還是用 exec(open().read()) 最像 include 
        # from . import __init__
        # from __init__ import ok
        # import subprocess; subprocess.call("__init__.py", shell=True)
        exec(open("__init__.py").read())  # this is like: include __init__.py 
        ok('\n')
    [X] __main__.py 還是要用 import peforth 的，若不然一開始 open("__init__.py") 就 file not found 了。
        而 test.py 當然是在對的 directory 之下才能執行，所以叫做 test.py ;-D 
    [x] 若要餵進 "python test.py foo bar" 執行 command line 則 test.py 就要用來分辨
        是否「從 ipython, jupyternotebook 執行」 (參見 quit.f) 所以 test.py 檔名
        就不能改了，要改連 quit.f 也要一起改。或者改進 quit.f 裡分辨 ipython 的方法。
        \ ~~~~~~ quit.f ~~~~~~
        \ When in ipython or jupyter notebook the command line is used by 
        \ ipython already. In jupyter notebook, it looks like:
        \
        \      vm.commandline ----------------------------------------------------------------------------------.
        \      sys.argv[0]    --------.                                                                         |
        \                             |                                                                         |
        \                             V                                                                         V
        \     --------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------
        \     c:\users\hcche\appdata\local\programs\python\python36\lib\site-packages\ipykernel_launcher.py -f C:\Users\hcche\AppData\Roaming\jupyter\runtime\kernel-4be53345-1ddd-47c2-bef2-5e9801688f3f.json
        \ So peforth can't support command line statements for ipython and jupyter notebook. 
        \ For none ipython cases, I have no better idea than to check sys.argv[0] for '.py' 
        \ and the likes so far 2019-05-15. See the following code, the filename 'test.py' is 
        \ fixed-coded here therefore.
        \
    [X] command line 也是跑 site-package 之外的 .f 檔的方法，例如：
            c:\Users\hcche\Documents\GitHub\peforth\peforth>python test.py include ..\playground\misc.f
            c:\Users\hcche\Documents\>python -m peforth include GitHub\peforth\playground\misc.f
        這兩行都可以。

[x] 18:35 2019-05-09 我忘了 peforth 要怎麼 maintain 了!!!! 以上程式要改到哪裡去？
    --> 直接在 github working directory 修改
    --> 這樣 run 到的還是 installed 到 site-packages 的版本，因為 __main__.py 其實是 import peforth 
            c:\Users\hcche\Documents\GitHub\peforth>python peforth 
            16:48 2019-05-11 這個早期的 run 法如今 改成 
                c:\Users\hcche\Documents\GitHub\peforth\peforth> python test.py  
    --> 16:48 2019-05-10 奇怪 LRV2 OA 上 pip list 看到的 peforth 是 1.21!! 
        但是 python -m peforth 跑到的是 1.22，經過 pip uninstall peforth 之後
        馬上 pip list 卻看到了 peforth 1.23 (對了) 
        [x] 16:38 2019-05-22 release v1.23 時在 T550 又看到類似現象： pip uninstall peforth 
            之後有把 python setup.py install 灌上的 v1.23 uninstall 掉，但是 site-packages 裡面一查，
            仍有 v1.22 的 egg 存在 --> 直接再 pip uninstall peforth 一次，才把它 uninstall 掉。
            --> pip install peforth 下來的在 site-packages 裡面就沒有 egg 字樣，如此可供分辨。同時
                也證實 pip uninstall 不會 remove egg 版的 (python setup.py install上去的) 要下
                多次 pip uninstall peforth 才輪得到舊版。
    --> 我猜： 剛才改好程式之後用 ~\GitHub\peforth>python setup.py install 安裝進 site-package
        的 1.23 並沒有蓋掉原來的, 因為這時裝上的是 egg, path 與用 whl 裝上的不同！
    [X] 經過 c:\Users\hcche\Documents\GitHub\peforth>python setup.py install 
        之後，確實會直接有類似  pip install 的效果 --> 可以 python -m peforth 執行了，但是 path 不同
        pip install 的 c:\Users\hcche\AppData\Local\Programs\Python\Python36\lib\site-packages\peforth\version.txt 
        setup.py 的    c:\Users\hcche\AppData\Local\Programs\Python\Python36\lib\site-packages\peforth-1.23-py3.6.egg\peforth\version.txt 
    [X] 用 ~\GitHub\peforth>python setup.py install 安裝進 site-package 雖然 path 不同，jupyter notebook
        完全沒問題，頂多 Kernel > Restart 一下，馬上生效。完全符合我 「從 source 直接 install」 的期待，免去 pip install 
        或先前暴力 setup.bat 的麻煩。
    結論：
        1. 直接修改 GitHub source code (善用 GitHub 保障各版本安全）
        2. pip uninstall peforth  把舊的清乾淨
        3. c:\Users\hcche\Documents\GitHub\peforth>python setup.py install 從 source code 安裝
        4. 有兩種方式執行、測試
           a. 用 Jupyter Notebook 試驗，只要 Kernel > Restart 新版就生效了。
           b. 執行 c:\Users\hcche\Documents\GitHub\peforth\peforth>python test.py 
        5. repeat 
        
[X] 19:07 2019-05-13 這段 code 在 peforth.f 裡面本應處裡 alias 的新 // help, 但是又有問題
        \
        \ Redefine // to "replace" alias' help message instead of "append".
        \
        \ Append if last().help has stack diagram but no help message, otherewise replace. 
        \ Stack diagram might be unexpectedly given again. That can be resolved by putting 
        \ complete help message to the original word or use the trick of // dummy and then 
        \ // again or simply don't give it again in the alias' help message.
        \
        <py> 
        '''
        m = re.match("(?P<before>.*?)(?P<stackdiagram>\(.*\))(?P<after>.*)", last().help)
        if m and (m.groupdict()['before'] + m.groupdict()['after']).strip()=="":
            last().help += nexttoken('\\n|\\r'); 
        else:
            last().help = nexttoken('\\n|\\r'); 
        ''' 
        </pyV> -indent ' // py: pop().xt=genxt("//",pop(1)) 

    問題如下，有些東西 help 裡面的 stack diagram 不見了！！
        [r Prepare an array of data to compare with rstack in selftest.
                Example: [r 1,2,3 r] [d True d] [p 'word1','word2' p]
                [r...r] section is optional, [d...d] section is the judge.
    --> 點掉也沒用！ --> 13:34 2019-05-15 misc.f 裡面的新 ( comment ) 造成的。
    --> 19:15 2019-05-15 已經乾脆放棄讓 (comment) 自動進 help 了，要 help 用 // 就好了。
        (comment) 直接改成 nested 的，更好。  v1.23 
        
    [X] 14:06 2019-05-15 現在覺得原來的 (comment) 沒有我 gist words4jupyter.py 的 nested (comment) 好。
        何必搞個這麼難懂的 (comment) 就會了讓 stack diagram 進 last.help 而已，有 // 就夠了！
    [X] 16:39 2019-05-16 本來的 // 一直想著前面有 (comment) 已經進 help 了！所以他是用 += 的，
        難怪有這個問題，不要了，直接用 last().help = nexttoken('\n|\r'); 就好了。  v1.23

    \ to be 
    code (      # ( <str> -- ) // Comment down to ')' which can be nested if balanced
        nextstring('\(|\)')['str']  # skip TIB to the next delimiter
        cc = tib[ntib]  # cc must be delimiter '(', ')', or '\n'
        vm.ntib+=1      # skip any of them
        if cc=='(': 
            execute(_me)  # recursion of (
            execute(_me)  # recursion of ) 
        end-code immediate 
    \ was 
    code ( # ( <stack diagram> -- ) Get stack diagram to the last's help.  
        a = nexttoken('\\)') 
        b = nexttoken()  # the ')' 
        if compiling and last().help=="": # skip if help alreay exists
           last().help = '( ' + a + b + ' ' 
        end-code immediate
        /// Nested not allowed yet.
    
    
[X] 經 marker 刪除的 value & constant 留在 vm[context] 裡面的 garbage
    沒有回收! marker 還要再加強，forget 也要注意。
    --> 123 value x char abc value ss vm.forth dict>keys --> 
        dict_keys(['CRLF', 'obj2dict', '_locals_', 'debug', 'screen-buffer', 
        'description', 'expected_rstack', 'expected_stack', 'test-result', 
        '[all-pass]', 'xxx', 'x', 'y', 'ss'])
                             ^^^       ^^^^   有在 vm.forth 裡面 
    --> 執行 marker --> words 裡沒有 x, ss 了, 當然 --> 但是 vm.forth 裡還是存在，造成堆積！！ 
        v1.23 還是有這個問題，不知道該怎麼做。。。。
    FP, see below 2020/07/27 08:38:15 value constant to 要重新定義. . . . .

[X] 改寫所有的 code words 把彆扭的 help 用新的 # 功能改自然點。
    done! v1.23 
[X] quit.f 裡的怪東西都不要了 --> inport, outport, harry_port  v1.23
[X] 把 gist 上的東西 include 進來，最主要的是有 support nesting 的 (comment) v1.23
[X] 取消 colon definition 中第一個 ( ... ) 的作用，只用 // 即可留 help
    --> 唉，試了就知道，很醜！  v1.23 真的實現了
    Notepad++ ^h replace regular expression
    Find what: "(\(\s+.*\))\s+(//)"
    Replace with: "// \1"
[x] dos , cd 太重要了，從 misc.f 移進 peforth.f     
[X] 17:53 2019-05-11 接下來考慮出 v1.23 版。
    [X] complete self-tests for new words , many are commented out.
    [X] 評估 misc.f unknown.f quit.f 的內容要怎麼分配 --> 全部放進 misc.f 加個 marker 全自動 load 進去。
        --> 不要的人只要跑一下 marker 就可以全清掉。
        --> 這些東西的 self-test 就要自己做，不能放 peforth.selftest 裡。
    [X] peforth.f source code 裡還有很多中文
    [X] 好像 *debug* 出不來.... 
        --> 喔喔 是給 breakpoint 用的 exit 出的問題。
        --> 趁放進 misc.f 的機會給它改名吧！ quit 
    [X] 測試 jupyter notebook
        [x] established the method to include misc.f from within quit.f
    [X] 測試 ipython (DOS box)
        [X] 進 ipython 之後 import peforth 看起來 self-test 都 ok, 但是從此之後 ipython 就無法輸出了。
            執行 ipython -m peforth 也一樣。
            --> ipython 自己的 display 也被關了，執行 peforth.dictate('display-on') 即可恢復。
            --> 是 selftest 的 display-off 造成的? --> 槓掉 self-test 試試看... 真的好了! 
                連 ipython -m peforth 也好了。 
            --> 執行 c:\Users\hcche\Documents\GitHub\peforth\peforth>ipython test.py self-test 與之後的
                功能都沒問題.
            [X] self-test on > 做出問題 > 然後下達 display-on 之後，治好了！證實 root cause 是 display-off. (最後發現，錯！不是這樣)
                but where? --> 從 quit.f 裡把 misc.f comment out 也好了, 故問題在他裡面。--> 找到了， pyclude 的
                self-test 之前 stop 就好了 --> 查 display-off 怎麼弄的? --> display-on 只是 reset sys.stdout 而已
                無可挑剔。算了,有 workaround 就好了。
            [x] WSL Ubuntu 之下 display-off 之後的斷點 *debug* 也怪怪的，本想在其中下 display-on 再回來繼續，
                結果一 exit 回來就回 Shell 了。試過 time delay 如下也無效。
                <py> 
                    # 拖時間
                    factorial = 1
                    for i in range(2,10000):
                        factorial = factorial * i
                </py>
            [X] 15:24 2019-05-22 靠! 連 Windows DOS 下也出現了這個問題， SRP: working directory 的差別
                有問題 c:\Users\hcche\Documents\GitHub\peforth>python -m peforth
                沒問題 c:\Users\hcche\Documents\GitHub\peforth\peforth>python -m peforth
                發生在 *** (pyclude) 之前 --> 故意先做個 display-off on 看看.... 
                RI: Bingo! Shit! selftest 裡 pyclude hello.py 必須以其所在位置為 working directory
        [x] 15:55 2019-05-22 發現這個 root cause 是耐心跑 v1.23 release check-list 時發現的，所以
            那個 check-list 還是要好好做。
            
    [/] 測試 ubuntu 的 ipython ---> 放棄，error message 如下：
        hcchen@WKS-4AEN0404:/mnt/c/Users/hcche/Documents/GitHub/peforth$ ipython
        Command 'ipython' not found, but can be installed with:
        sudo apt install ipython

        hcchen@WKS-4AEN0404:/mnt/c/Users/hcche/Documents/GitHub/peforth$ sudo apt install ipython
        [sudo] password for hcchen:
        Reading package lists... Done
        Building dependency tree
        Reading state information... Done
        Package ipython is not available, but is referred to by another package.
        This may mean that the package is missing, has been obsoleted, or
        is only available from another source
        E: Package 'ipython' has no installation candidate
    
    [X] Error! tib. unknown! --> 改成 "-->" 了  1.23
    [X] 改寫 pypi.org 上的 readme.rst 本來的例子不太好了, pdb 其實很強。
        改用 Azure notebook 介紹 ipython 的 magic command 比較好。
        [X] 17:33 2019-05-19 改了 Github.com 上的 README.md , local 的 .rst 
    [X] jupyter notebook 用 import peforth 就很好用了, 
        把 readme.md 裡沒有的 peforth kernel 拿掉，移進 Wiki 裡去。
        --> 17:34 2019-05-19 done 
    [X] 把 misc.f hello.py 等都加進 package    
[X] Test ubuntu 發現 cd 有必要進 peforth.f 但 dos 就該留在 misc.f 裡，且要判斷 os 是哪個。
    --> py> os.name . cr ( posix or nt )
[X] v1.23 測試 ubuntu --> 靠！都忘了怎麼測試了，可以不經過 pip 版嗎? 
    09:35 2019-05-22
    --> T550 ubuntu 16.04 連 pip 都沒有, python 版本也搞不清, 更不用說 virtualenv 了。
    --> 感覺用 Linux 很恐慌，乾脆把 T550 上的 Ubuntu 16.04 remove 掉，改用新版的，希望可以避開
        python 版本的問題。(See Ynote:"[筆記] Install Mozilla DeepSpeech Project" > "wsl ubuntu install python3.6.txt") 
    --> 09:39 2019-05-22 T550 Ubuntu removed --> The recent is still 18.04 on 
        Microsoft Store, so be it --> 10:43 2019-05-22 WSL installed 
        --> how's the built-in python? --> See Ynote "好久沒玩 WSL Ubuntu, 為了 release peforth v1.23 測試整個再玩一次"
            [X] 有 python 3.6.5 built-in 沒有 pip <--- 先不管它，只測 python test.py 過了再說。 --> 一番折騰，過了！
            [/] 沒有 pip 可以 python -m peforth 嗎？ 試試 python setup.py install 結果失敗
                hcchen@WKS-4AEN0404:/mnt/c/Users/hcche/Documents/GitHub/peforth$ python setup.py install
                Traceback (most recent call last):
                  File "setup.py", line 4, in <module>
                    from setuptools import setup
                ModuleNotFoundError: No module named 'setuptools' <------------------ 
                hcchen@WKS-4AEN0404:/mnt/c/Users/hcche/Documents/GitHub/peforth$            
                [X] 看了這篇 https://askubuntu.com/questions/861265/python-3-importerror-no-module-named-setuptools-ubuntu-14-04-lts 
                    決定放棄，有測過 test.py 就好了。
    [/] 即使上了 pypi.org 也還需要 pip (但 18.04 default 沒有), 不管了，有測過 test.py 就好了。
    [/] 上了 pypi.org 之後，再用 Azure Notebooks 測試。
    
[X] Tests before a Release v1.23
    [X] setup.py 裡的 copy right 年份要改成 2019 
    *** 打包上 pypi.org 的方法 setup.bat 可以大簡化了。
        [V1.22之後的新版] 打包步驟  2018/12/16 11:02 
        See my Ynote: "Pack peforth to peforth.whl"
        1.  檢查 ~\GitHub\peforth\setup.py 看有沒有漏掉新檔案，有沒有要去掉的檔案。
        2.  跑 c:\Users\hcche\Documents\GitHub\peforth>python setup.py sdist bdist_wheel
            得到 peforth.whl in c:\Users\hcche\Documents\GitHub\peforth\dist
        3.  執行 c:\Users\hcche\Documents\GitHub\peforth>twine upload dist/* 
            需要帳號密碼，看這裡 Ynote: "python pypi 研究 -- upload to PyPI ok now.note"
        4.  pip uninstall peforth 然後再 pip install peforth 試驗看看。
        5.  完成！
    [X] See (15:55 2019-05-22) 這個 check-list 要耐心好好做完！
    [X] 所有 run 法帶 selftest：
        [X] 改 GitHub\peforth\quit.f
            ' <selftest> :: enabled=True
        [X] Run python setup.py install 更新本地 site-package 版本以供測試
        [X] 1.  python -i -m peforth [/] with-selftest .s words exit bye
        [X] 2.  ipython -i -m peforth .' Hello World!!' cr bye
        [X] 3.  ipython import peforth .s words
                [x] selftest peforth.ok() .s words <--- w/parent
                [x] 1234 bye check echo %errorlevel% <-- 從 ipython 下直接出來也無誤。
        [X] 4.  jupyter notebook 
                kernel > restart and clear outputs 
                x = 123
                %f x .     
                x . \ ==> 123 (<class 'int'>)
        [/] 5.  jupyter notebook --> peforth kernel --> .s words 
        [/] 考慮 README.rst 改良
            [X] 若有改過 README.rst 則 wheel 就要重做
                --> quit.f selftest=False --> 重來
    [X] 所有 run 法不帶 selftest 跑一遍，準備要 release 的版本：
        [X] 改 GitHub\peforth\quit.f
            ' <selftest> :: enabled=False
        [X] 做出取消 selftest 的 wheel
            See my Ynote: "Pack peforth to peforth.whl"
            [x] 1.  檢查 ~\GitHub\peforth\setup.py 看有沒有漏掉新檔案，有沒有要去掉的檔案。
                    test.py hello.py misc.f 
            [X] 2.  跑 c:\Users\hcche\Documents\GitHub\peforth>python setup.py sdist bdist_wheel
                    得到 peforth.whl in c:\Users\hcche\Documents\GitHub\peforth\dist
        [X] pip uninstall peforth
        [X] 切 CD 到 c:\Users\hcche\Documents\GitHub\peforth\dist>
            pip install peforth-1.23-py3-none-any.whl  <== 注意！用剛做好的 wheel 否則會上網抓。
        [X] 1. (i)python -i -m peforth [/] no-selftest .s words exit
        [X] 2. (i)python -i -m peforth version 12345 bye --> echo %errorlevel%
        [X] 3. (i)python import peforth
               [X] no selftest, peforth.ok() .s words <--- no parent
               [X] 1234 bye check echo %errorlevel%
        [X] 4. jupyter notebook --> *debug* ok> .s cd help exit
               %f %%f magic command
        [/] 5. repeat 以上 in ubuntu <------- Ubuntu 18.04 沒有 pip built-in 不想搞了
                [/] pip uninstall peforth
                [/] pip install (use /mnt/...the wheel) to WSL ubuntu
                [/] ipython -m peforth
                [/] ipython , import peforth , magic commands 
    [X] 直接用測過的 wheel update Pypi
        執行 c:\Users\hcche\Documents\GitHub\peforth>twine upload dist/* 
        需要帳號密碼，看這裡 Ynote: "python pypi 研究 -- upload to PyPI ok now.note"
        ID, password search my Ynote with pypi _account_
    [X] 查看 pypi.org 網頁，若不行，晚點 (過幾分鐘就好) 再看。
        [/] WSL Ubuntu 下試 pip uninstall peforth -> pip install peforth
            [/] WSL Ubuntu with and w/o w/o virtualenv --> python -m peforth
        [X] Windows DOS 下試 
    [X] Test Azure Online Jupyter Notebooks
        https://peforthplayground-hcchen1471.notebooks.azure.com/j/notebooks/peforth-playground.ipynb 
        !pip install peforth
        import peforth
        %f version drop
        x = 12345
        %f x --> \ 查看 unknown 的效果
    [X] Make a master release up to GitHub --> 用 GitHub Windows 很簡單。
        1. 先 commit 上 develop branch, upload 上網上 Github.
        2. 切到 master 
        3. 用 GitHub for Windows desktop 的 Branch > Merge into current branch 選 develop 把它 merge 過來。
           解決 conflicts 之後完成 merge. 
        4. 再 repeat 2-3 但切到 develop 把 master merge 過去。
           Master 上的應該是些 README.md 的修改。 
    [X] version 改成 1.24  (必須跳過 1.20 直接到 1.21 否則會變成 1.2）
[X] 11:28 2019-05-26 make a master merge for the article of Febenacci and Decorator
    [X] rename the article to 'peforth helps to understand python Decorator'
    [/] 11:35 2019-05-26 write an article to introduce 'unknown' 
        --> forget this, covered already. 
    [/] 11:35 2019-05-26 find the video I introduce 'unknown' and the other thing
        --> forget this, covered already. 

[X] 09:11 2019-11-21 本來跑 GitHub\peforth\setup.bat 讓改好的新版生效，在 anaconda 之下還行嗎？
    1. 跑 anaconda's prompt make sure python runable
    2. peforth runable too, check path 
    3. cd to GitHub\peforth run setup
    4. check peforth 
    OneNote 筆記：
    "Develop peforth in an Anaconda virtual environment"
    https://onedrive.live.com/view.aspx?resid=A796EA18AC8C1DA9%2112289&id=documents&wd=target%28Anaconda.one%7CB4E0DFAB-84F7-43D2-A5AB-515B43314252%2FDevelop%20peforth%20in%20an%20Anaconda%20virtual%20environment%7C99DE5C5F-B36D-4949-9471-BC7A857E3C2B%2F%29
    
[X] 16:54 2019-07-22 從這裡 https://jupyter-contrib-nbextensions.readthedocs.io/en/latest/install.html 讀到
    有從 github repo 上直接 pip install 的方法，e.g.:
        pip install https://github.com/ipython-contrib/jupyter_contrib_nbextensions/tarball/master
    試試看 peforth 可不可以這樣 install ? 可以的話就不用上 pypi 了
        pip install https://github.com/hcchengithub/peforth/master 
        or
        pip install https://github.com/hcchengithub/peforth
    ==> 結果兩個都失敗
    [ ] GitHub 有開始做 package hosting 了：
        https://help.github.com/en/github/managing-packages-with-github-packages/about-github-packages#supported-clients-and-formats
[X] 2019/11/24 06:10:22 projectk.py 裡 import 好多它本身不用的 modules (它自己只 
    用到 re regular expression 一個) 我的註解說：
    import re # import whatever we want, don't rely on parent module e.g. peforth __init__.py
    也是有理，因為 projectk.py kernel 有自己的 space. 然而 modules 應該是 global
    的, 不是嗎？從 forth code 裡 import 不行嗎？ --> 試了就知道，把 projectk.py 裡
    多餘的 imports comment 掉 --> 出問題的時候很晚，只要是 native modules 有機會解決.....
        來自 help import 的 hints
        \ import os __main__ :: peforth.projectk.os=pop(1) \ peforth global , does not work when run by 'python test.py'
        import os      py> vm ::      os=pop(1) \ this works! when run by 'python test.py'
        import inspect py> vm :: inspect=pop(1)
        import dis     py> vm ::     dis=pop(1)
        import json    py> vm ::    json=pop(1)
    但是 sys 太根本了必須要在 projectk.py 裡 import 好。 
[X] setup.py 裡的 copy right 年份要改成 2019 
[/] 2019/11/24 05:20 用 Anaconda 之後似乎 kernel.json 也有問題？
    裡面描述的 peforthkernel.py path 是寫死的，在我 OA、Anaconda 上就不對了。
    好像只要無意把 peforth 加進 JupyterNotebook 的 kernel 就沒問題。
[X] 05:29 2019-11-21 projectk.py 裡面的 local, Comment, debug 這三個 global token 好像是多
    餘的, 有空檢討看看. 
    [X] local 可能是 ok(prompt='OK ', loc={}, glo={}, cmd="") 或 redefined unknown 用的 <--- 不是
    13:47 2019/11/25 delete all suspected things from projectk.py --> dos ok, jupyternotebook ok.
    * 注意！setup.bat 不會更新 site-packages 的 peforth\ folder 要手動從 peforth-1.24-py3.7.egg  <== 2020.7.28 解了！ see OneNote2020 > "Develop peforth in an Anaconda virtual environment" 
      copy peforth\ 來蓋過 site-packages 裡的 peforth\ folder. 
      refer to https://onedrive.live.com/view.aspx?resid=A796EA18AC8C1DA9%2112289&id=documents&wd=target%28Anaconda.one%7CB4E0DFAB-84F7-43D2-A5AB-515B43314252%2FDevelop%20peforth%20in%20an%20Anaconda%20virtual%20environment%7C99DE5C5F-B36D-4949-9471-BC7A857E3C2B%2F%29
[X] 14:41 2019/11/25 quit.f 裡這種東西應該要改良，太笨了：
        import os py> vm :: os=pop(1) \ 太笨
        import os \ 應該改良成這樣
[X] 15:21 2019/11/25 整理 peforth.f quit.f peforth.selftest 的關係，更有系統了。
    __init__.py 只 load 進基本的 peforth.f quit.f 其他的都由 quit.f 負責，使 quit.f 
    成為 eforth 系統的 main program, 統籌者。
[X] 16:07 2019/11/25 一舉搞懂 pop(1) 
    code test # ( a b c -- ) print given things
        print(pop(), pop(), pop()) end-code
    1 2 3 test
    3 2 1 <-- 結果，顯示三個 pop() 是從左到右抓取 TOS 的。
[X] Tests before a Release v1.24
    [X] setup.py 裡的 copy right 年份要改成 2019 
    *** 打包上 pypi.org 的方法 setup.bat 可以大簡化了。
        [V1.22之後的新版] 打包步驟  2018/12/16 11:02 
        See my Ynote: "Pack peforth to peforth.whl"
        1.  檢查 ~\GitHub\peforth\setup.py 看有沒有漏掉新檔案，有沒有要去掉的檔案。
        2.  (記得先把 dist , build , peforth.egg-info 等 folder 先殺掉) 跑 
            c:\Users\hcche\Documents\GitHub\peforth>python setup.py sdist bdist_wheel
            得到 peforth.whl in c:\Users\hcche\Documents\GitHub\peforth\dist
        3.  執行 c:\Users\hcche\Documents\GitHub\peforth>twine upload dist/* 
            需要帳號密碼，看這裡 Ynote: "python pypi 研究 -- upload to PyPI ok now.note"
        4.  pip uninstall peforth 然後再 pip install peforth 試驗看看。
        5.  完成！
    [X] See (15:55 2019-05-22) 這個 check-list 要耐心好好做完！
    [X] 所有 run 法帶 selftest：
        [X] 改 GitHub\peforth\quit.f
            ' <selftest> :: enabled=True
        [X] 先通過最基本的 selftest： GitHub\peforth\peforth>python test.py
        [X] Run python setup.py install 更新本地 site-package 版本以供測試
            [X] 可能要 (Anaconda virtualenv 之下) 從 site-packages\peforth-1.24-py3.7.egg 
                裡 copy peforth\ 去蓋掉 site-packages\peforth\ 這樣 upgrade 才有生效。
        [X] 1.  python -i -m peforth [X] with-selftest .s words exit bye
        [X] 2.  ipython -i -m peforth .' Hello World!!' cr bye
        [X] 3.  ipython import peforth .s words
                [X] selftest peforth.ok() .s words <--- w/parent
                [X] 1234 bye check echo %errorlevel% <-- 從 ipython 下直接出來也無誤。
        [X] 4.  jupyter notebook 
                kernel > restart and clear outputs 
                x = 123
                %f x .     
                x . \ ==> 123 (<class 'int'>)
        [X] 5.  jupyter notebook --> peforth kernel --> .s words 
        [/] 考慮 README.rst 改良
            [/] 若有改過 README.rst 則 wheel 就要重做
                --> quit.f selftest=False --> 重來
    [X] 所有 run 法不帶 selftest 跑一遍，準備要 release 的版本：
        [X] 改 GitHub\peforth\quit.f
            ' <selftest> :: enabled=False
        [X] 同上 python test.py 先試試看
        [X] Run python setup.py install 更新本地 site-package 版本以供測試
            [X] 可能要 (Anaconda virtualenv 之下) 從 site-packages\peforth-1.24-py3.7.egg 
                裡 copy peforth\ 去蓋掉 site-packages\peforth\ 這樣 upgrade 才有生效。
        [X] 同上 repeat 1) python -m peforth  2) ipython -m peforth
        [X] 做出取消 selftest 的 wheel
            See my Ynote: "Pack peforth to peforth.whl"
            [X] 1.  檢查 ~\GitHub\peforth\setup.py 看有沒有漏掉新檔案，有沒有要去掉的檔案。
                    test.py hello.py misc.f 
            [X] 2.  跑 c:\Users\hcche\Documents\GitHub\peforth>python setup.py sdist bdist_wheel
                    得到 peforth.whl in c:\Users\hcche\Documents\GitHub\peforth\dist
        [X] pip uninstall peforth
            site-packages 下兩個 peforth folder 刪掉了。
            setup.bat 建立的 EGG 檔 peforth-1.24-py3.7.egg 也刪掉，否則 pip install 會
            被 skip 過去。
        [X] 切 CD 到 c:\Users\hcche\Documents\GitHub\peforth\dist>
            pip install peforth-1.23-py3-none-any.whl  <== 注意！用剛做好的 wheel 否則會上網抓。
        [X] 1. (i)python -i -m peforth [X] no-selftest .s words exit
        [X] 2. (i)python -i -m peforth version 12345 bye --> echo %errorlevel%
        [X] 3. (i)python import peforth
               [X] no selftest, peforth.ok() .s words <--- no parent
               [X] 1234 bye check echo %errorlevel%
        [X] 4. jupyter notebook --> *debug* ok> .s cd help exit
               %f %%f magic command
        [/] 5. repeat 以上 in ubuntu <------- Ubuntu 18.04 沒有 pip built-in 不想搞了
                [/] pip uninstall peforth     已知 Colab & Azure 都是 Ubuntu 故不必自己多測了 
                [/] pip install (use /mnt/...the wheel) to WSL ubuntu
                [/] ipython -m peforth
                [/] ipython , import peforth , magic commands 
    [X] 直接用測過的 wheel update Pypi
        執行 c:\Users\hcche\Documents\GitHub\peforth>twine upload dist/* 
        需要帳號密碼，看這裡 Ynote: "python pypi 研究 -- upload to PyPI ok now.note"
        ID, password search my Ynote with pypi _account_
        Note: Anaconda base 沒有 twine, 在 Anaconda Navigator 裡找到 twine 把它勾起來 Apply.
    [X] 查看 pypi.org 網頁，若不行，晚點 (過幾分鐘就好) 再看。
        [X] Windows DOS 下試 
        [/] WSL Ubuntu 下試 pip uninstall peforth -> pip install peforth
            [/] WSL Ubuntu with and w/o w/o virtualenv --> python -m peforth
    [X] Test Online Jupyter Notebooks Google Colab, Microsoft Azure, and Notebooks.ai 
        !pip install peforth
        import peforth
        %f version drop
        x = 12345
        %f x --> \ 查看 unknown 的效果
        \ Colab & Azure 都用 Ubuntu 查版本, Notebooks.ai 用 Debian 都可用這行指令
        !cat /etc/os-release 
        %f py> path --> \ 查看 path 發現 Azure 就是用 Anaconda 所以它有 support Ubuntu！ 
        %pwd \ 查看 working directory 
        [x] Colab https://colab.research.google.com/drive/1nZpybQryEiwYzpMvG1tHg4qbNnd_rMey#scrollTo=yAuF9DZcrFaT
        [X] Azure https://peforthplayground-hcchen1471.notebooks.azure.com/j/notebooks/peforth-playground.ipynb 
        [X] notebooks.ai 也測測看
    [X] Make a master release up to GitHub --> 用 GitHub Windows 很簡單。
        1. 先 commit 上 develop branch, upload 上網上 Github.
        2. 切到 master 
        3. 用 GitHub for Windows desktop 的 Branch > Merge into current branch 選 develop 把它 merge 過來。
           解決 conflicts 之後完成 merge. 
        4. 再 repeat 2-3 但切到 develop 把 master merge 過去。
           Master 上的應該是些 README.md 的修改。 
    [X] version 改成 1.25  (必須跳過 1.20 直接到 1.21 否則會變成 1.2）
    [X] 要不要把 projectk.py sync 回 project-k
        (很早以前) projectk.py 改了一點，忘了如何 sync 回 project-k 的？
        05:30 2019-11-21 peforth source code 裡的 projectk.py 本身不是從 github 直接下來的, 而是
        硬放上去的，因此不會與 project-k github 自動同步 <--- 想想看怎麼辦。

[ ] 15:56 2019/11/25 經常要 (see) 東西都會出這個問題：
    Callable in phaseB <function compyle_anonymous at 0x00000232B1164A68>: Circular reference detected
    問問看有沒有 workaround ？

[ ] 13:42 2019/11/27 下回 release 要在 README.rst ~.md 裡明列有測過的系統：
    1. Windows Anaconda DOSBox pyhon 3.7, DOSBox ipython, JupyterNotebook, JupyterLab
    2. Colab (Ubuntu,Anaconda), Azure notebooks (Ubuntu), Notebooks.ai (Debian)

[X] 2020/07/27 08:33 可以把 [obj>keys] 'keys' 定義成 dir | dict>keys 這樣就不會與 dir 重複了。又可以與 jeforth 相容。
[X] 2020/07/27 08:38:15 value constant to 要重新定義，不要再用 vm.forth 存放了，改用 variable 自己 word. 
    See OneNote2020 > "Jeforth variable 變革" --> 成功了。
[ ] 考慮 projectk.py 本身也上 pypi , 可以 pip install projectk 更有意義！
[X] 07:49 2020/10/04 參考 KsanaVM 發現我原先對 prompt 的時機有誤解，改好了。
[ ] 15:49 2020/10/24 v1.25 好了以後 projectk.py 要 sync 回 projectk 
[X] 15:30 2020/10/24 準備 release v1.25 to pypi so as to allow gom to have it easily
    [X] 15:54 2020/10/24 先試試看 gom ok? --> Pass, 連 selftest 也都 pass. 
    [X] setup.py 裡的 copy right 年份要改成 2019 
    *** 打包上 pypi.org 的方法 setup.bat 可以大簡化了。
        [V1.22之後的新版] 打包步驟  2018/12/16 11:02 
        See my Ynote: "Pack peforth to peforth.whl"
        1.  檢查 ~\GitHub\peforth\setup.py 看有沒有漏掉新檔案，有沒有要去掉的檔案。
        2.  (記得先把 dist , build , peforth.egg-info 等 folder 先殺掉) 跑 
            c:\Users\hcche\Documents\GitHub\peforth>python setup.py sdist bdist_wheel
            得到 peforth.whl in c:\Users\hcche\Documents\GitHub\peforth\dist
        3.  若無 twine 則 pip install twine 很快很順
            執行 c:\Users\hcche\Documents\GitHub\peforth>twine upload dist/* 
            需要帳號密碼，看這裡 Ynote or Evernote: "python pypi 研究 -- upload to PyPI ok now.note"
        4.  pip uninstall peforth 然後再 pip install peforth 試驗看看。
        5.  完成！
    [X] See (15:55 2019-05-22) 這個 check-list 要耐心好好做完！
    [ ] 所有 run 法帶 selftest：
        [X] 改 GitHub\peforth\quit.f
            ' <selftest> :: enabled=True
        [X] 先通過最基本的 selftest： GitHub\peforth\peforth>python test.py
        [X] Run python setup.py install 更新本地 site-package 版本以供測試
            [X] 要 (Anaconda virtualenv 之下) 從 site-packages\peforth-1.24-py3.7.egg 
                裡 copy peforth\ 去蓋掉 site-packages\peforth\ 這樣 upgrade 才有生效。
                16:27 2020/10/24 不必這樣，因為 python setup.py install 灌好的 peforth v1.25 是
                    c:\Users\8304018\AppData\Local\Continuum\anaconda3\lib\site-packages\peforth-1.25-py3.7.egg 
                而 pip install peforth 灌好的是另一個 peforth v1.25 
                    c:\Users\8304018\AppData\Local\Continuum\anaconda3\lib\site-packages\peforth\
                兩個可以並存！而且後者優先。只要把後者 directory name 改成 peforth.disabled
                就可以讓前者生效，前者是 local install 測試時有其方便性。
        [X] 1.  python -i -m peforth [X] with-selftest .s words exit bye
        [X] 2.  ipython -i -m peforth .' Hello World!!' cr bye
        [/] 3.  ipython import peforth .s words
                [/] selftest peforth.ok() .s words <--- w/parent
                [/] 1234 bye check echo %errorlevel% <-- 從 ipython 下直接出來也無誤。
        [X] 4.  jupyter notebook 
                kernel > restart and clear outputs 
                x = 123
                %f x .     
                x . \ ==> 123 (<class 'int'>)
        [X] 5.  jupyter notebook --> peforth kernel --> .s words 
        [X] 6.  Gom 手動移除現有的 peforth directories from:
                    c:\Users\8304018\AppData\Roaming\gom\2020\python\.. 
                然後從 SCRIPTING > Script Choice >  pip install peforth > Tools > Install Python Package 灌 peforth 很快很順
                    import peforth, peforth_gom_port
                執行 peforth.ok() 無誤。
                新增 peforth_gom_port.py 放到 peforth repo 的 playground directory 裡。
        [/] 考慮 README.rst 改良
            [/] 若有改過 README.rst 則 wheel 就要重做
                --> quit.f selftest=False --> 重來
    [ ] 所有 run 法不帶 selftest 跑一遍，準備要 release 的版本：
        [ ] 改 GitHub\peforth\quit.f
            ' <selftest> :: enabled=False
        [ ] 同上 python test.py 先試試看
        [ ] Run python setup.py install 更新本地 site-package 版本以供測試
            [X] 可能要 (Anaconda virtualenv 之下) 從 site-packages\peforth-1.24-py3.7.egg 
                裡 copy peforth\ 去蓋掉 site-packages\peforth\ 這樣 upgrade 才有生效。
        [ ] 同上 repeat 1) python -m peforth  2) ipython -m peforth
        [ ] 做出取消 selftest 的 wheel
            See my Ynote: "Pack peforth to peforth.whl"
            [ ] 1.  檢查 ~\GitHub\peforth\setup.py 看有沒有漏掉新檔案，有沒有要去掉的檔案。
                    test.py hello.py misc.f 
            [ ] 2.  跑 c:\Users\hcche\Documents\GitHub\peforth>python setup.py sdist bdist_wheel
                    得到 peforth.whl in c:\Users\hcche\Documents\GitHub\peforth\dist
        [ ] pip uninstall peforth
            site-packages 下兩個 peforth folder 刪掉了。
            setup.bat 建立的 EGG 檔 peforth-1.24-py3.7.egg 也刪掉，否則 pip install 會
            被 skip 過去。
        [ ] 切 CD 到 c:\Users\hcche\Documents\GitHub\peforth\dist>
            pip install peforth-1.23-py3-none-any.whl  <== 注意！用剛做好的 wheel 否則會上網抓。
        [ ] 1. (i)python -i -m peforth [ ] no-selftest .s words exit
        [ ] 2. (i)python -i -m peforth version 12345 bye --> echo %errorlevel%
        [ ] 3. (i)python import peforth
               [ ] no selftest, peforth.ok() .s words <--- no parent
               [ ] 1234 bye check echo %errorlevel%
        [ ] 4. jupyter notebook --> *debug* ok> .s cd help exit
               %f %%f magic command
        [ ] 5. repeat 以上 in ubuntu <------- Ubuntu 18.04 沒有 pip built-in 不想搞了
                [ ] pip uninstall peforth     已知 Colab & Azure 都是 Ubuntu 故不必自己多測了 
                [ ] pip install (use /mnt/...the wheel) to WSL ubuntu
                [ ] ipython -m peforth
                [ ] ipython , import peforth , magic commands 
    [ ] 直接用測過的 wheel update Pypi
        執行 c:\Users\hcche\Documents\GitHub\peforth>twine upload dist/* 
        需要帳號密碼，看這裡 Ynote: "python pypi 研究 -- upload to PyPI ok now.note"
        ID, password search my Ynote with pypi _account_
        Note: Anaconda base 沒有 twine, 在 Anaconda Navigator 裡找到 twine 把它勾起來 Apply.
    [ ] 查看 pypi.org 網頁，若不行，晚點 (過幾分鐘就好) 再看。
        [ ] Windows DOS 下試 
        [ ] WSL Ubuntu 下試 pip uninstall peforth -> pip install peforth
            [ ] WSL Ubuntu with and w/o w/o virtualenv --> python -m peforth
    [ ] Test Online Jupyter Notebooks Google Colab, Microsoft Azure, and Notebooks.ai 
        !pip install peforth
        import peforth
        %f version drop
        x = 12345
        %f x --> \ 查看 unknown 的效果
        \ Colab & Azure 都用 Ubuntu 查版本, Notebooks.ai 用 Debian 都可用這行指令
        !cat /etc/os-release 
        %f py> path --> \ 查看 path 發現 Azure 就是用 Anaconda 所以它有 support Ubuntu！ 
        %pwd \ 查看 working directory 
        [ ] Colab https://colab.research.google.com/drive/1nZpybQryEiwYzpMvG1tHg4qbNnd_rMey#scrollTo=yAuF9DZcrFaT
        [ ] Azure https://peforthplayground-hcchen1471.notebooks.azure.com/j/notebooks/peforth-playground.ipynb 
        [ ] notebooks.ai 也測測看
    [ ] Make a master release up to GitHub --> 用 GitHub Windows 很簡單。
        1. 先 commit 上 develop branch, upload 上網上 Github.
        2. 切到 master 
        3. 用 GitHub for Windows desktop 的 Branch > Merge into current branch 選 develop 把它 merge 過來。
           解決 conflicts 之後完成 merge. 
        4. 再 repeat 2-3 但切到 develop 把 master merge 過去。
           Master 上的應該是些 README.md 的修改。 
    [X] version 改成 1.25  (必須跳過 1.20 直接到 1.21 否則會變成 1.2）
    [ ] 要不要把 projectk.py sync 回 project-k
        (很早以前) projectk.py 改了一點，忘了如何 sync 回 project-k 的？
        05:30 2019-11-21 peforth source code 裡的 projectk.py 本身不是從 github 直接下來的, 而是
        硬放上去的，因此不會與 project-k github 自動同步 <--- 想想看怎麼辦。
[X] 17:01 2020/10/24 v1.25 已經上了 pypi 也測過 Gom 成功，以上測試慢慢做，先上 github 再說。
[X] 14:22 2020/10/29 vm.prompt 是要給 gom port dialog 知道目前 prompt 否則只在 ok() 肚子裡。
[X] 13:52 2020/11/23 把 pypi 的 v1.25 直接換成 local 的 v1.26 
    --> 直接 copy __init__.py version.txt 蓋過去 c:\Users\8304018\AppData\Roaming\gom\2020\python\peforth  
    --> 11> <py> ok() </py> --> prompt 變成 ok , exit --> prompt 變回 11> 成功！ 這就是 v1.26 無誤。
[X] 10:26 2020/11/26 改良 breakpoint 不需要改 peforth, 從 application 端外掛就可以了。
    Usage of breakpoint:
        peforth.bp(22,locals())                # drop breakpoint 22 with locals()
        for i in [11,22,33]: peforth.bps[i]=0    # disable breakpoints 11,22,33 
        for i in [11,22,33]: peforth.bps[i]=i    # enable  breakpoints 11,22,33 
        peforth.bps=[i for i in range(1000)]     # reload and enable all breakpoints    
    'exit' or ESC leaves the breakpoint and continue running.
    'bye' to totally stop the script session.

    # breakpoint
    #	peforth.bp()   # drop a breakpoint using default prompt bp> 
    #	peforth.bp(11) # drop a breakpoint using prompt bp11> w/p passing locals()
    #	peforth.bp(22,locals())  # drop a breakpoint using prompt bp22> with locals()
    #	peforth.bps=[] # disable all breakpoints
    #	peforth.dictate("peforth :: bps=[]") # disable all breakpoints
    #	peforth.dictate("peforth :: bps=[123,345,567]") # enable only listed breakpoints 
    #	peforth.dictate("peforth :: bps[123]=0") # disable the breakpoint 123
    #	peforth.dictate("peforth :: pop(111)")   # disable the breakpoint 111
    #	for i in [11,22,33]: peforth.bps[i]=0    # disable breakpoints 11,22,33 
    #	peforth.bps=[i for i in range(1000)]     # reload and enable all breakpoints    

    def bp(id=None,locals=None):
        if id==None: 
            id = 0
            prompt='bp> '
        else:
            prompt="bp{}>".format(id)
        if id in peforth.bps: peforth.push(locals).ok(prompt, cmd="to _locals_")
    peforth.bp = bp
    peforth.bps = [i for i in range(1000)]
[X] 17:33 2020/12/07 配合 peforth.bp(22,locals()) 新增 bl be bd be* bd* 等指令
[ ] 17:34 2020/12/07 release v1.26 to pypi 
    [X] 17:37 2020/12/07 先試試看 gom ok? --> Pass, 連 selftest 也都 pass. 
    [X] setup.py 裡的 copy right 年份要改成 2019 
    *** 打包上 pypi.org 的方法 setup.bat 可以大簡化了。
        [V1.22之後的新版] 打包步驟  2018/12/16 11:02 
        See my Ynote: "Pack peforth to peforth.whl"
        1.  檢查 ~\GitHub\peforth\setup.py 看有沒有漏掉新檔案，有沒有要去掉的檔案。
        2.  (記得先把 dist , build , peforth.egg-info 等 folder 先殺掉) 跑 
            c:\Users\hcche\Documents\GitHub\peforth>python setup.py sdist bdist_wheel
            得到 peforth.whl in c:\Users\hcche\Documents\GitHub\peforth\dist
        3.  若無 twine 則 pip install twine 很快很順
            執行 c:\Users\hcche\Documents\GitHub\peforth>twine upload dist/* 
            需要帳號密碼，看這裡 Ynote or Evernote: "python pypi 研究 -- upload to PyPI ok now.note"
        4.  pip uninstall peforth 然後再 pip install peforth 試驗看看。
        5.  完成！
    [ ] See (15:55 2019-05-22) 這個 check-list 要耐心好好做完！
    [ ] 所有 run 法帶 selftest：
        [ ] 改 GitHub\peforth\quit.f
            ' <selftest> :: enabled=True
        [ ] 先通過最基本的 selftest： GitHub\peforth\peforth>python test.py
        [ ] Run python setup.py install 更新本地 site-package 版本以供測試
            [ ] 要 (Anaconda virtualenv 之下) 從 site-packages\peforth-1.24-py3.7.egg 
                裡 copy peforth\ 去蓋掉 site-packages\peforth\ 這樣 upgrade 才有生效。
                16:27 2020/10/24 不必這樣，因為 python setup.py install 灌好的 peforth v1.25 是
                    c:\Users\8304018\AppData\Local\Continuum\anaconda3\lib\site-packages\peforth-1.25-py3.7.egg 
                而 pip install peforth 灌好的是另一個 peforth v1.25 
                    c:\Users\8304018\AppData\Local\Continuum\anaconda3\lib\site-packages\peforth\
                兩個可以並存！而且後者優先。只要把後者 directory name 改成 peforth.disabled
                就可以讓前者生效，前者是 local install 測試時有其方便性。
        [ ] 1.  python -i -m peforth [X] with-selftest .s words exit bye
        [ ] 2.  ipython -i -m peforth .' Hello World!!' cr bye
        [ ] 3.  ipython import peforth .s words
                [/] selftest peforth.ok() .s words <--- w/parent
                [/] 1234 bye check echo %errorlevel% <-- 從 ipython 下直接出來也無誤。
        [ ] 4.  jupyter notebook 
                kernel > restart and clear outputs 
                x = 123
                %f x .     
                x . \ ==> 123 (<class 'int'>)
        [ ] 5.  jupyter notebook --> peforth kernel --> .s words 
        [ ] 6.  Gom 手動移除現有的 peforth directories from:
                    c:\Users\8304018\AppData\Roaming\gom\2020\python\.. 
                然後從 SCRIPTING > Script Choice >  pip install peforth > Tools > Install Python Package 灌 peforth 很快很順
                    import peforth, peforth_gom_port
                執行 peforth.ok() 無誤。
                新增 peforth_gom_port.py 放到 peforth repo 的 playground directory 裡。
        [ ] 考慮 README.rst 改良
            [ ] 若有改過 README.rst 則 wheel 就要重做
                --> quit.f selftest=False --> 重來
    [ ] 所有 run 法不帶 selftest 跑一遍，準備要 release 的版本：
        [ ] 改 GitHub\peforth\quit.f
            ' <selftest> :: enabled=False
        [ ] 同上 python test.py 先試試看
        [ ] Run python setup.py install 更新本地 site-package 版本以供測試
            [X] 可能要 (Anaconda virtualenv 之下) 從 site-packages\peforth-1.24-py3.7.egg 
                裡 copy peforth\ 去蓋掉 site-packages\peforth\ 這樣 upgrade 才有生效。
        [ ] 同上 repeat 1) python -m peforth  2) ipython -m peforth
        [ ] 做出取消 selftest 的 wheel
            See my Ynote: "Pack peforth to peforth.whl"
            [ ] 1.  檢查 ~\GitHub\peforth\setup.py 看有沒有漏掉新檔案，有沒有要去掉的檔案。
                    test.py hello.py misc.f 
            [ ] 2.  跑 c:\Users\hcche\Documents\GitHub\peforth>python setup.py sdist bdist_wheel
                    得到 peforth.whl in c:\Users\hcche\Documents\GitHub\peforth\dist
        [ ] pip uninstall peforth
            site-packages 下兩個 peforth folder 刪掉了。
            setup.bat 建立的 EGG 檔 peforth-1.24-py3.7.egg 也刪掉，否則 pip install 會
            被 skip 過去。
        [ ] 切 CD 到 c:\Users\hcche\Documents\GitHub\peforth\dist>
            pip install peforth-1.23-py3-none-any.whl  <== 注意！用剛做好的 wheel 否則會上網抓。
        [ ] 1. (i)python -i -m peforth [ ] no-selftest .s words exit
        [ ] 2. (i)python -i -m peforth version 12345 bye --> echo %errorlevel%
        [ ] 3. (i)python import peforth
               [ ] no selftest, peforth.ok() .s words <--- no parent
               [ ] 1234 bye check echo %errorlevel%
        [ ] 4. jupyter notebook --> *debug* ok> .s cd help exit
               %f %%f magic command
        [ ] 5. repeat 以上 in ubuntu <------- Ubuntu 18.04 沒有 pip built-in 不想搞了
                [ ] pip uninstall peforth     已知 Colab & Azure 都是 Ubuntu 故不必自己多測了 
                [ ] pip install (use /mnt/...the wheel) to WSL ubuntu
                [ ] ipython -m peforth
                [ ] ipython , import peforth , magic commands 
    [ ] 直接用測過的 wheel update Pypi
        執行 c:\Users\hcche\Documents\GitHub\peforth>twine upload dist/* 
        需要帳號密碼，看這裡 Ynote: "python pypi 研究 -- upload to PyPI ok now.note"
        ID, password search my Ynote with pypi _account_
        Note: Anaconda base 沒有 twine, 在 Anaconda Navigator 裡找到 twine 把它勾起來 Apply.
    [ ] 查看 pypi.org 網頁，若不行，晚點 (過幾分鐘就好) 再看。
        [ ] Windows DOS 下試 
        [ ] WSL Ubuntu 下試 pip uninstall peforth -> pip install peforth
            [ ] WSL Ubuntu with and w/o w/o virtualenv --> python -m peforth
    [ ] Test Online Jupyter Notebooks Google Colab, Microsoft Azure, and Notebooks.ai 
        !pip install peforth
        import peforth
        %f version drop
        x = 12345
        %f x --> \ 查看 unknown 的效果
        \ Colab & Azure 都用 Ubuntu 查版本, Notebooks.ai 用 Debian 都可用這行指令
        !cat /etc/os-release 
        %f py> path --> \ 查看 path 發現 Azure 就是用 Anaconda 所以它有 support Ubuntu！ 
        %pwd \ 查看 working directory 
        [ ] Colab https://colab.research.google.com/drive/1nZpybQryEiwYzpMvG1tHg4qbNnd_rMey#scrollTo=yAuF9DZcrFaT
        [ ] Azure https://peforthplayground-hcchen1471.notebooks.azure.com/j/notebooks/peforth-playground.ipynb 
        [ ] notebooks.ai 也測測看
    [ ] Make a master release up to GitHub --> 用 GitHub Windows 很簡單。
        1. 先 commit 上 develop branch, upload 上網上 Github.
        2. 切到 master 
        3. 用 GitHub for Windows desktop 的 Branch > Merge into current branch 選 develop 把它 merge 過來。
           解決 conflicts 之後完成 merge. 
        4. 再 repeat 2-3 但切到 develop 把 master merge 過去。
           Master 上的應該是些 README.md 的修改。 
    [ ] 要不要把 projectk.py sync 回 project-k
        (很早以前) projectk.py 改了一點，忘了如何 sync 回 project-k 的？
        05:30 2019-11-21 peforth source code 裡的 projectk.py 本身不是從 github 直接下來的, 而是
        硬放上去的，因此不會與 project-k github 自動同步 <--- 想想看怎麼辦。
    [X] version 改成 1.27  (必須跳過 1.20 直接到 1.21 否則會變成 1.2）

