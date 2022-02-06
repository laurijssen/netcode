# ssh-copy-id paramiko.pub

import os
import paramiko
import subprocess
import threading

# run remote command
def ssh_command(ip, user, command):
    key = paramiko.RSAKey.from_private_key_file(os.getenv('HOME') + '/.ssh/paramiko')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, pkey=key)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.exec_command(command)
        out = []
        r = ssh_session.recv(1024).decode('utf-8')
        while r:
            out.append(r)
            r = ssh_session.recv(1024).decode('utf-8')

        return ''.join(out)
    return ''

res = ssh_command('127.0.0.1', 'kali', 'cd / ; ls */ | xargs ls')
for file in str(res).split('\\n'):
    print(file)

