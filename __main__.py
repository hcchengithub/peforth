import sys
import pdb

if __package__:
    # peforth is imported as a package
    from . import projectk as vm
else:    
    # peforth is run from __main__.py
    import projectk as vm

# Let projtct-k know itself
vm.vm = vm

# Get command line, as is
vm.commandline = " ".join(sys.argv[1:])

# panic() when something wrong
def panic(msg,serious=False):
    # defined in project-k kernel peforth.py
    print("\n{}".format(msg))
    if serious:
        c = input("Continue, Debug, or Abort? [C/d/a] ")
        if c in ['D', 'd']:
            pdb.set_trace()
        elif c in ['A', 'a']:
            vm.reset()
    else:
        vm.reset()
    
vm.panic = panic

# Toggle multiple or single lines by ^D 
vm.multiple = False

def readTextFile(pathname):
    f = open(pathname,'r',encoding='utf-8')
    # for line in f:
    s = f.read()
    f.close()
    return s
vm.readTextFile = readTextFile
    
def writeTextFile(pathname, string):
    f = open(pathname,"wt",encoding='utf-8')
    f.write(string)
    f.close
vm.writeTextFile = writeTextFile    

# Get peforth home path
# On python 3.6 __file__ is either path\\__init__.py or path\\__main__.py 
# Cases are: 
#   '__main__.py' or '__init__.py' when run by "python __main__.py" or the other
#   'peforth\\__main__.py' when run by "python peforth" from ..\peforth 
#   'C:\\...\\peforth\\__main__.py' when double click __main__.py or python -m peforth
#   'C:\\...\\peforth\\__init__.py' when double click __init__.py or import peforth
if __file__.find('__init__.py')==-1:
    # __main__.py
    path = __file__.split('__main__.py')[0]
    path = (path and [path] or ['.\\'])[0]
else:
    # __init__.py
    path = __file__.split('__init__.py')[0]
    path = (path and [path] or ['.\\'])[0]
vm.path = path
    
# Get version code from peforth/version.txt for whl package
# to see the single source of version code.
exec(readTextFile(path + "version.txt"),{},locals())
vm.version = __version__ 
def greeting():
    print("p e f o r t h    v" + str(vm.version));
    print("source code http://github.com/hcchengithub/peforth");
    if __package__:
        print("Type 'peforth.ok()' enters forth interpreter, 'exit' to come back.");
    print()
    return vm.version;
vm.greeting = greeting
    
# Run once
if not vm.tick('version'): 
    vm.dictate(readTextFile(path+'peforth.f'))
    vm.dictate(readTextFile(path+'peforth.selftest'))
    vm.dictate(readTextFile(path+'quit.f'))
    
# Invoke the peforth interpreter or, in another word, shells to peforth.
# Put an ok() anywhere in python code as a breakpoint. The prompt argument
# indicates which breakpoint it is. The loc (locals) argument passes the 
# recent locals as a dictionary to peforth so we can investigate them with 
# all the power of peforth.  
def ok(prompt='OK ',loc={}, cmd=""):
    if loc: vm.push((loc,'<== Identifiers ok() Prompt ==>',prompt))
    if not vm.commandline.strip(): print(prompt,end='')
    while True:
        if cmd == "":                                    # 
            if vm.tick('accept') and not vm.multiple:    # Input can be single line (default) or    
                vm.execute('accept')                     # multiple lines. Press Ctrl-D to toggle
                cmd = vm.pop().strip()                   # between the two modes. Place a Ctrl-D     
            elif vm.tick('accept2') and vm.multiple:     # before the last <Enter> key to end the    
                vm.execute('accept2')                    # input when in multiple-line mode.
                cmd = vm.pop().strip()                   # 
            else:                                        #  
                cmd = input("").strip()                  # 

        # pass the command line to forth VM          
        if cmd == "":
            print(prompt, end="")
            continue
        # elif cmd == "exit": 
        elif 'exit' == cmd.split()[-1]: # 'exit' appears at EOL?
            break # Go back to the caller e.g. python interpreter
        elif cmd == chr(4):
            vm.multiple = not vm.multiple
            if not vm.multiple: print(prompt, end="")
        else:    
            vm.dictate(cmd)
            if vm.multiple: vm.multiple = False # switch back to the normal mode
            print(prompt, end="")
        cmd = ""
vm.ok = ok

if __name__ == '__main__':
    ok(loc=locals(), cmd=":> [0] inport") # for investigating the application root
    # ok()
