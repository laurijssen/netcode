import threading
import paramiko
import subprocess

# run remote command
def ssh_command(ip, user, command):
    key = paramiko.RSAKey.from_private_key_file('/home/kali/.ssh/paramiko')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, pkey=key)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.exec_command(command)
        return ssh_session.recv(1024)
    return ''

res = ssh_command('127.0.0.1', 'kali', 'pwd')
for file in str(res).split('\\n'):
    print(file)

