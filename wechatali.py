import os
import json
import requests
import socket
print('WECHATMSG VER 2124 IMPORTED')
sendswitch=False

def getresult(requestraw):
    global sendswitch
    print(requestraw)
    jsonout=json.loads(requestraw)
    print('JSONOUT')
    command={}
    #print(jsonout)
    for x in jsonout['slotEntities']:
        print(x['intentParameterName'],x['originalValue'])
        command[x['intentParameterName']]=x['originalValue']
    print(jsonout['intentId'])
    if 'com' in command:
        if command['com']=='下一条' or command['com']=='继续':
            print('继续')
            try:
                rst=requests.get('http://localhost:8562/nextmsg').text
                print(rst)
                if rst=='':
                    return requests.get('http://localhost:8562/count').text
                else:
                    return rst
            except:
                return '微信登陆失效'
        if command['com']=='全部' or command['com']=='所有':
            print('all')
            try:
                rst=requests.get('http://localhost:8562/getmsg').text
                if rst=='':
                    return requests.get('http://localhost:8562/count').text
                else:
                    return rst
            except:
                return '微信登陆失效'
        if command['com']=='发消息':
            print('发消息')
            try:
                if sendswitch==False:
                    sendswitch=True
                else:
                    sendswitch=False
                    reqs=command['touser']+'$$'+command['msg']
                    so=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    so.connect(('localhost',8562))
                    sox='POST /send HTTP/1.1\r\n\r\n'+command['touser']+'$$'+command['msg']
                    so.send(sox.encode('utf-8'))
                    rst=str(so.recv(1024).decode('utf-8')).split('\r\n\r\n')
                    print(rst[1])
                    #print(rst)
                    return rst[1]
            except:
                print('unable')
                return '由于系统原因发送失败'
    print(command)
    return 

def packresult(result,code=0,message=None,type='RESULT',askinfo=[],intentid=0,excode='SUCCESS'):
    #PACK RESULT
    jsonpackprep={'returnCode':str(code)}
    if message!=None:
        if code!=0:
            jsonpackprep['returnErrorSolution']=message
        else:
            jsonpackprep['returnMessage']=message
    jsonpackprep['returnValue']={}
    jsonpackprep['returnValue']['reply']=result
    jsonpackprep['returnValue']['resultType']=type
    if type=='ASK_INF':
        infox=[]
        for x in askinfo:
            infox.append({'parameterName':x,'intentId':intentid})
        jsonpackprep['returnValue']['askedInfos']=infox
        jsonpackprep['returnValue']['resultType']='ASK_INF'
    else:
        jsonpackprep['returnValue']['resultType']=type
    jsonpackprep['returnValue']['executeCode']=excode
    packed = json.dumps(jsonpackprep, sort_keys=True, indent=4, separators=(',', ': '))
    #print(packed)
    return packed

def procraw(raw):
    print(raw)
    return raw


def proc(raw):
    msg=raw.split()
    #print(msg)
    try:
        if msg[0]==b'POST' and msg[2]==b'HTTP/1.1' and msg[6]==b'ali-genie':
            print('OK')
            msgs=raw.decode('utf-8')
            msgs=str(msgs).split('\r\n\r\n')
            msgfinal=''
            print(msgs)
            for x in range(len(msgs)-1):
                msgfinal=msgfinal+msgs[x+1]+'\n'
            print('MSGFINAL',msgfinal)
            getresult(msgfinal)
            return packresult(getresult(msgfinal))
        return
    except:
        #exccc()
        print('ERROR WHEN SPLITING RAW')
