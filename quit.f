    
\ My misc tools 

    <text>
    \ 
    \ WshShell - users may not install win32 packages so only a clue here
    \ 
    py:~ import win32com.client; push(win32com.client)
    constant win32com.client // ( -- module )
    win32com.client :> Dispatch("WScript.Shell") constant WshShell // ( -- obj )
        /// Windows display off power saving mode:
        /// WshShell :: run("c:\Windows\System32\scrnsave.scr") 
        /// WshShell :> run("__main__.py",5,True) \ True to wait for errorlevel
        /// WshShell ::~ run("cmd /k __main__.py",5,True) \ Stay in the DOSBox
        /// WshShell :: SendKeys("abc")
        /// WshShell :: AppActivate("python.exe")
    </text> constant WshShell // ( -- "clue" ) Guide how to use WshShell

    <py>
        def outport(loc): 
            '''
            # The input argument is supposed locals() of the caller.
            # Make all local variables forth constants
            # Examine locals after a <Py>...</Py> section 
            # For studying maching learning, tersorflow, ... etc. 
            '''
            for i in loc: 
                push(loc[i]) # vale
                push(i) # variable name
                execute('(constant)')
                last().type='value'
        vm.outport = outport
    </py>

    : inport    ( dict -- ) // Make all pairs in dict peforth values. 
                py: outport(pop()) ; 
                /// Example: investigate the root application
                /// ( locals() when calling ok() ) :> [0] inport 
                
    : OK ;      // ( -- ) Do nothing, ignore it when copy-paste the display
    
    : dir       ( x -- dir ) // get dir list of anything x                
                py> dir(pop()) ;
                
    : keys      ( x -- keys ) // get keys of the dict
                py> pop().keys() ;

\ Drop a fence 

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
    
    

    