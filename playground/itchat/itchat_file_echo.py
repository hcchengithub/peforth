<py>
#
# 執行後，從手機端傳照片給自己（hcchen5600可以），過會兒就會收到
# 從本程式 echo 回手機的同一張照片以及 'Picture received' message.
#
import peforth; 
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
itchat.run(
    debug=False, 
    blockThread=False  # 這樣就不會 block 住了，所以下面的 peforth.ok() 緊跟著上手。
    )
peforth.ok('itchat> ')
</py>
