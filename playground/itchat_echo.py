import peforth;peforth.ok(loc=locals(),cmd='include xray.f')
import itchat
@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    peforth.ok('11> ',glo=globals(),loc=locals(),cmd='constant bp11 ." --- breakpoint 11 ---" cr')
    return msg.text
itchat.auto_login()
itchat.run()

'''

    Login successfully as hcchen5600
    Start auto replying.
    --- breakpoint ---
    11> .s
          0: ({'msg': <Message: {'MsgId': '2179882316038211453', 'FromUserName': '@4ad76ee64ed7c4c30ab7a9d02c379433b743f242efad9f2a747b912add3620ff', 'ToUserName': '@4ad76ee64ed7c4c30ab7a9d02c379433b743f242efad9f2a747b912add3620ff', 'MsgType': 1, 'Content': 'ww', 'Status': 3, 'ImgStatus': 1, 'CreateTime': 1510630563, 'VoiceLength': 0, 'PlayLength': 0, 'FileName': '', 'FileSize': '', 'MediaId': '', 'Url': '', 'AppMsgType': 0, 'StatusNotifyCode': 0, 'StatusNotifyUserName': '', 'RecommendInfo': {'UserName': '', 'NickName': '', 'QQNum': 0, 'Province': '', 'City': '', 'Content': '', 'Signature': '', 'Alias': '', 'Scene': 0, 'VerifyFlag': 0, 'AttrStatus': 0, 'Sex': 0, 'Ticket': '', 'OpCode': 0}, 'ForwardFlag': 0, 'AppInfo': {'AppID': '', 'Type': 0}, 'HasProductId': 0, 'Ticket': '', 'ImgHeight': 0, 'ImgWidth': 0, 'SubMsgType': 0, 'NewMsgId': 2179882316038211453, 'OriContent': '', 'User': <User: {'MemberList': <ContactList: []>, 'UserName': '@4ad76ee64ed7c4c30ab7a9d02c379433b743f242efad9f2a747b912add3620ff', 'City': '', 'DisplayName': '', 'PYQuanPin': 'hcchen5600', 'RemarkPYInitial': '', 'Province': 'New Taipei City', 'KeyWord': '', 'RemarkName': '', 'PYInitial': 'HCCHEN5600', 'EncryChatRoomId': '', 'Alias': '', 'Signature': 'hcchen5600', 'NickName': 'hcchen5600', 'RemarkPYQuanPin': '', 'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=640010596&username=@4ad76ee64ed7c4c30ab7a9d02c379433b743f242efad9f2a747b912add3620ff&skey=@crypt_6868670c_a83bc00780ece043f126cad63f3d618a', 'UniFriend': 0, 'Sex': 1, 'AppAccountFlag': 0, 'VerifyFlag': 0, 'ChatRoomId': 0, 'HideInputBarFlag': 0, 'AttrStatus': 33788007, 'SnsFlag': 1, 'MemberCount': 0, 'OwnerUin': 0, 'ContactFlag': 1, 'Uin': 1423539136, 'StarFriend': 0, 'Statues': 0, 'WebWxPluginSwitch': 1, 'HeadImgFlag': 1, 'IsOwner': 0}>, 'Type': 'Text', 'Text': 'ww'}>}, {}, '11> ') (<class 'tuple'>)
    11> depth . cr
    1
    11> :> [0] constant parent // ( -- locals ) echo.py message handler locals
    reDef parent
    11> words
    ...snip... --- parent parent
    11> parent inport
    11> words
    ...snip... --- parent parent msg <-------- 取得 msg 這才是重點
    
    \ 整個 msg 的內容看這裡
    11> msg . cr
    {'MsgId': '2179882316038211453',
     'FromUserName': '@4ad76ee64ed7c4c30ab7a9d02c379433b743f242efad9f2a747b912add3620ff',
     'ToUserName': '@4ad76ee64ed7c4c30ab7a9d02c379433b743f242efad9f2a747b912add3620ff',
     'MsgType': 1,
     'Content': 'ww',  <---------- the message I typed
     'Status': 3,
     'ImgStatus': 1,
     'CreateTime': 1510630563,
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
     'NewMsgId': 2179882316038211453,
     'OriContent': '',
     'User': <User: {'MemberList': <ContactList: []>,
     'UserName': '@4ad76ee64ed7c4c30ab7a9d02c379433b743f242efad9f2a747b912add3620ff',
     'City': '',
     'DisplayName': '',
     'PYQuanPin': 'hcchen5600',
     'RemarkPYInitial': '',
     'Province': 'New Taipei City',
     'KeyWord': '',
     'RemarkName': '',
     'PYInitial': 'HCCHEN5600',
     'EncryChatRoomId': '',
     'Alias': '',
     'Signature': 'hcchen5600',
     'NickName': 'hcchen5600',
     'RemarkPYQuanPin': '',
     'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=640010596&username=@4ad76ee64ed7c4c30ab7a9d02c379433b743f242efad9f2a747b912add3620ff&skey=@crypt_6868670c_a83bc00780ece043f126cad63f3d618a',
     'UniFriend': 0,
     'Sex': 1,
     'AppAccountFlag': 0,
     'VerifyFlag': 0,
     'ChatRoomId': 0,
     'HideInputBarFlag': 0,
     'AttrStatus': 33788007,
     'SnsFlag': 1,
     'MemberCount': 0,
     'OwnerUin': 0,
     'ContactFlag': 1,
     'Uin': 1423539136,
     'StarFriend': 0,
     'Statues': 0,
     'WebWxPluginSwitch': 1,
     'HeadImgFlag': 1,
     'IsOwner': 0}>,
     'Type': 'Text',
     'Text': 'ww'}
     
    11> msg type . cr
    <class 'itchat.storage.messagequeue.Message'>
    11> msg obj>keys . cr
    ['__class__', '__contains__', '__delattr__', '__delitem__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattr__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__len__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'clear', 'copy', 'download', 'fromkeys', 'get', 'items', 'keys', 'pop', 'popitem', 'setdefault', 'update', 'values']
    11> msg :> keys() . cr
    dict_keys(['MsgId', 'FromUserName', 'ToUserName', 'MsgType', 'Content', 'Status', 'ImgStatus', 'CreateTime', 'VoiceLength', 'PlayLength', 'FileName', 'FileSize', 'MediaId', 'Url', 'AppMsgType', 'StatusNotifyCode', 'StatusNotifyUserName', 'RecommendInfo', 'ForwardFlag', 'AppInfo', 'HasProductId', 'Ticket', 'ImgHeight', 'ImgWidth', 'SubMsgType', 'NewMsgId', 'OriContent', 'User', 'Type', 'Text'])
    11> msg :> ToUserName type . cr
    <class 'str'>
    11> msg :> ToUserName . cr                                         # 
    @081973df42edc4e88530f54cb6a4cd70a28feb34098c9c55ae3ce118d721b97c  # user name UUID
    11> msg :> FromUserName . cr                                       # 每次都不一樣！！
    @081973df42edc4e88530f54cb6a4cd70a28feb34098c9c55ae3ce118d721b97c  # 
    11> msg :> FromUserName . cr                                       # 
    @4377bc6bd0a19220a60c73292271ad391b590282ce9a26271a5fddfbea3cfd0e  # 
    
    11> msg py: help(pop())
    Help on Message in module itchat.storage.messagequeue object:
    class Message(itchat.storage.templates.AttributeDict)
     |  dict() -> new empty dictionary
     |  dict(mapping) -> new dictionary initialized from a mapping object's
     |      (key, value) pairs
     .... snip ......
     
    11> msg :> values . cr
    <built-in method values of Message object at 0x0000024503C2CB48>
    11> msg :> values() . cr
    dict_values([
        '2179882316038211453', 
        '@4ad76ee64ed7c4c30ab7a9d02c379433b743f242efad9f2a747b912add3620ff', 
        '@4ad76ee64ed7c4c30ab7a9d02c379433b743f242efad9f2a747b912add3620ff', 
        1, 
        'ww', 
        3, 
        1, 
        1510630563, 0, 0, '', '', '', '', 0, 0, '', 
        {'UserName': '', 'NickName': '', 'QQNum': 0, 'Province': '', 'City': '', 'Content': '', 'Signature': '', 'Alias': '', 'Scene': 0, 'VerifyFlag': 0, 'AttrStatus': 0, 'Sex': 0, 'Ticket': '', 'OpCode': 0}, 
        0, 
        {'AppID': '', 'Type': 0}, 
        0, '', 0, 0, 0, 2179882316038211453, '', 
        <User: {
                'MemberList': <ContactList: []>, 
                'UserName': '@4ad76ee64ed7c4c30ab7a9d02c379433b743f242efad9f2a747b912add3620ff', 
                'City': '', 
                'DisplayName': '', 
                'PYQuanPin': 'hcchen5600', 
                'RemarkPYInitial': '', 
                'Province': 'New Taipei City', 
                'KeyWord': '', 
                'RemarkName': '', 
                'PYInitial': 'HCCHEN5600', 
                'EncryChatRoomId': '', 
                'Alias': '', 
                'Signature': 'hcchen5600', 
                'NickName': 'hcchen5600', 
                'RemarkPYQuanPin': '', 
                'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=640010596&username=@4ad76ee64ed7c4c30ab7a9d02c379433b743f242efad9f2a747b912add3620ff&skey=@crypt_6868670c_a83bc00780ece043f126cad63f3d618a', 
                'UniFriend': 0, 
                'Sex': 1, 
                'AppAccountFlag': 0, 
                'VerifyFlag': 0, 
                'ChatRoomId': 0, 
                'HideInputBarFlag': 0, 
                'AttrStatus': 33788007, 
                'SnsFlag': 1, 
                'MemberCount': 0, 
                'OwnerUin': 0, 
                'ContactFlag': 1, 
                'Uin': 1423539136, 
                'StarFriend': 0, 
                'Statues': 0, 
                'WebWxPluginSwitch': 1, 
                'HeadImgFlag': 1, 
                'IsOwner': 0
            }
        >, 
        'Text', 'ww'])
    11>

    \ 由以上方法取得的 ToUserName UUID 真的有效
    11> itchat :>~ send('Hello', toUserName='lskdjflsdjf')   \ 故意亂打
    11> .s
          0: {'BaseResponse': {'Ret': -1, 'ErrMsg': '', 'RawMsg': ''}, 'MsgID': '', 'LocalID': ''} (<class 'itchat.returnvalues.ReturnValue'>)
          
    11> itchat :>~ send('Hello', toUserName='hcchen5600') \ 用我的 WeChatID 無效！！！
    11> .s
          1: {'BaseResponse': {'Ret': -1, 'ErrMsg': '', 'RawMsg': ''}, 'MsgID': '', 'LocalID': ''} (<class 'itchat.returnvalues.ReturnValue'>)
    
    \ 用 userName UUID 真的有效！！    
    11> itchat :>~ send('Hello', toUserName='@4377bc6bd0a19220a60c73292271ad391b590282ce9a26271a5fddfbea3cfd0e')
    11> .s
          2: {'BaseResponse': {'Ret': 0, 'ErrMsg': '请求成功', 'RawMsg': '请求成功'}, 'MsgID': '5852875319741225439', 'LocalID': '15106370753679'} (<class 'itchat.returnvalues.ReturnValue'>)
    11>

    \ 用舊的 UUID 試試。。。
    itchat :>~ send('ffabc1234', toUserName='@081973df42edc4e88530f54cb6a4cd70a28feb34098c9c55ae3ce118d721b97c')
    --> 不行，當然不行。
    
'''
