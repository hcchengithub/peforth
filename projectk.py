
# 
# project-k Forth kernel in python
# Use the same kernel code for all applications.
# FigTaiwan H.C. Chen hcchen5600@gmail.com 21:14 2017-07-31
#

import re    # import whatever we want, don't rely on parent module
import pdb

name = "peforth"
vm = __import__(__name__)
major_version = 1;  # major version, peforth.py kernel version.
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
    rstack = [];
    compiling = False;
    ip = 0;  # forth VM instruction pointer
    stop = True; 
    ntib = len(tib);  # don't clear tib, a clue for debug.

    
# panic() calls out to vm.panic()
# The panic() function gets only message and severity level. 
# Kernel has no idea how to handle these information so it checks if vm.panic() exists
# and pass the {msg,serious}, or even more info, over that's all. That's why vm.panic() has to
# receive a hash structure, because it must be.
def panic(msg,serious=False):
    # defined in project-k kernel peforth.py
    print("\n{}".format(msg))
    c = input("Debug? [y/N] ")
    if c in ['y', 'Y']:
        pdb.set_trace()
        
# Forth words are instances of Word() constructor.
class Word:
    def __init__(self, name, xt):
        self.name = name
        self.xt = xt
        self.immediate = False
        self.help = "( ?? ) No help message. Use // to add one."
        self.comment = ""
    def __str__(self):    # return help message
        return self.name + " " + self.help + ' __str__'
    def __repr__(self):   # execute xt and return help message
        return self.name
    
# Support Vocabulary
def last():  # returns the last defined word.
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
    if deli == '\\s': 
        tib = tib[:ntib] + tib[ntib:].lstrip() # skip all leading white spaces
        # [ ] 這地方考慮 ntib+1 避免把應有的 space 也殺掉了
    # deli=\n should skip to EOL but don't skip next token after the EOL!
    elif deli in ['\\n','\n','\\r','\r','\\n|\\r','\n|\r','\\r|\\n', '\r|\n']: 
        if tib[ntib] not in ['\n','\r']:
            ntib += 1 # ok skip the next character
    else: 
        ntib += 1  # skip next character
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
        elif callable(entry) or type(entry)==Word: # function or Word
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
    if type(w)==int:
        # Usually a number is the entry of does>. Can't use inner() to call it 
        # The below push-jump mimics the call instruction of a CPU.
        rstack.append(ip);  # Forth ip is the "next" instruction to be executed. Push return address.
        ip = w;  # jump
    elif callable(w) :  # a function
        w();
    elif type(w)==Word: # Word object
        try:  # take care of errors to avoid being kicked out
            w.xt(w);
        except Exception as err:
            panic(err)
    else:
        panic("Error! don't know how to execute : "+w+" ("+type(w)+")\n","error");
        
# execute("unknown") == do nothing, this is beneficial when executing a future word
# May be redefined for selftest to detect private words called by name.
# vm.execute keeps the original version.
def execute(entry):
    # defined in proejct-k peforth.py
    w = phaseA(entry)
    if w:
        if type(w) in [int, float]:
            panic("Error! please use inner("+w+") instead of execute("+w+").\n","severe");
        else:
            phaseB(w); 

def inner(entry, resuming=None):
    # defined in project-k kernel peforth.py
    global ip
    w = phaseA(entry);
    while True: 
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

# -------------------------- the outer loop ----------------------------------------------------
# forth outer loop, 
# If entry is given then resume from the entry point by executing 
# the remaining colon thread down until ip reaches 0. That's resume.
# Then proceed with the tib/ntib string.
# 
def outer(entry=None):
    # Handle one token. 
    def outerExecute(token):
        w = tick(token);  # not found is 0. w is an Word object.
        if (w) :
            if(not compiling): # interpret state or immediate words
                if getattr(w,'compileonly',False):
                    panic(
                        "Error! "+token+" is compile-only.", 
                        len(tib)-ntib>100  # error or warning? depends
                    ); 
                    return;
                execute(w);
            else:  # compile state
                if (w.immediate) :
                    execute(w);  # Not inner(w);
                else:
                    if getattr(w,'interpretonly',False):
                        panic(
                            "Error! "+token+" is interpret-only.", 
                            len(tib)-ntib>100  # error or warning? depends
                        );
                        return;
                    comma(w);  # compile w into dictionary. w is a Word() object
        else:
            try:
                # token is a number, int or float
                n = eval(token) + 0 # triggers exception if token is not a number
                push(n)
                if (compiling):
                    execute("literal");
            except:
                panic(
                    "Error! "+token+" unknown.", 
                    len(tib)-ntib>100  # error or warning? depends
                );
    if (entry):
        inner(entry, True);  # resume from the breakpoint 
    while(not stop):
        token = nexttoken();
        if (token==""):
            break;  # TIB done, loop exit.
        outerExecute(token);
    ### End of the outer loop ###
    
# code ( -- ) Start to compose a code word. docode() is its run-time.
# "( ... )" and " \ ..." on first line will be brought into word.help attribute.
# peforth.py kernel has only two words, 'code' and 'end-code', peforth.f
# will be read from a file that will be a big TIB actually. So we don't 
# need to consider about how to get user input from keyboard.
def genxt(name, body):
    ll = {}
    source = "def xt(_me=None): ### {} ###"
    # _me will be the code word object itself.
    if body.strip()=="":
        source = (source+"\n    pass\n").format(name)
    else:
        source = (source+'\n{}').format(
            name,
            "".join("{}\n".format(line)
            # An ending \n makes # comment at end of body safe
            for line in body.splitlines()))
    try:
        exec(source,globals(),ll)
    except Exception as err:
        panic("Failed to compose {} : {}\nBody:\n{}".format(name, err, body))
        
    ll['xt'].source = source  # keep source code [ ] is this redundent?
    ll['xt'].name = name 
    return ll['xt']

# forth 'code' definition        
def docode(_me=None):
    # [ ] check if this is true for python, it is for javascript
    # All future code words can see local variables in here, so don't use
    # any local variable. They can *see* variables & functions out side 
    # this function too, that's normal.
    global compiling, newname, newxt, newhelp, ntib
    newname = nexttoken();
    if isReDef(newname): # don't use tick(newname), it's wrong.
        panic("reDef "+newname);
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

# forth 'end-code' definition    
def doendcode(_me=None):
    global compiling
    if compiling!="code":
        panic("Error! 'end-code' a none code word.")
    current_word_list().append(Word(newname,newxt))
    last().vid = current;
    last().wid = len(current_word_list())-1;
    last().type = 'code';
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
# words[current] = [
#     0,  # Letting current_word_list()[0] == 0 has many advantages. When tick('name') 
#         # returns a 0, current_word_list()[0] is 0 too, indicates a not-found.
#     code,
#     endcode
#     ];
words[current] = [0,code,endcode]
    
# Use the best of JavaScript to find a word.
wordhash = {"code":current_word_list()[1], "end-code":current_word_list()[2]};
    
# -------------------- main() ----------------------------------------
# Recursively evaluate the input. The input can be multiple lines or 
# an entire ~.f file yet it usually is the TIB.
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

# Stack access easier. e.g. pop(1) gets tos(1) and leaves ( tos(2) tos(1) tos(void|0) -- tos(2) tos(void|0) )
# push(formula(pop(i)),i-1) manipulate the tos(i) directly, usually when i is the index of a loop.
def pop(index=None):
    if index==None:
        return stack.pop();
    else:
        return stack.pop(len(stack)-1-index);

# Stack access easier. e.g. push(data,1) inserts data to tos(1), ( tos2 tos1 tos -- tos2 tos1 data tos )
# push(formula(pop(i)),i-1) manipulate the tos(i) directly, usually when i is the index of a loop.
def push(data=None, index=None):
    global stack
    if data==None: 
        panic(" push() what?");
    elif index==None:
        stack.append(data); 
    else:
        stack.insert(len(stack)-1-index,data);
