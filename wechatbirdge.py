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

def logout():
    STATUS=False
    print('WECHAT_LOGGED_OUT')

def login():
    STATUS=True
    print('WECHAT_LOGGED_IN')

def sendr(sock,header,response=None):
    try:
        sock.send(header.encode('utf-8'))
        sock.send(response)
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
            soc, addr=So.accept()
            data=soc.recv(1024)
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
                if switch==False:
                    switch=True
                else:
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
                datanew=data.decode('utf-8')
                senddata=datanew.split('\r\n\r\n')
                print('SENDDATA',senddata)
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
