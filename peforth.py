import pdb
import projectk as vm

# panic() when something wrong
def panic(msg,serious=True):
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

if not vm.tick('version'): 
    # run from python interpreter only once
    vm.dictate(readTextFile('peforth.f'))
    vm.dictate(readTextFile('quit.f'))
    
# The eforth.py command line interface, the main program loop
def main():
    print('OK ',end='')
    while True:
        cmd = ""                                   # 
        if vm.tick('accept') and not vm.multiple:  # 
            vm.execute('accept')                   # 
            if vm.pop():                           # Input can be single line (default) or 
                cmd = vm.pop().strip()             # multiple lines. Press Ctrl-D to switch
        elif vm.tick('accept2') and vm.multiple:   # to multiple-line mode. Place a Ctrl-D
            vm.execute('accept2')                  # before the last enter to end the input
            if vm.pop():                           # when in multiple-line mode and back to
                cmd = vm.pop().strip()             # single-line mode automatically.
        else:                                      # 
            cmd = input("").strip()                # 
            
        # pass the command line to forth VM    
        if cmd == "":
            print('OK ', end="")
            continue
        elif cmd == "exit": # A backup way to stop the program other than the bye command
            break
        elif cmd == chr(4):
            vm.multiple = not vm.multiple
        else:    
            vm.dictate(cmd)
            print('OK ', end="")

if __name__ == '__main__':
    main()
