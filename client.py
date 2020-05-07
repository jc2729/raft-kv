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
from queue import Queue, PriorityQueue
from socket import SOCK_STREAM, socket, AF_INET
from threading import Thread, Timer, Lock

address = 'localhost'
threads = {}
awaiting_res = False
leader_timeout = 1000

lock = Lock()
leader = 0
serial_no = 8000
pending_rpcs = {} # sent but awaiting response; pending_rpc[serial_no] = (leader, msg, timeout thr)
queued_rpcs = PriorityQueue() # item: ((serial_no, (leader, msg)))


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
        global awaiting_res, queued_rpcs, pending_rpcs, leader, lock
        awaiting_res = False
        print('$$$$$$$$$$ client payload $$$$$$$$$$', payload)
        msg = kv.RaftResponse()
        text_format.Parse(payload, msg)
        lock.acquire()
        try:
            if msg.type == kv.RaftResponse.REDIRECT:
                
                leader = msg.redirect.leaderId
                serial_no = msg.redirect.originalRequest.serialNo
                if serial_no in pending_rpcs:
                    pending_rpcs[serial_no][2].cancel()
                    del pending_rpcs[serial_no]

                new_msg = kv.RaftRequest()
                new_msg.type = kv.RaftRequest.Type.KV_REQ
                new_msg.request.action = msg.redirect.originalRequest.action
                new_msg.request.serialNo = msg.redirect.originalRequest.serialNo
                new_msg.request.cmd = msg.redirect.originalRequest.cmd

                queued_rpcs.put((serial_no, (msg.redirect.leaderId, new_msg)))
            elif msg.type == kv.RaftResponse.KV_RES:
                if msg.result.serialNo in pending_rpcs:
                    pending_rpcs[msg.result.serialNo][2].cancel()
                    del pending_rpcs[msg.result.serialNo]
                if msg.result.action == kv.Action.GET:
                    print('***************requested state below***************\n', msg.result.state)
        finally:
            lock.release()

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
            except ConnectionError:
                print ('Client detected problem with', self.index)
                self.valid = False
                del threads[self.index]
                self.sock.close()
                break
            except Exception:
                print ('Client detected problem with', self.index)
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

def send(index, msg, set_awaiting_res=False):
    global threads, awaiting_res
    pid = int(index)
    if pid not in threads:
        return
    if set_awaiting_res:
        awaiting_res = True
    threads[pid].send(msg)

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
    time.sleep(3000)
    exit(True)

def retry_random(serial_no):
    global pending_rpcs, threads, leader, queued_rpcs, lock, awaiting_res
    lock.acquire()
    try:
        if serial_no in pending_rpcs:
            pending_rpcs[serial_no][2].cancel()
            retry_leader = leader if leader != pending_rpcs[serial_no][0] else random.sample(threads.keys(), 1)[0]
            queued_rpcs.put((serial_no, (retry_leader, pending_rpcs[serial_no][1])))
        awaiting_res = False
    finally:
        lock.release()

def try_requests():
    global leader, leader_timeout, queued_rpcs, pending_rpcs, awaiting_res
    lock.acquire()
    try:
        if queued_rpcs.qsize() > 0:
            try:
              item = queued_rpcs.get(block=False)
              if item[1][0] == 'start':
                start(item[1][1], address, item[1][2], item[1][3])
              elif item[1][1].type == kv.RaftRequest.Type.CRASH:
                send(item[1][0], item[1][1])
              elif not awaiting_res:
                serial_no = item[1][1].request.serialNo
                leader_timeout_thr = Timer(leader_timeout/1000, retry_random, args=[serial_no])
                pending_rpcs[serial_no] = (item[1][0],item[1][1],leader_timeout_thr)
                leader_timeout_thr.start()
                send(item[1][0], item[1][1], True)
            except:
                return
        if queued_rpcs.qsize() > 0:
            try:
              item = queued_rpcs.get(block=False)
              if item[1][0] == 'start':
                start(item[1][1], address, item[1][2], item[1][3])
              else:
                queued_rpcs.put(item)
            except:
                return
    finally:
        lock.release()

def start(pid, address, port, n):
    process = subprocess.Popen(['./process', str(pid), n, str(port)], preexec_fn=os.setsid)
    time.sleep(3)
    handler = ClientHandler(pid, address, port, process)
    threads[pid] = handler
    handler.start()
    time.sleep(0.1)

def main():
    global leader, threads, awaiting_res, lock, serial_no, pending_rpcs, leader_timeout
    timeout_thread = Thread(target=timeout, args=[])
    timeout_thread.setDaemon(True)
    timeout_thread.start()
    temp_lines = []
    while True:
        try:
            line = sys.stdin.readline().strip()
            if line == 'exit':
                break
            temp_lines.append(line)
        except:  # keyboard exception
            exit(True)

    for line in temp_lines:
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
            queued_rpcs.put((serial_no, (cmd, pid, port, n)))
            serial_no += 1

            
        elif cmd == 'crash':
            msg = kv.RaftRequest()
            msg.type = kv.RaftRequest.Type.CRASH
            queued_rpcs.put((serial_no, (pid, msg)))
            serial_no += 1

        elif cmd == 'get':
            msg = kv.RaftRequest()
            msg.type = kv.RaftRequest.Type.KV_REQ
            msg.request.action = kv.Action.GET
            predicted_leader = leader
            lock.acquire()
            try:
                predicted_leader = leader
                msg.request.serialNo = serial_no 
                msg.request.cmd = "GET " + server_cmd[2]
                queued_rpcs.put((serial_no, (leader, msg)))
                serial_no += 1
            finally:
                lock.release()
        elif cmd == 'put':
            msg = kv.RaftRequest()
            msg.type = kv.RaftRequest.Type.KV_REQ
            msg.request.action = kv.Action.PUT
            predicted_leader = leader
            lock.acquire()
            try:
                predicted_leader = leader
                msg.request.serialNo = serial_no 
                msg.request.cmd = "PUT " + server_cmd[2]+ ' ' + server_cmd[3]
                queued_rpcs.put((serial_no, (leader, msg)))
                serial_no += 1
            finally:
                lock.release()
        elif cmd == 'append':
            msg = kv.RaftRequest()
            msg.type = kv.RaftRequest.Type.KV_REQ
            msg.request.action = kv.Action.APPEND
            predicted_leader = leader
            lock.acquire()
            try:
                predicted_leader = leader
                msg.request.serialNo = serial_no 
                msg.request.cmd = "APPEND " + server_cmd[2]+' '+server_cmd[3]
                queued_rpcs.put((serial_no, (leader, msg)))
                serial_no += 1
            finally:
                lock.release()
        
    while True:
        try_requests()
        time.sleep(2)


if __name__ == '__main__':
    main()
