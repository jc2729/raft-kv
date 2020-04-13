#!/usr/bin/env python
"""
Client
"""

import os
import signal
import subprocess
import raft.kv_pb2 as kv
import random
import sys
import time
import traceback
from google.protobuf import text_format
from queue import Queue
from socket import SOCK_STREAM, socket, AF_INET
from threading import Thread, Timer, Lock

address = 'localhost'
threads = {}
awaiting_res = False
leader_timeout = 20000

lock = Lock()
leader = 0
server_outq = Queue()
serial_no = 8000
pending_rpcs = {}


class ClientHandler(Thread):
    def __init__(self, index, address, port, process):
        Thread.__init__(self)
        self.index = index
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((address, port))
        self.buffer = ""
        self.valid = True
        self.process = process

    def handle_payload(self, payload):
        msg = kv.RaftResponse()
        text_format.Parse(payload, msg)
        global leader, pending_rpcs, server_outq, lock
        if msg.type == kv.RaftResponse.REDIRECT:
            with lock:
                leader = msg.redirect.leaderId
                pending_rpcs[msg.originalRequest.serialNo][2].cancel()
            server_outq.put(msg.redirect.leaderId, text_format.MessageToString(msg.redirect.originalRequest))
        elif msg.type == kv.RaftResponse.KV_RES:
            with lock:
                (_, leader, thr)= pending_rpcs[msg.result.serialNo]
                del pending_rpcs[msg.result.serialNo]
            thr.cancel()
            if msg.result.action == kv.Action.GET:
                print('***requested state below***\n', msg.result.state)

    def run(self):
        global threads
        while self.valid:
            try:
                if '*' in self.buffer:
                    split_buf = self.buffer.split('*', 1)
                    self.handle_payload(split_buf[0])
                    self.buffer = split_buf[1] if len(split_buf) == 2 else ''
                data = self.sock.recv(1024).decode('utf-8')
                self.buffer += data
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
            self.sock.send((text_format.MessageToString(s) + '*').encode('utf-8'))
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

def retry_random(serial_no):
    global pending_rpcs, retry_leader, threads, leader, server_outq, lock
    with lock:
        retry_leader = leader if leader != pending_rpcs[serial_no][1] else random.randint(len(threads))
        server_outq.put(retry_leader, text_format.MessageToString( pending_rpcs[serial_no][0]))

def retry_requests():
    global server_outq, leader, leader_timeout, pending_rpcs
    while server_outq.qsize() > 0:
        item = None
        try:
          pending_rpcs[msg.originalRequest.serialNo][1] = item[0]
          leader_timeout_thr = Timer(leader_timeout/1000, retry_random)
          leader_timeout_thr.start()
          pending_rpcs[msg.originalRequest.serialNo][2] =  leader_timeout_thr
          item = server_outq.get(block=False)
          send(item[0], item[1])
          leader = item[0]
        except Exception as e:
          print('BAD exception in reading out queue to send to client', e)


def main(debug=False):
    global leader, threads, awaiting_res, lock, serial_no, pending_rpcs, leader_timeout
    timeout_thread = Thread(target=timeout, args=[])
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
            msg = kv.RaftRequest()
            msg.type = kv.RaftRequest.Type.CRASH
            send(pid, msg)
        elif cmd == 'get': # TODO
            msg = kv.RaftRequest()
            msg.type = kv.RaftRequest.Type.KV_REQ
            msg.request.action = kv.Action.GET
            predicted_leader = leader
            with lock:
                predicted_leader = leader
                msg.request.serialNo = serial_no 
                leader_timeout_thr = Timer(leader_timeout/1000, retry_random, args=[serial_no])
                leader_timeout_thr.start()
                pending_rpcs[serial_no] = (msg, leader, leader_timeout_thr)
                serial_no += 1
            send(predicted_leader, msg)
        elif cmd == 'put':
            
            msg = kv.RaftRequest()
            msg.type = kv.RaftRequest.Type.KV_REQ
            msg.request.action = kv.Action.PUT
            predicted_leader = leader
            with lock:
                predicted_leader = leader
                msg.request.serialNo = serial_no 
                msg.request.cmd = server_cmd[2]+'='+server_cmd[3]
                leader_timeout_thr = Timer(leader_timeout/1000, retry_random, args=[serial_no])
                leader_timeout_thr.start()
                pending_rpcs[serial_no] = (msg, leader, leader_timeout_thr)
                serial_no += 1
            send(predicted_leader, msg)

        time.sleep(2)


if __name__ == '__main__':
    debug = False
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        debug = True

    main(debug)
