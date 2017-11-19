import peforth
import itchat
from itchat.content import * # TEXT PICTURE 等 constant 的定義
    # Failed in compyle command : import * only allowed at module level 
    # 因此本程式適合用 .py 直接執行
@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
    peforth.ok('notGrupChat> ',loc=locals(),cmd=':> [0] inport cr')
    msg.user.send('%s: %s' % (msg.type, msg.text))

@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
    msg.download(msg.fileName)
    typeSymbol = {
        PICTURE: 'img',
        VIDEO: 'vid', }.get(msg.type, 'fil')
    return '@%s@%s' % (typeSymbol, msg.fileName)

@itchat.msg_register(FRIENDS)
def add_friend(msg):
    msg.user.verify()
    msg.user.send('Nice to meet you!')

@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
    peforth.ok('isGrupChat> ',loc=locals(),cmd=':> [0] inport cr')
    if msg.isAt:
        msg.user.send(u'@%s\u2005I received: %s' % (
            msg.actualNickName, msg.text))

itchat.auto_login(False)  # hotReload=True
itchat.run(True, blockThread=False) # debug=True 

peforth.vm.outport(locals()) 
peforth.ok('itchat> ',cmd='cr')

'''
[x] 用 PC client 視訊或語音時，itchat 端就會斷掉。
    itchat.run(True, blockThread=True) 經 blockThread=True 就可以避免
[ ] debug isGroupChat 時，發現 function name 都是 text_reply() 
    decorator 裡好像這個無所謂。
[ ] 不會 echo chatroom 的 message <== bug!
    RI: msg.isAt 是 False !! 所以沒反應。 
    --> 比對普通 chat 與 GroupChat 的 msg ...... 
    isGroupChat> msg . cr
        {'MsgId': '1422233572015927974',
        'FromUserName': '@@26536008f1c1307c892640411bf7f60ffd2a3feb138ed6591e65e4fe7541708e',
        'ToUserName': '@9f15931b5d2a9ea59d4c5e220e079c5574b036939a4300c985ae83094d0b8250',
        'MsgType': 1,
        'Content': '22',
        'Status': 3,
        'ImgStatus': 1,
        'CreateTime': 1511086807,
        'VoiceLength': 0,
        'PlayLength': 0,
        'FileName': '',
        'FileSize': '',
        'MediaId': '',
        'Url': '',
        'AppMsgType': 0,
        'StatusNotifyCode': 0,
        'StatusNotifyUserName': '',
        'RecommendInfo': {'UserName': '',
            'NickName': '',
            'QQNum': 0,
            'Province': '',
            'City': '',
            'Content': '',
            'Signature': '',
            'Alias': '',
            'Scene': 0,
            'VerifyFlag': 0,
            'AttrStatus': 0,
            'Sex': 0,
            'Ticket': '',
            'OpCode': 0},
        'ForwardFlag': 0,
        'AppInfo': {'AppID': '',
            'Type': 0},
        'HasProductId': 0,
        'Ticket': '',
        'ImgHeight': 0,
        'ImgWidth': 0,
        'SubMsgType': 0,
        'NewMsgId': 1422233572015927974,
        'OriContent': '',
        'ActualNickName': 'hcchen5600',  <---- isGroupChat only 
        'IsAt': False,                   <----- isGroupChat only
        'ActualUserName':                <----- isGroupChat only
            '@102dffe8deaaa7160fae7db1214b0bf69285399c0e94bbb35bb5457cde76b001',
        'User': 
            <Chatroom:                   <----- isGroupChat only 
                {'MemberList': 
                    <ContactList: 
                        [
                            <ChatroomMember: {'MemberList': <ContactList: []>,
                                'Uin': 0,
                                'UserName': '@9f15931b5d2a9ea59d4c5e220e079c5574b036939a4300c985ae83094d0b8250',
                                'NickName': '網路分享小寶貝',
                                'AttrStatus': 33558565,
                                'PYInitial': '',
                                'PYQuanPin': '',
                                'RemarkPYInitial': '',
                                'RemarkPYQuanPin': '',
                                'MemberStatus': 0,
                                'DisplayName': '',
                                'KeyWord': ''}
                            >,
                            <ChatroomMember: {'MemberList': <ContactList: []>,
                                'Uin': 0,
                                'UserName': '@102dffe8deaaa7160fae7db1214b0bf69285399c0e94bbb35bb5457cde76b001',
                                'NickName': 'hcchen5600',
                                'AttrStatus': 33788007,
                                'PYInitial': '',
                                'PYQuanPin': '',
                                'RemarkPYInitial': '',
                                'RemarkPYQuanPin': '',
                                'MemberStatus': 0,
                                'DisplayName': '',
                                'KeyWord': ''}
                            >,
                            <ChatroomMember: {'MemberList': <ContactList: []>,
                                'Uin': 0,
                                'UserName': '@747c321e4170daada2e873aa731a3e6b0799b6ae98fceabfb69322aa3fe232bb',
                                'NickName': '陳厚成0922',
                                'AttrStatus': 266277,
                                'PYInitial': '',
                                'PYQuanPin': '',
                                'RemarkPYInitial': '',
                                'RemarkPYQuanPin': '',
                                'MemberStatus': 0,
                                'DisplayName': '',
                                'KeyWord': ''}
                            >
                        ]
                    >,
                    'Uin': 0,
                    'UserName': '@@26536008f1c1307c892640411bf7f60ffd2a3feb138ed6591e65e4fe7541708e',
                    'NickName': 'me and myself',
                    'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgetheadimg?seq=0&username=@@26536008f1c1307c892640411bf7f60ffd2a3feb138ed6591e65e4fe7541708e&skey=@crypt_24f3c9b8_8745523c9c4ecd2615222a8cf1a2e9e5',
                    'ContactFlag': 2,
                    'MemberCount': 3,
                    'RemarkName': '',
                    'HideInputBarFlag': 0,
                    'Sex': 0,
                    'Signature': '',
                    'VerifyFlag': 0,
                    'OwnerUin': 0,
                    'PYInitial': '',
                    'PYQuanPin': '',
                    'RemarkPYInitial': '',
                    'RemarkPYQuanPin': '',
                    'StarFriend': 0,
                    'AppAccountFlag': 0,
                    'Statues': 1,
                    'AttrStatus': 0,
                    'Province': '',
                    'City': '',
                    'Alias': '',
                    'SnsFlag': 0,
                    'UniFriend': 0,
                    'DisplayName': '',
                    'ChatRoomId': 0,
                    'KeyWord': '',
                    'EncryChatRoomId': '',
                    'IsOwner': 0,
                    'IsAdmin': None,
                    'Self': <ChatroomMember: {'MemberList': <ContactList: []>,
                    'Uin': 0,
                    'UserName': '@9f15931b5d2a9ea59d4c5e220e079c5574b036939a4300c985ae83094d0b8250',
                    'NickName': '網路分享小寶貝',
                    'AttrStatus': 33558565,
                    'PYInitial': '',
                    'PYQuanPin': '',
                    'RemarkPYInitial': '',
                    'RemarkPYQuanPin': '',
                    'MemberStatus': 0,
                    'DisplayName': '',
                    'KeyWord': ''}>,
                    'HeadImgUpdateFlag': 1,
                    'ContactType': 0,
                    'ChatRoomOwner': '@102dffe8deaaa7160fae7db1214b0bf69285399c0e94bbb35bb5457cde76b001'
                } # 'MemberList'
            >, # Chatroom:
        'Type': 'Text',
        'Text': '22'}
    isGrupChat>
    --> 怎解？與一般 message 比對看看。。。
    notGrupChat> msg . cr
        {'MsgId': '2003695809776296585',
        'FromUserName': '@3102312982f699ea667ea6f1da7274c41a0a04de0d39304b9c23cb53532eaf36',
        'ToUserName': '@b56266318a18a59dfde8de5c771d45b588e6804ad1a440201cc7155d601df7a5',
        'MsgType': 1,
        'Content': 'not groupchat',
        'Status': 3,
        'ImgStatus': 1,
        'CreateTime': 1511087391,
        'VoiceLength': 0,
        'PlayLength': 0,
        'FileName': '',
        'FileSize': '',
        'MediaId': '',
        'Url': '',
        'AppMsgType': 0,
        'StatusNotifyCode': 0,
        'StatusNotifyUserName': '',
        'RecommendInfo': {'UserName': '',
            'NickName': '',
            'QQNum': 0,
            'Province': '',
            'City': '',
            'Content': '',
            'Signature': '',
            'Alias': '',
            'Scene': 0,
            'VerifyFlag': 0,
            'AttrStatus': 0,
            'Sex': 0,
            'Ticket': '',
            'OpCode': 0},
        'ForwardFlag': 0,
        'AppInfo': {'AppID': '',
            'Type': 0},
        'HasProductId': 0,
        'Ticket': '',
        'ImgHeight': 0,
        'ImgWidth': 0,
        'SubMsgType': 0,
        'NewMsgId': 2003695809776296585,
        'OriContent': '',
        'User': <User: {'MemberList': <ContactList: []>,
            'Uin': 0,
            'UserName': '@3102312982f699ea667ea6f1da7274c41a0a04de0d39304b9c23cb53532eaf36',
            'NickName': 'hcchen5600',
            'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=647060216&username=@3102312982f699ea667ea6f1da7274c41a0a04de0d39304b9c23cb53532eaf36&skey=@crypt_24f3c9b8_0dc65510ad7649edb30b6fb91b87cd98',
            'ContactFlag': 3,
            'MemberCount': 0,
            'RemarkName': '',
            'HideInputBarFlag': 0,
            'Sex': 1,
            'Signature': 'hcchen5600',
            'VerifyFlag': 0,
            'OwnerUin': 0,
            'PYInitial': 'HCCHEN5600',
            'PYQuanPin': 'hcchen5600',
            'RemarkPYInitial': '',
            'RemarkPYQuanPin': '',
            'StarFriend': 0,
            'AppAccountFlag': 0,
            'Statues': 0,
            'AttrStatus': 33788007,
            'Province': 'New Taipei City',
            'City': '',
            'Alias': '',
            'SnsFlag': 1,
            'UniFriend': 0,
            'DisplayName': '',
            'ChatRoomId': 0,
            'KeyWord': '',
            'EncryChatRoomId': '',
            'IsOwner': 0}>,
        'Type': 'Text',
        'Text': 'not groupchat'}
    notGrupChat>



'''



