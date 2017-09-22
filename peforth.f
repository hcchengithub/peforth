code \ nexttoken('\n') end-code 
code // last().help += nexttoken('\n|\r'); end-code // ( <comment> -- ) Give help message to the new word with the rest of the line
code <selftest> 
    push(nexttoken("</selftest>"));
    end-code
    // ( <statements> -- ) \ Collect self-test statements. interpret-only
code </selftest> 
    my = tick("<selftest>");
    my.buffer = getattr(my, "buffer", "") # initialize my.buffer
    my.buffer += pop();
    end-code
    // ( "selftest" -- ) Save the self-test statements to <selftest>.buffer. interpret-only

code bye 
            if len(stack) and type(tos())==int: 
                exit(pop()) 
            else:
                exit()
            end-code // ( ERRORLEVEL -- ) Exit to shell with TOS as the ERRORLEVEL.
code /// 
            ss = nexttoken('\n|\r');
            ss = "\t" + ss   # Add leading \t to each line.
            ss = ss.rstrip()+'\n' # trim tailing white spaces
            last().comment = getattr(last(), 'comment', "") + ss;
            end-code
            // ( <comment> -- ) Add comment to the new word, it appears in 'see'.

code immediate last().immediate=True end-code // ( -- ) Make the last new word an immediate.
code stop reset() end-code // ( -- ) Stop the TIB loop
code compyle 
    execute('-indent');execute('indent') 
    source = pop()
    try:
        f = genfunc(source,"","compyle_anonymous")  # body,args,name
        push(f) 
    except Exception as err:
        panic("Failed in compyle command : {}\nBody:\n{}".format(err, source))
    end-code
    // ( "source" -- function ) Compile source code to a python function
    /// The given one line or multiple lines function body with NO argument 
    /// will be converted to an annoymous function left on TOS. Intent problem
    /// is moderated.
    /// Usage: "...python code..." compyle execute 
code trim push(pop().strip()) end-code 
    // ( string -- string' ) Remove leading & ending white spaces
    /// NOT every line of the multi-line string, only the begin/end of it.
    
code indent
    array = pop().splitlines() # [lines] 
    joined = "\n".join(["    "+s for s in array])
    push(joined) 
    end-code // ( string -- string' ) Indent the string    
    /// ( text ) -indent indent \ <== to indentize the text.

code -indent    
    lines = pop()+"\n"+" "*100 # guarantee multiple lines
    array = lines.splitlines() # [lines] 
    if array[0].strip()=="": array=array[1:] # avoid invisible spaces in first line
    for i in range(len(array)): # avoid blank lines become the shortest 
        if len(array[i])==0:
            array[i] += " " * 100;
    spaces = [len(x)-len(x.lstrip()) for x in array]
    indent = min(spaces) # number of common indent 
    cooked = [i[indent:].rstrip() for i in array]  # [cooked lines] 
    joined = "\n".join(cooked).rstrip() 
    push(joined) 
    end-code
    // ( multi-lines -- cooked ) Remove common indent of the string

code <py> 
    push(nexttoken("</py>|</pyV>")) 
    end-code immediate
    // ( <python statements> -- "statements" ) Starting in-line python statements

code </py>     
    try:
        source = tos()
        execute('compyle')
        if compiling:
            comma(pop()) 
        else:
            pop()()
    except Exception as err:
        panic("Failed in </py> (compiling={}): {}\nBody:\n{}".format(compiling,err, source))
    end-code immediate
    // ( "statements" -- ) exec in-line python statements

code </pyV>
    push("push(" + pop() + ")")
    execute('</py>')
    end-code immediate
    // ( "statements" -- value ) Eval in-line python statement

    <py>
        # Workarounds when now <PY>...</PY> is available
        tick('//').immediate=True
        tick('\\').immediate=True
        tick('\\').help="( <comment> -- ) Comment out the rest of the line"
        def v(name):
            '''
            # FORTH variables (value or constant) can be accessed in python code
            # throuth getattr(vm,context)[variableName] or vm.forth[variableName]
            # shorter form v(variableName) is getattr(vm,context)[variableName]
            # where 'v' means (V)ariable in the context. '''
            return getattr(vm,context)[name]
        vm.v = v

        def r(name):
            '''
            # FORTH variables (value or constant) can be accessed in python code
            # throuth getattr(vm,context)[variableName] or vm.forth[variableName]
            # shorter form r(variableName) is vm.forth[variableName] where 'r' 
            # means variable in the (R)oot context, the forth vocabulary.'''
            return vm.forth[name]
        vm.r = r
    </py>
    
code words
    for i in words['forth']: 
        print(i and i.name, end=" ")
    print() end-code 
    // ( -- ) List all words in active vocabularies.
    /// Examples of listing screened words:
    /// 1.List all code words
    ///   <py> [w.name for w in words['forth'][1:] if 'code' in w.type] </pyV>
    /// 2.List all words that have passed their own selftest
    ///   <py> [w.name for w in words['forth'][1:] if 'pass'==getattr(w,'selftest',False)] </pyV>
    /// 3.List all words named with something like 'ASCII'
    ///   <py> [w.name for w in words['forth'][1:] if w.name.find('ASCII')!=-1] </pyV>
    /// 4.List all words named, helped, or commented with something like 'self'
    ///   <py> [w.name for w in words['forth'][1:] if w.name.find('self')!=-1 or w.help.find('self')!=-1 or w.comment.find('self')!=-1]</pyV> 
    
code . print(pop(),end="") end-code // ( x -- ) Print the TOS
code cr print() end-code // ( -- ) print a carriage return

code help
    n=nexttoken();
    if n:
        print(tick(n).help)
        print(tick(n).comment or "") 
    else:
        list = context_word_list()
        for i in range(1,len(list)):
            print(list[i].name, end=" ")
            if getattr(list[i],"help",False):
                print(list[i].help)
            else:
                print("( ?? ) No help, use // command to add help to the 'last' word")
            if getattr(list[i],"comment",False):
                print(list[i].comment)
    end-code // ( <word name> -- ) Print word's help and comment of the given word or all of them
    
code interpret-only
    last().interpretonly=True;
    end-code interpret-only
    // ( -- ) Make the last new word an interpret-only.
code compile-only    
    last().compileonly=True
    end-code interpret-only
    // ( -- ) \ Make the last new word a compile-only.
    
code literal    
    def f(n): # function generator
        def literal(): # literal run time function
            push(n)
        literal.__doc__ = "Literal: {} {}".format(n,type(n))    
        return literal
    comma(f(pop()))
    end-code
    // ( n -- ) \ Compile TOS as an annonymous constant    
    
code reveal    
    wordhash[last().name]=last() end-code
    // ( -- ) Add the last word into wordhash
    /// We don't want the last word to be seen during its colon definition.
    /// So 'reveal' is done in ';' command.
    
code privacy push(False) end-code 
    // ( -- false ) Default is false, words are nonprivate by default.
code (create)    
    global newname
    newname = pop()
    if not newname: panic("(create) what?") 
    if not commandline.strip() and isReDef(newname): # non-selftest 才檢查 reDef
        print("reDef " + newname); # 不能用 tick(newname) 檢查
    current_word_list().append(Word(newname,None));
    last().vid = current; # vocabulary ID
    last().wid = len(current_word_list())-1; # word ID
    last().type = "colon-create";
    vm.execute("privacy"); # use the original execute() to avoid warning
    last().private = bool(pop());
    end-code
    // ( "name" -- ) Create a code word that has a dummy xt, not added into wordhash{} yet
    
code :    
    def xt(_me):
        rstack.append(ip)
        inner(_me.cfa)
    global newname, tib, newhelp, compiling
    newname = nexttoken();
    push(newname); execute("(create)");  # 故 colon definition 裡有 last or last() 可用來取得本身。
    compiling=True;
    tick(':').stackwas = stack[:] # Should not be changed, ';' will check.
    last().type = "colon";
    last().cfa = here;
    last().help = newhelp;
    last().xt = vm.colonxt = xt # also vm['colonxt']
    end-code
    // ( <name> -- ) Begin a forth colon definition.

code ;    
    global calling, compiling
    if tick(':').stackwas!=stack:
        panic("Stack changed during colon definition, it must be a mistake!");
        words[current].pop() # drop the unrevealed new word
    else:
        comma(RET);
    compiling = False;
    execute('reveal');
    end-code immediate compile-only
    // ( -- ) End of the colon definition.

code (   
    a = nexttoken('\\)') 
    b = nexttoken()  # the ')' 
    if compiling and last().help=="": # skip if help alreay exists
        last().help = '( ' + a + b + ' ' 
    end-code immediate
    // ( <stack diagram> -- ) Get stack diagram to the last's help.  
code BL push("\\s") end-code // ( -- "\s" ) RegEx white space, works with 'word' command.
code CR push("\\n|\\r") end-code // ( -- '\n|\r' ) RegEx new line, works with 'word' command.
code word push(nexttoken(pop())) end-code
    // ( "delimiter" -- "token" <delimiter> ) Get next "token" from TIB.
    /// First character after 'word' will always be skipped first, token separator.
    /// If delimiter is RegEx '\s' then white spaces before the "token"
    /// will be removed. Otherwise, return TIB[ntib] up to but not include the delimiter.
    /// If delimiter not found then return the entire remaining TIB (can be multiple lines!).

code ' push(tick(nexttoken())) # use the original tick() to avoid warning
    end-code // ( <name> -- Word ) Tick, get word name from TIB, leave the Word object on TOS.
    
code , comma(pop()) end-code // ( n -- ) Compile TOS to dictionary.
: [compile] ' , ; immediate // ( <string> -- ) Compile the next immediate word.
    /// 把下個 word 當成「非立即詞」進行正常 compile, 等於是把它變成正常 word 使用。
: py: ( <statement> -- ) BL word [compile] </py> ; immediate // Inline python statement down to the next whitespace   
: py> ( <statement> -- ) BL word [compile] </pyV> ; immediate // Inline python statement down to the next whitespace
: py:~ ( <statement> -- ) CR word [compile] </py> ; immediate // Inline python statement for rest of the line
: py>~ ( <statement> -- ) CR word [compile] </pyV> ; immediate // Inline python statement for rest of the line
    
\ ------------ above are most basic words for developing and for debug ----------------
\ 以下都應該盡量改成 colon words 

code 0branch 
    global ip;
    if pop():
        ip += 1;
    else:
        ip = dictionary[ip] 
    end-code compile-only 
    // ( n -- ) 若 n!==0 就將當前 ip 內數值當作 ip, 否則將 ip 進位 *** 20111224 sam
code here! global here; here=pop() end-code // ( a -- ) 設定系統 dictionary 編碼位址
code here push(here) end-code // ( -- a ) 系統 dictionary 編碼位址 a
code swap push(pop(1)) end-code // ( a b -- b a ) stack operation
code !    dictionary[pop()]=pop(1) end-code // ( n a -- ) 將 n 存入位址 a
          \ python 是等號右邊先執行,都好了才執行等號左邊的 assignments
code @    push(dictionary[pop()]) end-code // ( a -- n ) 從位址 a 取出 n
code ?    print(dictionary[pop()],end=" ") end-code // ( a -- ) 查看位址 a 的值

code >r   rstack.append(pop()) end-code  // ( n -- ) Push n into the return stack.
code r>   push(rstack.pop()) end-code  // ( -- n ) Pop the return stack
code r@   push(rtos()) end-code // ( -- r0 ) Get a copy of the TOS of return stack
code drop pop(); end-code // ( x -- ) Remove TOS.
code dup  push(tos()) end-code // ( a -- a a ) Duplicate TOS.
code over push(tos(1)) end-code // ( a b -- a b a ) Stack operation.
code 0<   push(pop()<0) end-code // ( a -- f ) 比較 a 是否小於 0
code +    push(pop(1)+pop()) end-code // ( a b -- a+b) Add two numbers or concatenate two strings.
code *    push(pop()*pop()) end-code // ( a b -- a*b ) Multiplex.
code -    push(pop(1)-pop()) end-code // ( a b -- a-b ) a-b
code /    push(pop(1)/pop()) end-code // ( a b -- c ) 計算 a 與 b 兩數相除的商 c
code 1+   push(pop()+1) end-code // ( a -- a++ ) a += 1
code 2+   push(pop()+2) end-code // ( a -- a+2 )
code 1-   push(pop()-1) end-code // ( a -- a-1 ) TOS - 1
code 2-   push(pop()-2) end-code // ( a -- a-2 ) TOS - 2
: compile ( -- ) // Compile the next word at dictionary[ip] to dictionary[here].
    r> dup @ , 1+ >r ; compile-only 
: if ( -- a ) // if..else..then, if..then
    compile 0branch here 0 , ; immediate compile-only
: then  ( a -- ) // if....else..then, for aft...then next, begin..while..until..then
    here swap ! ; immediate compile-only
code compiling push(compiling) end-code // ( -- boolean ) Get system state
: char ( <str> -- str ) // Get character(s).
    BL word compiling if literal then ; immediate
    /// "char abc" gets "abc", unlike ANS forth "char abc" gets only 'a'.
code last push(last()) end-code // ( -- word ) Get the word that was last defined.
: version py> vm.greeting() ; // ( -- revision ) print the greeting message and return the revision code

code execute execute(pop()); end-code
    // ( Word|"name"|function -- ... ) Execute the given word.
: cls ( -- ) // DOS box clear creen 
    py: os.system("cls") ;
    \ os.system('cls')  # on windows
    \ os.system('clear')  # on linux / os x
: private ( -- ) // Make the last word invisible when out of the context.
    py: last().private=True ;
    /// The opposite is 'nonprivate'.
: nonprivate ( -- ) // Make the last word non-private so it's globally visible.
    py: last().private=False ;
    /// The opposite of 'private'.
                

: \s ( -- ) // Stop outer loop which may be loading forth source files.
    py: vm.stop=True
    py: vm.ntib=len(tib) ; \ 雙重保險。


\ ------------------ Fundamental words ------------------------------------------------------

code (space) push(" ") end-code // ( -- " " ) Put a space on TOS.
code exit comma(EXIT) end-code immediate compile-only
    // ( -- ) Exit this colon word.
code ret comma(RET) end-code immediate compile-only
    // ( -- ) Mark at the end of a colon word.
code rescan-word-hash    
    global wordhash, context
    # Scan given VID into wordhash{}
    def scan_vocabulary(v,isContext):
        for i in range(1,len(words[v])): # The [0] is 0, skip it.
            if compiling and last()==words[v][i]: 
                # skip the last() to avoid unexpected 'reveal'.
                continue; 
            if isContext or not getattr(words[v][i], 'private', False) :
                # skip private words unless in context
                wordhash[words[v][i].name] = words[v][i];
    wordhash = {}; context = order[len(order)-1];
    scan_vocabulary("forth",False); # forth always available
    for j in range(len(order)-1): 
        scan_vocabulary(order[j],False);  # The latter the higher priority
    scan_vocabulary(context,True);  # The context has the highest priority
    end-code
    // ( -- ) \ Rescan all word-lists in the order[] to rebuild wordhash{}
code (') push(tick(pop())) # use the original tick() to avoid warning
    end-code // ( "name" -- Word ) name>Word like tick but the name is from TOS.
code branch vm.ip=dictionary[ip] end-code compile-only 
    // ( -- ) 將當前 ip 內數值當作 ip *** 20111224 sam
code bool push(bool(pop())) end-code // ( x -- boolean(x) ) Cast TOS to boolean.
code and  b=pop();a=pop();push(bool(a) and bool(b)) end-code // ( a b -- a and b ) Logical and
code or   b=pop();a=pop();push(bool(a) or bool(b)) end-code // ( a b -- a or b ) Logical or
code not  push(not bool(pop())) end-code // ( x -- !x ) Logical not
: (forget) ( -- ) // Forget the last word
    py> getattr(last(),'cfa',None) if py: vm.here=last().cfa then
    py: words[current].pop() \ drop the last word
    rescan-word-hash ;

\ ------------------ eforth code words ----------------------------------------------------------------------
code AND        push(pop() & pop()) end-code // ( a b -- a & b ) Bitwise AND
code OR         push(pop() | pop()) end-code // ( a b -- a | b ) Bitwise OR
code NOT        push(~pop()) end-code // ( a -- ~a ) Bitwise NOT
code XOR        push(pop() ^ pop()) end-code // ( a b -- a ^ b ) Bitwise exclusive OR.
code true       push(True) end-code // ( -- True ) boolean True.
code false      push(False) end-code // ( -- False ) boolean False.
code ""         push("") end-code // ( -- "" ) empty string.
code []         push([]) end-code // ( -- [] ) empty array.
code {}         push({}) end-code // ( -- {} ) empty dictionary
code none       push(None) end-code // ( -- None ) Get a None value.
code >>  n=pop();push(pop()>>n) end-code // ( data n -- data>>n ) Singed right shift
code <<  n=pop();push(pop()<<n) end-code // ( data n -- data<<n ) Singed left shift
code 0=  push(pop()==0) end-code // ( a -- f ) 比較 a 是否等於 0
code 0>  push(pop()>0) end-code // ( a -- f ) 比較 a 是否大於 0
code 0<> push(pop()!=0) end-code // ( a -- f ) 比較 a 是否不等於 0
code 0<= push(pop()<=0) end-code // ( a -- f ) 比較 a 是否小於等於 0
code 0>= push(pop()>=0) end-code // ( a -- f ) 比較 a 是否大於等於 0
code =   push(pop()==pop()) end-code // ( a b -- a=b ) 經轉換後比較 a 是否等於 b, "123" = 123.
code ==         push(Boolean(pop())==Boolean(pop())) end-code // ( a b -- f ) 比較 a 與 b 的邏輯
code >          b=pop();push(pop()>b) end-code // ( a b -- f ) 比較 a 是否大於 b
code <          b=pop();push(pop()<b) end-code // ( a b -- f ) 比較 a 是否小於 b
code !=         push(pop()!=pop()) end-code // ( a b -- f ) 比較 a 是否不等於 b
code >=         b=pop();push(pop()>=b) end-code // ( a b -- f ) 比較 a 是否大於等於 b
code <=         b=pop();push(pop()<=b) end-code // ( a b -- f ) 比較 a 是否小於等於 b
code abs push(abs(pop())) end-code // ( n -- |n| ) Absolute value or magnitude of a complex number
code max push(max(pop(),pop())) end-code // ( a b -- max(a,b) ) The maximum.
code min push(min(pop(),pop())) end-code // ( a b -- min(a,b) ) The minimum.
code doVar push(ip); vm.ip = rstack.pop(); end-code compile-only private
    // ( -- a ) 取隨後位址 a , runtime of created words
code doNext 
    i = rstack.pop() - 1;
    if i>0:
        vm.ip = dictionary[ip]; 
        rstack.append(i);
    else: 
        vm.ip += 1
    end-code compile-only
    // ( -- ) next's runtime.
code depth push(len(stack)) end-code // ( -- depth ) Data stack depth
code pick push(tos(pop())) end-code // ( nj ... n1 n0 j -- nj ... n1 n0 nj ) Get a copy
    /// Use py> tos(n) is better I think
code roll push(pop(pop())) end-code // ( ... n3 n2 n1 n0 3 -- ... n2 n1 n0 n3 ) Make a rolling
    /// see rot -rot roll pick
: space (space) . ; // ( -- ) Print a space.
code [ vm.compiling=False end-code immediate // ( -- ) 進入直譯狀態, 輸入指令將會直接執行 *** 20111224 sam
code ] vm.compiling=True end-code // ( -- ) 進入編譯狀態, 輸入指令將會編碼到系統 dictionary *** 20111224 sam
: colon-word ( -- ) // Decorate the last() as a colon word.
    py: last().type="colon";last().cfa=here;last().xt=vm.colonxt
    ; private
: create ( <name> -- ) // Create a new word. The new word is a variable by default.
    BL word (create) reveal colon-word compile doVar ;
    
code (marker)
    # defined in peforth.f original version, supports only one vocabulary 'forth'
    lengthwas = len(current_word_list()) # save current word list length before create the new marker word
    execute("(create)");execute("reveal");
    last().type = "marker";
    last().herewas = here;
    last().lengthwas = lengthwas; # 此 marker 在只有 forth-wordlist 時使用。有多個 word-list 之後要改寫。
    last().help = "( -- ) I am a marker. I forget everything after me.";
    def marker(_me):
        vm.here = _me.herewas;
        vm.current = vm.context = "forth"
        vm.order = [vm.current]; # 萬一此 marker 在引入 vocabulary 之後被 call 到。
        for vid in words:
            if vid != "forth": 
                del(words[vid]); # "forth" is the only one, clean up other word-lists.
        words[current] = current_word_list()[:_me.lengthwas];
        vm.dictionary = dictionary[:here];
        vm.wordhash = {};
        for i in range(1,len(current_word_list())):  
            # 從舊到新，以新蓋舊，重建 wordhash{} hash table.
            wordhash[current_word_list()[i].name] = current_word_list()[i];
        # end of marker()    
    last().xt = marker
    end-code
    // ( "name" -- ) \ Create marker "name". Run "name" to forget itself and all newers.
: marker ( <name> -- ) // Create marker <name>. Run <name> to forget itself and all newers.
    BL word (marker) ;
code next 
    comma(vm.tick("doNext")); # use original tick() to avoid warning
    dictionary[here], vm.here = pop(), here+1
    end-code immediate compile-only 
    // ( -- ) for ... next (FigTaiwan SamSuanChen)
code abort reset() end-code // ( -- ) Reset the forth system.
code alias      
    w = pop();
    # Avoid corrupting TIB use execute("word") instead of dictate("word").
    execute("BL"); execute("word"); execute("(create)");execute("reveal");
    for i in [n for n in dir(w) if not n.startswith('__')]:
        # copy from predecessor but arrays and objects are by reference
        setattr(last(),i,getattr(w,i)) # last()[i] = getattr(w,i); 
    last().predecessor = last().name;
    last().name = newname;
    last().type = "alias";
    end-code
    // ( Word <alias> -- ) Create a new name for an existing word
' != alias <>   // ( a b -- f ) 比較 a 是否不等於 b, alias of !=.
' nonprivate alias public // ( -- ) alias of nonprivate

code nip        pop(1) end-code // ( a b -- b ) 
code rot        push(pop(2)) end-code // ( w1 w2 w3 -- w2 w3 w1 ) 
                /// see rot -rot roll pick
code -rot       push(pop(),1) end-code // ( w1 w2 w3 -- w3 w1 w2 ) 
                /// see rot -rot roll pick
code 2drop      vm.stack=stack[:-2] end-code // ( a b c d-- a b )
: 2dup          ( w1 w2 -- w1 w2 w1 w2 ) over over ;
' NOT alias invert // ( w -- ~w )
: negate        -1 * ; // ( n -- -n ) Negated TOS.
: within        ( n low high -- within? ) -rot over max -rot min = ;
: ['] ( <name> -- Word ) // In colon definitions, compile next word object as a literal.
    ' literal ; immediate compile-only
: allot ( n -- ) // 增加 n cells 擴充 memory 區塊
    \ here 一般指在下一個 available 處, 即 len(dictionary) 之值。
    \ Python 的 len(dictionary) 若小於 here 會觸發 exception.
    \ 因此 here 到 len(dictionary) 之間不夠的要先 append()。
    <py> 
    for i in range(tos()-len(dictionary)+here): dictionary.append(0)
    </py>
    here + here! ; 
: for ( count -- ) // for..next loop.
    compile >r here ; immediate compile-only
    /// for ... next (count ... 2,1) but when count <= 0 still do once!!
    /// for aft ... then next (count-1 ... 2,1) but do nothing if count <= 1.
    /// Pattern : The normalized for-loop pattern. 0 based.
    ///   : test ?dup if dup for dup r@ - ( COUNT i ) . space ( COUNT ) next drop then ; 
    ///   5 test ==> 0 1 2 3 4 
    /// Pattern : The normalized for-loop pattern. Count down
    ///   : test ?dup if for r@ . space next then ;
    ///   5 test ==> 5 4 3 2 1
    /// Pattern : Normalized for-loop pattern but n based.
    ///   : test js: push(tos()+3,0) for dup r@ - ( count+n i ) . space next drop ; 
    ///   5 test ==> 3 4 5 6 7 ; 1 test ==> 1 ; 0 test ==> nothing
    /// Pattern : Simplest, fixed times.
    ///   : test 5 for r@ . space next ; 
    ///   test ==> 5 4 3 2 1
    /// Pattern : fixed times and 0 based index
    ///   : test 5 for 5 r@ - . space next ; 
    ///   test ==> 0 1 2 3 4 
    /// Pattern of break : "r> drop 0 >r" or "js: rstack[rstack.length-1]=0"
    ///   : test 10 for 10 r@ - dup . space 5 >= if r> drop 0 >r then next ; 
    ///   test ==> 0 1 2 3 4 5 
                
: begin ( -- a ) // begin..again, begin..until, begin..while..until..then, begin..while..repeat
    here ; immediate compile-only
: until ( a -- ) // begin..until, begin..while..until..then,
    compile 0branch , ; immediate compile-only
: again ( a -- ) // begin..again,
    compile  branch , ; immediate compile-only
: ahead         ( -- a ) // aft internal use
                compile branch here 0 , ; immediate compile-only
' ahead alias never immediate compile-only // ( -- a ) never ... then for call-back entry inner(word.cfa+n) 
: repeat        ( a a -- ) // begin..while..repeat
                [compile] again here swap ! ; immediate compile-only
: aft           ( a -- a a ) // for aft ... then next
                drop [compile] ahead [compile] begin swap ; immediate compile-only
: else          ( a -- a ) // if..else..then
                [compile] ahead swap [compile] then ; immediate compile-only
: while         ( a -- a a ) // begin..while..repeat, begin..while..until..then
                [compile] if swap ; immediate compile-only
: ?stop         if stop then ; // ( flag -- ) Stop TIB task if flag is True.
: ?dup          dup if dup then ; // ( w -- w w | 0 ) Dup TOS if it is not 0|""|False.
: variable      ( <string> -- ) // Create a variable.
                create 0 , py: last().type='colon-variable' ;
: +!            ( n addr -- ) // Add n into addr, addr is a variable.
                swap over @ swap + swap ! ;
: chars         ( n str -- ) // Print str n times.
                swap 0 max dup 0= if exit then for dup . next drop ;

: spaces        ( n -- ) // print n spaces.
                (space) chars ;
: .(            char \) word . BL word drop ; immediate // ( <str> -- ) Print following string down to ')' immediately.
: ."            ( <str> -- ) // Print following string down to '"'.
                char " word compiling if literal compile .
                else . then BL word drop ; immediate
                \ 本來是 compile-only, 改成都可以。 hcchen5600 2014/07/17 16:40:04
: .'            ( <str> -- ) // Print following string down to "'".
                char ' word compiling if literal compile .
                else . then BL word drop ; immediate
                \ 本來是 compile-only, 改成都可以。 hcchen5600 2014/07/17 16:40:04
: s"            ( <str> -- str ) // Get string down to the next delimiter.
                char " word compiling if literal then BL word drop ; immediate
: s'            ( <str> -- str ) // Get string down to the next delimiter.
                char ' word compiling if literal then BL word drop ; immediate
: s`            ( <str> -- str ) // Get string down to the next delimiter.
                char ` word compiling if literal then BL word drop ; immediate
: does>         ( -- ) // redirect the last new colon word.xt to after does>
                [compile] ret \ dummy 'ret' mark for 'see' to know where is the end of a creat-does word
                \ r> [ s" push(function(){push(last().cfa)})" jsEvalNo , ] ! ; 
                r> py: push(last().cfa) ! ; 
: count         ( thing -- thing length ) // Get length of the thing if it has
                py: push(len(tos())) ;
code accept     
    # python v3.6 IDLE fires KeyboardInterrupt unexpectedly!
    try:
        s = input()
    except KeyboardInterrupt:
        s = ""
    push(s)
    end-code // ( -- str ) Read a line from terminal.
    
code accept2 
    result = nexttoken('\\n')+'\n' # rest of the line after accept2
    execute('accept'); s = pop()+'\n'
    while (not chr(4) in s) and (not '</accept>' in s):  # py> chr(4)=='^D' --> True
        result += s
        execute('accept'); s = pop()+'\n'
    result += s 
    if len(result):
        push(result)
        execute('-indent')
    else:
        push("")
    end-code // ( -- str ) Read multiple lines from terminal. 
    /// Ctrl-D or </accept> appear in the last line to terminate the input. 
    last alias <accept> // ( -- str ) Read multiple lines from terminal.

code nop end-code // ( -- ) no operation
    ' nop alias </accept> last py: pop().help="" 
        // ( -- ) Ending mark of a multiple-line input, do nothing.
    ' nop alias temp last py: pop().name=chr(4) last py: pop().help="" 
        // ( -- ) Ctrl-D ending mark of a multiple-line input, do nothing.
    rescan-word-hash
    
: refill        ( -- flag ) // Reload TIB from stdin. return false means no input or EOF
                accept count if py: vm.tib=pop();vm.ntib=0 true else false then ;

: [else] ( -- ) // 丟掉以下 TIB 到 "[else]" or "[then]" 為止，考慮了中間的 nested 結構。
                1 \ ( [if] structure nested level )
                begin \ level
                    begin \ ( level )
                        BL word count \ (level $word len ) 取出 [if] 之後 word 下一個 
                    while \ (level $word) 查看這個每個要丟掉的 word 做 nested 處裡。
                        dup s" [if]" = if \ ( level $word )
                            drop 1+ \ ( level' ) 如果這個 word 是 [if] 就把它丟掉，再進一層
                        else \ ( level $word ) 不是 [if] 那麼是否 [else]
                            dup s" [else]" = if \ (level $word)
                                drop \ ( level ) 丟掉 "[else]"
                                1- dup if 1+ then \ (level') level==1 時把它變成 0 準備走出 [if] 結構，
                                \ 其他 level 值則不變，繼續處理剩下的 [if] 結構。
                            else \ level $word, 不是 [else] 那麼是否 [then]
                                s" [then]" = if \ (level)
                                    1- \ level' \ (level') 如果這個 word 是 [then] 就剝掉一層
                                then \ (level')
                            then \ level'
                        then \ level'
                        \ 整個結構的正常出口在這裡
                        ?dup if else exit then 
                        \ 已經到最外層就離手走出 [if] 結構，否則繼續看下一個 word.
                    repeat \ (level) 回頭重來,看 TIB 裡下一個 word。
                    drop   \ (level) TIB 空了，把 null string 丟掉，留下 level。
                refill not until \ reload TIB 然後繼續
                \ level, TIB 斷尾了，可能是 ^z ^d 之類，做不下去了。
                drop \ 把 TIB 斷尾中止後剩下的 level 丟掉。
                ; immediate
                
: [if]          ( flag -- ) // Conditional compilation [if] [else] [then]
                if else [compile] [else] then \ skip everything down to [else] or [then] when flag is not True.
                ; immediate
                /// [if] 用來把 iTIB 視條件跳到這個 [if] 之後或 [else] 之後。

: [then]        ( -- ) // Conditional compilation [if] [else] [then]
                ; immediate
                
: (::)          ( obj "sub-statement" -- ) // Simplified form of "obj py: pop().foo.bar" w/o return value
                <py> tos()[0]=='[' or tos()[0]=='(' </pyV> 
                if char pop() else char pop(). then 
                swap + compiling if compyle , 
                else [compile] </py> then ;
                
: (:>)          ( obj "sub-statement" -- value ) // Simplified form of "obj js> pop().foo.bar" w/return value
                <py> tos()[0]=='[' or tos()[0]=='(' </pyV>
                if char push(pop() else char push(pop(). then 
                swap + char ) + compiling if compyle ,
                else [compile] </py> then ;
                        
: ::            ( obj <sub-statement> -- ) // Simplified form of "obj py: pop().foo.bar" w/o return value
                BL word (::) ; immediate   /// down to the next whitespace
: :>            ( obj <sub-statement> -- value ) // Simplified form of "obj js> pop().foo.bar" w/return value
                BL word (:>) ; immediate   /// down to the next whitespace
: ::~           ( obj <sub-statement> -- ) // Simplified form of "obj py: pop().foo.bar" w/o return value
                CR word (::) ; immediate   /// for rest of the line
: :>~           ( obj <sub-statement> -- value ) // Simplified form of "obj js> pop().foo.bar" w/return value
                CR word (:>) ; immediate   /// for rest of the line

\ 有 bug 先暫時不要這個 nested ( ) comment
\ : (     ( <str> -- ) // Ignore the comment down to ')', can be nested but must be balanced
\         <py> compiling and last().help</pyV> if : 
\             \ comment out the stack diagram if help alreay exists
\             py> nextstring(r"\(|\)")['str'] \ word 固定會吃掉第一個 character 故不適用。
\             drop py: push(tib[ntib]);vm.ntib+=1 \ 撞到停下來的字母非 '(' 即 ')' 要不就是行尾，都可以 skip 過去
\             char ( = if \ 剛才那個字母是啥？
\             [ last literal ] dup \ 取得本身
\             execute \ recurse nested level
\             execute \ recurse 剩下來的部分
\             then
\         else
\             \ add stack diagram into the word's help
\             <py> last().help = '( ' + nexttoken('\\)') + nexttoken() + ' '</py>
\         then ; immediate
\         /// '(' command 用 recursion 完成, 正點! 

: "msg"abort    ( "errormsg" -- ) // Panic with error message and abort the forth VM
                py: panic(pop()) abort ; nonprivate

: abort"        ( <msg> -- ) // Through an error message and abort the forth VM
                char " word literal BL word drop compile "msg"abort ;
                immediate compile-only

: "msg"?abort   ( "errormsg" flag -- ) // Conditional panic with error message and abort the forth VM
                if "msg"abort else drop then ; nonprivate

: ?abort"       ( f <errormsg> -- ) // Conditional abort with an error message.
                char " word literal BL word drop
                compile swap compile "msg"?abort ;
                immediate compile-only

\ 其實所有用 word 取 TIB input string 的 words， 用 file 或 clipboard 輸入時， 都是可
\ 以跨行的！只差用 keyboard 輸入時受限於 console input 一般都是以「行」為單位的，造成
\ TIB 只能到行尾為止後面沒了，所以才會跨不了行。將來要讓 keyboard 輸入也能跨行時，就
\ 用 text。

\ 費了一番功夫寫就能 nested 的 <text> 及 <comment> , 開發心得在 Ynote 上
\ search "jeforth.3we design a nesting supported〈text〉also〈comment〉"
\ '(' command 的 nested support 也用 recursion 完成, 正點! 

variable '<text> private
    // ( -- <text> ) Variable reference to the <text> Word object, for indirect call.
: (<text>)      ( <text> -- "text"+"</text>" ) // Auxiliary <text>, handles nested portion
                '<text> @ execute ( string ) \ 此時 TIB 非 </text> 即行尾
                BL word char </text> = ( string is</text>? )
                if \ 剛才撞上了 </text> ( string )
                    s" </text> " + ( string1' )
                then ; private
                /// (<text>) is almost same as <text> but it consumes the 
                /// next </text> in TIB and returns <text> + "</text>"

: <text>        ( <text> -- "text" ) // Get multiple-line string, can be nested.
                char </text>|<text> word ( string1 )
                \ 撞到 delimiter 停下來非 <text> 即 </text> 要不就是行尾
                BL word dup char <text> = ( string1 deli is<text>? )
                if \ 剛才撞上了 <text> ( string1 deli )
                    drop s" <text> " + ( string1' )
                    (<text>) ( string1' string2 ) + 
                    [ last literal ] execute ( string1'' string3 ) + ( string )
                else \ 剛才撞上了 </text> 或行尾  ( string1 deli )
                    char </text> swap over = ( string1 "</text>" is</text>? ) 
                    if py: vm.ntib-=len(pop()) ( string1 )
                    else drop then  ( string1 )
                then ; immediate last '<text> !
                /// If <text> hits <text> in TIB then it returns 
                /// string1 +  "<text>" + (<text>) + <text> 
                /// leaves the next </text> in TIB
                /// Colon definition 中萬一前後不 ballance 會造成 colon definition
                /// 不如預期結束而停留在 compiling state 裡等 closing </text> 的現象。
                
: </text>       ( "text" -- ... ) // Delimiter of <text>
                compiling if literal then ; immediate
                /// Usage: <text> word of multiple lines </text>

                \ Ready to add comment to 'privacy' 
                <text>
                    Example 'privacy' definition for a vocabulary. Assume current == context.
                    False constant privacy private // ( -- False ) All words in this module are public
                    True  constant privacy private // ( -- True ) All words in this module are private
                </text> ' privacy :: comment=pop(1)

: <comment>     ( <comemnt> -- ) // Can be nested
                \ If <comment> hits <comment> in TIB then it drops string1 
                \ and does <comment> and does again <comment>
                char <comment>|</comment> word drop ( empty )
                BL word char <comment> = ( is<comment>? )
                if \ 剛才撞上了 <comment> ( empty )
                    [ last literal ] dup execute execute
                then ; immediate
: </comment>    ; // ( -- ) Delimiter of <comment>
: (constant)    ( n "name" -- ) // Create a constnat
                (create) <py>   
                source = '    push(getattr(vm,"{}")["{}"])'.format(current, last().name)
                last().xt = genxt('constant',source)
                if not getattr(vm,current,False): setattr(vm,current,{})
                exec('getattr(vm,"{}")["{}"]=pop()'.format(current, last().name)) 
                </py> 
                reveal ; 
: constant      ( n <name> -- ) // Create a constnat
                BL word (constant) ;
: value         ( n <name> -- ) // Create a 'value' variable.
                constant last :: type='value' ; 
: to            ( n <value> -- ) // Assign n to <value>.
                ' ( n word ) 
                py> tos().type!="value" ?abort" Error! Assigning to a none-value."
                compiling if ( n word ) 
                    char getattr(vm,"{}")["{}"]=pop() 
                    :> format(tos().vid,pop().name) ( n s ) 
                    compyle , ( n ) \ n has already been compiled as a literal
                else ( n word )
                    py: getattr(vm,tos().vid)[pop().name]=pop(1)
                then ; immediate
code            cut vm.tib=tib[ntib:];vm.ntib=0 end-code
                // ( -- ) // Cut off used TIB.
                /// "cut ~ 10 nap rewind" repeat running the TIB.
                /// See also <task>
code -word 
                # 加上 dummy 頭尾再 split 以統一所有狀況。丟掉 dummy 頭尾 
                push(('h ' + tib[:ntib] + ' t').split()[1:-1]); end-code
                // ( -- array[] ) Get TIB used tokens.
                /// 跟 word 有點相反的味道，故以 -word 為名。用來找 nap。peforth 可能沒用?
: rewind ( -- ) // Rewind TIB so as to repeat it. 'stop' to terminate.
                py: vm.ntib=0 ;
                /// "cut ~ 10 nap rewind" repeat running the TIB.
                /// See also <task>
: ?rewind ( boolean -- ) // Conditional rewind TIB so as to repeat it. 'stop' to terminate.
                if rewind then ;

: tib. ( result -- ) // Print the command line and the TOS.
                py> tib[:ntib].rfind('\n') py> tib[max(pop(),0):ntib].strip() ( result cmd-line )
                s" {} \ ==> {} ({})" :> format(pop(),tos(),type(pop())) . cr ;
                /// Good for experiments that need to show command line and the result.
                /// "" tib. prints the command line only, w/o the TOS.

\ To TIB command line TSRs, the tib/ntib is their only private storage. So save-restore and
\ loop back information must be using the tib. That's why we have >t t@ and t> 

code >t         
                # \n\\ 1234$ <--- 一個數字的 pattern
                vm.tib += "\n\\ " + str(pop());
                end-code // ( int -- ) Push the integer to end of TIB

code t@         
                # \n\\ 1234$ <--- 一個數字的 pattern
                r = re.search( r'\n\\ (\d*)$', tib)
                push(int(r.group(1))); 
                end-code // ( -- int ) Get integer from end of the TIB 

code t>            
                # \n\\ 1234$ <--- 一個數字的 pattern
                r = re.search( r'\n\\ (\d*)$', tib)
                push(int(r.group(1))); 
                vm.tib = tib[:-len(r.group())]
                end-code // ( -- int ) Pop integer from end of the TIB 

: [begin]       ( -- ) // [begin]..[again], [begin].. flag [until]
                py> ntib >t ; interpret-only
                /// Don't forget some nap.
                /// 'stop' command or {Ctrl-Break} hotkey to abort.
                /// ex. [begin] .s js> rstack . cr 1000 nap [again]
                
: [again]       ( -- ) // [begin]..[again]
                t@ py: vm.ntib=pop() ; interpret-only
                /// Don't forget some nap.
                /// 'stop' command or {Ctrl-Break} hotkey to abort.

: [until]       ( flag -- ) // [begin].. flag [until]
                if  t> drop else [compile] [again] then ; interpret-only
                /// Don't forget some nap.
                /// 'stop' command or {Ctrl-Break} hotkey to abort.
                /// ex. [begin] now t.second dup . space 5 mod not 100 nap [until]

: [for]         ( count -- ) // (T -- ntib count ) [for]..[next] 
                [compile] [begin] >t ; interpret-only
                /// Instead of using rstack, [for] loop uses tib tail to save-restore 
                /// the loop back address and the count. Thus >t t> and t@ replace
                /// >r r> and r@ respectively.
                /// Pattern : The normalized for-loop pattern. 0 based.
                ///   5 ?dup [if] dup [for] dup t@ - ( COUNT i ) . space ( COUNT ) [next] drop [then]
                ///   ==> 0 1 2 3 4
                /// Pattern : Normalized for-loop pattern but n(66) based.
                ///   5 js: push(tos()+66,0) [for] dup t@ - ( count+n i ) . space [next] drop
                ///   ==> 66 67 68 69 70  OK        
                /// Pattern : Simplest, fixed times.
                ///   5 [for] t@ . space [next]
                ///   ==> 5 4 3 2 1
                /// Pattern : fixed times and 0 based index
                ///   5 [for] 5 t@ - . space [next]
                ///   ==> 0 1 2 3 4
                /// Pattern of break : "t> drop 0 >t" or "js: rstack[rstack.length-1]=0"
                ///   10 [for] 10 t@ - dup . space 5 >= [if] t> drop 0 >t [then] [next]
                ///   ==> 0 1 2 3 4 5
                /// Don't forget some nap.
                /// 'stop' command or {Ctrl-Break} hotkey to abort.

: [next]        ( -- ) // (T ntib count -- ntib count-1 | empty ) [for]..[next]
                t> 1- dup >t py> pop()>0 ( count>0 ) if 
                    \ rewind
                    t> t> py: vm.ntib=tos() >t >t 
                else
                    \ exit the for loop
                    t> t> 2drop \ drop the count and loop back ntib address
                then ; interpret-only
                /// Don't forget some nap.
                /// 'stop' command or {Ctrl-Break} hotkey to abort.

\ code (run:)     ( "..if.." -- "..[if].." ) // Run string with "if","begin","for" in interpret mode
\                 var ss = pop();
\                 var result = ss
\                     .replace(/(^|\s)(if|else|then|begin|again|until|for|next)(\s|$)/mg,"$1[$2]$3")
\                     .replace(/(^|\s)(if|else|then|begin|again|until|for|next)(\s|$)/mg,"$1[$2]$3");
\                     // 連做兩次解決 if else then 翻成 [if] else [then] 的現象。 
\                 push(result);execute("tib.insert"); // 不能用 dictate(), 多重 suspend 時，會有怪現象。
\                 end-code
\                 /// Replace "if", "for", "begin", .. etc to "[if]", "[for]", "[beign]" .. etc
\                 /// I like to use "if" in interpret mode directly instead of "[if]" and
\                 /// to merge them is difficult to me so far. So I defined this word.
\ : run:          ( <string> -- ... ) // Run one-liner with "if","begin","for", in interpret mode
\                 CR word (run:) ; interpret-only
\                 /// To run multiple lines use <text>...</text> (run:) or "run>" instead of "run:".
\                 /// run: is oneliner. I think run: may be used in ~.f files while run> certainly can't.
\ : run>          ( <string> -- ... ) // Run multiple lines with "if","begin","for", in interpret mode
\                 js> push(ntib);ntib=tib.length;tib.slice(pop()) (run:) ; interpret-only
\                 /// run> go through all the rest of the inputbox; 
\                 /// run: is oneliner. I think run: may be used in ~.f files while run> certainly can't.

\ ------------------ Tools  ----------------------------------------------------------------------
                
code int        push(int(pop())) end-code   // ( float|string -- integer|NaN )
code float      push(float(pop())) end-code // ( string -- float|NaN ) 
: drops         ( ... n -- ... ) // Drop n cells from data stack.
                py: vm.stack=stack[:-pop()] ;
                /// We need 'drops' <py> sections in a colon definition are easily 
                /// to have many input arguments that need to be dropped.
: dropall       ( ... -- empty ) // Drop all cells from data stack
                0 drops ;
code char>ASCII push(ord(pop())) end-code // ( str -- ASCII ) Get str[0]'s ASCII or whatever code
                /// Actually it returns utf-8, big-5, or whatever numeric code.
                \ https://stackoverflow.com/questions/227459/ascii-value-of-a-character-in-python
                
code ASCII>char push(chr(pop())) end-code // ( ASCII -- 'c' ) ASCII or whatever code number to character
                /// 65 ASCII>char tib. \ ==> A (string)
                \ https://stackoverflow.com/questions/180606/how-do-i-convert-a-list-of-ascii-values-to-a-string-in-python
                
: ASCII         ( <str> -- ASCII ) // Get <str>[0]'s ASCII code.
                BL word char>ASCII compiling if literal then
                ; immediate
code .s         
                for i in range(len(stack)):
                    x, typex = stack[i], type(stack[i])
                    if typex==int:
                        s = "{0:>7}: {1:11,} {2:11X}h ({3})".format(i,x,x,type(x))
                        print(s)
                    elif typex==float or typex==complex:    
                        s = "{0:>7}: {1:11,} {2:11}  ({3})".format(i,x,'',type(x))
                        print(s)
                    else:
                        # push(stack[i]); push(i); dictate("decimal 7 .r char : . space .");
                        s = "{0:>7}: {1} ({2})".format(i,str(x),type(x))
                        print(s)
                if stack==[]:
                    print("empty\n");
                end-code
                // ( ... -- ... ) Dump the data stack.

code (*debug*)
                print('---- Break point {} ----'.format(pop()))
                pdb.set_trace() end-code 
                // ( msg -- ) Invoke python pdb debugger
: *debug*       ( <prompt> -- resume ) // Breakpoint enters pdb debugger
                BL word compiling if literal compile (*debug*) 
                else (*debug*) then ; immediate
code readTextFile 
                pathname = pop()
                try:
                    data = vm.readTextFile(pathname); 
                except Exception as err:
                    panic("Failed reading {}: {}".format(pathname,err))
                    data = "";
                push(data);
                end-code // ( "pathname" -- string ) Return an utf-8 string, "" if failed

code writeTextFile 
                pathname = pop()
                try:
                    vm.writeTextFile(pathname,pop())
                except Exception as err:
                    panic("Failed writing {}: {}".format(pathname,err))
                    data = "";
                end-code // ( string "pathname" -- ) Write utf-8 string to file

code tib.insert  
                before, after = tib[:ntib], tib[ntib:] 
                vm.tib = before + " " + str(pop()) + " " + after 
                end-code // ( "string" -- ) Insert the "string" into TIB

: sinclude      ( "pathname" -- ... ) // Lodad the given forth source file.
                readTextFile ( file ) py: dictate(pop()) ;

: include       ( <filename> -- ... ) // Load the source file
                BL word sinclude ; interpret-only
    
: type          ( x -- type ) // get type object of anything x                
                py> type(pop()) ;
        
code obj>keys      
                if type(tos())==dict:
                    push(pop().keys())
                else:
                    push(dir(pop()))
                end-code
                // ( obj -- [keys] ) Get all attributes of an object or all kyes of an dict

    \ json.dumps() needs this function to convert a Word object to dict 
    <py>   
        def obj2dict(obj):
            #convert object to a dict
            d = {}
            d['__class__'] = obj.__class__.__name__
            d['__module__'] = getattr(obj,"__module__","unknown")
            d['__doc__'] = getattr(obj,"__doc__",None)
            d.update(getattr(obj,"__dict__",{}))
            return d
        push(obj2dict)
    </py> constant obj2dict // ( -- func ) obj to dict converter for json.dumps(...,default=r('obj2dict'))

: stringify     ( thing -- "string" ) // JSON.stringify anything
                py> json.dumps(pop(),default=r('obj2dict'),indent=4) ;

code toString # To see a cell in dictionary
                x = pop();
                if x==None: 
                    push('RET')
                elif x=="": 
                    push('EXIT')
                elif type(x)==int:  # remove numbers to protect getattr()
                    push(str(x))
                else: 
                    push(str(x));
                end-code private // ( value -- string ) To see dictionary cell, toString() of the variable consider ret and exit

: .literal      ( addr -- T|f ) // Do the (dump) if addr @ is a literal
                dup @ ( addr code ) 
                py> getattr(tos(),'__name__',False)=='literal' if 
                    \ is literal function ( addr code )
                    s" {:05}: {}" :> format(pop(1),pop().__doc__) . cr 
                    true
                else 2drop false then ;
                
: .function     ( addr -- T|f ) // Do the (dump) if addr @ is a literal
                dup @ ( addr func ) 
                py> callable(tos()) if  \ is function ( addr code )
                    s" {:05}: {} ({})" 
                    :> format(pop(1),tos().__doc__,type(tos())) . cr ( code )
                    py: dis.dis(pop()) \ disassembled code
                    true
                else 2drop false then ;
                
: (dump)        ( addr -- ) // dump one cell of dictionary
                py> len(dictionary)<=tos() if drop exit then 
                dup .literal  if drop exit then
                dup .function if drop exit then
                dup @ ( addr value ) dup toString ( addr value toString )
                s" {:05}: {}  ({})" :> format(pop(2),pop(),type(pop())) 
                . cr ;

                
: dump          ( addr length -- addr' ) // dump dictionary
                for ( addr ) dup (dump) 1+ next ;
                
: dump2ret      ( addr -- ) // dump dictionary until next RET
                begin dup (dump) ( addr ) 
                py> dictionary[tos()]==None py> len(dictionary)<=tos() or
                if drop exit then \ it's RET, all done
                1+ again ;
                
: d             ( <addr> -- ) // dump dictionary
                [ last literal ]
                BL word                     \ (me str)
                count 0=                    \ (me str undef?) No start address?
                if                          \ (me str)
                    drop                    \ drop the null str (me)
                    py> tos().lastaddress   \ (me addr)
                else                        \ (me str)
                    py> int(pop())          \ (me addr)
                then ( me addr )
                20 dump                     \ (me addr')
                py: pop().lastaddress=pop()
                ;
                
: (see)         ( thing -- ) // See into the given word, object, array, ... anything.
                dup ( thing thing ) stringify . cr ( thing )
                \ for colon words, dump its forth code 
                dup type py> Word = if \ is a Word ( w ) \ the thing is a Word
                    py> tos().type.find('colon')!=-1 if  ( w ) \ it is a colon word 
                        ." ------------ Definition in dictionary ------------" cr
                        :> cfa ( cfa ) dump2ret 
                        ." ------------ End of the difinition ---------------" cr
                    else \ Not colon word must be a code word
                        ( w ) 
                        ." ------------ Source code ------------" cr
                        :> xt.__doc__ . cr cr
                        ." -------------------------------------" cr
                    then
                then ;
                /// Also .members .source

: .members      ( obj -- ) // See the object details through inspect.getmembers(obj)
                py> inspect.getmembers(pop()) cr (see) cr ;
                /// Also (see) .source
                
: .source      ( function -- ) // See source code through inspect.getsource(func)
                py> inspect.getsource(pop()) cr . cr ;
                /// Also .members (see)

: see           ' (see) ; // ( <name> -- ) See definition of the word
: dos           py> os.system('cmd/k') ; // ( -- ) Shell to DOS Box

code notpass
                for v in words: 
                    print(
                        v,
                        ':',
                        [w for w in words[v] if getattr(w,'selftest',False)!='pass']
                    )
                end-code // ( -- ) List words who's selftest flag are not 'pass'.
                
                
code passed
                for v in words: 
                    print(
                        v,
                        ':',
                        [w for w in words[v] if getattr(w,'selftest',False)=='pass']
                    )
                end-code // List words who's sleftest flag are 'pass'.

: slice         ( 1 2 3 -2 -- 1 [2,3] ) // Slice the ending -n cells to a new array 
                ( -2 ) >r py: t,vm.stack=stack[rtos():],stack[:rpop()];push(t) ;
                /// 很多 function 的傳回值是一列 tuple, 有需要把它們集合起來。    

\ ----------------- Self Test -------------------------------------

\ Important!
\ private words referenced by name from out of the context will be a problem.
\ private words called (execute) or referenced (tick) by name warning when in 
\ selftest to find them without reducing the performance of none-selftest mode. 
\ : referenced-by-name-warning-on    ( -- ) // Turn on run-time warnings 
\                 js: tick=vm.g.selftest_tick;execute=vm.g.selftest_execute ;
\ : referenced-by-name-warning-off   ( -- ) // Turn off run-time warnings
\                 js: tick=vm.tick;execute=vm.execute ;
                
"" value description     ( private ) // ( -- "text" ) description of a selftest section
[] value expected_rstack ( private ) // ( -- [..] ) an array to compare rstack in selftest
[] value expected_stack  ( private ) // ( -- [..] ) an array to compare data stack in selftest
0  value test-result     ( private ) // ( -- boolean ) selftest result from [d .. d] 
[] value [all-pass]      ( private ) // ( -- ["words"] ) array of words for all-pass in selftest
: ***           ( <description> -- ) // Start a selftest section
                CR word trim ( desc )
                s" *** {} ... " :> format(pop()) to description
                depth if 
                    description . ." aborted" cr 
                    ." *** Warning, Data stack is not empty." cr
                    stop
                then ;
                
code all-pass   
                a = pop();
                for i in a:
                    w = tick(i)
                    if not w: 
                        panic("Error! {} unknown!\n".format(i));
                    else: 
                        w.selftest='pass';
                end-code private
                // ( ["name",...] -- ) Mark 'pass' to these word's selftest flag

: [r            ( <"text"> -- ) // Prepare an array of data to compare with rstack in selftest.
                char r] word s" [{}]" :> format(pop()) \ string
                py> eval(pop()) \ string to array
                to expected_rstack ;
                /// Example: [r 1,2,3 r] [d True d] [p 'word1','word2' p]
                /// [r...r] section is optional, [d...d] section is the judge.
: r]            ( -- boolean ) // compare rstack and expected_rstack in selftest
                py> rstack expected_rstack = ;
                ' [r :> comment last :: comment+=pop(1)
                
: [d            ( <"text"> -- ) // Prepare an array to compare with data stack. End of a selftest section.
                char d] word s" [{}]" :> format(pop()) \ string
                py> eval(pop()) \ string to array
                to expected_stack ;
                /// Data stack will be clean after check
                ' [r :> comment last :: comment+=pop(1)
                
: d]            ( -- boolean ) // compare data stack and expected_stack in selftest
                depth negate slice expected_stack =  to test-result 
                description . test-result if ." pass" cr
				else ." fail" cr stop then ;                
                /// Data stack will be clean after check
                ' [r :> comment last :: comment+=pop(1)

: [p            ( <"text"> -- ) // Prepare an array of words for all-pass if test-result is True
                char p] word s" [{}]" :> format(pop()) \ string
                py> eval(pop()) \ string to array
                to [all-pass] ; 
                ' [r :> comment last :: comment+=pop(1)
                
: p]            ( -- boolean ) // all-pass if test-result is True
                test-result if [all-pass] all-pass then ; 
                ' [r :> comment last :: comment+=pop(1)
                
                \ Make these words private. Do it this way instead 
                \ of at their definitions to void selftest_tick() warnings
                ' description     :: private=True
                ' expected_rstack :: private=True
                ' expected_stack  :: private=True
                ' test-result     :: private=True
                ' [all-pass]      :: private=True

    \ I/O may not be ready enough to read selftest.f at this moment, 
    \ so the below code has been moved to quit.f of each applications.
    \ Do the jeforth.f self-test only when there's no command line
    \   js> vm.argv.length 1 > \ Do we have jobs from command line?
    \   [if] \ We have jobs from command line to do. Disable self-test.
    \       js: tick('<selftest>').enabled=False
    \   [else] \ We don't have jobs from command line to do. So we do the self-test.
    \       js> tick('<selftest>').enabled=True;tick('<selftest>').buffer tib.insert
    \   [then] js: tick('<selftest>').buffer="" \ recycle the memory

    
    