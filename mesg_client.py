import threading
import socket, struct
import getpass

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
    
    
if __name__ == '__main__':
    login = '0'
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 1060))

    while True :
        s = 0
        while login == '0' :
            account = input('Account  :').encode("ascii")
            pwd = getpass.getpass("Enter your password:").encode("ascii")
            put_block(sock, account)
            put_block(sock, pwd)
            mesg = get_block(sock)
            login = get_block(sock)
            print (mesg)
        if s == 0:
            tp = b'check'
            put_block(sock, tp)
            asd = get_block(sock)
            s = 1
            if asd != 'No message' :
                print (asd)
            
        op = input('operation :').encode("ascii")
        if op == b'logout' :
            put_block(sock, op)
            mesg = get_block(sock)
            print (mesg)
            sock.close()
            login = '0'
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', 1060))
        elif op == b'listuser' :
            put_block(sock, op)
            mesg = get_block(sock)
            print (mesg)
        elif op == b'send' :
            to = input('sendto and text :').encode("ascii")
            put_block(sock, op)
            put_block(sock, to)
            mesg = get_block(sock)
            print (mesg)
        elif op == b'check' :
            put_block(sock,op)
            mesg = get_block(sock)
            print (mesg)
        elif op == b'broadcast' :
            put_block(sock, op)
            text = input('Message :').encode("ascii")
            put_block(sock, text)
            mesg = get_block(sock)
            print(mesg)
            
        #else :
            #print ('Error input')
        
    
