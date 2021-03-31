'''

peforth - an eforth ported to python

peforth provides a FORTH virtual machine alongside Python, iPython,
and Jupyter notebook for you to work in FORTH way. This is good for
debugging,  studying,  or  even  participating  to  your developing.
Because  FORTH  is a programming language of flexibility that makes
jobs easier in many ways.

Call peforth.ok() to enter the interpret state and you star talking
interactively in FORTH, 'exit' command to return to python prompt.

peforth.dictate('command string') handles FORTH command line(s).

This cascaded line :

    peforth.push(12).push(34).dictate('+ . cr')

actually prints the sum of 12 + 34.

Visit https://github.com/hcchengithub/peforth/wiki for more information.

May the FORTH be with you!
H.C. Chen @ FigTaiwan 2018.7.3

'''

import sys,os,site,pdb

if __package__:
    # peforth is imported as a package
    from . import projectk as vm
else:
    # peforth is run from test.py when developping
    import projectk as vm

# Let projtct-k know itself
vm.vm = vm

# Get command line, as is
vm.commandline = " ".join(sys.argv[1:])

# panic() when something wrong
def panic(msg,serious=False):
    # defined in __init__.py
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

# Get the path of data files is really frustrating.
# The below method is the only ugly way I have so far:
deli = '\\' if os.name == 'nt' else '/'
for path in sys.path:
    if os.path.isfile(path + deli + 'peforth' + deli + 'version.txt'):
        # for the pip'ed package
        path = path + deli + 'peforth' + deli
        break
    if os.path.isfile(path + deli + 'version.txt'):
        # for running "python test.py" without pip install from source directory when developping
        path = path + deli
        break
vm.path = path

# Get version code from peforth/version.txt for whl package
# to see the single source of version code.
exec(readTextFile(path + "version.txt"),{},locals())
vm.version = __version__
def greeting():
    print("p e f o r t h    v" + str(vm.version));
    print("source code http://github.com/hcchengithub/peforth");
    print("Type 'peforth.ok()' to enter forth interpreter, 'exit' to come back.\n");
    return vm.version;
vm.greeting = greeting

# Master switch to break ok() and return to python interpreter
vm.exit = False

def ok(prompt='OK ', loc={}, glo={}, cmd=""):
    '''
    Invoke the peforth interpreter that can be used as a breakpoint. New and better breakpoint pattern :
    if peforth.execute('debug').pop() : peforth.push(locals()).ok("bp>",cmd='to _locals_');
    However, old pattern is still available : peforth.ok(prompt='OK ', loc=locals(), glo=globals(), cmd="")
    The prompt indicates which breakpoint it is if there are many. Arguments loc (locals) and glo (globals)
    along with the prompt are the debuggee's informations that is packed as a tuple (loc,glo,prompt) left
    on TOS of the FORTH vm when ok() is called with loc or glo. Replace locals() with dict(locals())
    to get a snapshot copy instead of a reference. 'exit' command to stop debugging.
    '''
    if loc or glo: vm.push((loc,glo,prompt))  # parent's data
    while True:
        vm.prompt = prompt  # 13:58 2020/10/16 dialog needs to know it to show the prompt before the text input box. In the loop because shell level can be multiple.
        if not vm.compiling and not vm.multiple: print(prompt, end="")  # [X] 07:49 2020/10/04 KsanaVM reveals my mistaken about prompt now fixed
        if cmd == "":                                    #
            if vm.tick('accept') and not vm.multiple:    # Input can be single line (default) or
                cmd = vm.dictate('accept').pop().strip()
            elif vm.tick('<accept>') and vm.multiple:    # before the last <Enter> key to end the
                vm.execute('<accept>')                   # input when in multiple-line mode.
                cmd = vm.pop().strip()                   #
            else:                                        #
                cmd = input("").strip()                  #

        # pass the command line to forth VM
        if cmd == "":
            continue
        elif cmd == chr(4):
            vm.multiple = not vm.multiple
        else:
            vm.dictate(cmd)
            if vm.multiple: vm.multiple = False # switch back to the normal mode
        cmd = ""
        # Master switch vm.exit is a flag of boolean. When it's True
        # then exit to the caller that usually is python interpreter.
        if vm.exit:
            vm.exit = False # Avoid exit immediately when called again
            break
    return(vm) # support function cascade
vm.ok = ok  # invoke REPL from within REPL, I don't know if we need this.

# Aliases that make it easier to access project-k methods and properties
# So we can use peforth.dictate(), peforth.execute(), and peforth.push() directly
# instead of peforth.vm.dictate(), peforth.vm.execute(), and peforth.vm.push().
dictate     = vm.dictate
execute     = vm.execute
push        = vm.push
dictionary  = vm.dictionary
ntib        = vm.ntib
pop         = vm.pop
reset       = vm.reset
rpop        = vm.rpop
rstack      = vm.rstack
rtos        = vm.rtos
stack       = vm.stack
tib         = vm.tib
tos         = vm.tos
words       = vm.words

##### Setup peforth magic command %f and %%f for ipython and jupyter notebook #####

# How to tell if ipython magic is available?
#     pdb.set_trace() works fine here even when run from jupyter notebook
#     if 'get_ipython' in globals():  <--- always false
#     if '__IPYTHON__' in dir(__builtins__):  <--- always false
#     if '__IPYTHON__' in __builtins__.keys(): <--- previous way, not suitable for ipython -m peforth
#     if 'IPython' in sys.modules.keys(): <--- a candidate never tried
try:
    is_ipython = "InteractiveShell" in str(get_ipython)
except:
    is_ipython = False

if is_ipython:
    from IPython.core.magic import register_line_cell_magic

    # Define peforth magic command, %f.
    @register_line_cell_magic
    def f(line, cell=None):
        '''
        peforth magic command %f can be used both as a line and cell magic in
        iPython and Jupyter notebooks.

        A %f leading line is interpreted as a FORTH command line. You can even
        use it as a python statement:

            def hi():
                %f ." Hello World!!" cr

        give it a try then run hi() to see it works.

        A %%f leading line starts a multiple-line block in iPython or grabs
        the entire cell in Jupyter notebook of FORTH code. The rest of the %%f
        line is ignored like a comment line. %%f must be the first none-white-
        space token in the block or the cell.

        '''
        if cell is None:
            vm.dictate(line)
        else:
            vm.dictate(cell)

    # Register auto '%load_ext peforth' at an ipython session
    def load_ipython_extension(ipython):
        ipython.register_magic_function(f, 'line_cell')
        # see http://ipython.readthedocs.io/en/stable/api/generated/IPython.core.interactiveshell.html?highlight=register_magic_function

# Load high level source code
if not vm.tick('version'):  # defined in peforth.f, run only once.
    vm.dictate(readTextFile(path+'peforth.f'))
    vm.dictate(readTextFile(path+'quit.f'))

##### End of peforth __init__.py #####

