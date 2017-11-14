
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
    itchat :: auto_login() \ return None anyway
    itchat :> check_login() char 400 = [if] ." Login: Success!" cr [else] ." Login: Failed!!" cr [then]
    
    \ send hello world to myself
    itchat :> send("中文也可以") :> ['BaseResponse']['Ret'] 
    [if] ." Failed!!" cr [else] ." Success!" cr [then]

    \ send message to a friend
    itchat :> search_friends(nickName='陳厚成0922')[0] constant chc0922 \ get user object 
    chc0922 :>~ send('Hello H.C.!')
    :> ['BaseResponse']['Ret'] [if] ." Failed!!" cr [else] ." Success!" cr [then]        
    
    
    
    [x] Your wechat account may be LIMITED to log in WEB wechat, error info:
        <error><ret>1203</ret><message>為了你的帳號安全，新註冊的WeChat帳號不能登入網頁WeChat。你可以使用Windows WeChat或Mac WeChat在電腦端登入。 Windows WeChat下載網址：https://pc.weixin.qq.com  Mac WeChat下載網址：https://mac.weixin.qq.com</message></error>
        OK    
        --> Try login the real WeChat web, ok, then try again ... ok!
        
    OK itchat . cr
    <module 'itchat' from 'C:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36\\lib\\site-packages\\itchat\\__init__.py'>
    
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
        OK itchat :> dump_login_status() tib. \ ==> None
        OK itchat :> check_login() tib. \ ==> 400
        OK itchat :> get_friends() . cr \ dump all friends, that's a big list.
    [x] itchat :: send() 
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
    [x] 當另一個 itchat login 時，前一個就會
        OK LOG OUT!
    [x] c:\Users\hcche\Documents\GitHub\itchat_app\echo.py 
        make PC a WeChat echo-er 
        I have a lot of study there in its comments
    [x] UserName is dynamic UUID, this is the method to get it:

        author = itchat.search_friends(nickName='LittleCoder')[0]
        author.send('greeting, littlecoder!')

        OK itchat :> search_friends(nickName='hcchen5600')
        OK constant hcchen5600
        OK hcchen5600 type . cr
        <class 'list'>   <----------------- 可能找到多個
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
        
        \ 用對方的 User Object 而非 nickName 才是好辦法
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
        OK
        OK chc0922 :> send type . cr
        <class 'method'>
        OK chc0922 :> send('aabbcc')
        OK .s
              1: {'BaseResponse': {'Ret': 0, 'ErrMsg': '请求成功', 'RawMsg': '请求成功'}, 'MsgID': '5323555895877586049', 'LocalID': '15106427029591'} (<class 'itchat.returnvalues.ReturnValue'>)
        
        itchat :> search_friends(nickName='陳厚成0922')[0] constant chc0922 
        chc0922 :>~ send('Hello H.C.!')
        :> ['BaseResponse']['Ret'] [if] ." Failed!!" cr [else] ." Success!" cr [then]        

        \ 
        itchat :> get_chatrooms() py> len(pop()) tib. \ ==> 4 (<class 'int'>)

        \ search_chatrooms 是用 'NickName': '奇迹四阶', 'NickName': '阿公,阿媽,厚伸,厚成,素娟,厚岐', 
        \ 但 argument 是 'name' 或直接給部分的 charroom Name
        OK  itchat :> search_chatrooms py: help(pop())
        Help on method search_chatrooms in module itchat.core:
        search_chatrooms(name=None, userName=None) method of itchat.core.Core instance
        itchat :> search_chatrooms('奇') . cr  <---- 找到 '奇迹四阶'
        itchat :> search_chatrooms('小大大客服群') <--- 還是找不到 [ ] 奇怪！！！
        
        \ [ ] 怎麼沒有 小多 小囡 客服群的聊天室？
        