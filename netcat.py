import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

def execute(cmd):
    cmd = cmd.strip()

    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Net tool', formatter_class=argsparse.RawDescriptionHelpFormatter,
                                    epilog=textwrap.dedent('''Example:
                                    netcat -t <ip> -p <port> -l -c
                                    netcat -t <ip> -p <port> -l -u=mytest.txt
                                    netcat -t <ip> -p <port> -l -e=\"cat /etc/pass\"
                                    echo 'ABC' | netcat -t <ip> -p <port>
                                    netcat -t <ip> -p <port>
                                    '''))
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', help='execute command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=10666, help='specified port')
    parser.add_argument('-t', '--target', default='192.168.178.38', help='specified ip')
    parser.add_argument('-u', '--upload', help='upload file')

    args = parser.parse_args()

    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()

    nc.run

class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        def run(self):
            if self.args.listen:
                self.listen()
            else:
                self.send()

        def send(self):
            self.socket.connect((self.args.target, self.args.port))
            if self.buffer:
                self.socket.send(self.buffer)

            try:
                while True:
                    recv_len = 1
                    response = ''
                    while recv_len:
                        data = self.socket.recv(4096)
                        recv_len = len(data)
                        response += data.decode()
                        if recv_len < 4096:
                            break
                    
                    if response:
                        print(response)
                        buffer = input('> ')
                        buffer += '\n'
                        self.socket.send(buffer.encode())
            except KeyboardInterrupt:
                print('terminate')
                self.socket.close()
                sys.exit()

        def listen(self):
            self.socket.bind((self.args.target, self.args.port))
            self.socket.listen(5)

            while True:
                client_socket, _ = self.socket.accept()
                client_thread = threading.Thread(target=self.handle, args=(client_socket,))
                client_thread.start()

            