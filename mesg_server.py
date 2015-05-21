import threading
import socket, struct
import codecs

header_struct = struct.Struct('!I') 


def recvall(sock, length):
    blocks = []
    while length:
        block = sock.recv(length)
        if not block:
            raise EOFError('socket closed with %d bytes left'
                           ' in this block'.format(length))
        length -= len(block)
        blocks.append(block)
    return b''.join(blocks)

def get_block(sock):
    data = recvall(sock, header_struct.size)
    (block_length,) = header_struct.unpack(data)
    return recvall(sock, block_length).decode("utf-8")

def put_block(sock, message):
    block_length = len(message)
    sock.send(header_struct.pack(block_length))
    sock.send(message)
    
def server(sock, lock, userlist, pwd, login, online_usr, message):
    i = 0
    j = 0
    print ('Socket name:', sock.getsockname())
    print ('Socket peer:', sock.getpeername())
    while login == 0 :
        account = get_block(sock)
        input_pwd = get_block(sock)
        lock.acquire()
        for i in range(4) :
            if userlist[i] == account :
                if pwd[i] == input_pwd :
                    login = 1
                    mesg = userlist[i].encode("ascii") + b', Welcome'
                    put_block(sock, mesg)
                    mesg = b'1'
                    put_block(sock, mesg)
                    j = i
                    break
        if login == 0 :
            mesg = b'Account or password error'
            put_block(sock, mesg)
            mesg = b'0'
            put_block(sock, mesg)        
        lock.release()

    online_usr.append(userlist[j])
    #online_usr = (set(online_usr))
    #online_usr = list(online_usr)
    
    while True :
        k = 0
        op = get_block(sock)
        if op == 'logout':
            for i in range(4) :
                if userlist[i] == account :
                    break
            online_usr.remove(userlist[i])
            mesg = b'Log out'
            put_block(sock, mesg)
            sock.close()
            break
        elif op == 'listuser':
            mesg = b''
            for k in range(len(online_usr)) :
                if k == len(online_usr)-1 :
                    mesg += online_usr[k].encode("ascii")
                else :
                    mesg += online_usr[k].encode("ascii") + b', '
            put_block(sock, mesg)
        elif op == 'send' :

            error = 0
            mesg = b''
            text = get_block(sock)
            temp = text.split()
            people = temp[0]
            for i in range (4):
                if people == userlist[i] :
                    error = 0
                    j = i
                    break
                error = 1
            if error == 1:
                mesg = b'No user'
                put_block(sock, mesg)
            message[j].append(account)
            for l in range(len(temp)) :
                if len(temp) == 1 :
                    mesg = b'Input Error no message to send'
                    put_block(sock, mesg)
                    error = 1
                    break
                message[j].append(temp[l])
                
            if error == 0:
                mesg = b'Message has sent to ' + people.encode("ascii")
                put_block(sock, mesg)
        elif op == 'check' :
            mesg = b''
            for i in range(4) :
                if account == userlist[i] :
                    j = i
                    break
            if len(message[j]) == 0 :
                mesg = b'No message'
                put_block(sock, mesg)
                continue
            mesg += b'Send from ' + message[j][0].encode("ascii") + b' Message :'
            for i in range(1,len(message[j])):
                if i == len(message[j]) -1 :
                    mesg += message[j][i].encode("ascii")
                else :
                    mesg += message[j][i].encode("ascii") + b' '
            message[j] = []
            put_block(sock, mesg)
        elif op == 'broadcast' :
            mesg = b''
            text = get_block(sock)
            for i in range(len(online_usr)) :
                for j in range(4):
                    if online_usr[i] ==userlist[j] :
                        break
                message[j].append(account)
                message[j].append(text)
            mesg = b'Message has sent'
            put_block(sock, mesg)
    
if __name__ == '__main__':
    userlist = ['John', 'Lisa', 'Alfonzo', 'May']
    userlist_pwd = ['123', '456', '789', '000']
    online = []
    temp1 = []
    temp2 = []
    temp3 = []
    temp4 = []
    message_queue = [temp1, temp2, temp3, temp4]
    lock = threading.Lock()
    login = 0
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('127.0.0.1', 1060))
    sock.listen(1)
    print('Listening at', sock.getsockname())
    while True :
        sc, sockname = sock.accept()
        t = threading.Thread(target = server, args=(sc, lock, userlist, userlist_pwd, login, online, message_queue))
        t.start()
        print ('We have accepted a connection from', sockname)
        
        


