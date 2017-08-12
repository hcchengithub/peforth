a = 111
b = 222
newname = ""
vm = globals()

def genxt(name, body):
    ll = {}
    source = "def xt(_me=None): ### {} ###"
    # _me will be the code word object itself.
    if body.strip()=="":
        source = (source+"\n    pass\n").format(name)
    else:
        source = (source+'\n{}').format(
            name,
            "".join("    {}\n".format(line)
            # An ending \n makes # comment at end of body safe
            for line in body.splitlines()))
    exec(source,globals(),ll)
    ll['xt'].source = source  # keep source code [ ] is this redundent?
    ll['xt'].name = name 
    return ll['xt']

c = '''
global a
b = 2222
a += b
print('a', a)'''
# c = ''
c = "print('abc')"

f = genxt('fff', c)
f()    
print(f.name, "\n"+f.source)
