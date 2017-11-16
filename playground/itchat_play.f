
    \ jump to -------  play with itchat --------

    \ Change DOSBox title
    :> [0] constant parent // ( -- locals ) Caller's locals() dict
    s" dos title " __main__ :> __file__ + CRLF + dictate drop

    exit break-include \ ------------------- Never Land -------------------------------------------
   
    ." Error!! You reached never land, what's the problem?" cr
    ." Error!! You reached never land, what's the problem?" cr
    ." Error!! You reached never land, what's the problem?" cr
    ." Error!! You reached never land, what's the problem?" cr
    ." Error!! You reached never land, what's the problem?" cr
    ." Press enter to continue but don't!" accept
    
    \ Depress Tensorflow warning message 
    py: os.environ['TF_CPP_MIN_LOG_LEVEL']='2'  \ # https://stackoverflow.com/questions/43134753/tensorflow-wasnt-compiled-to-use-sse-etc-instructions-but-these-are-availab
    
    \ Imports 
    \ 把 mnist_data 放在了公共的地方，改由 peforth 來 import 避免重複浪費時間、空間。
    
    py> os.getcwd() constant working-directory // ( -- "path" ) Saved copy of tutorial home directory path
    
    \ my MNIST_data directory is there
    cd c:\Users\hcche\Downloads
    
    py:~ from tensorflow.examples.tutorials.mnist import input_data; push(input_data)
    constant mnist_module // ( -- mnist_module ) module

    \ # Download images and labels into mnist.test (10K images+labels) and mnist.train (60K images+labels)
    \ # mnist = mnist_data.read_data_sets("data", one_hot=True, reshape=False, validation_size=0)
    mnist_module :>~ read_data_sets('MNIST_data', one_hot=True)
    constant mnist // ( -- datasets ) 3 datasets (train, validation, test)
    mnist parent :: ['mnist']=pop(1) \ feedback to the tutorial 
    mnist_module parent :: ['input_data']=pop(1) \ feedback to the tutorial 

    working-directory py: os.chdir(pop()) \ Go home
    
    
    \ Common tools 

    \ To drop a breakpoint into python
    import peforth;peforth.ok('11> ',loc=locals(),cmd="parent inport")
   
    
    dos title Tensorflow MNIST tutorial playground

    1000 value pause // ( -- n ) Loop count to pause 
    : autoexec pause py> tos(1)%pop() not and if py: ok('loop-100>>',cmd="cr") then ;
    // ( i -- ) Auto-run at breakpoint 
    
    cr ."     Tensorflow version "  tf :> __version__ . cr
    
    <text>
    
    MNIST dataset imported.
    You can now make some setups, like py: vm.debug=22 or the likes.
    You can play around and 'exit' to continue the tutorial.

    </text> . cr
    
    marker ---xray---
    \ py: vm.debug=22

    \ Initial Check 
    dos title working play ground
    cr version drop ." Current directory is : " cd
    dos if exist MNIST_data exit 34157
    34157 = [if] 
        ." TenserFlow dataset ./MNIST_data is existing. Good! Good! Good! let's go on ...." cr 
        \ exit \ <---------- exit to tutorial
    [else]
        ." TenserFlow dataset at ./MNIST_data is expected but not found!" cr
        ." Move it over to here if you have it already." cr
        \ ." Type <Enter> to proceed downloading it or 'abort' to STOP "
        \ accept char abort = [if] ." Action aborted by user." cr bye \ terminate
        \ [else] exit *debug* 22 ( <---------------- exit to tutorial ) [then] 
    [then]
    ." Type <Enter> to proceed " accept drop 
    break-include
    

    \ 抽換 marker 界線，把 --- 改成 ---xray--- replace marker 
        <accept> <text> 
        locals().update(harry_port());  # bring in all FORTH value.outport
        dictate("### marker ---xray---"); outport(locals()) # bring out all locals()
        </text> -indent py: exec(pop())
        </accept> dictate 
    
    \ This snippet adds batch_X, batch_Y into value.outport for investigation
        <accept> <text> 
        locals().update(harry_port());  # bring in all things
        # ------------ get what we want --------------------------
        batch_X, batch_Y = mnist.train.next_batch(100);  
        # ------------ get what we want --------------------------
        dictate("---xray--- marker ---xray---"); outport(locals()) # bring out all things
        </text> -indent py: exec(pop())
        </accept> dictate 

    bp11> batch_X :> [0].shape . cr
    (28, 28, 1)
    bp11> batch_X :> shape . cr
    (100, 28, 28, 1)
    bp11>
    bp11> batch_Y :> shape . cr
    (100, 10)
    bp11> batch_Y :> [0] . cr
    [ 0.  0.  0.  0.  0.  0.  0.  0.  1.  0.]
    bp11>

    \ If we can see placeholders X and Y then we can see anything...
    <text>
    locals().update(harry_port());  # bring in all things
    myX = sess.run(X,feed_dict={X: batch_X, Y_: batch_Y})
    myY = sess.run(Y,feed_dict={X: batch_X, Y_: batch_Y})
    ok(cmd="---xray--- marker ---xray--- exit");  # clear things in forth
    outport(locals())
    </text> -indent py: exec(pop()) 

    \ it works!!! hahahaha
    bp11> words
    ... snip ....
    yclude) pyclude .members .source dos cd ### --- __name__ __doc__ __package__ 
    __loader__ __spec__ __annotations__ __builtins__ __file__ __cached__ peforth 
    tf tensorflowvisu mnist_data mnist X Y_ W b XX Y cross_entropy 
    correct_prediction accuracy train_step allweights allbiases I It datavis init 
    sess training_step batch_X batch_Y myX myY
    bp11>              ^^^^^^^^^^^^^^^^^^^^^^^^------Bingo!!                

    \ peforth can import modules with the ability of cd, dos,
    \ os.chdir() and os.getcwd() they can be at different paths
    
    py:~ import tensorflow as tf; push(tf)
    parent :: ['tf']=pop(1)
    py:~ import tensorflowvisu; push(tensorflowvisu)
    parent :: ['tensorflowvisu']=pop(1)

    
    \ include c:\Users\hcche\Documents\GitHub\ML\tutorials\tensorflowTUT\tf18_CNN2\full_code.f 
    
    --- \ remove older garbage
    
    : ce ( -- value ) // Get value of cross_entropy
        <text>
        locals().update(harry_port())
        rslt = sess.run(cross_entropy,feed_dict={xs: X_train, ys: y_train, keep_prob: 1})
        push(rslt)
        </text> \ 不能用 <py>..</py> 否則 sess 會馬上被 compile 而那時 harry_port() 帶進的 variables 未定義
        -indent py: exec(pop()) ;

    py:~ import PIL.Image as image; push(image)
    value image
    image :> new("L",(8,8)) value pic // ( -- PIL.image ) object
      
    \ Macro 形式用在 [for]...[next] 會有問題 [ ] 待解 --> 用 exec(code) 看看。。。。
    \ : digit ( index -- ) // View the handwritten digit image pointed by the index
    \     <text>
    \     digits :> data[pop()] py> tuple(pop()*16) pic :: putdata(pop()) pic :: show() 
    \     </text> dictate ;

    marker --- \ set a fense


































    \ ---------------------  play with itchat --------------------------------
    
    \ invoke     
    import itchat constant itchat // ( -- module ) itchat
    
    \ login
    itchat :: auto_login()
    \ itchat :: auto_login(hotReload=True)
    \ import time :: sleep(10) \ 單 sleep 5 sec 就算了，不要去 check_login()
    \ itchat :> check_login() tib. 
    \ char 400 = [if] ." Login: Success!" cr [else] ." Login: Failed!!" cr [then]
    
    \ send hello world to myself
    itchat :> send("中文也可以") :> ['BaseResponse']['Ret'] 
    [if] ." Failed!!" cr [else] ." Success!" cr [then]

    \ send message to a friend
    itchat :> search_friends(nickName='陳厚成0922')[0] constant chc0922 \ get user object 
    chc0922 :>~ send('Hello H.C.!')
    :> ['BaseResponse']['Ret'] [if] ." Failed!!" cr [else] ." Success!" cr [then]        
    \
    itchat :> search_friends(nickName='hcchen5600')[0] constant hcchen5600 \ get user object 
    hcchen5600 :>~ send('Hello H.C.!')
    :> ['BaseResponse']['Ret'] [if] ." Failed!!" cr [else] ." Success!" cr [then]        
    
    \ message echo-er 這裡教的 https://www.shiyanlou.com/courses/684/labs/2237/document
    OK ' itchat :> type tib. \ ==> constant
    OK ' itchat :: type='value.outport'
    OK ' itchat :> type tib. \ ==> value.outport

    marker ---
    ' itchat :: type='value.outport'
    <accept> <text> 
    # ------------ get what we want --------------------------
    import pdb;pdb.set_trace()
    @itchat.msg_register(itchat.content.TEXT)
    def print_content(msg):
        print(msg['Text'])
    # itchat.auto_login()
    itchat.run()
    # ------------ get what we want --------------------------
    dictate("--- marker ---"); outport(locals()) # bring out all things
    </text> -indent py: exec(pop(),harry_port())
    </accept> dictate 
    
[x] try itchat attributes,
    OK itchat dir . cr
    ['Core', 'VERSION', '__builtins__', '__cached__', '__doc__', 
    '__file__', '__loader__', '__name__', '__package__', '__path__', 
    '__spec__', '__version__', 'add_friend', 'add_member_into_chatroom', 
    'auto_login', 'check_login', 'components', 'config', 
    'configured_reply', 'content', 'core', 'create_chatroom', 
    'delete_member_from_chatroom', 'dump_login_status', 'get_QR', 
    'get_QRuuid', 'get_chatrooms', 'get_contact', 'get_friends', 
    'get_head_img', 'get_mps', 'get_msg', 'instanceList', 
    'load_login_status', 'log', 'login', 'logout', 'msg_register', 
    'new_instance', 'originInstance', 'returnvalues', 'revoke', 'run', 
    'search_chatrooms', 'search_friends', 'search_mps', 'send', 
    'send_file', 'send_image', 'send_msg', 'send_raw_msg', 'send_video', 
    'set_alias', 'set_chatroom_name', 'set_logging', 'set_pinned', 
    'show_mobile_login', 'start_receiving', 'storage', 'update_chatroom', 
    'update_friend', 'upload_file', 'utils', 'web_init']
[x] itchat :> dump_login_status() tib. \ ==> None
[x] itchat :> check_login() tib. \ ==> 400  login 之後馬上 check 會被 log out 甩出去,
    was that because of peforth environment?
[x] itchat :> get_friends() . cr \ dump all friends, that's a big list.
[x] itchat :: send() \ default is send to myself 
    send(msg, toUserName=None, mediaId=None) method of itchat.core.Core instance
    OK itchat :>~ send("中文也可以")
    OK .s
          0: {'BaseResponse': {'Ret': 0, 'ErrMsg': '请求成功', 'RawMsg': '请求成功'}, 
              'MsgID': '6549390734616950133', 
              'LocalID': '15106280423664'
             } (<class 'itchat.returnvalues.ReturnValue'>)
    OK
    dup :> ['BaseResponse']['Ret'] tib. \ ==> 0 (<class 'int'>)
    dup :> ['BaseResponse']['ErrMsg'] tib. \ ==> 请求成功 (<class 'str'>)
    OK        
[x] 當另一個 itchat login 時，前一個就會 --> OK LOG OUT!
    * 有些帳號不能 send() 
    * 有裝了 WeChat App 的電腦可能就不能用 itchat or WeChat Web 
[x] c:\Users\hcche\Documents\GitHub\itchat_app\echo.py 
    make PC a WeChat echo-er 
    I have a lot of study there in its comments
    這裡教的 https://www.shiyanlou.com/courses/684/labs/2237/document 就是上面的 echo─er
[x] itchat :> search_friends("陳厚成0922") <---- best form 等於 (name="陳厚成0922")
    (default) 'name' is 備註、微信號、昵稱中的任何一項「全等於」name
    'userName' is dynamic UUID 
    'nickName' is 昵稱「全等於」name, 但「聊天室」就變成「有出現」 即可。
    'wechatAccount' 用不上, get_friends() 裡面沒有

    author = itchat.search_friends(nickName='LittleCoder')[0]
    author.send('greeting, littlecoder!')

    OK itchat :> search_friends(nickName='hcchen5600')
    OK constant hcchen5600
    OK hcchen5600 type . cr
    <class 'list'>   <----------------- 可能找到多個嗎？ friends 不會 chatroom 則會
    OK .s
          0: 400 (<class 'str'>)
          1: <class 'list'> (<class 'type'>)
    OK dropall
    OK hcchen5600 type . cr
    <class 'list'>
    OK
    OK hcchen5600 obj>keys . cr
    ['__add__', '__class__', '__contains__', '__delattr__', '__delitem__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__iadd__', '__imul__', '__init__', '__init_subclass__', '__iter__', '__le__', '__len__', '__lt__', '__mul__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__reversed__', '__rmul__', '__setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', 'append', 'clear', 'copy', 'count', 'extend', 'index', 'insert', 'pop', 'remove', 'reverse', 'sort']
    OK hcchen5600 . cr
    [<User: {'MemberList': <ContactList: []>, 'UserName': '@a70cde46dabe665b89a1710988706183894babf158b5aa58404278fa8fab8857', 'City': '', 'DisplayName': '', 'PYQuanPin': 'hcchen5600', 'RemarkPYInitial': '', 'Province': 'New Taipei City', 'KeyWord': '', 'RemarkName': '', 'PYInitial': 'HCCHEN5600', 'EncryChatRoomId': '', 'Alias': '', 'Signature': 'hcchen5600', 'NickName': 'hcchen5600', 'RemarkPYQuanPin': '', 'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=640010596&username=@a70cde46dabe665b89a1710988706183894babf158b5aa58404278fa8fab8857&skey=@crypt_6868670c_142e779b38f0f26f5a0cef0ebd565edf', 'UniFriend': 0, 'Sex': 1, 'AppAccountFlag': 0, 'VerifyFlag': 0, 'ChatRoomId': 0, 'HideInputBarFlag': 0, 'AttrStatus': 33788007, 'SnsFlag': 1, 'MemberCount': 0, 'OwnerUin': 0, 'ContactFlag': 1, 'Uin': 1423539136, 'StarFriend': 0, 'Statues': 0, 'WebWxPluginSwitch': 1, 'HeadImgFlag': 1, 'IsOwner': 0}>]
    OK hcchen5600 py> len(pop()) . cr
    1
    OK hcchen5600 :> [0] type . cr
    <class 'itchat.storage.templates.User'>
    OK hcchen5600 :> [0] obj>keys . cr
    ['__class__', '__contains__', '__deepcopy__', '__delattr__', '__delitem__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattr__', '__getattribute__', '__getitem__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__len__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_core', 'add_member', 'clear', 'copy', 'core', 'delete_member', 'fromkeys', 'get', 'get_head_image', 'items', 'keys', 'pop', 'popitem', 'search_member', 'send', 'send_file', 'send_image', 'send_msg', 'send_raw_msg', 'send_video', 'set_alias', 'set_pinned', 'setdefault', 'update', 'values', 'verify', 'verifyDict']
    OK

    \ 用 itchat :> get_friends() 先列出所有的人，然後找到目標 nickName。只能這樣，因為 nickName 很搞怪。
    
    \ 找到 '黃于庭' 了！
    OK dropall itchat :> search_friends(nickName='黃于庭') .s
          0: [<User: {'MemberList': <ContactList: []>, 'Uin': 0, 'UserName': '@0c699fbb5924792959eced716656a14bdcf506209eea38e8a2e0d13ae30f16cb', 'NickName': '黃于庭', 'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=676874999&username=@0c699fbb5924792959eced716656a14bdcf506209eea38e8a2e0d13ae30f16cb&skey=@crypt_6868670c_142e779b38f0f26f5a0cef0ebd565edf', 'ContactFlag': 3, 'MemberCount': 0, 'RemarkName': '黃于庭 永和國泰 0921807343', 'HideInputBarFlag': 0, 'Sex': 2, 'Signature': '堅持就是力量，不放棄就有希望', 'VerifyFlag': 0, 'OwnerUin': 0, 'PYInitial': 'HYT', 'PYQuanPin': 'huangyuting', 'RemarkPYInitial': 'HYTYHGT0921807343', 'RemarkPYQuanPin': 'huangyutingyongheguotai0921807343', 'StarFriend': 0, 'AppAccountFlag': 0, 'Statues': 0, 'AttrStatus': 2461701, 'Province': '台湾', 'City': '台北市', 'Alias': '', 'SnsFlag': 0, 'UniFriend': 0, 'DisplayName': '', 'ChatRoomId': 0, 'KeyWord': '', 'EncryChatRoomId': '', 'IsOwner': 0}>] (<class 'list'>)
    OK

    \ 找到 'Natalie' 了！ 大小寫有關。
    OK dropall itchat :> search_friends(nickName='natalie') .s
          0: [] (<class 'list'>)
    OK dropall itchat :> search_friends(nickName='Natalie') .s
          0: [<User: {'MemberList': <ContactList: []>, 'Uin': 0, 'UserName': '@28b67274eaefe406e2a18a7386719ba110010ee26711dac26c7e2fc97b490eab', 'NickName': 'Natalie', 'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=661260843&username=@28b67274eaefe406e2a18a7386719ba110010ee26711dac26c7e2fc97b490eab&skey=@crypt_6868670c_142e779b38f0f26f5a0cef0ebd565edf', 'ContactFlag': 2115, 'MemberCount': 0, 'RemarkName': 'nana', 'HideInputBarFlag': 0, 'Sex': 0, 'Signature': '', 'VerifyFlag': 0, 'OwnerUin': 0, 'PYInitial': 'NATALIE', 'PYQuanPin': 'Natalie', 'RemarkPYInitial': 'NANA', 'RemarkPYQuanPin': 'nana', 'StarFriend': 1, 'AppAccountFlag': 0, 'Statues': 0, 'AttrStatus': 33558565, 'Province': '', 'City': '', 'Alias': '', 'SnsFlag': 0, 'UniFriend': 0, 'DisplayName': '', 'ChatRoomId': 0, 'KeyWord': '', 'EncryChatRoomId': '', 'IsOwner': 0}>] (<class 'list'>)
    
    \ DOSBox 下 Wendy 的 nickName 呈現為 '???', chcp 950 (Big-5) or 65001 (utf-8) 都這樣
    \ 但是從這裡 copy-paste 過去到 DOSBox 下的 python peforth 執行是可以的，只有簡體字呈現的問題而已，
    \ 連 copy 過來都還是好的。
    dropall itchat :> search_friends(nickName='马玮赟') .s
    OK dropall itchat :> search_friends(nickName='马玮赟') .s
          0: [<User: {'MemberList': <ContactList: []>, 'Uin': 0, 'UserName': '@d2dc5257a4c2e1064584744b1f96618ddbef6fbd0a4a7b071528607604e654a6', 'NickName': '马玮赟', 'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=666233582&username=@d2dc5257a4c2e1064584744b1f96618ddbef6fbd0a4a7b071528607604e654a6&skey=@crypt_6868670c_142e779b38f0f26f5a0cef0ebd565edf', 'ContactFlag': 259, 'MemberCount': 0, 'RemarkName': '', 'HideInputBarFlag': 0, 'Sex': 2, 'Signature': '玮赟', 'VerifyFlag': 0, 'OwnerUin': 0, 'PYInitial': 'MWB', 'PYQuanPin': 'maweibin', 'RemarkPYInitial': '', 'RemarkPYQuanPin': '', 'StarFriend': 0, 'AppAccountFlag': 0, 'Statues': 0, 'AttrStatus': 103421, 'Province': '江苏', 'City': '苏州', 'Alias': '', 'SnsFlag': 17, 'UniFriend': 0, 'DisplayName': '', 'ChatRoomId': 0, 'KeyWord': '', 'EncryChatRoomId': '', 'IsOwner': 0}>] (<class 'list'>)

    \ 陳厚成0922
    OK dropall itchat :> search_friends(nickName='陳厚成0922') .s
          0: [<User: {'MemberList': <ContactList: []>, 'Uin': 0, 'UserName': '@b9d27eaef94ca06e59862d90e526f25c51e5af431ee7de10d367c16905a819a2', 'NickName': '陳厚成0922', 'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=676879946&username=@b9d27eaef94ca06e59862d90e526f25c51e5af431ee7de10d367c16905a819a2&skey=@crypt_6868670c_142e779b38f0f26f5a0cef0ebd565edf', 'ContactFlag': 515, 'MemberCount': 0, 'RemarkName': '', 'HideInputBarFlag': 0, 'Sex': 0, 'Signature': '', 'VerifyFlag': 0, 'OwnerUin': 0, 'PYInitial': 'CHC0922', 'PYQuanPin': 'chenhoucheng0922', 'RemarkPYInitial': '', 'RemarkPYQuanPin': '', 'StarFriend': 0, 'AppAccountFlag': 0, 'Statues': 0, 'AttrStatus': 4133, 'Province': '', 'City': '', 'Alias': '', 'SnsFlag': 0, 'UniFriend': 0, 'DisplayName': '', 'ChatRoomId': 0, 'KeyWord': '', 'EncryChatRoomId': '', 'IsOwner': 0}>] (<class 'list'>)

    \ 不接受 PYInitial, PYQuanPin,  
    OK dropall itchat :> search_friends(PYInitial='CHC0922') .s
    Failed in </py> (compiling=False): search_friends() got an unexpected keyword argument 'PYInitial'
    OK dropall itchat :> search_friends(PYQuanPin='chenhoucheng0922') .s
    Failed in </py> (compiling=False): search_friends() got an unexpected keyword argument 'PYQuanPin'

    \ 我知道為何不接受 PYInitial, PYQuanPin 了，因為像以下這個就拼不出來了。。。
    dropall itchat :> search_friends(nickName='糖果🐝') .s
          0: [<User: {'MemberList': <ContactList: []>, 'Uin': 0, 'UserName': '@df2c50dd67607ed7e711dce512d9a03e', 'NickName': '糖果🐝', 'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=676898210&username=@df2c50dd67607ed7e711dce512d9a03e&skey=@crypt_6868670c_142e779b38f0f26f5a0cef0ebd565edf', 'ContactFlag': 257, 'MemberCount': 0, 'RemarkName': '22唐', 'HideInputBarFlag': 0, 'Sex': 2, 'Signature': '我木有你想象中那么坚强。', 'VerifyFlag': 0, 'OwnerUin': 0, 'PYInitial': 'TG?', 'PYQuanPin': 'tangguo?', 'RemarkPYInitial': '22T', 'RemarkPYQuanPin': '22tang', 'StarFriend': 0, 'AppAccountFlag': 0, 'Statues': 0, 'AttrStatus': 100453, 'Province': '江苏', 'City': '苏州', 'Alias': '', 'SnsFlag': 177, 'UniFriend': 0, 'DisplayName': '', 'ChatRoomId': 0, 'KeyWord': 'gag', 'EncryChatRoomId': '', 'IsOwner': 0}>] (<class 'list'>)
    \ 看來只有 nickName 能用了
    
    OK itchat :> search_friends() . cr
        {'MemberList': <ContactList: []>,
         'UserName': '@e43c87a61d1a6737b1ae6d8a738f5d4cb2f43b9fbf50796da042ad007012eb2c',
         'City': '',
         'DisplayName': '',
         'PYQuanPin': '',
         'RemarkPYInitial': '',
         'Province': '',
         'KeyWord': '',
         'RemarkName': '',
         'PYInitial': '',
         'EncryChatRoomId': '',
         'Alias': '',
         'Signature': '',
         'NickName': '陳厚成0922',
         'RemarkPYQuanPin': '',
         'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=109628115&username=@e43c87a61d1a6737b1ae6d8a738f5d4cb2f43b9fbf50796da042ad007012eb2c&skey=@crypt_7340b66c_8408cf3e69826c36dbf79279137945fb',
         'UniFriend': 0,
         'Sex': 0,
         'AppAccountFlag': 0,
         'VerifyFlag': 0,
         'ChatRoomId': 0,
         'HideInputBarFlag': 0,
         'AttrStatus': 0,
         'SnsFlag': 0,
         'MemberCount': 0,
         'OwnerUin': 0,
         'ContactFlag': 0,
         'Uin': 2609342470,
         'StarFriend': 0,
         'Statues': 0,
         'WebWxPluginSwitch': 0,
         'HeadImgFlag': 1}

    OK itchat :> search_friends(name='0922') . cr
    []
    OK itchat :> search_friends(name='陳厚成') . cr
    []
    OK itchat :> search_friends(nickName='陳厚成') . cr
    []
    OK itchat :> search_friends(nickName='陳厚成0922') . cr
    [<User: {'MemberList': <ContactList: []>, 'UserName': '@e43c87a61d1a6737b1ae6d8a738f5d4cb2f43b9fbf50796da042ad007012eb2c', 'City': '', 'DisplayName': '', 'PYQuanPin': '', 'RemarkPYInitial': '', 'Province': '', 'KeyWord': '', 'RemarkName': '', 'PYInitial': '', 'EncryChatRoomId': '', 'Alias': '', 'Signature': '', 'NickName': '陳厚成0922', 'RemarkPYQuanPin': '', 'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=109628115&username=@e43c87a61d1a6737b1ae6d8a738f5d4cb2f43b9fbf50796da042ad007012eb2c&skey=@crypt_7340b66c_8408cf3e69826c36dbf79279137945fb', 'UniFriend': 0, 'Sex': 0, 'AppAccountFlag': 0, 'VerifyFlag': 0, 'ChatRoomId': 0, 'HideInputBarFlag': 0, 'AttrStatus': 0, 'SnsFlag': 0, 'MemberCount': 0, 'OwnerUin': 0, 'ContactFlag': 0, 'Uin': 2609342470, 'StarFriend': 0, 'Statues': 0, 'WebWxPluginSwitch': 0, 'HeadImgFlag': 1}>]
    OK itchat :> search_friends(name='陳厚成0922') . cr
    [<User: {'MemberList': <ContactList: []>, 'UserName': '@e43c87a61d1a6737b1ae6d8a738f5d4cb2f43b9fbf50796da042ad007012eb2c', 'City': '', 'DisplayName': '', 'PYQuanPin': '', 'RemarkPYInitial': '', 'Province': '', 'KeyWord': '', 'RemarkName': '', 'PYInitial': '', 'EncryChatRoomId': '', 'Alias': '', 'Signature': '', 'NickName': '陳厚成0922', 'RemarkPYQuanPin': '', 'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=109628115&username=@e43c87a61d1a6737b1ae6d8a738f5d4cb2f43b9fbf50796da042ad007012eb2c&skey=@crypt_7340b66c_8408cf3e69826c36dbf79279137945fb', 'UniFriend': 0, 'Sex': 0, 'AppAccountFlag': 0, 'VerifyFlag': 0, 'ChatRoomId': 0, 'HideInputBarFlag': 0, 'AttrStatus': 0, 'SnsFlag': 0, 'MemberCount': 0, 'OwnerUin': 0, 'ContactFlag': 0, 'Uin': 2609342470, 'StarFriend': 0, 'Statues': 0, 'WebWxPluginSwitch': 0, 'HeadImgFlag': 1}>]
    OK itchat :> search_friends(name='tw0922417555') . cr
    []
    OK itchat :> search_friends(name='chc0922') . cr
    []
    OK itchat :> search_friends(name='CHC0922') . cr
    []

    \ 聊天室 chatrooms 類似 friends 
    itchat :> get_chatrooms() py> len(pop()) tib. \ ==> 4 (<class 'int'>)

    \ search_chatrooms 是 default 用 'name': '奇迹四阶', 'NickName': '阿公,阿媽,厚伸,厚成,素娟,厚岐', 
    \ 傳回部分符合的 charroom Name
    OK  itchat :> search_chatrooms py: help(pop())
    Help on method search_chatrooms in module itchat.core:
    search_chatrooms(name=None, userName=None) method of itchat.core.Core instance
    itchat :> search_chatrooms('奇') . cr  <---- 找到 '奇迹四阶'
    itchat :> search_chatrooms('小大大客服群') <--- 還是找不到 [X] 奇怪！！！
    [x] 怎麼沒有 小多 小囡 客服群的聊天室？
        itchat :> get_chatrooms() py> len(pop()) tib. \ ==> 0 (<class 'int'>) ！！！！
        --> 保存「聊天室」到「通訊錄」之後，好了！！
        itchat :> get_chatrooms() py> len(pop()) tib. \ ==> 1 (<class 'int'>)
        OK        
    
[x] 用對方的 User Object 而非 nickName 才是好辦法
    dropall itchat :> search_friends(nickName='陳厚成0922')[0] constant chc0922 
    // ( -- obj ) WeChat user object

    \ user object 看到的只是 __str__ 它其實有很多 method 
    OK chc0922 . cr
        {'MemberList': <ContactList: []>, 'Uin': 0, 'UserName': 
        '@b9d27eaef94ca06e59862d90e526f25c51e5af431ee7de10d367c16905a819a2', 
        'NickName': '陳厚成0922', 'HeadImgUrl': 
        '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=676879946&username=@b9d27eaef94c
        a06e59862d90e526f25c51e5af431ee7de10d367c16905a819a2&skey=@crypt_686867
        0c_142e779b38f0f26f5a0cef0ebd565edf', 'ContactFlag': 515, 
        'MemberCount': 0, 'RemarkName': '', 'HideInputBarFlag': 0, 'Sex': 0, 
        'Signature': '', 'VerifyFlag': 0, 'OwnerUin': 0, 'PYInitial': 
        'CHC0922', 'PYQuanPin': 'chenhoucheng0922', 'RemarkPYInitial': '', 
        'RemarkPYQuanPin': '', 'StarFriend': 0, 'AppAccountFlag': 0, 
        'Statues': 0, 'AttrStatus': 4133, 'Province': '', 'City': '', 
        'Alias': '', 'SnsFlag': 0, 'UniFriend': 0, 'DisplayName': '', 
        'ChatRoomId': 0, 'KeyWord': '', 'EncryChatRoomId': '', 'IsOwner': 0}
    OK chc0922 keys . cr
        dict_keys(['MemberList', 'Uin', 'UserName', 'NickName', 'HeadImgUrl', 
        'ContactFlag', 'MemberCount', 'RemarkName', 'HideInputBarFlag', 
        'Sex', 'Signature', 'VerifyFlag', 'OwnerUin', 'PYInitial', 
        'PYQuanPin', 'RemarkPYInitial', 'RemarkPYQuanPin', 'StarFriend', 
        'AppAccountFlag', 'Statues', 'AttrStatus', 'Province', 'City', 
        'Alias', 'SnsFlag', 'UniFriend', 'DisplayName', 'ChatRoomId', 
        'KeyWord', 'EncryChatRoomId', 'IsOwner'])
    
    \ user object 看到的只是 __str__ 它其實有很多 method 
    OK chc0922 dir . cr
        ['__class__', '__contains__', '__deepcopy__', '__delattr__', 
        '__delitem__', '__dict__', '__dir__', '__doc__', '__eq__', 
        '__format__', '__ge__', '__getattr__', '__getattribute__', 
        '__getitem__', '__getstate__', '__gt__', '__hash__', '__init__', 
        '__init_subclass__', '__iter__', '__le__', '__len__', '__lt__', 
        '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', 
        '__repr__', '__setattr__', '__setitem__', '__setstate__', 
        '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_core', 
        'add_member', 'clear', 'copy', 'core', 'delete_member', 'fromkeys', 
        'get', 'get_head_image', 'items', 'keys', 'pop', 'popitem', 
        'search_member', 'send', 'send_file', 'send_image', 'send_msg', 
        'send_raw_msg', 'send_video', 'set_alias', 'set_pinned', 
        'setdefault', 'update', 'values', 'verify', 'verifyDict']

[x] \ message echo-er
    OK ' itchat :> type tib. \ ==> constant
    OK ' itchat :: type='value.outport'
    OK ' itchat :> type tib. \ ==> value.outport
    ' itchat :: type='value.outport'
    <accept> <text> 
    # ------------ get what we want --------------------------
    import pdb;pdb.set_trace()
    @itchat.msg_register(itchat.content.TEXT)
    def print_content(msg):
        print(msg['Text'])
    # itchat.auto_login()
    itchat.run()
    # ------------ get what we want --------------------------
    # dictate("--- marker ---"); outport(locals()) # bring out all things
    </text> -indent py: exec(pop(),harry_port())
    </accept> dictate 
[x] 如果你不想要每次运行程序都扫码，可以在登陆命令中进行设置：
    itchat :: auto_login(hotReload=True)
    --> 第一次會要求刷條碼，之後就不再要求了。實際上 logout 時會 log out 多次。
    --> 已經用 auto_login(hotReload=True) login 之後： 
    OK itchat :: auto_login() \ login as hcchen5600
    itchat has already logged in. <----------- 再想重新刷條碼，不行，要先 logout 吧？
    OK itchat :> logout() . cr                 ---> Yes!! 
    LOG OUT!
    {'BaseResponse': {'ErrMsg': '请求成功', 'Ret': 0, 'RawMsg': 'logout successfully.'}}
    OK    
    
[ ] itchat :> check_login() 好像用 陳厚成0922 login 時就不能用！
    \ 不 check 還好，一 check 馬上 loglout !!    
    \ 已經 login 成功了，會有這個 message 不需要再去 check_login()
    Login successfully as 陳厚成0922             \ 第一次
    OK     itchat :: auto_login(hotReload=True)  \ 第二次
    OK     itchat :: auto_login(hotReload=True)  \ 第三次
    OK     itchat :> check_login() tib.          \ 結果一 check 就 logout 3 次！
    LOG OUT!
    LOG OUT!
    LOG OUT!
    itchat :> check_login() tib. \ ==> 200 (<class 'str'>)
    OK
[x] 好像用 陳厚成0922 login 時就不能 send('...') 給自己？ 真的！！！ <--- RI: 帳號天生
    OK itchat :> send('abc')
    OK . cr
    {'BaseResponse': {'Ret': 1204, 'ErrMsg': '', 'RawMsg': ''}, 'MsgID': '', 'LocalID': ''}
    OK    
    OK \ send message to a friend
    OK itchat :> search_friends(nickName='hcchen5600')[0] constant hcchen5600 \ get user object
    OK hcchen5600 :>~ send('Hello hcchen5600!')
    OK :> ['BaseResponse']['Ret'] [if] ." Failed!!" cr [else] ." Success!" cr [then]
    Success!  <----------- 這樣就成功
    OK
    itchat :> search_friends(nickName='陳厚成0922')[0] constant chc0922 // ( -- user ) WeChat user object
    chc0922 :> send('Hello_陳厚成0922!') \ 發送給自己不行！可是昨天用 hcchen5600 帳號可以！
    :> ['BaseResponse']['Ret'] [if] ." Failed!!" cr [else] ." Success!" cr [then]        
    --> Failed!! 'Ret':1204 
    --> 改用 hcchen5600 login 證實之 。。。
        itchat :: auto_login() \ login as hcchen5600
        itchat :> send("中文也可以")
        結果一刷完條碼，馬上 logout --> 重跑 DOSBox
    --> https://itchat.readthedocs.io/zh/latest/FAQ/
        无法给自己发送消息
        Q: 为什么我发送信息的时候部分信息没有成功发出来？
        A: 有些账号是天生无法给自己的账号发送信息的，建议使用filehelper代替。    
    --> 試試。。果然傳給了自己的「文件傳輸助手」或「檔案傳輸」。
        Login successfully as 陳厚成0922
        OK itchat :> send("abc","filehelper") . cr
        {'BaseResponse': {'Ret': 0, 'ErrMsg': '请求成功', 'RawMsg': '请求成功'}, 'MsgID': '8504523964048646048', 'LocalID': '15107911818667'}
        OK
        
[x] Your wechat account may be LIMITED to log in WEB wechat, error info:
    <error><ret>1203</ret><message>為了你的帳號安全，新註冊的WeChat帳號不能登入網頁WeChat。你可以使用Windows WeChat或Mac WeChat在電腦端登入。 Windows WeChat下載網址：https://pc.weixin.qq.com  Mac WeChat下載網址：https://mac.weixin.qq.com</message></error>
    OK    
    --> Try login the real WeChat web, ok, then try again ... ok!
    --> 又來了！這回連 Chrome 上 login 也失敗！--> 換電腦也一樣！！！
        OK     itchat :: auto_login()
        Getting uuid of QR code.
        Downloading QR code.
        Please scan the QR code to log in.
        Please press confirm on your phone.
        Your wechat account may be LIMITED to log in WEB wechat, error info:
        <error><ret>1203</ret><message>為了你的帳號安全，新註冊的WeChat帳號不能登入網頁WeChat。你可以使用Windows WeChat或Mac WeChat在電腦端登入。 Windows WeChat下載網址：https://pc.weixin.qq.com  Mac WeChat下載網址：https://mac.weixin.qq.com</message></error>
        OK     itchat :: auto_login()
        Getting uuid of QR code.
        Downloading QR code.
        Please scan the QR code to log in.
        Please press confirm on your phone.
        Log in time out, reloading QR code.
        Getting uuid of QR code.
        Downloading QR code.
        Please scan the QR code to log in.
        Please press confirm on your phone.
        Your wechat account may be LIMITED to log in WEB wechat, error info:
        <error><ret>1203</ret><message>為了你的帳號安全，新註冊的WeChat帳號不能登入網頁WeChat。你可以使用Windows WeChat或Mac WeChat在電腦端登入。 Windows WeChat下載網址：https://pc.weixin.qq.com  Mac WeChat下載網址：https://mac.weixin.qq.com</message></error>
        OK    
        --> 改試 chc0922 的帳號就可以了 
        Login successfully as 陳厚成0922
        --> 可能是有裝 app 的電腦就不能用 web 版 
            --> Try vmware ubuntu box ... OK! 
                證明不是 account 的問題，因為換了 Ubuntu 就可以了。
[x] 正點！直接用 DOSBox 畫出 QR code ! itChat's README.md @ GitHub 有介紹
    itchat.auto_login(enableCmdQR=True)
    # 如部分的linux系统，块字符的宽度为一个字符（正常应为两字符），故赋值为2
    itchat.auto_login(enableCmdQR=2)
    默认控制台背景色为暗色（黑色），若背景色为浅色（白色），可以将enableCmdQR赋值为负值：
    itchat.auto_login(enableCmdQR=-1)
    --> 查看 itchat 的 QR code 產生器。。。 
        OK modules qr
        pyqrcode pyqrcode.tables pyqrcode.builder
        OK
        from pyqrcode import QRCode <-- login.py of itchat
        Downloading pypng-0.0.18.tar.gz (377kB) # itchat installs them too
        Downloading PyQRCode-1.2.1.zip (41kB)   # itchat installs them too     
    --> 搞懂了！ see this one liner ...
        cls pyqrcode :> create("12345").terminal('white','blue') . cr \ default color is ('black','gray') 
        cls pyqrcode py: help(pop()) \ see its very rich help
[ ] 
    [ ] 一定要 itchat.run() 之後才有效


    import itchat constant itchat py: last().type='value.outport' // ( -- module ) WeChat automation
    itchat :: auto_login()
    <accept> <text> 
    # ------------ get what we want --------------------------
    @itchat.msg_register([itchat.content.PICTURE, itchat.content.RECORDING, itchat.content.ATTACHMENT, itchat.content.VIDEO])
    def download_files(msg):
        with open('o.txt', 'w') as f:
            ok('11>> ',loc=locals(),cmd='cr')
            d = msg.download(msg.fileName)
            f.write(d)
    # ------------ get what we want --------------------------
    # dictate("--- marker ---"); outport(locals()) # bring out all things
    </text> -indent py: exec(pop(),globals(),harry_port())
    </accept> dictate 

TypeError: download() missing 1 required positional argument: 'fileName'
TypeError: a bytes-like object is required, not 'ReturnValue' <--- open(fname,'wb') 之故？對！
TypeError: write() argument must be str, not ReturnValue
TypeError: write() argument must be str, not ReturnValue

msg.downlaod() 傳回 status object, 實際檔案不是直接傳回的 ......

OK itchat :> get_friends().__len__() . cr
0  <---- zero means status is logout 
OK

check_login() 即使已經 logout 他也回 400 搞不懂
OK itchat :> check_login py: help(pop())
Help on method check_login in module itchat.components.login:
check_login(uuid=None) method of itchat.core.Core instance

OK



    
    <accept> <text> 
    # ------------ get what we want --------------------------
    ok('11>> ',loc=locals(),cmd='cr') # itchat.run() 之後無效了
    # ------------ get what we want --------------------------
    # dictate("--- marker ---"); outport(locals()) # bring out all things
    </text> -indent py: exec(pop(),globals(),harry_port())
    </accept> dictate 


@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
    msg.download(msg.fileName)
    itchat.send('@%s@%s' % (
        'img' if msg['Type'] == 'Picture' else 'fil', msg['FileName']),
        msg['FromUserName'])
    return '%s received' % msg['Type']
    
    import itchat constant itchat py: last().type='value.outport' // ( -- module ) WeChat automation
    itchat :: auto_login()
    <accept> <text> 
    # ------------ get what we want --------------------------
    @itchat.msg_register([itchat.content.PICTURE, itchat.content.RECORDING, itchat.content.ATTACHMENT, itchat.content.VIDEO])
    def download_files(msg):
        msg.download(msg.fileName)
        ok('11>> ',loc=locals(),cmd='cr')
        itchat.send('@%s@%s' % (
            'img' if msg['Type'] == 'Picture' else 'fil', msg['FileName']),
            msg['FromUserName'])
        return '%s received' % msg['Type']

    # ------------ get what we want --------------------------
    # dictate("--- marker ---"); outport(locals()) # bring out all things
    </text> -indent py: exec(pop(),globals(),harry_port())
    </accept> dictate 

    
[ ]         
[ ]         
[ ]         
[ ]         
[ ]         

