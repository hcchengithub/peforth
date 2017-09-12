\ Show the start up greeting

    version drop 
    
\ My misc tools 

    <py>
    def outport(loc): 
        # The input argument is supposed locals() of the caller.
        # Make all local variables forth constants
        # Examine locals after a <Py>...</Py> section 
        # For studying maching learning, tersorflow, ... etc.
        for i in loc: 
            push(loc[i]) # vale
            push(i) # variable name
            execute('(constant)')
            last().type='value'
    vm.outport = outport
    </py>

    : OK ; // Do nothing, 方便 copy-paste 螢幕重跑
    
    : dir   ( x -- dir ) // get dir list of anything x                
        py> dir(pop()) ;

    : keys  ( x -- keys ) // get keys of the dict
        py> pop().keys() ;

\ Drop a fence before running the rest of the command line

    marker ---
    
\ Run the command line commands
    
    <py> " ".join(sys.argv[1:]) </pyV> tib.insert

    