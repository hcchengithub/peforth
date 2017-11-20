import peforth
import itchat
from itchat.content import * # TEXT PICTURE 等 constant 的定義
    # Failed in compyle command : import * only allowed at module level 
    # 因此本程式適合用 .py 直接執行
@itchat.msg_register(TEXT)
def console(msg):
    cmd = msg.Text.strip()
    print(cmd)
    peforth.vm.dictate("display-off")
    if cmd:
        peforth.vm.dictate(cmd)
        peforth.vm.dictate("display-on screen-buffer")
        screen = peforth.vm.pop()[0]
        print(screen); msg.user.send(screen)
    print("OK"); msg.user.send("OK")
    if peforth.vm.debug: peforth.ok('console> ',cmd="cr")
    
# def _(msg):
#     peforth.ok('TEXT> ',loc=locals(),cmd=':> [0] inport cr')
#     msg.user.send('%s: %s' % (msg.type, msg.text))

@itchat.msg_register([MAP, CARD, NOTE, SHARING])
def _(msg):
    peforth.ok('notGroupChat> ',loc=locals(),cmd=':> [0] inport cr')
    msg.user.send('%s: %s' % (msg.type, msg.text))
    
@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def _(msg):
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
    peforth.ok('isGrupChat> ',loc=locals(),cmd=':> [0] inport cr')
    # if msg.isAt:
    msg.user.send(u'@%s\u2005I received: %s' % (
        msg.actualNickName, msg.text))

itchat.auto_login(False)  # hotReload=True
itchat.run(True, blockThread=True) # debug=True 
peforth.ok('itChat> ')

'''

def console(msg):
    cmd = msg.Text.strip()
    peforth.vm.dictate("display-off")
    if cmd:
        print(cmd)
        peforth.vm.dictate(cmd)
        peforth.vm.dictate("display-on screen-buffer")
        screen = pop()[0]
        print(screen)
        msg.user.send(screen)

'''