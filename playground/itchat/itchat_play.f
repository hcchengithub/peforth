
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
    itchat py: vm.itchat=pop(1)

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
    itchat :> search_friends('陳厚成0922')[0] constant chc0922 \ get user object 
    chc0922 :>~ send('Hello H.C.!')
    :> ['BaseResponse']['Ret'] [if] ." Failed!!" cr [else] ." Success!" cr [then]        
    
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
    (default) 'name' is 備註(RemarkName)、昵稱(NickName) 其中的任何一項「全等於」name
    'userName' is dynamic UUID 
    'nickName' is 昵稱「全等於」name, 但「聊天室」就變成「有出現」 即可。
    'RemarkName' is 備註，也是 name 會搜尋的 key.
    'wechatAccount' 用不上, get_friends() 裡面沒有

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
    
    \ DOSBox 下 Wendy 的 nickName 呈現為 '???', chcp 950 (Big-5) or 65001 (utf-8) 
    \ 皆然。但是從 npp editor 這裡 copy-paste 過去到 DOSBox 下的 python peforth 
    \ 執行是可以的，只有簡體字「呈現」的問題而已，連 copy 過來都還是好的。
    dropall itchat :> search_friends(nickName='马玮赟') .s
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
    
    OK itchat :> search_friends() . cr  \ 當 arg empty 時傳回自己
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

    \ search_friends() 的 arg 之 default 是本人，第一個 arg 之 default 是 'name'
    \ name arg 必須全等，含大小寫。從以上 dump 來看，只有 NickName 存在，但 
    \ 'RemarkName' 如果全等應該也可以。https://itchat.readthedocs.io/zh/latest/

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
    itchat :> search_chatrooms('小大大客服群') <--- 還是找不到 [X] 奇怪 <-- RI
    [x] 怎麼沒有 小多 小囡 客服群的聊天室？
        itchat :> get_chatrooms() py> len(pop()) tib. \ ==> 0 (<class 'int'>) ！！！！
        --> 保存「聊天室」到「通訊錄」之後，好了！！
        itchat :> get_chatrooms() py> len(pop()) tib. \ ==> 1 (<class 'int'>)
        OK        
    
[x] 用對方的 User Object 而非 nickName 才是好辦法
    dropall itchat :> search_friends('陳厚成0922')[0] constant chc0922 
    // ( -- obj ) WeChat user object

    author = itchat.search_friends('LittleCoder')[0]
    author.send('greeting, littlecoder!')

    OK itchat :> search_friends('hcchen5600') :> [0] constant hcchen5600
    OK hcchen5600 type . cr
    <class 'itchat.storage.templates.User'>

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
    itchat :> check_login() tib. \ ==> 200 (<class 'str'>) <--- login successful 

    API Document https://itchat.readthedocs.io/zh/latest/api/

    [x] check_login() 即使已經 logout 他也回 400 搞不懂，表示回 200 或 400 都
        沒有意義，因為兩個值代表 login 或 logout 都有可能。
        OK itchat :> check_login py: help(pop())
            Help on method check_login in module itchat.components.login:
            check_login(uuid=None) method of itchat.core.Core instance
    [x] 想要查 check_login status, 用替代方法：
        OK itchat :> get_friends().__len__() . cr
        0  <---- zero means status is logout 
        \ 此法證實有效
        11>> itchat :> get_friends().__len__() . cr
        117
        11>> itchat :> logout()
        LOG OUT!
        11>> . cr
        {'BaseResponse': {'ErrMsg': '请求成功', 'Ret': 0, 'RawMsg': 'logout successfully.'}}
        11>> itchat :> get_friends().__len__() . cr
        0
        11>>

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
    --> X1 Yoga was same, but now in C-sotre ok now!!
        WeChat web ok, itchat ok too.

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

[x] itchat echo-er 簡單回應收到檔案的種類與檔名
    https://www.shiyanlou.com/courses/684/labs/2237/document
    [x] 用 @decorater register event handler 一定要 itchat.run() 之後才有效
    [x] 這個 demo 收各種檔案並回覆 message 給 sender
        <py>
        import itchat; outport(locals())
        itchat.auto_login()
        @itchat.msg_register(itchat.content.TEXT)
        def print_content(msg):
            return msg['Text']
        @itchat.msg_register([itchat.content.PICTURE, itchat.content.RECORDING, itchat.content.ATTACHMENT, itchat.content.VIDEO])
        def download_files(msg):
            # f.write(data) 當中 data 要給 byte-like object，原文傳回值是個 status object 不對。
            # with open(msg.fileName, 'wb') as f:
            #     f.write(msg.download(msg.fileName))
            # 光這樣就可以了，自動會存進 working directory
            msg.download(msg.fileName) 
            # getattr(vm,context)['msg'] = msg # or simply outport()
            outport(locals())
            return msg.fileName + ' received' 
        itchat.run(
            debug=True,        # 多出一些 message 
            blockThread=False  # 這樣就不會 block 住了，所以下面的 peforth.ok() 緊跟著上手。
            )
        ok('itchat_2> ',glo=globals(),loc=locals(),cmd='cr')
        </py>

    [x] 同上，多了 echo 所收到的檔案
        <py>
        import itchat; outport(locals())
        itchat.auto_login()
        # ------------ get what we want --------------------------
        @itchat.msg_register(itchat.content.TEXT)
        def print_content(msg):
            return msg['Text']
        @itchat.msg_register([itchat.content.PICTURE, itchat.content.RECORDING, itchat.content.ATTACHMENT, itchat.content.VIDEO])
        def download_files(msg):
            msg.download(msg.fileName)
            itchat.send('@%s@%s' % (
                'img' if msg['Type'] == 'Picture' else 'fil', msg['FileName']),
                msg['FromUserName'])
            outport(locals())
            return '%s received' % msg['Type']
        itchat.run(
            debug=True,        # 多出一些 message 
            blockThread=False  # 這樣就不會 block 住了，所以下面的 peforth.ok() 緊跟著上手。
            )
        ok('itchat_2> ',glo=globals(),loc=locals(),cmd='cr')
        </py>

    [x] 上面兩個方法 (刪掉了，用 <text> dictate 想繼承 peforth 的 value.outport 
        things) 對 event handler 來說太挑戰了，
        <py>
        #
        # 執行後，從手機端傳照片給自己（hcchen5600可以），過會兒就會收到
        # 從本程式 echo 回手機的同一張照片以及 'Picture received' message.
        #
        import itchat 
        itchat.auto_login()
        @itchat.msg_register([itchat.content.PICTURE, itchat.content.RECORDING, itchat.content.ATTACHMENT, itchat.content.VIDEO])
        def download_files(msg):
            # 抓好以後用 "@img@171118-141101.png" or "@fil@filename" access 該 file
            # 實際抓到 working directory 下
            msg.download(msg.fileName)
            # "@img@171118-141101.png" or "@fil@filename" 不只是字串而已，真的會把檔案送出去！
            itchat.send('@%s@%s' % (
                'img' if msg['Type'] == 'Picture' else 'fil', msg['FileName']),
                msg['FromUserName'])
                # 這個 send() 真的會把該檔案 echo 回去！
            return '%s received' % msg['Type']  # 手機端收到 'Picture received' string
            # return string 傳回給 msg['FromUserName']
        ok('itchat_1> ',cmd='cr')
        itchat.run(
            debug=False, 
            blockThread=False  # 這樣就不會 block 住了，所以下面的 peforth.ok() 緊跟著上手。
            )
        ok('itchat_2> ',glo=globals(),loc=locals(),cmd='cr')
        </py>

    
[x] run() 了以後，怎麼停下來？ --> blockThread=False 即可
    但是 blockThread=False 有諸多問題：
    [x] blockThread=False 時 Friend 傳來視訊或語音時，itchat 端就會斷掉。
        blockThread=True 就可以避免
    [x] Event handler 內部的 peforth breakpoint isGroupChat> 與最後的 
        itChat> 交替出現, 一 exit 就整個結束
        經 blockThread=True --> 果然就好了！！！

    OK itchat :> run py: help(pop())
    Help on method run in module itchat.components.register:
    run(debug=False, blockThread=True) method of itchat.core.Core instance

    Login successfully as 陳厚成0922
    itchat> import itchat constant itchat
    itchat :> send('@img@171118-175505.png','hcchen5600') tib. \ ==> {'BaseResponse': {'Ret': -1, 'ErrMsg': '', 'RawMsg': ''}, 'MsgID': '', 'LocalID': ''} (<class 'itchat.returnvalues.ReturnValue'>)
    itchat> itchat :> find_friends('hcchen5600')
    itchat> itchat :> search_friends('hcchen5600')
    itchat> :> [0] constant hcchen5600
    hcchen5600 :> send('hello') tib. \ ==> {'BaseResponse': {'Ret': 0, 'ErrMsg': '请求成功', 'RawMsg': '请求成功'}, 'MsgID': '3601277865234063183', 'LocalID': '15109991699778'} (<class 'itchat.returnvalues.ReturnValue'>)
    hcchen5600 :> send('@fil@1') tib. \ ==> {'BaseResponse': {'Ret': 0, 'ErrMsg': '请求成功', 'RawMsg': '请 求成功'}, 'MsgID': '2897197281269928857', 'LocalID': '15109993423516'} (<class 'itchat.returnvalues.ReturnValue'>)
    itchat> hcchen5600 :> send('@fil@1.txt') tib.
    hcchen5600 :> send('@fil@1.txt') tib. \ ==> {'BaseResponse': {'Ret': 0, 'ErrMsg': '请求成功', 'RawMsg': '请求成功'}, 'MsgID': '9023165568502968432', 'LocalID': '15109993732982'} (<class 'itchat.returnvalues.ReturnValue'>)
    itchat>

[x] 在使用个人微信的过程当中主要有三种账号需要获取 https://itchat.readthedocs.io/zh/latest/intro/contact/        
    •好友 friends •公众号 mps •群聊 chatrooms
    itchat_2> itchat :> get_friends() <py> [ n.nickName for n in tos() ]</pyV> . cr
    ['陳厚成0922', 'hcchen5600', 'Ada', 'dada', 'Natalie', 'coder']
    itchat_2> itchat :> get_contact() <py> [ n.nickName for n in tos() ]</pyV> . cr
    ['☆☆ 熱情 MAMA MIA 洋溢 ☆☆', 'test,coder,华,陳厚成0922,hcchen5600', 'WeChat remote control Lab']
    itchat_2> itchat :> get_chatrooms() <py> [ n['NickName'] for n in tos() ]</pyV> . cr
    ['☆☆ 熱情 MAMA MIA 洋溢 ☆☆', 'test,coder,华,陳厚成0922,hcchen5600', 'WeChat remote control Lab']
    itchat_2> itchat :> get_contact(update=True) <py> [ n['NickName'] for n in tos() ]</pyV> . cr
    ['test,coder,华,陳厚成0922,hcchen5600', 'WeChat remote control Lab']
    --> 好像 contact 就是 chatrooms
    --> 不知 update 何義？ --> 上網重抓，而非直回 memory 裡的資料
    itchat_2> itchat :> get_chatrooms(update=True) <py> [ n['NickName'] for n in tos() ]</pyV> . cr
    ['☆☆ 熱情 MAMA MIA 洋溢 ☆☆', 'test,coder,华,陳厚成0922,hcchen5600', 'WeChat remote control Lab']
    itchat_2> itchat :> get_chatrooms(contactOnly=True) <py> [ n['NickName'] for n in tos() ]</pyV> . cr
    ['test,coder,华,陳厚成0922,hcchen5600', 'WeChat remote control Lab']
    itchat_2>    

[ ] 通过如下代码，微信已经可以就日常的各种信息进行获取与回复。
    https://itchat.readthedocs.io/zh/latest/
    
    {} value itchat // ( -- module ) WeChat automation
    {} value msg // ( -- dict ) WeChat received message 
    <py>
    import itchat
    from itchat.content import * # TEXT PICTURE 等 constant 的定義
        # Failed in compyle command : import * only allowed at module level 
        # 因此本程式適合用 .py 直接執行
    @itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
    def text_reply(msg):
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
        if msg.isAt:
            msg.user.send(u'@%s\u2005I received: %s' % (
                msg.actualNickName, msg.text))
    pdb.set_trace() # 222

    itchat.auto_login(True)  # hotReload=True
    itchat.run(True, blockThread=False) # debug=True 
    outport(locals()) 
    ok('itchat> ',cmd='cr')
    </py>


[x] debug isGroupChat 時，發現 function name 都是 text_reply() 
    decorator 裡好像這個無所謂，其實是個 anonymous function。
[x] 不會 echo chatroom 的 msg.isAt message <== bug!
    RI: msg.isAt 是 False !! 所以沒反應。 --> FP: 不考慮 msg.isAt 即可。
    目前 itchat v1.3.10 , msg.isAt 我查看都是 False 所以來自作者 demo 的這段 code 無反應
    ```
    @itchat.msg_register(TEXT, isGroupChat=True)
    def text_reply(msg):
        if msg.isAt:
            msg.user.send(u'@%s\u2005I received: %s' % (
                msg.actualNickName, msg.text))
    ```
    還是有問題呀！是同一個問題嗎？  ---> #425 可能就是答案
    或者根本沒問題！要加 @name 才回答
        
[ ] Unexpected sync check result: window.synccheck={retcode:"1101",selector:"0"}
    LOG OUT!
    See https://github.com/littlecodersh/ItChat/issues/441
    --> 改寫成 itchat_remote_peforth2.py 希望用自動重起的方式避開問題。
    
[x] WeChat 傳訊息，不能太大，要分 chunk 傳，或者打包成 file 來傳 -- 兩個都要
    <accept> <text> 
    def send_chunk(text, send, pcs=2000):
        s = text
        while True:
            if len(s)>pcs:
                print(s[:pcs]); send(s[:pcs])
            else:
                print(s); send(s)
                break
            s = s[pcs:]    
    push(send_chunk)
    </text> -indent py: exec(pop())
    </accept> dictate constant send_chunk // ( -- function ) send a chunk to Wechat
    /// Where send can be itchat.send or msg.user.send up to the caller

    \ 成功！
    itChat> hcchen5600 :> send send_chunk :> ("lalalalsdfsdsdfdsfdsfdsfdsfsdfala",pop(),3)

[x] Moniter UUT
    \ UUT is running AI training, also running itchat_remote_peforth.py
    \ from my OA computer control the UUT through WeChat :
    import PIL.ImageGrab constant im 
        \ 取得 PIL 圖像處理工具
        // ( -- module ) PIL.ImageGrab
    im tib. \ ==> <module 'PIL.ImageGrab' from 'C:\\Users\\YY\\AppData\\Local\\Programs\\Python\\Python36\\lib\\site-packages\\PIL\\ImageGrab.py'>
    im :> grab() value grab \ or 'to grab'
        \ 抓好桌面畫面
        // ( -- obj ) full screen
    grab :> size tib. \ ==> (1536, 864) (<class 'tuple'>) 圖片大小，看好玩的。
    grab :> mode tib. \ ==> RGB (<class 'str'>) 圖片種類，看好玩的。
    grab :: save("1.jpg") \ 圖片存檔。用 cd command 即可看到 working directory 在哪。
    \ 準備由 WeChat 把圖片送到遠端（OA or Cell phone）來
    py> sys.modules['itchat'] constant itchat 
        \ 取得 itchat module object 
        // ( -- module ) WeChat automation
    itchat :> search_friends('hcchen5600')[0] constant hcchen5600 
        \ 取得聯絡對象
        // ( -- obj ) WeChat friend
    hcchen5600 :> send("@img@1.jpg") tib. \ ==> {'BaseResponse': {'Ret': 0, 'ErrMsg': '请求成功', 'RawMsg': '请求成功'}, 'MsgID': '7603896662611832927', 'LocalID': '15120087471654'} (<class 'itchat.returnvalues.ReturnValue'>)
        \ 圖片送過來，成功了！
        
    : check ( -- ) // check UUT
        im :> grab() to grab
        grab :: save("1.jpg") 
        hcchen5600 :> send("@img@1.jpg")
        . cr ;
[x] 改用 chatroom 其他同上
    \ 用部分 nickName 取得 chatroom object 
    itchat :> search_chatrooms('ITLAB')[0] constant itlab // ( -- obj ) ITLAB chatroom object
    : check ( -- ) // check UUT
        im :: grab().save("1.jpg") 
        itlab :> send("@img@1.jpg")
        . cr ;

[x] check command 的完整設定過程，讓 UUT 回覆它的畫面：
    \ UUT 注意要領：
        [ ] 跑 demo2.py 以及 itchat bot ～\GitHub\peforth\playground\itchat\itchat_remote_peforth.py 
        [ ] power saving setting AC 'never' sleep 
    \ 完整設定過程，讓 UUT 回覆它的畫面經由 itchat bot 傳給 AILAB Chatroom.
    \ 讓遠端可以來監看執行狀況。這段程式是由遠端灌過來給 UUT 的。
        \ 取得 itchat module object. UUT 的 peforth 是
        py> sys.modules['itchat'] constant itchat // ( -- module ) WeChat automation
        \ 取得 PIL 圖像處理工具
        import PIL.ImageGrab constant im // ( -- module ) PIL.ImageGrab
        \ 用部分 nickName 取得 AILAB chatroom object 
        itchat :> search_chatrooms('AILAB')[0] constant ailab // ( -- obj ) AILAB chatroom object
        \ 定義 check command :
        import time constant time // ( -- module )
        cr time :> ctime() . cr \ print recent time on UUT when making this setting
        : check ( -- ) // check UUT
            time :: sleep(7) \ 固定 anti-robot delay time 7 sec.
            cr time :> ctime() . cr \ print the recent time on UUT 
            im :: grab().save("1.jpg") \ 抓 Screenshot 
            \ Windows 10 的顯示比例設定不要改 100% 就是全螢幕。
            ailab :> send("@img@1.jpg") \ 結果都送到 AILAB chatroom 
            . cr ;
        \ 完成設定，可以從遠端下達 @<版主> check 命令取得 UUT 畫面了。
        \ ( 注意！ 注意！ ) exit \ 現在 console() 裡改用 peforth.ok() 可能就要記得 exit 
        
        : getfile ( "pathname" -- ) // Get source code for debugging
            time :: sleep(7) \ 固定 anti-robot delay time 7 sec.
            py> str(pop()).strip() \ 整理 pathname 
            s" @fil@" swap + \ command string 
            cr time :> ctime() . space s" getfile: " . dup . cr
            ailab :> send(pop()) \ 傳送到 AILAB chatroom 
            . cr \ 顯示打印結果
            ;

[ ]         
[ ]         
[ ]         
[ ]         


