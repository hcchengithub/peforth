
\ Imports 

	\ peforth imports only native packages, so far 
	import os      	
	import inspect 	
	import dis     	
	import json    	

\ Includes
\   include foo.f          \ in the current directory 
\   include ..\foo\bar.f   \ in the specified directory

    py> path char peforth.selftest + sinclude   \ compose the pathname
    py> path char misc.f + sinclude     		\ compose the pathname

\ Do selftest or run command-line

    ' <selftest> :: enabled=False \ Master switch of selftest, True:on or False:off

    py> vm.commandline trim ( commandLine ) ?dup [if] 
        \ When in ipython or jupyter notebook the command line is used by 
        \ ipython already. In jupyter notebook, it looks like:
        \
        \      vm.commandline ----------------------------------------------------------------------------------.
        \      sys.argv[0]    --------.                                                                         |
        \                             |                                                                         |
        \                             V                                                                         V
        \     --------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------
        \     c:\users\hcche\appdata\local\programs\python\python36\lib\site-packages\ipykernel_launcher.py -f C:\Users\hcche\AppData\Roaming\jupyter\runtime\kernel-4be53345-1ddd-47c2-bef2-5e9801688f3f.json
        \ So peforth can't support command line statements for ipython and jupyter notebook. 
        \ For none ipython cases, I have no better idea than to check sys.argv[0] for '.py' 
        \ and the likes so far 2019-05-15. See the following code, the filename 'test.py' is 
        \ fixed-coded here therefore.
        \
        <py> sys.argv[0].endswith(('.py','.ipy','.ipynb')) and not sys.argv[0].endswith(('test.py')) </pyV> [if] 
            \ ignore if running in jupyter notebook or the likes is suspected
            drop
        [else]
            \ Run the command line commands
            tib.insert
        [then]
    [else]
        \ No command line, show greeting and run selftest
        version drop 
        ' <selftest> :> enabled [if]
            marker ###  // ( -- ) Marker before self-test 
            ' <selftest> :> buffer tib.insert
            ###         \ Clean up 
        [then]
    [then] py: tick('<selftest>').buffer="" \ release the memory



