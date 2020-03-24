#!/usr/bin/env python
"""
Client
"""

import os
import signal
import subprocess
import sys
import time
import traceback
from socket import SOCK_STREAM, socket, AF_INET
from threading import Thread

address = 'localhost'
threads = {}
awaiting_res = False


class ClientHandler(Thread):
    def __init__(self, index, address, port, process):
        Thread.__init__(self)
        self.index = index
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((address, port))
        self.buffer = ""
        self.valid = True
        self.process = process

    def handle_msg(self, msg):
        print(msg)

    def run(self):
        global threads
        res_len = 0
        while self.valid:
            try:
                # No message is being processed
                # message format: [response length]-[response]
                if (res_len == 0):
                    if (len(self.buffer) < 4):
                        # Not long enough for response length
                        data = str(self.sock.recv(1024))
                        self.buffer += data
                    else:
                        (res_len,res)= self.buffer.split("-",1)
                        res_len = int(res_len)
                        self.buffer = res
                else:
                    # Message has not yet been fully received
                    if (len(self.buffer)<res_len):
                        data = str(self.sock.recv(1024))
                        self.buffer += data
                    else:
                        self.handle_msg(self.buffer[0:res_len])
                        self.buffer = self.buffer[res_len:]
                        res_len = 0
            except Exception:
                print (traceback.format_exc())
                self.valid = False
                del threads[self.index]
                self.sock.close()
                break


    def kill(self):
        if self.valid:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
            except:
                pass
            self.close()

    def send(self, s):
        if self.valid:
            self.sock.send((str(s) + '*').encode('utf-8'))
        else:
            print ("Socket invalid")

    def close(self):
        try:
            self.valid = False
            self.sock.close()
        except:
            pass

def send(index, data, set_awaiting_res=False):
    global threads, awaiting_res
    wait = awaiting_res
    while wait:
        time.sleep(0.01)
        wait = awaiting_res
    pid = int(index)
    assert pid in threads
    if set_awaiting_res:
        awaiting_res = True
    threads[pid].send(data)

def exit(exit=False):
    global threads, awaiting_res
    wait = awaiting_res and (not exit)
    while wait:
        time.sleep(0.01)
        wait = awaiting_res

    time.sleep(2)
    for k in threads:
        threads[k].kill()
    subprocess.Popen(['./stopall'], stdout=open('/dev/null'), stderr=open('/dev/null'))
    time.sleep(0.1)
    os._exit(0)


def timeout():
    time.sleep(120)
    exit(True)


def main(debug=False):
    global leader, threads, awaiting_res
    timeout_thread = Thread(target=timeout, args=())
    timeout_thread.setDaemon(True)
    timeout_thread.start()

    while True:
        try:
            line = sys.stdin.readline().strip()
        except:  # keyboard exception
            exit(True)
        if line == 'exit':
            exit()

        server_cmd = line.split()
        try:
            pid = int(server_cmd[0])  
        except ValueError:
            print ("Invalid pid: " + server_cmd[0])
            exit(True)

        cmd = server_cmd[1] 
        if cmd == 'start':
            n = server_cmd[2]
            port = int(server_cmd[3])

            if debug:
                process = subprocess.Popen(['./process', str(pid), n, str(port)], preexec_fn=os.setsid)
            else:
                process = subprocess.Popen(['./process', str(pid), n, str(port)], stdout=open('/dev/null', 'w'),
                    stderr=open('/dev/null', 'w'), preexec_fn=os.setsid)

            # sleep for a while to allow the process to set up
            time.sleep(3)

            handler = ClientHandler(pid, address, port, process)
            threads[pid] = handler
            handler.start()
            time.sleep(0.1)
        elif cmd == 'crash':
            send(pid, cmd)
        time.sleep(2)


if __name__ == '__main__':
    debug = False
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        debug = True

    main(debug)