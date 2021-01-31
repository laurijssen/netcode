import socket
import paramiko
import threading
import sys

host_key = paramiko.RSAKey(filename='test_rsa.key')

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        print('check pw')
        if username == 'laurijssen' and password == 'test':
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

server = sys.argv[1]
ssh_port = int(sys.argv[2])

try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((server, ssh_port))
    server_socket.listen(20)
    client, addr = server_socket.accept()

except Exception as e:
    print('listen failed: ' + str(e))
    sys.exit(1)

print('connection success')

try:
    session = paramiko.Transport(client)
    session.add_server_key(host_key)
    server = Server()
    try:
        session.start_server(server=server)
    except paramiko.SSHException as x:
        print('ssh nego failed')

    chan = session.accept(20)
    print('authenticated')
    print(chan.recv(1024))
    chan.send('connected ssh')
    while True:
        try:
            cmd = input('enter: ').strip('\n')
            if cmd != 'exit':
                chan.send(cmd)
                print(chan.recv(1024).decode('ascii') + '\n')
            else:
                chan.send('exit')
                print('exit')
                session.close()
                raise Exception('exit')
        except KeyboardInterrupt:
                session.close()
except Exception as e:
    print('caught ' + str(e))
    try:
        session.close()
    except:
        pass
    sys.exit(1)