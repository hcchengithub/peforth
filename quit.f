    
\ My misc tools 

    \
    \ Redirect print() to screen-buffer 
    \

        py> [""] value screen-buffer // ( -- ['string'] ) Selftest screen buffer
                                     /// Enveloped in array is for "access by reference"
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
                def flush(self):
                    # self.buffer[0]=''
                    pass
            vm.Screenbuffer=Screenbuffer
        </py>
        \ # Start redirection
        \ sys.stdout=Screenbuffer(vm.forth['screen-buffer'])
        \ 
        \ # Print to screen when redirected
        \ sys.stdout.stdoutwas.write("-------1111-----\n")
        \ sys.stdout.stdoutwas.write("-------2222-----\n")
        \ 
        \ # view screen buffer
        \ sys.stdout.view()
        \ 
        \ # reset
        \ sys.stdout.reset()

    : display-off ( -- ) // Redirect stdout to a empty screen-buffer
        py: sys.stdout=Screenbuffer(vm.forth['screen-buffer']) 
        screen-buffer :: [0]="" ;

    : display-on ( -- ) // Redirect stdout back to what it was. screen-buffer has data during it off.
        py: sys.stdout.reset() ;


    <text>
    \ 
    \ WshShell - users may not install win32 packages yet so only a clue here
    \ Run "WshShell dictate" to vitalize this word
    \ 
    py:~ import win32com.client; push(win32com.client)
    constant win32com.client // ( -- module )
    win32com.client :> Dispatch("WScript.Shell") constant WshShell // ( -- obj ) The "Windows Script Host" object https://technet.microsoft.com/en-us/library/ee156607.aspx
        /// WshShell :: run("c:\Windows\System32\scrnsave.scr") \ Windows display off power saving mode
        /// WshShell :: SendKeys("abc")
        /// WshShell :: AppActivate("python.exe")
        /// WshShell ::~ run("python -i -m peforth WshShell dictate cls version drop dos title child peforth")
    </text> constant WshShell // ( -- "clue" ) Guide how to use WshShell

    <py>
        def outport(loc): 
            '''
            # Make all local variables forth constants.
            # The input argument is supposed locals() of the caller.
            # Examine locals after a <Py>...</Py> section 
            # For studying maching learning, tersorflow, ... etc. 
            # Usage: outport(locals())
            '''
            for i in loc: 
                push(loc[i]) # vale
                push(i) # variable name
                execute('(constant)')
                last().type='value.outport'
        vm.outport = outport
    </py>

    : inport    ( dict -- ) // Make all pairs in dict peforth values. 
                py: outport(pop()) ; 
                /// Example: investigate the root application
                /// ok(loc=locals(),glo=globals(),cmd=':> [0] inport')
                
    <py>
        def harry_port(loc={}):
            '''
            # Note! Don't use this technique in any compiled snippet, but run by exec() 
            # instead. This function returns a dict of all FORTH values with type of 
            # "value.outport". Refer to 1) FORTH word 'inport' which converts a dict, a 
            # snapshot of locals(), at TOS to FORTH values, and 2) python function 
            # outport() which converts the given locals() to FORTH values. The two are 
            # similar. While harry_port() does the reverse, it brings FORTH values, that 
            # were outported from a locals(), back to python locals().             
            # Usage: 
            #   1. exec("x = sess.run(myXX); print(x)", harry_port())
            #   2. locals().update(harry_port()) # in code executed by exec()
            '''
            ws = [w.name for w in words[context][1:] if 'outport' in w.type]
            for i in ws:
                loc.update({i:v(i)})
            return loc 
        vm.harry_port = harry_port    
    </py>
                
    : harry_port py> harry_port.__doc__ -indent . cr ; // ( -- ) Print help message
                
    : OK ;      // ( -- ) Do nothing, ignore it when copy-paste the display
    
    : dir       ( x -- dir ) // get dir list of anything x                
                py> dir(pop()) ;
                
    : keys      ( x -- keys ) // get keys of the dict
                py> pop().keys() ;
                
    : (pyclude) ( <pathname.py> -- "code" ) // Prepare the .py file into a <PY>..</PY> section ready to run
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
                
    : pyclude   ( <pathname.py> -- ... ) // Run the .py file in a <PY>..</PY> space
                (pyclude) dictate ; 
                ' (pyclude) :> comment last :: comment=pop(1)

    : .members  ( obj -- ) // See the object details through inspect.getmembers(obj)
                py> inspect.getmembers(pop()) cr (see) cr ;
                /// Also (see) .source
                    
    : .source   ( function -- ) // See source code through inspect.getsource(func)
                py> inspect.getsource(pop()) cr . cr ;
                /// Also .members (see)

    : dos       ( <command line> -- errorlevel ) // Shell to DOS Box run rest of the line
                CR word ( cml ) trim ( cml' )
                ?dup if py> os.system(pop())
                else py> os.system('cmd/k') then ;
                /// See also WshShell 
                
    : cd            ( <path> -- ) // Mimic DOS cd command
                CR word ?dup if py: os.chdir(pop())
                else py> os.getcwd() . cr then ;
                /// Use 'dos' command can do the same thing.
                /// Ex. 'dos dir', 'dos cd', and all other dos commands.
                /// But 'dos cd ..' does not work while 'cd ..' works fine.
                /// See also: os.chdir('path'); path=os.getcwd()

                
\ Drop a fence before selftest

    marker ---

\ Do selftest or run command-line
    
    ' <selftest> :: enabled=True \ Master switch of selftest, True:on or False:off

    py> vm.commandline trim ( commandLine ) 
    ?dup [if] 
        \ Run the command line commands
        tib.insert
    [else] 
        \ No command line, show greeting and run selftest
        version drop 
        ' <selftest> :> enabled [if]
            ' <selftest> :> buffer tib.insert
        [then]
    [then] py: tick('<selftest>').buffer="" \ release the memory
    
    

    