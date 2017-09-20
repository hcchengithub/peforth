\ Show the start up greeting

    version drop 
    
\ My misc tools 

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
    
    ' <selftest> :: enabled=False \ Assume command line has jobs to do
    <py> " ".join(sys.argv[1:]) </pyV> trim ( commandLine ) 
    ?dup [if] 
        \ Run the command line commands
        tib.insert
    [else] 
        \ No command line, do selftest.
        py: tick('<selftest>').enabled=True
        py> tick('<selftest>').buffer tib.insert
    [then] py: tick('<selftest>').buffer="" \ release the memory

    
    

    