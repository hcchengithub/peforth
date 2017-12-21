import sys
import itchat
from itchat.content import * # TEXT PICTURE 等 constant 的定義
import peforth

import time
import random
nextDelay = 3  # Initial anti-robot sleep time.
nextDelay_msg = "Initial anti-robot delay time: %i seconds\n" % (nextDelay)
# Anti-Robot delay time , thanks to Rainy's great idea.
# Sleep <nextDelay> seconds and then return a string to indicate 
# the next delay time in seconds.
def antiRobotSleep():
    global nextDelay, nextDelay_msg
    time.sleep(nextDelay)  # Anti-Robot delay 
    nextDelay = random.choice(range(3,18))    
    nextDelay_msg = 'Next anti-robot delay time: %i seconds\n' % (nextDelay)
    return nextDelay_msg

# Inhibit 'bye' command, it terminates DOSBox session immediately 
# and leaves 'bye' in msg! Only a re-login can resolve it. To avoid this,
# itchat's event decorators must return instead of doing the 'bye' command 
# directly or the last msg object will keep the last 'bye' command that
# blocks all following activities.
peforth.ok(loc=locals(),cmd='''
    :> [0] constant main.locals // ( -- dict ) main locals
    none value console.locals // ( -- dict ) console() locals 
    py> sys.modules['itchat'] constant itchat // ( -- module ) WeChat automation
    : bye itchat :: logout() bye ; 
    exit
    ''')  

# Send message to friend or chatroom depends on the given 'send'
# function. It can be itchat.send or msg.user.send up to the caller.
# WeChat text message has a limit at about 2000 utf-8 characters so
# we need to split a bigger string into chunks.
def send_chunk(text, send, pcs=2000):
    s = text
    while True:
        if len(s)>pcs:
            print(s[:pcs]); send(s[:pcs])
        else:
            print(s); send(s)
            break
        s = s[pcs:]    

# Console is a peforth robot that listens and talks.
# Used in chatting with friends and in a chatroom.
def console(msg,cmd):
    if cmd:
        print(cmd)  # already on the remote side, don't need to echo 
        if peforth.vm.debug==11: peforth.ok('11> ',loc=locals(),cmd=":> [0] constant loc11 cr")  # breakpoint    
        # re-direct the display to peforth screen-buffer
        peforth.vm.dictate("display-off")  
        try:
            peforth.vm.push((locals(),globals(),'console prompt'))
            peforth.vm.dictate(":> [0] to console.locals " + cmd)
            # peforth.ok('OK ', loc=locals(),
            #     cmd=":> [0] to console.locals " + cmd + "\n exit")
        except Exception as err:
            errmsg = "Failed! : {}\n".format(err)
            peforth.vm.dictate("display-on")
            send_chunk(errmsg + nextDelay_msg, msg.user.send)
        else:
            peforth.vm.dictate("display-on screen-buffer")
            screen = peforth.vm.pop()[0]
            send_chunk(screen + nextDelay_msg, msg.user.send)

@itchat.msg_register([ATTACHMENT,PICTURE], isGroupChat=True)
def _(msg):
    if peforth.vm.debug==33: peforth.ok('33> ',loc=locals(),cmd=":> [0] constant loc33 cr")  # breakpoint    
    if msg.user.NickName[:5]=='AILAB': # 只在 AILAB 工作，過濾掉其他的。
        anti_robot_msg = antiRobotSleep()
        msg.download('download\\' + msg.fileName)
        send_chunk('Attachment: %s \nreceived at %s\n' % (msg.fileName,time.ctime()) + anti_robot_msg, msg.user.send)

@itchat.msg_register(TEXT, isGroupChat=True)
def _(msg):
    if peforth.vm.debug==44: peforth.ok('44> ',loc=locals(),cmd=":> [0] constant loc44 cr")  # breakpoint    
    if msg.user.NickName[:5]=='AILAB': # 只在 AILAB 工作，過濾掉其他的。
        if msg.isAt: 
            time.sleep(nextDelay)  # Anti-Robot delay 
            cmd = (msg.text+"\n").split("\n",maxsplit=1)[1] # remove the first line: @nickName ...
            console(msg, cmd)                               # 避免帶有空格的 nickName 惹問題
    
itchat.auto_login(hotReload=False)
itchat.run(debug=False, blockThread=True)
peforth.ok('Examine> ',loc=locals(),cmd=':> [0] value locals')

'''

# --------------- Playground ---------------------------------------------------
# Setup the playground for testing without itchat (avoid the need to login)

def msg():
    pass
def _():
    pass
msg.user = _    
msg.user.send = print
msg.user.NickName = 'A believer'    
msg.isAt = True
def _():
    print('msg.user.verify() ... pass')
msg.user.verify = _
msg.fileName = 'pathname.dmy'
msg.type = 'fil' # also 'img'(image), 'vid'(video)
def _(fileName):
    print('Downloaded %s from WeChat cloud' % fileName)
msg.download = _
msg.text = "Message text from the WeChat cloud"
msg.Text = msg.text

\ Demo-1 

    \ 讓 UUT 回覆它的畫面經由 itchat bot 傳給 AILAB Chatroom
    \ 讓遠端可以來監看執行狀況。這段程式是由遠端灌過來給 UUT 的。
    @版主 This line will be ignored 
    \ get itchat module object
    py> sys.modules['itchat'] constant itchat // ( -- module ) WeChat automation
    \ get PIL graph tool
    import PIL.ImageGrab constant im // ( -- module ) PIL.ImageGrab
    \ get AILAB chatroom object through partial nickName 
    itchat :> search_chatrooms('AILAB')[0] constant ailab // ( -- obj ) AILAB chatroom object
    \ Define check command that checks the UUT desktop screenshot
    import time constant time // ( -- module )
    cr time :> ctime() . cr \ print recent time on UUT when making this setting
    : check ( -- ) // check UUT
        time :: sleep(7) \ anti-robot delay time be always 7 seconds
        cr time :> ctime() . cr \ print the recent time on UUT 
        im :: grab().save("1.jpg") \ capture screenshot 
        ailab :> send("@img@1.jpg") \ send to AILAB chatroom 
        . cr \ shows the responsed message
        ;
    \ Define getfile command in case source code were modified on the UUT
    : getfile ( "pathname" -- ) // Get source code for debugging
        time :: sleep(7) py> str(pop()).strip() \ trim pathname 
        s" @fil@" swap + \ command string 
        cr time :> ctime() . space s" getfile: " . dup . cr
        ailab :> send(pop()) \ send to AILAB chatroom so everybody gets it
        . cr \ shows the responsed message
        ;

\ ---------- My Original Demo ----------------------------------------------

\ It shows how to handle variant events from itchat

import itchat
from itchat.content import * # TEXT PICTURE 等 constant 的定義

import peforth

# Inhibit 'bye' command, it terminates DOSBox session immediately 
# and leaves 'bye' in msg! Only a re-login can resolve it. To avoid this,
# decorator must return instead of doing the 'bye' command directly.
peforth.ok(loc=locals(),cmd=":> [0] constant locals : bye locals :> ['itchat'].logout() ; exit")  

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
peforth.ok()  # breakpoint    

\ --------- end of My Original Demo -------------------------------------------

'''
