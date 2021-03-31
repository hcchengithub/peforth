
# 
# project-k Forth kernel in python
# Use the same kernel code for all applications.
# FigTaiwan H.C. Chen hcchen5600@gmail.com 21:14 2017-07-31
#

import re, sys

name = "peforth"
vm = __import__(__name__)
major_version = 1;  # major version, peforth.py kernel version, integer.
ip = 0;
stack = [] ;
rstack = [];
vocs = [];
words = {};
current = "forth";
context = "forth";
order = [context];
wordhash = {};
dictionary = []; 
dictionary.append(0);
here = 1;  # dictionary[0] is 0
tib = "";
ntib = 0;
RET = None;    # The 'ret' instruction code. It marks the end of a colon word.
EXIT = "";     # The 'exit' instruction code.
compiling = False;
stop = False;  # Stop the outer loop
newname = "";  # new word's name
newxt = None
newhelp = "";
    
# Reset the forth VM
def reset():
    # defined in project-k kernel peforth.py
    global rstack, compiling, ip, stop, ntip
    # rstack = []; this creates extra error when return from the inner loop
    compiling = False;
    ip = 0;  # forth VM instruction pointer
    stop = True; 
    ntib = len(tib);  # don't clear tib, a clue for debug.
        
# All peforth words are instances of this Word() constructor.
class Word:
    def __init__(self, name, xt):
        self.name = name
        self.xt = xt
        self.immediate = False
        self.help = ""
        self.comment = ""
    def __str__(self):    # return help message
        return self.name + " " + self.help + ' __str__'
    def __repr__(self):   # execute xt and return help message
        return "<Word '{}'>".format(self.name)
        
# returns the last defined word.
def last():  
    return words[current][-1]

    
# Get the word-list where new defined words are going to
def current_word_list():
    return words[current]

    
# Get the word-list that is searched first.
def context_word_list():
    return words[context]

    
# Get string from recent ntib down to, but not including, the next delimiter.
# Return result={str:"string", flag:boolean}
# If delimiter is not found then return the entire remaining TIB, multiple-lines, 
# through result.str, purpose is to maximum the severity.
# result.flag indicates delimiter found or not found.
# o  If you want to read the entire line in TIB, use nexttoken('\n|\r'). 
#    nexttoken() skip the next character which is usually white space in Forth source code, 
#    e.g. s", this is reasonable because it's Forth. While the leading white space(s) 
#    will be included if useing the lower level nextstring('\\s') instead of nexttoken().
# o  If you need to know whether the delimiter is found, use nextstring()。
# o  result.str is "" if TIB has nothing left.
# o  The ending delimiter is remained. 
# o  The delimiter is a regular expression.
def nextstring(deli):
    # search for delimiter in tib from ntib
    # index = tib[ntib:].find(deli) does not support regular expression, no good
    global ntib
    result = {}
    try:
        index = re.search(deli, tib[ntib:]).start()  # start() triggers exception when not found
        # see https://stackoverflow.com/questions/2674391/python-locating-the-position-of-a-regex-match-in-a-string
        result['str'] = tib[ntib:ntib+index];  # found, index is the length
        result['flag'] = True;
        ntib += index;  # Now ntib points at the delimiter.
    except Exception:
        result['str'] = tib[ntib:] # get the tib from ntib to EOL
        result['flag'] = False;
        ntib = len(tib) # skip to EOL
    return result;

    
# Get next token which is found after the recent ntib of TIB.
# If delimiter is RegEx white-space ('\\s') or absent then skip all leading white spaces first.
# Usual case, skip the next character which should be a white space for Forth.
# But if delimiter is CRLF, which is to read the entire line, for blank lines the ending CRLF won't be skipped.
# o  Return "" if TIB has nothing left. 
# o  Return the remaining TIB if delimiter is not found.
# o  The ending delimiter is remained. 
# o  The delimiter is a regular expression.
def nexttoken(deli='\\s'):
    global tib, ntib
    if ntib >= len(tib): return ""
    if deli == '\\s': 
        # skip all leading white spaces
        while tib[ntib] in [" ","\t","\n","\r"]:
            if (ntib+1) < len(tib):
                ntib += 1
            else:
                break
    elif deli in ['\\n','\n','\\r','\r','\\n|\\r','\n|\r','\\r|\\n', '\r|\n']: 
        # skip the next character that must be whitespace
        if tib[ntib] not in ['\n','\r']:
            # But don't skip the EOL itself!
            ntib += 1 
    else: 
        # skip next character that must be whitespace
        ntib += 1  
    token = nextstring(deli)['str'];
    return token; 

    
# tick() is same thing as forth word '。 
# Letting words[voc][0]=0 also means tick() return 0 indicates "not found".
# Return the word obj of the given name or 0 if the word is not found.
# May be redefined for selftest to detect private words referenced by name. 
# vm.tick keeps the original version.
def tick(name):
    # defined in project-k peforth.py
    if name in wordhash.keys():
        return wordhash[name]
    else: 
        return 0  # name not found
    
# Return a boolean.
# Is the new word reDef depends on only the words[current] word-list, not all 
# word-lists, nor the word-hash table. Can't use tick() because tick() searches 
# the word-hash that includes not only the words[current] word-list.
def isReDef(name):
    result = False;
    wordlist = current_word_list();
    for i in range(1,len(wordlist)):  # skip [0] which is 0
        if wordlist[i].name == name :
            result = True;
            break;
    return result;

    
# comma(x) compiles anything into dictionary[here]. x can be number, string, 
# function, object, array .. etc。
# To compile a word, comma(tick('word-name'))
def comma(x):
    global dictionary, here
    try: 
        dictionary[here], here = x , here + 1
    except:
        dictionary.append(x) 
        here += 1
    # dummy RET
    try: 
        dictionary[here] = RET
    except:
        dictionary.append(RET) 
    # [here] will be overwritten, we do this dummy because 
    # RET is the ending mark for 'see' to know where to stop. 
    
'''    
    Discussions:
    
    'address' or 'ip' are index of dictionary[] array. dictionary[] is the memory of the
    Forth virtual machine.
    
    execute() executes a function, a word "name", and a word Object.  
    
    inner(entry) jumps into the entry address. The TOS of return stack can be 0, in that
    case the control will return back to python host, or the return address.
    
    inner() used in outer(), and colon word's xt() while execute() is used everywhere.
    
    We have 3 ways to call forth words from Python: 1. execute('word'), 
    2. dictate('word word word'), and 3. inner(cfa). 
    
    dictate() cycles are stand alone tasks. We can suspend an in-completed dictate() and we
    can also run another dictate() within a dictate().
    
    The ultimate inner loop is like this: while(w){ip++; w.xt(); w=dictionary[ip]}; 
    Boolean(w) == False is the break condition. So I choose None to be the RET instruction
    and the empty string "" to be the EXIT instruction. Choices are None, "", [], {}, False, 
    and 0. While 0 neas 'suspend' the inner loop. 
    
    To suspend the Forth virtual machine means to stop inner loop but not pop the 
    return stack, resume is possible because return stack remained. We need an instruction 
    to do this and it's 0. dictionary[0] and words[<vid>][0] are always 0 thus ip=w=0 
    indicates that case. Calling inner loop from outer loop needs to push(0) first so 
    as to balance the return stack also letting the 0 instruction to stop popping the
    return stack because there's no more return address, it's outer interpreter remember? 
'''
# -------------------- ###### The inner loop ###### -------------------------------------

# Translate all possible entry or input to the suitable word type.
def phaseA (entry):
        global ip
        w = 0; 
        if type(entry)==str: 
            # "string" is word name
            w = tick(entry.strip());  # remove leading and tailing white spaces
        elif (type(entry)==Word or callable(entry)) : # function, Word
            w = entry; 
        elif type(entry)==int: 
            # number could be dictionary entry or 0. 
            # could be does> branch entry or popped from return stack by RET or EXIT instruction.
            ip = entry;
            w = dictionary[ip]; 
        else:
            panic("Error! execute() doesn't know how to handle this thing : "+entry+" ("+type(entry)+")\n","err");
        return w;


# Execute the given w by the correct method 
def phaseB(w):
    global ip, rstack
    if type(w)==Word: # Word object
        try:
            w.xt(w)
        except Exception as err:
            panic("Word in phaseB {}: {}\nBody:\n{}".format(repr(w),err,w.xt.__doc__))
    elif callable(w) :  # a function
        try:
            w();
        except Exception as err:
            panic("Callable in phaseB {}: {}\nBody:\n{}".format(repr(w),err,w.__doc__))
    elif str(type(w))=="<class 'code'>": # code object
        exec(w)
    elif type(w)==int:
        # Usually a number is the entry of does>. Can't use inner() to call it 
        # The below push-jump mimics the call instruction of a CPU.
        rstack.append(ip);  # Forth ip is the "next" instruction to be executed. Push return address.
        ip = w;  # jump
    else:
        panic("Error! don't know how to execute : "+w+" ("+type(w)+")\n");
        
# execute("unknown") == do nothing, this is beneficial when executing a future word
# May be redefined for selftest to detect private words called by name.
# vm.execute keeps the original version.
def execute(entry):
    # defined in proejct-k peforth.py
    w = phaseA(entry)
    if w:
        if type(w) in [int, float]:
            panic("Error! please use inner("+w+") instead of execute("+w+").\n");
        else:
            phaseB(w); 
            return(vm) # support function cascade
    else:
        panic(entry + " unknown!")

# FORTH inner loop of project-k VM
def inner(entry, resuming=None):
    # defined in project-k kernel peforth.py
    global ip
    w = phaseA(entry);
    while not stop: 
        while w:      # this is the very inner loop
            ip += 1   # Forth general rule. IP points to the *next* word. 
            phaseB(w) # execute it
            w = dictionary[ip]  # get next word
        if (w==0): 
            break;  # w==0 is suspend, break inner loop but reserve rstack.
        else: 
            ip = rstack.pop();  # w is either ret(None) or exit(""), return to caller, or 0 when resuming through outer(entry)
        if(resuming):
            w = dictionary[ip]; # Higher level of inner()'s have been terminated by suspend, do their job.
        if not (ip and resuming): 
            break  # Resuming inner loop. ip==0 means resuming has done。
    ### End of the inner loop ###

# FORTH outer loop of project-k VM
# If entry is given then resume from the entry point by executing 
# the remaining colon thread down until ip reaches 0, that's resume.
# Then proceed with the tib/ntib string.
def outer(entry=None):
    # Handle one token. 
    def outerExecute(token):
        w = tick(token);  # not found is 0. w is an Word object.
        if (w) :
            if(not compiling): # interpret state or immediate words
                if getattr(w,'compileonly',False):
                    panic("Error! "+token+" is compile-only."); 
                    return;
                execute(w);
            else:  # compile state
                if (w.immediate) :
                    execute(w);  # Not inner(w);
                else:
                    if getattr(w,'interpretonly',False):
                        panic("Error! "+token+" is interpret-only.");
                        return;
                    comma(w);  # compile w into dictionary. w is a Word() object
        else:
            # token is unknown or number
            # This line: f = float(token) makes problems try-except can not catch
            def is_number(s):
                # https://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-float
                try:
                    complex(s) # for int, float and complex
                except ValueError:
                    return False
                return True            
            n = None  # 
            if is_number(token):
                # token is (int, float, complex) we ignore complex so far
                f = complex(token).real
                i = int(f)
                if i==f: 
                    n = i
                else:
                    n = f
            else: 
                # token is unknown or (hex, oct, binary)
                def panic_unknown():
                    panic("Error! "+token+" unknown.\n");
                try:
                    # token is a number
                    if token[:2] in ["0x","0X"]:
                        n = int(token,base=16)
                    elif token[:2] in ["0o","0O"]:
                        n = int(token,base=8)
                    elif token[:2] in ["0b","0B"]:
                        n = int(token,base=2)
                    else:
                        if not push(token).execute("unknown").pop():
                            panic_unknown()
                except Exception as err:
                        if not push(token).execute("unknown").pop():
                            panic_unknown()
            if n != None :
                push(n)
                if (compiling):
                    execute("literal");
    if (entry):
        inner(entry, True);  # resume from the breakpoint 
    while(not stop):
        token = nexttoken();
        if (token==""):
            break;  # TIB done, loop exit.
        outerExecute(token);
    ### End of the outer loop ###


# Generates the .xt() function of all code words.
# Python does not support annonymous function so we use genxt() instead.
# _me argument refers to the word object itself, if you need to access
# any attribute of the word. 
# xt.__doc__ keeps the source code.
# py: help(genxt) to read me.
def genxt(name, body):
    ll = {}
    # _me will be the code word object itself.
    source = "def xt(_me=None): ### {} ###"
    if tick('-indent') and tick('indent'):
        # Beautify source code if -indent and indent are defined
        push(body);execute('-indent');execute('indent')
        body = pop()
    if body.strip()=="":
        source = (source+"\n    pass\n").format(name)
    else:
        source = (source+'\n{}').format(name,body)
    try:
        exec(source,globals(),ll)
    except Exception as err:
        panic("Failed in genxt({},Body) : {}\nBody:\n{}".format(name, err, body))
        
    ll['xt'].__doc__ = source
    ll['xt'].name = name 
    return ll['xt']


# Python does not support annoymous function, this can be recovered by 
# using closure. genfunc("body","args","name") returns a function which 
# is composed by the given function name, source code and arguments.
# <name>.__doc__ keeps the source code.
# py: help(genfunc) to read me.
def genfunc(body,args,name):
    local = {}
    source = "def {}({}):".format(name,args)
    # args can be "", or 'x, y=123,z=None' 
    if body.strip()=="":
        source = source+"\n    pass\n";
    else:
        source = (source+'\n{}').format(body)
    exec(source,globals(),local)
    local[name].__doc__ = source
    return local[name]


# The basic FORTH word 'code's run time. 
def docode(_me=None):
    # All future code words can see local variables in here, for jeforth.3we.
    # [x] check if this is true for python, <== Not True for Python.
    global compiling, newname, newxt, newhelp, ntib
    newname = nexttoken();
    if isReDef(newname): # don't use tick(newname), it's wrong.
        print("reDef " + newname);
    # get code body
    push(nextstring("end-code")); 
    if tos()['flag']:
        compiling = "code";  # it's true and a clue of compiling a code word.
        newxt = genxt(newname, pop()['str'])
    else:
        panic("Error! expecting 'end-code'.");
        reset();

code = Word('code', docode)
code.vid  = 'forth'
code.wid  = 1
code.type = 'code'
code.help = '( <name> -- ) Start composing a code word.'

# The basic FORTH word 'end-code's run time. 
def doendcode(_me=None):
    global compiling
    if compiling!="code":
        panic("Error! 'end-code' a none code word.")
    current_word_list().append(Word(newname,newxt))
    last().vid = current;
    last().wid = len(current_word_list())-1;
    last().type = 'code';
    # ---------
    mm = re.match(r"^.*?#\s*(.*)$", last().xt.__doc__.split('\n')[1])
    last().help = mm.groups()[0] if mm and mm.groups()[0] else ""
    # ---------
    wordhash[last().name] = last();
    compiling = False; 

endcode = Word('end-code', doendcode)
endcode.vid  = 'forth'
endcode.wid  = 2
endcode.type = 'code'
endcode.immediate = True
endcode.compileonly = True
endcode.help = '( -- ) Wrap up the new code word.'

# forth master word-list
# Letting current_word_list()[0] == 0 has many advantages. When tick('name') 
# returns a 0, current_word_list()[0] is 0 too, indicates a not-found.
words[current] = [0,code,endcode]
    
# Find a word as soon as possible.
wordhash = {"code":current_word_list()[1], "end-code":current_word_list()[2]};
    
# Command interface to the project-k VM. 
# The input can be multiple lines or an entire ~.f file.
# Yet it usually is the TIB (Terminal input buffer).
def dictate(input):
    global tib, ntib, ip, stop
    tibwas  = tib
    ntibwas = ntib
    ipwas   = ip
    tib = input; 
    ntib = 0;
    stop = False; # stop outer loop
    outer();
    tib = tibwas;
    ntib = ntibwas;
    ip = ipwas;
    return(vm) # support function cascade
# -------------------- end of main() -----------------------------------------

# Top of Stack access easier. ( tos(2) tos(1) tos(void|0) -- ditto )
# tos(i,new) returns tos(i) and by the way change tos(i) to new value this is good
# for counting up or down in a loop.
def tos(index=None,value=None):
    global stack
    if index==None:
        return stack[-1]
    elif value==None: 
        return stack[len(stack)-1-index];
    else: 
        data = stack[len(stack)-1-index];
        stack[len(stack)-1-index] = value; 
        return(data); 

# Top of return Stack access easier. ( rtos(2) rtos(1) rtos(void|0) -- ditto )
# rtos(i,new) returns rtos(i) and by the way change rtos(i) to new value this is good
# for counting up or down in a loop.
def rtos(index=None,value=None):
    global rstack
    if index==None:
        return rstack[-1]
    elif value==None: 
        return rstack[len(rstack)-1-index];
    else: 
        data = rstack[len(rstack)-1-index];
        rstack[len(rstack)-1-index] = value; 
        return(data); 
        
# rstack access easier. e.g. rpop(1) gets rtos(1) 
# ( rtos(2) rtos(1) rtos(0) -- rtos(2) rtos(0) )
# push(formula(rpop(i)),i-1) manipulates the rtos(i) directly, usually when i is the index 
# of a loop.
def rpop(index=None):
    if index==None:
        return rstack.pop();
    else:
        return rstack.pop(len(rstack)-1-index);

# Stack access easier. e.g. pop(1) gets tos(1) ( tos(2) tos(1) tos(0) -- tos(2) tos(0) )
# push(formula(pop(i)),i-1) manipulate the tos(i) directly, when i is the index of a loop.
def pop(index=None):
    if index==None:
        try:
            return stack.pop();
        except Exception as err:
            print(err);
            return None;
    else:
        return stack.pop(len(stack)-1-index);

# Stack access easier. e.g. push(data,1) inserts data to tos(1), 
# ( tos2 tos1 tos -- tos2 tos1 data tos )
# push(formula(pop(i)),i-1) manipulate the tos(i) directly, usually when i 
# is the index of a loop.
def push(data=None, index=None):
    global stack
    if index==None:
        stack.append(data); 
    else:
        stack.insert(len(stack)-1-index,data);
    return(vm) # support function cascade

# ---- end of projectk.py ----