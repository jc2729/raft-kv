#!/usr/bin/env python
"""
Client
"""

import os
import argparse
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
import logging

address = 'localhost'
threads = {}
awaiting_res = False
leader_timeout = 1000

lock = Lock()
leader = 1
serial_no = 8000
pending_rpcs = {} # sent but awaiting response; pending_rpc[serial_no] = (leader, msg, timeout thr)
queued_rpcs = PriorityQueue() # item: ((serial_no, (leader, msg)))

#latency = {} # latency[serial_no]: [start, end]
tput = []
class ClientHandler(Thread):
    def __init__(self, index, address, port):
        Thread.__init__(self)
        self.index = index
        self.sock = socket(AF_INET, SOCK_STREAM)
        print('client connecting to', (address, port))
        self.sock.connect((address, port))
        self.buffer = ""
        self.valid = True
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
                new_msg.request.client = cid
                new_msg.request.action = msg.redirect.originalRequest.action
                new_msg.request.serialNo = msg.redirect.originalRequest.serialNo
                new_msg.request.cmd = msg.redirect.originalRequest.cmd

                queued_rpcs.put((serial_no, (new_msg)))
            elif msg.type == kv.RaftResponse.KV_RES:
                if msg.result.serialNo in pending_rpcs:
                    pending_rpcs[msg.result.serialNo][2].cancel()
                    del pending_rpcs[msg.result.serialNo]
                    #latency[msg.result.serialNo].append(time.time())
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

    def send(self, s):
        if self.valid:
            try:
                print(s)
                self.sock.send((text_format.MessageToString(s) + '*').encode('utf-8'))
            except:
                print('send failed')
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


def timeout():
    time.sleep(3000)

def retry_random(serial_no):
    global pending_rpcs, threads, leader, queued_rpcs, lock, awaiting_res
    lock.acquire()
    try:
        if serial_no in pending_rpcs:
            pending_rpcs[serial_no][2].cancel()
            queued_rpcs.put((serial_no, (pending_rpcs[serial_no][1])))
        awaiting_res = False
    finally:
        lock.release()

def try_requests():
    global leader, leader_timeout, queued_rpcs, pending_rpcs, awaiting_res
    lock.acquire()
    try:
        if queued_rpcs.qsize() > 0:
            try:
              if not awaiting_res:
                item = queued_rpcs.get(block=False)
                serial_no = item[1].request.serialNo
                leader_timeout_thr = Timer(leader_timeout/1000, retry_random, args=[serial_no])
                if serial_no in pending_rpcs:
                    recipient = leader if leader != pending_rpcs[serial_no][0] else random.sample(threads.keys(), 1)[0]
                else:
                    recipient = leader
                pending_rpcs[serial_no] = (recipient,item[1],leader_timeout_thr)
                leader_timeout_thr.start()
                tput.append(time.time())
                send(recipient, item[1], True)
                # latency #
                #latency[serial_no] = [time.time()]
                ###########
            except:
                return
    finally:
        lock.release()

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
            print('exception')

    for line in temp_lines:
        server_cmd = line.split()
        try:
            pid = int(server_cmd[0])  
        except ValueError:
            print ("Invalid pid: " + server_cmd[0])

        cmd = server_cmd[1] 
        if cmd == 'start':
            n = server_cmd[2]
            global cid
            
            port = 21000 + pid*100 + cid

            # sleep for a while to allow the process to conn

            handler = ClientHandler(pid, address, port)
            threads[pid] = handler
            handler.start()
            time.sleep(0.1)

        elif cmd == 'get':
            msg = kv.RaftRequest()
            msg.type = kv.RaftRequest.Type.KV_REQ
            msg.request.client = cid
            msg.request.action = kv.Action.GET
            lock.acquire()
            try:
                msg.request.serialNo = serial_no 
                msg.request.cmd = "GET " + server_cmd[2]
                queued_rpcs.put((serial_no, (msg)))
                serial_no += 1
            finally:
                lock.release()
        elif cmd == 'put':
            msg = kv.RaftRequest()
            msg.request.client = cid
            msg.type = kv.RaftRequest.Type.KV_REQ
            msg.request.action = kv.Action.PUT
            lock.acquire()
            try:
                msg.request.serialNo = serial_no 
                msg.request.cmd = "PUT " + server_cmd[2]+ ' ' + server_cmd[3]
                queued_rpcs.put((serial_no, (msg)))
                serial_no += 1
            finally:
                lock.release()
        elif cmd == 'append':
            msg = kv.RaftRequest()
            msg.request.client = cid
            msg.type = kv.RaftRequest.Type.KV_REQ
            msg.request.action = kv.Action.APPEND
            lock.acquire()
            try:
                msg.request.serialNo = serial_no 
                msg.request.cmd = "APPEND " + server_cmd[2]+' '+server_cmd[3]
                queued_rpcs.put((serial_no, (msg)))
                serial_no += 1
            finally:
                lock.release()
        
    while True:
        try_requests()
        lock.acquire()
        if queued_rpcs.qsize() == 0 and len(pending_rpcs) == 0:
            break
        lock.release()
        time.sleep(1)
    tput.append(time.time())
    print(cid, 'has 30 reqs in', tput[-1] - tput[0])

    # print(cid, 'has latencies', latency)
    # total_lat = 0
    # for serial_no in latency:
    #     total_lat += latency[serial_no][1]-latency[serial_no][0]
    # print(cid, 'has', len(latency), 'requests with total latency', total_lat)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='client [cid]')
    parser.add_argument('cid', type=int, nargs='+',
                   help='the client ID')
    
    logging.basicConfig(level=logging.DEBUG,
                      format='%(name)s: %(message)s',)

    args = parser.parse_args()
    global cid
    cid = args.cid[0]
    main()
