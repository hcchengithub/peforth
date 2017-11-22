import itchat
from itchat.content import * # TEXT PICTURE 等 constant 的定義

import peforth

# Inhibit 'bye' command, it terminates DOSBox session immediately 
# and leaves 'bye' in msg!
peforth.ok(cmd=": bye .' Bye does nothing.' cr ; exit")  

# Send message to friend or chatroom depends on the given 'send'
# function. It can be itchat.send or msg.user.send up to the caller.
def send_chunk(text, send, pcs=2000):
    s = text
    while True:
        if len(s)>pcs:
            print(s[:pcs]); send(s[:pcs])
        else:
            print(s); send(s)
            break
        s = s[pcs:]    

# Console is like a robot that listens and talks.
# Used in chating with friends and in a chatroom.
def console(msg,cmd):
    # cmd = msg.Text.strip()
    if cmd:
        print(cmd)
        peforth.vm.dictate("display-off")
        try:
            peforth.vm.dictate(cmd)
        except Exception as err:
            errmsg = "Failed! : {}".format(err)
            peforth.vm.dictate("display-on")
            send_chunk(errmsg, msg.user.send)
        else:
            peforth.vm.dictate("display-on screen-buffer")
            screen = peforth.vm.pop()[0]
            send_chunk(screen, msg.user.send)
        send_chunk("OK", msg.user.send)

@itchat.msg_register(TEXT)
def _(msg):
    if peforth.vm.debug==99: peforth.ok('99> ',loc=locals(),cmd=":> [0] inport cr")  # breakpoint    
    console(msg, msg.Text.strip())

@itchat.msg_register([MAP, CARD, NOTE, SHARING])
def _(msg):
    if peforth.vm.debug==11: peforth.ok('11> ',loc=locals(),cmd=":> [0] inport cr")  # breakpoint    
    send_chunk('%s: %s' % (msg.type, msg.text), msg.user.send)
    
@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def _(msg):
    if peforth.vm.debug==22: peforth.ok('22> ',loc=locals(),cmd=":> [0] inport cr")  # breakpoint    
    msg.download(msg.fileName)
    typeSymbol = {
        PICTURE: 'img',
        VIDEO: 'vid', }.get(msg.type, 'fil')
    return '@%s@%s' % (typeSymbol, msg.fileName)

@itchat.msg_register(FRIENDS)
def _(msg):
    if peforth.vm.debug==33: peforth.ok('33> ',loc=locals(),cmd=":> [0] inport cr")  # breakpoint    
    msg.user.verify()
    send_chunk('Nice to meet you!', msg.user.send)

@itchat.msg_register(TEXT, isGroupChat=True)
def _(msg):
    if peforth.vm.debug==44: peforth.ok('44> ',loc=locals(),cmd=":> [0] inport cr")  # breakpoint    
    if msg.isAt: 
        cmd = msg.text.split(maxsplit=1)[1] # remove the leading @nickName
        console(msg, cmd)

# peforth.vm.debug=99
itchat.auto_login(True)  # hotReload=True
itchat.run(False, blockThread=True) # debug=True 
peforth.ok('itChat> ',loc=locals(),cmd=":> [0] inport cr")  # breakpoint    

