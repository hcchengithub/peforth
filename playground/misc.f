

    \ <text>
    \ \ 
    \ \ WshShell - users may not install win32 packages yet so only a clue here
    \ \ Run "WshShell dictate" to vitalize this word
    \ \ 
    \ import win32com.client constant win32com.client // ( -- module )
    \ win32com.client :> Dispatch("WScript.Shell") constant WshShell // ( -- obj ) The "Windows Script Host" object https://technet.microsoft.com/en-us/library/ee156607.aspx
    \     /// WshShell :: rUn("c:\Windows\System32\scrnsave.scr") \ Windows display off power saving mode
    \     /// WshShell :: SeNdKeYs("abc")
    \     /// WshShell :: ApPaCtIvAtE("c:\\") \ beginning 2+ chars of the window title, case insensitive.
    \     /// WshShell ::~ RuN("python -i -m peforth WshShell dictate cls version drop dos title child peforth")
    \ </text> constant WshShell // ( -- "clue" ) Guide how to use WshShell

    \ Obsoleted
    \ <py>
    \     def outport(loc): 
    \         '''
    \         # Make all local variables forth constants.
    \         # The input argument is supposed locals() of the caller.
    \         # Examine locals after a <Py>...</Py> section 
    \         # For studying maching learning, tersorflow, ... etc. 
    \         # Usage: outport(locals())
    \         '''
    \         for i in loc: 
    \             push(loc[i]) # vale
    \             push(i) # variable name
    \             execute('(constant)')
    \             last().type='value.outport'
    \     vm.outport = outport
    \ </py>
    \ 
    \ : inport    // ( dict -- ) Make all pairs in dict peforth values. 
    \             py: outport(pop()) ; 
    \             /// Example: investigate the root application
    \             /// ok(loc=locals(),glo=globals(),cmd=':> [0] inport')
    \             
    \ <py>
    \     def harry_port(loc={}):
    \         '''
    \         # Note! Don't use this technique in any compiled snippet, but run by exec() 
    \         # instead. This function returns a dict of all FORTH values with type of 
    \         # "value.outport". Refer to 1) FORTH word 'inport' which converts a dict, a 
    \         # snapshot of locals(), at TOS to FORTH values, and 2) python function 
    \         # outport() which converts the given locals() to FORTH values. The two are 
    \         # similar. While harry_port() does the reverse, it brings FORTH values, that 
    \         # were outported from a locals(), back to python locals().             
    \         # Usage: Method A) exec(python_code, harry_port()) 
    \         #        Method B) locals().update(harry_port())
    \         # <PY> exec("locals().update(harry_port()); x = sess.run(myXX); print(x)") </PY>
    \         # Usage: 
    \         #   1. exec("x = sess.run(myXX); print(x)", harry_port())
    \         #   2. locals().update(harry_port()) # in code executed by exec()
    \         '''
    \         ws = [w.name for w in words[context][1:] if 'outport' in w.type]
    \         for i in ws:
    \             loc.update({i:v(i)})
    \         return loc 
    \     vm.harry_port = harry_port    
    \ </py>
    \             
    \ : harry_port py> harry_port.__doc__ -indent . cr ; // ( -- ) Print help message

    : slice     // ( 1 2 3 -2 -- 1 [2,3] ) Slice the ending -n cells to a new array 
                ( -2 ) >r py: t,vm.stack=stack[rtos():],stack[:rpop()];push(t) ;
                /// Group the tuple returned from a function
    
    : (pyclude) // ( <pathname.py> -- "code" ) Prepare the .py file into a <PY>..</PY> section ready to run
                CR word readTextFile py> re.sub("#__peforth__","",pop()) 
                py> re.sub(r"(from\s+__future__\s+import\s+print_function)",r"#\1",pop()) 
                <text> 
                os.environ['TF_CPP_MIN_LOG_LEVEL']='2' # https://stackoverflow.com/questions/43134753/tensorflow-wasnt-compiled-to-use-sse-etc-instructions-but-these-are-availab
                </text> -indent swap + 
                -indent indent <py> "    <p" + "y>\n" + pop() 
                + "\n    </p" + "y>\n" </pyV> ;
                /// Auto-remove all #__peforth__ marks so we can add debug
                /// statements that are only visible when debugging.
                /// Auto comment out "from __future__ import print_function" 
                /// that is not allowed when in a <PY>..</PY> space.
                
    : pyclude   // ( <pathname.py> -- ... ) Run the .py file in a <PY>..</PY> space
                (pyclude) dictate ; 
                ' (pyclude) :> comment last :: comment=pop(1)

    : .members  // ( obj -- ) See the object details through inspect.getmembers(obj)
                py> inspect.getmembers(pop()) cr (see) cr ;
                /// Also (see) .source
                    
    : .source   // ( function -- ) See source code through inspect.getsource(func)
                py> inspect.getsource(pop()) cr . cr ;
                /// Also .members (see)
                /// py: dis.dis(pop()) \ sees pseudo code of a function at TOS.

    : dos       // ( <command line> -- errorlevel ) Shell to DOS Box run rest of the line
                CR word ( cml ) trim ( cml' )
                ?dup if py> os.system(pop())
                else py> os.system('cmd/k') then ;
                /// See also WshShell 
                
    : cd        // ( <path> -- ) Mimic DOS cd command
                CR word ?dup if py: os.chdir(pop())
                else py> os.getcwd() . cr then ;
                /// Use 'dos' command can NOT do chdir, different shell.
                /// See also: os.chdir('path'); path=os.getcwd()

    \ : ( // ( <str> -- ) Comment down to ')' which can be nested if balanced
    \     py> nextstring('\(|\)')['str'] \ word 固定會吃掉第一個 character 故不適用。
    \     drop py> tib[ntib] py: vm.ntib+=1 \ 撞到停下來的字母非 '(' 即 ')' 要不就是行尾，都可以 skip 過去
    \     char ( = if \ 剛才那個字母是啥？
    \         [ last literal ] dup \ 取得本身
    \         execute \ recurse nested level
    \         execute \ recurse 剩下來的部分
    \     then ; immediate
        
    : round-off // ( f 100 -- f' ) 對 f 取小數點以下 2 位四捨五入
        py> int(pop(1)*tos(0)+0.5)/pop(0) ;
        
    code % push(pop(1)%pop(0)) end-code // ( a b -- a%b ) 
    
    code txt2json # ( txt -- dict ) Convert given string to dictionary
        push(json.loads("".join([ c if c != "'" else '"' for c in pop()])))
        end-code
        
    marker ===

    