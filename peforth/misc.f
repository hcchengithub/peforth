
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
    \ Redefine unknown try to find global variables in __main__ 
    \                          and local variables in _locals_
    \
    
    none value _locals_ // ( -- dict ) locals passed down from ok()
    false value debug // ( -- flag ) enable/disable the ok() breakpoint
	' unknown :: name='unknown_deactivated'
    : unknown   // ( token -- thing Y|N) Try to find the unknown token in __main__ or _locals_
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
                /// 'quit' to leave the breakpoint and forget locals.
                /// 'exit' to leave the breakpoint w/o forget locals.

    : quit      // ( -- ) Quit the breakpoint forget _locals_ and continue the process
                none to _locals_ py: vm.exit=True ;  
                /// 'exit' also quit the breakpoint but it won't forget _locals_ 

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

*debug* 33> 

<comment>
import IPython
: paste 		py> IPython.lib.clipboard.win32_clipboard_get() tib.insert ;
				// ( ... -- ... ) 執行 clipboard 裡的內容，jupyternotebook 進了 peforth prompt 特別需要此功能。
: path-to-find-modules ( <path> -- ) // Add path to sys.path so "import module-name" can find the module
				CR word trim ( "path" ) py: sys.path.append(pop()) ;

( 預設有這麼多 Breakpoint ID ) <py> [i for i in range(100)] </pyV> __main__ :: peforth.bps=pop(1)
__main__ :> peforth <py>
	peforth = pop()
	def bp(id=None,locals=None):
		# Breakpoint ID 不能超過 peforth.bps 保留，超過的無效。
		if id==None: 
			id = 0
			prompt='bp> '
		else:
			prompt="{}>".format(id)
		if id in peforth.bps: peforth.push(locals).ok(prompt, cmd="to _locals_")
	push(bp)
</py> __main__ :: peforth.bp=pop(1)

: bp ." Usage: peforth.bp(11,locals())  # drop a breakpoint with ID=11" cr ;
: bl // ( -- ) List all breakpoints
	__main__ :> peforth.bps 
	<py>
	bps = pop()
	print('Disabled breakpoints:')
	for i in range(len(bps)):
		if not bps[i]: 
			print(i, end=' ')
	print(); print('Enabled breakpoints:')
	count = 0
	for i in range(len(bps)):
		if bps[i]: 
			print(i, end=' ')
			count += 1
	print(); print('Enabled breakpoints count: {}/{}'.format(count,len(bps)))
	</py> cr ;
	/// Breakpoint commands:
	///   bl  - list all breakpoints (capital BL is white space) 
	///   be  - enable breakpoints, e.g. be 1 2 3 
	///   bd  - disable breakpoints, e.g. bd 1 2 3 
	///   be* - enable all breakpoints
	///   bd* - disable all breakpoints 
	/// Also: 
	///   for i in [11,22,33]: peforth.bps[i]=0  # disable breakpoints 11,22,33 
	///   for i in [11,22,33]: peforth.bps[i]=i  # enable  breakpoints 11,22,33 

: bd // ( <1 2 3 4...> -- ) Disable listed breakpoints 
	CR word ( line ) __main__ :> peforth.bps ( line bps )
	<py>
	line, bps = pop(1), pop(0)
	points = map(int, line.split(' '))
	for i in points: bps[i] = 0
	</py> ; 
	' bl :> comment last :: comment=pop(1)

: be // ( <1 2 3 4...> -- ) Enable listed breakpoints 
	CR word ( line ) __main__ :> peforth.bps ( line bps ) 
	<py>
	line, bps = pop(1), pop(0)
	points = map(int, line.split(' '))
	for i in points: bps[i] = i
	</py> ; 
	' bl :> comment last :: comment=pop(1)

: bd* // ( -- ) Disable all breakpoints 
	__main__ :> peforth.bps  ( bps ) 
	<py>
	bps = pop()
	for i in range(len(bps)): bps[i] = 0
	</py> ;
	' bl :> comment last :: comment=pop(1)

: be* // ( -- ) Enable all breakpoints 
	__main__ :> peforth.bps  ( bps ) 
	<py>
	bps = pop()
	for i in range(len(bps)): bps[i] = i
	</py> ;
	' bl :> comment last :: comment=pop(1)
\ ------ xtack ------------------------------------------------------------
[] value xstack xstack py: vm.xstack=pop() // ( -- array ) The xstack. 掛進 vm 就可以直接以 py> xstack 取用。
: x@ xstack :> [-1] ; // ( -- n ) Get TOS of the xstack
: x> xstack :> pop() ; // ( -- n ) Pop the xstack
: >x xstack :: append(pop()) ; // ( n -- ) Push n into the xstack
: .sx xstack . ; // ( -- ) List xstack 
: xdrop x> drop ; // ( X: ... a -- X: ... ) drop xstack 
: xdropall [] to xstack ; // ( X: ... -- X: empty ) clear xstack 
</comment>

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






