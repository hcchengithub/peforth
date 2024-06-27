
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

\
\ Ported from forth.py 
\

	\ 23:45 2024/06/21 DevTools.py 加上 forth.py 是客製化 peforth 的方法，不用動到 peforth 本身, 只要在
	\ 用場上當地動手即可。 但今天 peforth v1.31 有了新 magic %ai 以及 %chat for Jupyter notebook, 更希望
	\ 單 import peforth 就可以，不用跑一大段 code (DevTools.py 的前半部)。 以下的 definitions moved from
	\ {Jupyter}\\forth.py 成功後那邊就可以少一點了。
	
    \ Timer -- the "with Timer():" block -----------------------------------------------------------
        <py>
            from time import time

            class Timer():
                """
                %%time equivalent Context manager -- the "with Timer():" block
                Learned from https://www.codingame.com/playgrounds/500/advanced-python-features
                Usage : with Timer('This job costs {} ms'): ...
                Where the argument of description can be omitted and use default 'Wall time: ... ms'.
                """
                def __init__(self, message=None):
                    self.message = message

                def __enter__(self):
                    self.start = time()
                    return None  # could return anything, to be used like this: with Timer("Message") as value:

                def __exit__(self, type, value, traceback):
                    elapsed_time = (time() - self.start) * 1000
                    if self.message:
                        print(self.message.format(elapsed_time))
                    else:
                        print("Wall time: {} ms".format(elapsed_time))
            push(Timer)
        </py> constant Timer // ( -- class ) %%time magic equivalent "with" block. Usage: with Timer('This job costs {} ms'): ...
                             /// Learned from https://www.codingame.com/playgrounds/500/advanced-python-features
                             /// Usage :
                             /// 	Timer = peforth.dictate('Timer').pop()
                             /// 	with Timer('This job costs {} ms'): ...
                             /// Arg omitted use default 'Wall time: ... ms'.

    \ Converter .py to .ipynb ----------------------------------------------------------------------

        : py2ipynb ( pathname -- ) // Create converted foo.py.ipynb from given foo.py
            dup readTextFile ( pathname file.py )
            py> json.encoder.JSONEncoder().encode(pop()) ( pathname file.py.json )
            ( before ) <text> {"cells":[{"cell_type":"code","execution_count":null,"metadata":{"collapsed":false},"outputs":[],"source":[</text>
            swap +
            ( after ) <text> ]}],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"codemirror_mode":{"name":"ipython","version":3},"file_extension":".py","mimetype":"text/x-python","name":"python","nbconvert_exporter":"python","pygments_lexer":"ipython3","version":"3.4.2"}},"nbformat":4,"nbformat_minor":0}</text>
            + ( pathname packed )
            swap char .ipynb + writeTextFile ;
            /// Usage:
            ///   char c:\Users\username\foo.py py2ipynb
            /// Result:
            ///   Created new file c:\Users\username\foo.py.ipynb
            /// 16:10 2018-01-12 https://www.webucator.com/blog/2015/07/bulk-convert-python-files-to-ipython-notebook-files-py-to-ipynb-conversion/

    \ Clear output box when in *debug* prompt ------------------------------------------------------
    
        \ https://stackoverflow.com/questions/24816237/ipython-notebook-clear-cell-output-in-code
        : clear // ( -- ) Clear output of this cell in Jupyternotebook
            py: IPython.display.clear_output() ;

    \ Magics %ai and %chat for Jupyter notebook ----------------------------------------------------
    
        none value @llm // ( -- llm ) Word llm ( prompt -- complete ) does the AI's job.
        none value @get_ipython // ( -- func ) Jupyter Notebook get_ipython() function.
            /// get_ipython().execution_count is the current cell number.
        import datetime
        "" value chat_history // ( -- str ) ChatBot history. 
            /// Using a string instead of an array makes editing more convenient.
        : check_llm_get_ipython // ( -- ) Check for the existence of llm and get_ipython.
            @llm none != ( flagLLM )
            @get_ipython type str <py> "method" in pop()</pyV> ( " flagGet_ipython )
            and if else
                [ last literal ] :> comment . cr abort
            then ;
            /// Peforth offers AI capabilities, such as %ai and %chat, for Jupyter notebooks.
            /// To enable the AI magics, all you need to prepare are:
            ///   %f llm constant llm_object
            ///   %f : llm_wrapper trim llm_object :> invoke(pop()).content ;
            ///   %f ' llm_wrapper to @llm
            ///   %f get_ipython to @get_ipython    
            /// Now either @llm or @get_ipython is not given, which is why you see this message.
            ///
            /// Explanation:
            /// When you provide a Forth word, like llm_wrapper, to peforth, it assigns the value @llm:
            ///   %f ' llm_wrapper to @llm
            /// The definition of llm_wrapper may look like this:
            ///   %f llm constant llm_object \ 'llm' is obtained from columbus.get_llm_for_LangChain()
            ///   %f : llm_wrapper ( "prompt" -- "completion" ) trim llm_object :> invoke(pop()).content ;
            /// Additionally, you provide the "get_ipython" function from your Jupyter notebook environment 
            /// to peforth:
            ///   %f get_ipython to @get_ipython

        : timestamp ( -- str ) \ ChatBot timestamp with the recent cell number
            py> "\n\nChat#" @get_ipython py> pop()().execution_count str + (space) +
            <py> datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")</pyV> + ;
        : ai: // ( <prompt> -- "AIMessage" ) Prompt to AI w/o history but add the answer to history.
            check_llm_get_ipython
            s" **User:** " char _uSeR_ word trim ( "User: " USERMessage )
            dup @llm execute trim ( "User: " USERMessage AIMessage )
            py> "\n" s" **Assistant:** " + swap ( "User: " USERMessage "Assistant: " AIMessage )
            timestamp + dup . cr cr ( "User: " USERMessage "Assistant: " AIMessage_timestamp )
            + py> "\n" swap + + + py> "\n---===---\n" + chat_history swap + to chat_history
            ;
        : chat: // ( <prompt> -- "AIMessage" ) Talk to AI with history.
            check_llm_get_ipython
            s" **User:** " char _uSeR_ word trim ( "User: " USERMessage )
            chat_history ( "User: " USERMessage history ) over + ( "User: " USERMessage history+USERMessage ) 
            @llm execute trim ( "User: " USERMessage AIMessage )
            py> "\n" s" **Assistant:** " + swap ( "User: " USERMessage "Assistant: " AIMessage )
            timestamp + dup . cr cr ( "User: " USERMessage "Assistant: " AIMessage_timestamp )
            + py> "\n" swap + + + py> "\n---===---\n" + chat_history swap + to chat_history
            ;

    \ ----------------------------------------------------------------------------------------------------------------------
	




