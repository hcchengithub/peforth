\ Show the start up greeting

    version drop 
    
\ Drop a fence 

    marker ---
    
\ Run the command line commands
    
    <py> " ".join(sys.argv[1:]) </pyV> tib.insert

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
    vm.outport = outport
    </py>
    