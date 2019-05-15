
    \
    \ Redefine unknown to try global variables in __main__ 
    \
    
    none value _locals_ // ( -- dict ) locals passed down from ok()
    false value debug // ( -- flag ) enable/disable the ok() breakpoint

    : unknown ( token -- thing Y|N) // Try to find the unknown token in __main__ or _locals_
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
      /// 'exit' to leave the breakpoint and forget locals.

    : exit ( -- ) // ( -- ) Exit the breakpoint forget locals and continue the process
      none to _locals_ py: vm.exit=True ;  

    code # print(nexttoken('\n')+'\n') end-code // print the comment line after #  

    : --> ( result -- ) // Print the result with the command line.
      py> tib[:ntib].rfind("\n") py> tib[max(pop(),0):ntib].strip() ( result cmd-line )
      s" {} {} ({})" :> format(pop(),tos(),type(pop())) . cr ;
      /// Good for experiments that need to show command line and the result.





