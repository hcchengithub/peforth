import pdb

if __package__:
    # peforth is imported as a package
    from . import projectk as vm
else:    
    # peforth is run from __main__.py
    import projectk as vm

# Let projtct-k know itself
vm.vm = vm

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
vm.panic = panic

# peforth version 
vm.version = float(vm.major_version) + 0.01 # 0.01 is the minor version or build number
def greeting():
    print("p e f o r t h    v" + str(vm.version));
    print("source code http://github.com/hcchengithub/peforth");
    if __package__:
        print("Type 'peforth.ok()' enters forth interpreter, 'exit' to come back.");
    print()
    return vm.version;
vm.greeting = greeting

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
    
# Run once
if not vm.tick('version'): 
    vm.dictate(readTextFile(path+'peforth.f'))
    vm.dictate(readTextFile(path+'quit.f'))
    
# The peforth interpreter user interface. 
# This function was named main() that might be clearer of what it is to you. 
# We can put an ok() anywhere in python code as a breakpoint so we can investigate 
# that point with all the power peforth provides. That's why I rename main() to ok() 
# because it invokes the OK prompt of Forth interpreter.
def ok(prompt='OK ',loc={}):
    vm.push(('Prompt is',prompt,'Local identifiers at the point this ok() was called, if given.',loc))
    print(prompt,end='')
    while True:
        cmd = ""                                     # 
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
vm.ok = ok

if __name__ == '__main__':
    ok(loc=locals())
