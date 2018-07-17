import socket
from socket import *
import _thread
import os
import time
from wxpy import *
import base64
STATUS=False
unread=[]
switch=False
msgsent=[]
clearswitch=0

def logout():
    STATUS=False
    print('WECHAT_LOGGED_OUT')

def login():
    STATUS=True
    print('WECHAT_LOGGED_IN')

def sendr(sock,header,response=None):
    try:
        sock.send(header.encode('utf-8')+response)
        sock.close()
    except:
        ex
        print('DATA SEND ERR')
        

def api():
    global So
    while True:
        try:
            global unread
            global switch
            global clearswitch
            soc, addr=So.accept()
            data=soc.recv(2048)
            print('New API request!')
            msgs=data.split()
            print('Source:',msgs[1].decode('utf-8'))
            source=msgs[1].decode('utf-8')
            if source=='/getmsg':
                print('200')
                header='HTTP/1.1 200 OK\nContent-type: text/html; charset=utf-8\r\n\r\n'
                msgtxt=''
                print(unread)
                for x in range(len(unread)):
                    msgtxt=msgtxt+unread[x]['name']+'说:'+unread[x]['content']+'\n'
                if switch==False:
                    switch=True
                else:
                    switch=False
                    unread.clear()
                sendr(soc,header,msgtxt.encode('utf-8'))
            elif source=='/nextmsg':
                print('next')
                header='HTTP/1.1 200 OK\nContent-type: text/html; charset=utf-8\r\n\r\n'
                try:
                    cont=unread[0]['name']+'说:'+unread[0]['content']
                except:
                    cont=''
                print('CONT',cont)
                sendr(soc,header,cont.encode('utf-8'))
                if switch==True:
                    switch=True
                else:#SWITCH CANCELLED
                    switch=False
                    unread.pop(0)
            elif source=='/count':
                header='HTTP/1.1 200 OK\nContent-type: text/html; charset=utf-8\r\n\r\n'
                if len(unread)==0:
                    rpy='你没有新消息'
                else:
                    rpy='你有'+str(len(unread))+'条新消息'
                sendr(soc,header,rpy.encode('utf-8'))
            elif source=='/send':
                header='HTTP/1.1 200 OK\nContent-type: text/html; charset=utf-8\r\n\r\n'
                try:
                    datanew=data.decode('utf-8')
                    print('DATANEW',datanew)
                    senddata=datanew.split('\r\n\r\n')
                    print('SENDDATA',senddata[1])
                    frd=senddata[1]
                    frd=frd.split('$$')
                    try:
                        print(frd[0])
                        friendobj=ensure_one(bot.friends().search(frd[0]))
                        #bot.friends.search(frd[0]) 存在问题
                    except:
                        print('FRIEND_SEARCH_ERR')
                        rpy='''无法找到指定好友或有多个重名好友'''
                        sendr(soc,header,rpy.encode('utf-8'))
                        continue
                    try:
                        msgsent.append({'sent':friendobj.send(frd[1]),'timestamp':time.time()})
                        rpy='''消息发送成功'''
                        sendr(soc,header,rpy.encode('utf-8'))
                        clearswitch=clearswitch+1
                        popswitch=[]
                        try:
                            if clearswitch>=10:
                                for x in range(len(msgsent)):
                                    if int(msgsent[x]['timestamp'])-int(time.time())>=121:
                                        popswitch.append(x)
                                clearswitch=0
                                for x in range(len(popswitch)):
                                    print('deleted',msgsent[popswitch[-x]])
                                    msgsent.pop(popswitch[-x])
                        except:
                            print('unable to delete sent msg.')
                        print('发送成功')
                    except:
                        rpy='''消息发送失败'''
                        sendr(soc,header,rpy.encode('utf-8'))                       
                except:
                    rpy='''服务异常,请稍后再试'''
                    sendr(soc,header,rpy.encode('utf-8'))                        
                    print('ERR_SEND')
            elif source=='/recall':
                print('撤回消息')
                header='HTTP/1.1 200 OK\nContent-type: text/html; charset=utf-8\r\n\r\n'
                if int(msgsent[-1]['timestamp'])-int(time.time())>=120:
                    print('超时')
                    msgsent.clear()
                    clearswitch=0
                    rpy='消息超过两分钟,撤回超时'
                    sendr(soc,header,rpy.encode('utf-8'))
                if len(msgsent)==0:
                    print('没有要撤回的消息')
                    rpy='没有要撤回的消息'
                    sendr(soc,header,rpy.encode('utf-8'))
                else:
                    try:
                        msgsent[-1]['sent'].recall()
                        msgsent.pop(-1)
                        print('撤回成功')
                        rpy='撤回成功'
                        sendr(soc,header,rpy.encode('utf-8'))
                    except:
                        print('撤回失败')
                        rpy='撤回失败'
                        sendr(soc,header,rpy.encode('utf-8'))
            else:
                print('404')
                header='HTTP/1.1 404 Not Found\nContent-type: text/html; charset=utf-8\r\n\r\n'
                display='''API Not Found!'''
                sendr(soc,header,display.encode('utf-8'))
            print('PROC')
        except:
            continue
def qr(uuid,status,qrcode):
    with open('qr.png','wb') as f:
        f.write(qrcode)
So=socket(AF_INET,SOCK_STREAM)
So.bind(('localhost',8562))
So.listen(5)
bot=Bot(console_qr=True,qr_callback='qr',cache_path='wechatbridge',qr_path='wechatbridgeqr.png',logout_callback='logout',login_callback='login')
@bot.register(Friend,TEXT)
def ftmsg_recv(msg):
    global unread
    print(msg)
    print(msg.sender.remark_name,msg.sender.nick_name,msg.text)
    if msg.sender.remark_name=='':
        unread.append({'name':msg.sender.nick_name,'content':msg.text,'type':'text'})
    else:
        unread.append({'name':msg.sender.remark_name,'content':msg.text,'type':'text'})
    print('UNREAD',unread)
_thread.start_new_thread(api,())
bot.join()
