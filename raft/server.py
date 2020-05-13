#!/usr/bin/env python3

import argparse
import constant
import logging
import random
import rpc_pb2 as rpc
import kv_pb2 as kv
import pickle
from os import path
import selectors
import socket
import sys
import threading
import types
import time

from google.protobuf import text_format

class Server():
  """
  Receives connections and establishes handlers for the client and other servers.
  """

  def __init__(self, server_id, address, n, num_clients):
    """
    Sets up this server to (1) connect to other servers and (2) connect to client
    """
    self.sel = selectors.DefaultSelector()
    self.logger = logging.getLogger('Server')
    logging.basicConfig(filename='test.log', level=logging.DEBUG)
    print(address)
    self.master_port : int = address[1]
    self.server_id : int = server_id
    self.server_port : int = 20000 + self.server_id
    self.client_port_base : int = 21000 + 100 * self.server_id
    self.partial_payload = ''
    self.client_lsocks = {} # lsock : id 
    
    # establish a listening TCP endpoint to master
    self.master_lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.master_lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # establish a listening TCP endpoint for other servers
    self.server_lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server_lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    self.n = n

    # bind to master-facing port; assumed guaranteed to be available
    while True:
      try:
        self.master_lsock.bind(address)
        break
      except:
        pass

    # bind to client-facing ports
    for i in range(num_clients):
      client_lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      client_lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

      try:
        client_lsock.bind(('localhost', self.client_port_base+i))
        print('binding to ', ('localhost', self.client_port_base+i))
      except:
        print('cannot bind')
      self.client_lsocks[i] = client_lsock

    # bind to server-facing port; available by port assigning convention
    while True:
      try:
        self.server_lsock.bind(('localhost', self.server_port))
        break
      except:
        pass

    self.master_csock = None
    self.client_id_to_sock = {}

    # map server IDs to sockets
    self.id_to_sock = {server:None for server in range(self.n)}
    del self.id_to_sock[self.server_id]
    
    # establish connections to all preceding servers
    for i in range(n):
      if i == self.server_id:
        continue

      # create a connecting socket for servers that have been started
      addr = 20000 + i
      print(self.server_id, 'connecting to', addr)
      csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      csock.setblocking(False)
      csock.connect_ex(('localhost', addr))
      events = selectors.EVENT_READ | selectors.EVENT_WRITE
      data = types.SimpleNamespace(connid=i, outb=b'')
      self.sel.register(csock, events, data=data)

    # finish setting up our master listening socket
    self.master_lsock.listen(int(n))
    self.master_lsock.setblocking(False)
    self.sel.register(self.master_lsock, selectors.EVENT_READ, data=None)

    for client in self.client_lsocks:
      self.client_lsocks[client].listen(int(n))
      self.client_lsocks[client].setblocking(False)
      self.sel.register(self.client_lsocks[client], selectors.EVENT_READ, data=None)

    # finish setting up our server listening socket
    self.server_lsock.listen(int(n))
    self.server_lsock.setblocking(False)
    self.sel.register(self.server_lsock, selectors.EVENT_READ, data=None)

    self.lock = threading.Lock()

    # raft-specific persistent state on ALL servers
    self.STORAGE = '{}.pkl'.format(self.server_id)
    if not self.load_from_storage():
      self.persistent_state = {
        'current_term': 0,
        'voted_for': None, # reset always when current term changes
        'log': {} # log[index] = (cmd, term, serial_no, client) where cmd one of: "PUT key val", "GET key", or "APPEND key val"
      }

    # volatile state on ALL servers
    self.commit_index = 0
    self.processed_serial_nos = {c:{} for c in range(num_clients)}
    self.last_applied = 0
    self.state = {}

    self.role = 'follower' # valid states: 'follower', 'leader', 'candidate'
    self.election_timeout_lower = 150
    self.election_timeout = random.randint(self.election_timeout_lower,self.election_timeout_lower*2) # slowed to allow sufficient time to see changes
    self.election_timer = threading.Timer(self.election_timeout/1000, self.convert_to_candidate)
    self.election_timer.daemon = True
    # https://www.cl.cam.ac.uk/~ms705/pub/papers/2015-osr-raft.pdf section 4
    self.leader_timeout = self.election_timeout_lower/2
    self.heartbeat_timer = threading.Timer(self.leader_timeout/1000, self.send_heartbeats)
    self.heartbeat_timer.daemon = True
    self.leader = None

    self.application_thr = threading.Thread(name='application_thr', target=self.apply_committed)
    self.application_thr.daemon = True
    self.application_thr_cv = threading.Condition(lock=self.lock)
    self.application_thr.start()
    

    # volatile state ONLY for leaders, None otherwise
    self.match_index = None
    self.next_index = None

    # state for candidates
    self.vote_count = 0

  def exec_command(self, cmd: str):
    if cmd.startswith('GET'):
      return
    var_val = cmd.split(' ') 
    if var_val[0] == 'PUT':
      self.state[var_val[1]]=var_val[2]
    elif var_val[0] == 'APPEND':
      self.state[var_val[1]] = self.state[var_val[1]] + var_val[2] if var_val[1] in self.state else var_val[2]

  def crash(self):
    """
    Immediately crashes this server
    """
    print(time.time(), 'crashing')
    sys.exit(0)

  def sock_to_id(self,sock):
    for item in id_to_sock.items():
        if item[1] == sock:
          return item[0]

  def send(self, msg, sock):
    try:
      sock.send((text_format.MessageToString(msg) + '*').encode('utf-8'))
    except Exception:
      pass

  def convert_to_follower(self):
    '''
    precond: has lock
    '''
    print(self.server_id, ' converted to follower')
    role = 'leader'
    self.role = 'follower'
    if role == 'leader':
        self.leader = None
        self.match_index = None
        self.next_index = None
        self.persistent_state['voted_for'] = None
        self.heartbeat_timer.cancel()
    else:
        pass

  def convert_to_candidate(self):
    print(self.server_id, 'became candidate')
    msg = rpc.Rpc()
    msg.type = rpc.Rpc.REQUEST_VOTE
    self.lock.acquire()
    try:
        self.role = 'candidate'
        self.leader = None
        self.persistent_state['current_term'] += 1
        msg.voteReq.candidateTerm = self.persistent_state['current_term']
        last_log_idx = self.last_log_index(self.persistent_state['log'])
        msg.voteReq.lastLogIndex = last_log_idx
        msg.voteReq.lastLogTerm = constant.EMPTY_LOG_LAST_LOG_TERM if last_log_idx == constant.EMPTY_LOG_LAST_LOG_INDEX else self.persistent_state['log'][last_log_idx][1]
        self.persistent_state['voted_for'] = self.server_id
        self.vote_count = 1
        self.reset_election_timer()
    finally:
        self.lock.release()
    for i in self.id_to_sock:
        self.send(msg, self.id_to_sock[i])
    
  def save_to_storage(self):
    with open(self.STORAGE, 'wb') as f:
      pickle.dump(self.persistent_state, f)

  def load_from_storage(self):
    if path.exists(self.STORAGE):
      with open(self.STORAGE, 'rb') as f:
        self.persistent_state = pickle.load(f)
        return True
    return False
      
  def reset_election_timer(self):
    '''
    precond: has lock
    '''
    self.election_timer.cancel()
    self.election_timer = threading.Timer(self.election_timeout/1000, self.convert_to_candidate)
    self.election_timer.daemon = True
    self.election_timer.start()

  def reset_heartbeat_timer(self):
    '''
    precond: has lock
    '''
    self.heartbeat_timer.cancel()
    self.heartbeat_timer = threading.Timer(self.leader_timeout/1000, self.send_heartbeats)
    self.heartbeat_timer.daemon = True
    self.heartbeat_timer.start()

  def handle_vote_req(self, vote_req, sock):
    msg = rpc.Rpc()
    msg.type = rpc.Rpc.REQUEST_VOTE_RES
    msg.voteRes.id = self.server_id
    msg.voteRes.candidateTerm = vote_req.candidateTerm

    self.lock.acquire()
    try:
      if vote_req.candidateTerm < self.persistent_state['current_term']:
          msg.voteRes.voteGranted = False
          msg.voteRes.term = self.persistent_state['current_term']
          
      else:
          if self.persistent_state['current_term'] < vote_req.candidateTerm:
              self.convert_to_follower()
              self.persistent_state['current_term'] = vote_req.candidateTerm
              self.persistent_state['voted_for'] = None
              msg.voteRes.term = self.persistent_state['current_term']
          last_log_idx = self.last_log_index(self.persistent_state['log'])
          last_log_term = constant.EMPTY_LOG_LAST_LOG_TERM if last_log_idx == constant.EMPTY_LOG_LAST_LOG_INDEX else self.persistent_state['log'][last_log_idx][1]
          if (self.persistent_state['voted_for'] is None or self.persistent_state['voted_for'] == vote_req.candidateId) and self.log_comparison(vote_req.lastLogIndex, vote_req.lastLogTerm, last_log_idx, last_log_term) >= 0:
              msg.voteRes.voteGranted = True
              self.persistent_state['voted_for'] = vote_req.candidateId
              msg.voteRes.term = self.persistent_state['current_term']
              self.reset_election_timer() # only reset if vote is granted
          else:
              msg.voteRes.term = self.persistent_state['current_term']
              msg.voteRes.voteGranted = False
    finally:
      self.lock.release()
    self.save_to_storage()
    self.send(msg, sock)

  def handle_vote_res(self, vote_res, sock):
    self.lock.acquire()
    try:
      if vote_res.term > self.persistent_state['current_term']:
          self.persistent_state['current_term'] = vote_res.term
          self.convert_to_follower()
          return
      if vote_res.candidateTerm != self.persistent_state['current_term']:
          return
      if vote_res.voteGranted:
        self.vote_count += 1
      if self.role != 'leader' and self.vote_count >= int(self.n/2 + 1):
          # convert to leader
          self.role = 'leader'
          print(self.server_id, ' became leader')
          self.leader = self.server_id
          # establish self as leader
          self.election_timer.cancel()
          next_index = self.last_log_index(self.persistent_state['log']) + 1
          self.next_index = {server:next_index for server in range(self.n)}
          self.match_index = {server:0 for server in range(self.n)}

          self.save_to_storage()
          for i in self.id_to_sock:
              msg = self.append_entries_rpc(i, self.persistent_state['current_term'], self.commit_index, self.persistent_state['log'], True)
              self.send(msg, self.id_to_sock[i])
          self.heartbeat_timer = threading.Timer(self.leader_timeout/1000, self.send_heartbeats)
          self.heartbeat_timer.daemon = True
          self.heartbeat_timer.start()
    finally:
      self.lock.release()
        
  def append_entries_rpc(self, receiver, current_term, commit_index, log, is_heartbeat, receiver_next_index=-1):
    msg = rpc.Rpc()
    msg.type = rpc.Rpc.APPEND_ENTRIES
    msg.appendEntriesReq.leaderTerm = current_term
    msg.appendEntriesReq.leaderId = self.server_id
    msg.appendEntriesReq.leaderCommit = commit_index
    if is_heartbeat:
      last_log_idx = self.last_log_index(log)
      msg.appendEntriesReq.prevLogIndex = last_log_idx
      msg.appendEntriesReq.prevLogTerm = constant.EMPTY_LOG_LAST_LOG_TERM if last_log_idx == constant.EMPTY_LOG_LAST_LOG_INDEX else log[last_log_idx][1]
      return msg
    for k in sorted(log):
      if k >= receiver_next_index:
        l = rpc.LogEntry()
        l.command = log[k][0]
        l.term = log[k][1]
        l.serialNo = log[k][2]
        l.client = log[k][3]
        msg.appendEntriesReq.entries.extend([l])
    prev_log_idx = receiver_next_index - 1
    msg.appendEntriesReq.prevLogIndex = prev_log_idx
    msg.appendEntriesReq.prevLogTerm = 0 if prev_log_idx not in log else log[prev_log_idx][1] # dummy value
    return msg


  def send_heartbeats(self):
    with self.lock:
      for i in self.id_to_sock:
        msg = self.append_entries_rpc(i, self.persistent_state['current_term'], self.commit_index, self.persistent_state['log'], True)
        self.send(msg, self.id_to_sock[i])
    self.heartbeat_timer = threading.Timer(self.leader_timeout/1000, self.send_heartbeats)
    self.heartbeat_timer.daemon = True
    self.heartbeat_timer.start()

  def handle_append_entries(self, append_entries_req, sock):
    msg = rpc.Rpc()
    msg.type = rpc.Rpc.APPEND_ENTRIES_RES
    msg.appendEntriesRes.id = self.server_id
    msg.appendEntriesRes.leaderTerm = append_entries_req.leaderTerm

    self.application_thr_cv.acquire()
    try:
      if append_entries_req.leaderTerm < self.persistent_state['current_term']:
          msg.appendEntriesRes.term = self.persistent_state['current_term']
          msg.appendEntriesRes.success = False
          self.save_to_storage()
          self.send(msg, sock)
          return
      else:
          if self.persistent_state['current_term'] < append_entries_req.leaderTerm:
              self.convert_to_follower()
          self.persistent_state['current_term'] = append_entries_req.leaderTerm
          self.leader = append_entries_req.leaderId
          print(self.server_id, '\'s leader is ', self.leader, ' at term ', self.persistent_state['current_term'], 'at time', time.time())
          print(self.persistent_state['log'])
          # vacuously true if leader has no entries
          if append_entries_req.prevLogIndex == constant.EMPTY_LOG_LAST_LOG_INDEX and len(append_entries_req.entries) == 0:
            msg.appendEntriesRes.success = True
            msg.appendEntriesRes.term = append_entries_req.leaderTerm
            msg.appendEntriesRes.lastLogIndex = constant.EMPTY_LOG_LAST_LOG_INDEX
            self.save_to_storage()
            self.send(msg, sock)
            self.reset_election_timer()
            return
          if append_entries_req.prevLogIndex != constant.EMPTY_LOG_LAST_LOG_INDEX and (append_entries_req.prevLogIndex not in self.persistent_state['log'] or self.persistent_state['log'][append_entries_req.prevLogIndex][1] != append_entries_req.prevLogTerm):
            
            msg.appendEntriesRes.success = False
            msg.appendEntriesRes.term = append_entries_req.leaderTerm
            self.save_to_storage()
            self.send(msg, sock)
            self.reset_election_timer()
            return
          idx = append_entries_req.prevLogIndex + 1
          last_new_idx = self.commit_index
          for e in append_entries_req.entries:
            if idx not in self.persistent_state['log']:
              self.persistent_state['log'][idx] = (e.command, e.term, e.serialNo, e.client)
              last_new_idx = idx
            elif idx in self.persistent_state['log'] and e.term != self.persistent_state['log'][idx][1]:
              self.persistent_state['log'] = {l:self.persistent_state['log'][l] for l in self.persistent_state['log'] if l < idx}
              self.persistent_state['log'][idx] = (e.command, e.term, e.serialNo, e.client)
              last_new_idx = idx
            idx += 1
          if append_entries_req.leaderCommit > self.commit_index:

            self.commit_index = min(append_entries_req.leaderCommit, last_new_idx)
            N = self.last_log_index(self.persistent_state['log'])
            self.application_thr_cv.notify()
            
          self.reset_election_timer()
          msg.appendEntriesRes.lastLogIndex = self.last_log_index(self.persistent_state['log'])
          msg.appendEntriesRes.success = True
          msg.appendEntriesRes.term = append_entries_req.leaderTerm
          self.save_to_storage()
          self.send(msg, sock)
    finally:
      self.application_thr_cv.release()
        
            
  def handle_append_entries_res(self, append_entries_res, sock):
    self.lock.acquire()
    try:
      if append_entries_res.term > self.persistent_state['current_term']:
          self.persistent_state['current_term'] = append_entries_res.term
          self.convert_to_follower()
          return
      if append_entries_res.leaderTerm != self.persistent_state['current_term']:
          return
      if append_entries_res.success:
        self.next_index[append_entries_res.id] = append_entries_res.lastLogIndex + 1
        self.match_index[append_entries_res.id] = append_entries_res.lastLogIndex
        if self.last_log_index(self.persistent_state['log'])>= self.next_index[append_entries_res.id]:
          msg = self.append_entries_rpc(append_entries_res.id, self.persistent_state['current_term'], self.commit_index, self.persistent_state['log'], False, self.next_index[append_entries_res.id])
          self.save_to_storage()
          self.send(msg, self.id_to_sock[append_entries_res.id])
        
        N = self.last_log_index(self.persistent_state['log'])
        while N > self.commit_index:
          if self.persistent_state['log'][N][1] == self.persistent_state['current_term']:
            matches = 0
            for m in self.match_index:
              if self.match_index[m] >= N:
                matches += 1
            if matches >= int(self.n/2) + 1:
              self.commit_index = N
              break
          N -= 1
        self.application_thr_cv.notify()
        return
      self.next_index[append_entries_res.id] -= 1
      msg = self.append_entries_rpc(append_entries_res.id, self.persistent_state['current_term'], self.commit_index, self.persistent_state['log'], False, self.next_index[append_entries_res.id])
      self.save_to_storage()
      self.send(msg, self.id_to_sock[append_entries_res.id])
    finally:
      self.application_thr_cv.release()

  def handle_client_request(self, client_req, sock):
    self.lock.acquire()
    try:
      print(self.server_id, ' got client request ', client_req)
      if self.server_id != self.leader:
        if self.leader != None:
          msg = kv.RaftResponse()
          msg.type = kv.RaftResponse.REDIRECT
          msg.redirect.leaderId = self.leader
          msg.redirect.originalRequest.serialNo = client_req.serialNo
          msg.redirect.originalRequest.action = client_req.action
          msg.redirect.originalRequest.cmd = client_req.cmd
          self.send(msg, sock)
        return

      # if client_req.serialNo in self.processed_serial_nos:
      #   self.send(self.processed_serial_nos[client_req.client][client_req.serialNo], sock)
      #   return
      idx = self.last_log_index(self.persistent_state['log']) + 1
      self.persistent_state['log'][idx] = (client_req.cmd, self.persistent_state['current_term'], client_req.serialNo, client_req.client)
      for i in self.id_to_sock:
        msg = self.append_entries_rpc(i, self.persistent_state['current_term'], self.commit_index, self.persistent_state['log'], False, self.next_index[i])
        self.send(msg, self.id_to_sock[i])
      self.reset_heartbeat_timer()
      self.match_index[self.server_id] = idx
    finally:
      self.application_thr_cv.release()



  def last_log_index(self, log):
    return constant.EMPTY_LOG_LAST_LOG_INDEX if len(log) == 0 else max(log)
    
  def log_comparison(self, last_log_idx_1, last_log_term_1, last_log_idx_2, last_log_term_2):
    """
    returns:
      > 0 if log 1 is more up-to-date
      0 if log 1 and 2 are equally up-to-date
      < 0 otherwise
    """
    if last_log_term_1 > last_log_term_2:
        return 1
    elif last_log_term_1 < last_log_term_2:
        return -1
    return last_log_idx_1 - last_log_idx_2
  
  def handle_handshake_req(self, handshake_req, sock):
    self.id_to_sock[handshake_req.id] = sock
    msg = rpc.Rpc()
    msg.type = rpc.Rpc.REQUEST_HANDSHAKE_RES
    msg.handshakeRes.id = self.server_id
    self.send(msg, sock)

  def handle_handshake_res(self, handshake_res, sock):
    self.id_to_sock[handshake_res.id] = sock

  def apply_committed(self):
    while True:
      self.application_thr_cv.acquire()      
      while self.last_applied == self.commit_index:
        self.application_thr_cv.wait()
      last_applied = self.last_applied
          
      for l in range(last_applied + 1, self.commit_index+1):
        self.exec_command(self.persistent_state['log'][l][0])

        serial_no = self.persistent_state['log'][l][2]
        msg = kv.RaftResponse()
        msg.type = kv.RaftResponse.KV_RES
        msg.result.serialNo = serial_no
        action_var_val = self.persistent_state['log'][l][0].split(' ')
        msg.result.action = self.kv_action(action_var_val[0])
        if msg.result.action == kv.Action.GET:
            state = [action_var_val[1]+'='+(self.state[action_var_val[1]] if action_var_val[1] in self.state else "")]
            msg.result.state.extend(state)
        # processed_serial_nos[client][serial_no] 
        client = self.persistent_state['log'][l][3]
        print(self.server_id, self.persistent_state['log'][l])
        self.processed_serial_nos[client][serial_no] = msg 

        if self.role == 'leader':
          self.send(msg, self.client_id_to_sock[client])

        self.last_applied += 1
      self.application_thr_cv.release()

  def kv_action(self,action):
    return {"PUT":kv.Action.PUT, "GET":kv.Action.GET, "APPEND":kv.Action.APPEND}[action]

  def accept_wrapper(self, sock):
    """
    Handles accepting a connection from client/server
    """
    
    conn, addr = sock.accept()  # Should be ready to read
    conn.setblocking(False)

    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    self.sel.register(conn, events, data=data)

    # request ID of the connecting server so we can map the socket for comm
    if self.master_csock is None and sock == self.master_lsock:
      self.master_csock = conn
    elif sock in self.client_lsocks.values():
      client = [c for c,lsock in self.client_lsocks.items() if lsock == sock][0]
      self.client_id_to_sock[client] = conn
    else:
      msg = rpc.Rpc()
      msg.type = rpc.Rpc.REQUEST_HANDSHAKE
      msg.handshakeReq.id = self.server_id
      try:
        self.send(msg, conn)
      except Exception as e:
        print('Error connecting! ', self.server_id, e)

  def service_connection(self, key, mask):
    """
    Handles incoming data from a given socket in [key]
    """
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
      try:
        recv_data = sock.recv(4096)  # Should be ready to read
        if recv_data:
          recv_buffer = self.partial_payload + recv_data.decode('utf-8')
          self.partial_payload = ''
          while len(recv_buffer) > 0:
            if '*' in recv_buffer:
              payload = recv_buffer[:recv_buffer.index('*')]
              recv_buffer = recv_buffer[recv_buffer.index('*') + 1:]
            else:
              self.partial_payload = recv_buffer
              break


            if sock == self.master_csock:
              self.crash()
            elif sock in self.client_id_to_sock.values():
              msg = kv.RaftRequest()
              text_format.Parse(payload, msg)
              self.handle_client_request(msg.request, sock)
              payload = ''
            else:
              msg = rpc.Rpc()
              text_format.Parse(payload, msg)
              if msg.type == rpc.Rpc.REQUEST_HANDSHAKE:
                self.handle_handshake_req(msg.handshakeReq, sock)
              elif msg.type == rpc.Rpc.REQUEST_HANDSHAKE_RES:
                self.handle_handshake_res(msg.handshakeRes, sock)
              elif msg.type == rpc.Rpc.REQUEST_VOTE:
                self.handle_vote_req(msg.voteReq, sock)
              elif msg.type == rpc.Rpc.REQUEST_VOTE_RES:
                self.handle_vote_res(msg.voteRes, sock)
              elif msg.type == rpc.Rpc.APPEND_ENTRIES:
                self.handle_append_entries(msg.appendEntriesReq, sock)
              elif msg.type == rpc.Rpc.APPEND_ENTRIES_RES:
                self.handle_append_entries_res(msg.appendEntriesRes, sock)
              payload = ''
        else:
          self.process_connection_fail(sock)
      except ConnectionError:
        self.process_connection_fail(sock)

  def start(self):
    """
    Starts the server
    """
    self.election_timer.start()
    while True:

      events = self.sel.select(timeout=None)
      for key, mask in events:
        if key.data is None:
          self.accept_wrapper(key.fileobj)
        else:
          self.service_connection(key, mask)

  def process_connection_fail(self, sock):
    """
    On any connection failure (a crash), unregister sock.
    """
    try:
      self.sel.unregister(sock)
      sock.close()
    except:
      pass


if __name__ == '__main__':

  parser = argparse.ArgumentParser(description='Process [pid] [n] [port] [num clients]')
  parser.add_argument('pid', type=int, nargs='+',
                   help='the process ID')
  parser.add_argument('n', type=int, nargs='+',
                   help='the number of servers')
  parser.add_argument('port', type=int, nargs='+',
                   help='the server port') # 60000 + i
  parser.add_argument('num_clients', type=int, nargs='+',
                   help='the number of clients')
  logging.basicConfig(level=logging.DEBUG,
                      format='%(name)s: %(message)s',)

  args = parser.parse_args()

  address = ('localhost', args.port[0])
  server = Server(args.pid[0], address, args.n[0], args.num_clients[0])
  server.start()