
# This jupyternotebook cell imports peforth and add breakpoint feature so as to be able to drop a bp in python code.
import peforth
peforth.bps = [i for i in range(100)]  # 預設有這麼多 Breakpoint ID
def bp(id=None,locals=None):
    # Breakpoint ID 不能超過 peforth.bps 保留，超過的無效。
	if id==None: 
		id = 0
		prompt='bp> '
	else:
		prompt="{}>".format(id)
	if id in peforth.bps: peforth.push(locals).ok(prompt, cmd="to _locals_")
peforth.bp = bp
peforth.push(bp).dictate("py: vm.bp=pop()")  # [ ] 忘了 vm.bp 有何用途？
peforth.dictate('''
    \ -------------- breakpoint ----------------------------------------------    
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
        ///	  bl  - list all breakpoints (capital BL is white space) 
        ///	  be  - enable breakpoints, e.g. be 1 2 3 
        ///	  bd  - disable breakpoints, e.g. bd 1 2 3 
        ///	  be* - enable all breakpoints
        ///	  bd* - disable all breakpoints 
        /// Also: 
        ///   for i in [11,22,33]: peforth.bps[i]=0	 # disable breakpoints 11,22,33 
        ///   for i in [11,22,33]: peforth.bps[i]=i	 # enable  breakpoints 11,22,33 
    
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
        __main__ :> peforth.bps	 ( bps ) 
        <py>
        bps = pop()
        for i in range(len(bps)): bps[i] = 0
        </py> ;
        ' bl :> comment last :: comment=pop(1)
    
    : be* // ( -- ) Enable all breakpoints 
        __main__ :> peforth.bps	 ( bps ) 
        <py>
        bps = pop()
        for i in range(len(bps)): bps[i] = i
        </py> ;
        ' bl :> comment last :: comment=pop(1)
    \ -------------- xtack ----------------------------------------------    
    [] value xstack xstack py: vm.xstack=pop() // ( -- array ) The xstack. 掛進 vm 就可以直接以 py> xstack 取用。
    : x@ xstack :> [-1] ; // ( -- n ) Get TOS of the xstack
    : x> xstack :> pop() ; // ( -- n ) Pop the xstack
    : >x xstack :: append(pop()) ; // ( n -- ) Push n into the xstack
    : .sx xstack . ; // ( -- ) List xstack 
    : xdrop x> drop ; // ( X: ... a -- X: ... ) drop xstack 
    : xdropall [] to xstack ; // ( X: ... -- X: empty ) clear xstack 
    ''')
%f version ==>
