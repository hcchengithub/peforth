import peforth
import itchat
from itchat.content import * # TEXT PICTURE 等 constant 的定義

@itchat.msg_register(TEXT)
def console(msg):
    cmd = msg.Text.strip()
    print(cmd)
    if cmd:
        peforth.vm.dictate("display-off")
        try:
            peforth.vm.dictate(cmd)
        except Exception as err:
            errmsg = "Failed! : {}".format(err)
            peforth.vm.dictate("display-on")
            print(errmsg); msg.user.send(errmsg)
        else:
            peforth.vm.dictate("display-on screen-buffer")
            screen = peforth.vm.pop()[0]
            print(screen); msg.user.send(screen)
    print("OK"); msg.user.send("OK")
    if peforth.vm.debug: peforth.ok('console> ',cmd="cr")  # breakpoint

@itchat.msg_register([MAP, CARD, NOTE, SHARING])
def _(msg):
    if peforth.vm.debug: peforth.ok('[MAP,CARD,NOTE,SHARING]>',cmd="cr")  # breakpoint
    msg.user.send('%s: %s' % (msg.type, msg.text))
    
@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def _(msg):
    if peforth.vm.debug: peforth.ok('[PICTURE,RECORDING,ATTACHMENT,VIDEO]>',cmd="cr")  # breakpoint
    msg.download(msg.fileName)
    typeSymbol = {
        PICTURE: 'img',
        VIDEO: 'vid', }.get(msg.type, 'fil')
    return '@%s@%s' % (typeSymbol, msg.fileName)

@itchat.msg_register(FRIENDS)
def _(msg):
    msg.user.verify()
    msg.user.send('Nice to meet you!')

@itchat.msg_register(TEXT, isGroupChat=True)
def _(msg):
    if msg.isAt:
        def print_piece(str, pcs=2000):
            i = 0; s = str
            while True:
                if len(s)>2000:
                    print(s[:2000]); msg.user.send(s[:2000])
                else:
                    print(s); msg.user.send(s)
                    break
                s = s[2000:]    
                
                
            
        cmd = msg.Text.strip()
        print(cmd)
        if cmd:
            peforth.vm.dictate("display-off")
            try:
                peforth.vm.dictate(cmd)
            except Exception as err:
                errmsg = "Failed! : {}".format(err)
                peforth.vm.dictate("display-on")
                print(errmsg); msg.user.send(errmsg)
            else:
                peforth.vm.dictate("display-on screen-buffer")
                screen = peforth.vm.pop()[0]
                # 不能太大，要切小塊
                print(screen); msg.user.send(screen)
                
        print("OK"); msg.user.send("OK")
        if peforth.vm.debug: peforth.ok('console> ',cmd="cr")  # breakpoint
        

itchat.auto_login(False)  # hotReload=True
itchat.run(True, blockThread=True) # debug=True 
peforth.ok('itChat> ',cmd="cr")  # breakpoint

