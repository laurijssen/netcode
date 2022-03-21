# netcode

```
1. have an order ready on the local machine (no network)

/home/user/316274

ls -l 316274/project-9/
-rwxrwxrwx 1 laurijssen domain users@fujicolor.nl    365943 Dec 14 08:04 8335619764.jpg
-rwxrwxrwx 1 laurijssen domain users@fujicolor.nl   2448629 Dec 14 08:04 8335619929.jpg

.......

-rwxrwxrwx 1 laurijssen domain users@fujicolor.nl         0 Dec 14 08:04 8335628376.jpg
-rwxrwxrwx 1 laurijssen domain users@fujicolor.nl     61788 Dec 14 07:58 project.json

2. run the container. added admin capability for debugging later

docker run --cap-add=SYS_ADMIN --security-opt seccomp=unconfined 
           --user 0:0 --rm -v /home/user/316274/project-9:/workspace 
           -w /workspace 10.203.32.90:5000/pablo pablo -t . project.json

3. the container hangs forever and ls -l shows that the pdf is generated and the very last file is zero bytes

-rwxrwxrwx 1 laurijssen@fujicolor.nl domain users@fujicolor.nl 129801775 Dec 14 08:04 0.pdf

.....

-rwxrwxrwx 1 laurijssen domain users@fujicolor.nl   2006613 Dec 14 08:04 8335628065.jpg
-rwxrwxrwx 1 laurijssen domain users@fujicolor.nl         0 Dec 14 08:04 8335628376.jpg
-rwxrwxrwx 1 laurijssen domain users@fujicolor.nl     61788 Dec 14 07:58 project.json

4. login at the container

docker exec -it 5329f3d90801  /bin/bash

5. install strace, lsof, ps and gdb

apt-get update && apt-get install -y procps strace lsof gdb

6. run ps shows the node process takes up 97% cpu

root           9 97.4  5.5 1440960 564872 ?      Ssl  07:04  11:27 node /pablo/bin/pablo -t . project.json

7. strace of process 9 shows the container is hanging in epoll_wait. It's a busy wait whats causing the high cpu
   node inspect -p 9 ?? could not pause

8. lsof -p 9 lists that the last file is still open and it is 0 bytes. the file descriptor is 66

node      9 root   66w      REG     253,0        0    420306 /workspace/8335628376.jpg

Also many files in the tmp directory are still open. should they be closed?

node      9 root   18u      REG     0,222  3119194    292494 /tmp/pablo_-9-8YmxtvXbpaAK

9. start gdb on the node process. 

gdb -p 9

10. confirm the processor is hanging in epoll_wait.

(gdb) set disassembly-flavor intel
(gdb) disassemble
Dump of assembler code for function epoll_wait:
   0x00007fd1242662d0 <+0>:     cmp    DWORD PTR [rip+0x2b5429],0x0        # 0x7fd12451b700 <__libc_multiple_threads>
   0x00007fd1242662d7 <+7>:     jne    0x7fd1242662ec <epoll_wait+28>
..............
   0x00007fd1242662e1 <+8>:     syscall
   0x00007fd1242662e3 <+10>:    cmp    rax,0xfffffffffffff001
   0x00007fd1242662e9 <+16>:    jae    0x7fd12426631f <epoll_wait+79>
   0x00007fd1242662eb <+18>:    ret
   0x00007fd1242662ec <+28>:    sub    rsp,0x8
   0x00007fd1242662f0 <+32>:    call   0x7fd124272500 <__libc_enable_asynccancel>

11. close the zero bytes opened file manually and quit gdb.

(gdb) call close(66)

12. now the container quits automatically with the error.

{"name":"pablo",
 "pid":9,
  "err":{"message":"EBADF: bad file descriptor, copyfile '/tmp/pablo_-9-EZih1Jd7k4ct' -> '/workspace/8335628376.jpg'",
  "name":"Error","stack":"Error: EBADF: bad file descriptor, copyfile '/tmp/pablo_-9-EZih1Jd7k4ct' -> '/workspace/8335628376.jpg'","code":"EBADF"},
  "msg":"EBADF: bad file descriptor, copyfile '/tmp/pablo_-9-EZih1Jd7k4ct' -> '/workspace/8335628376.jpg'","time":"2021-12-14T07:36:05.965Z","v":0}

So it looks like that the node process was hanging in epoll_wait while trying to copy from the /tmp directory to the original /workspace file.

/tmp/pablo_-9-EZih1Jd7k4ct' -> '/workspace/8335628376.jpg

```
