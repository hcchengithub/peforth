
    marker === // ( -- ) Marker before misc.f, forget misc.f and all following definitions.

    : (pyclude) // ( "pathname.py" -- "code" ) Prepare the .py file into a <PY>..</PY> section ready to run
                readTextFile py> re.sub("#__peforth__","",pop()) 
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
                CR word (pyclude) dictate ; 
                ' (pyclude) :> comment last :: comment=pop(1)

                <selftest> 
                *** (pyclude) pyclude run ~.py file 
                    display-off 
                    py> path char hello.py + (pyclude) dictate    \ compose the pathname
                    display-on
                    screen-buffer <py> pop()[0].find('Hello peforth!!')!=-1 </pyV> ( True )
                    [d True d] [p '(pyclude)', 'pyclude' p]
                </selftest>

    : .members  // ( obj -- ) See the object details through inspect.getmembers(obj)
                py> inspect.getmembers(pop()) cr (see) cr ;
                /// Also (see) .source
                    
    : .source   // ( function -- ) See source code through inspect.getsource(func)
                py> inspect.getsource(pop()) cr . cr ;
                /// Also .members (see)
                /// py: dis.dis(pop()) \ sees pseudo code of a function at TOS.

                <selftest>
                *** .members .source
                    display-off
                    ' + .members
                    py> genxt .source
                    display-on
                    screen-buffer <py> pop()[0].find('"name": "+"')!=-1 </pyV> ( True )
                    screen-buffer <py> pop()[0].find('__doc__ = source')!=-1 </pyV> ( True )
                    [d True,True d]
                    [p '.members','.source' p]
                </selftest>

    : sign      // ( n -- sign ) sign of n which is 1 or -1 
                ?dup if dup abs ( n abs(n) ) / int else 1 then ;
				\ 用 copysign() 好但是我至今沒有 import math 因此還是自己兜。
				\ https://stackoverflow.com/questions/1986152/why-doesnt-python-have-a-sign-function
				\ copysign() usage: math :> copysign(1,pop()) int
				
                <selftest>
                *** sign gets the + or - of the given number to 1 or -1 
                    0.000001 sign ( 1 )
                    -0.003 sign   ( -1 )
                    0 sign        ( 1 )
                    [d 1, -1, 1 d] [p 'sign' p]
                </selftest>



    : round-off // ( f 100 -- f' ) Round at 0.00 in this example, 0.005 --> 0.01, 0.00499 --> 0.0
                over sign ( f 100 sign )
                py> int(abs(pop(2))*tos(1)+0.500000000001)/pop(1) * ;
                /// numpy.round(n,decimal) is better where decimal=0 means integer
        
                <selftest>
                *** round-off
                    1.005 100 round-off ( 1.01 )
                    1.00499 100 round-off ( 1.0 )
                    [d 1.01, 1.0 d] [p 'round-off' p]
                </selftest>
        
    code txt2json # ( txt -- dict ) Convert given string to dictionary
                push(json.loads("".join([ c if c != "'" else '"' for c in pop()])))
                end-code

                <selftest>
                *** txt2json
                    s' {"a":1,"b":2}' txt2json
                    [d {'a': 1, 'b': 2} d] [p 'txt2json' p]
                </selftest>

\
\ For Windows only (not, say, Ubuntu)
\
py> os.name char nt = [if]

    : dos       // ( <command line> -- errorlevel ) Shell to DOS Box run rest of the line
                CR word ( cml ) trim ( cml' )
                ?dup if py> os.system(pop())
                else py> os.system('cmd/k') then ;
                /// See also WshShell 
                
                <selftest>
                *** dos shell to DOSbox or run DOS command
                    display-off
                    dos exit /b 567
                    display-on
                    [d 567 d]
                    [p 'dos' p]
                </selftest>
[then]

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






