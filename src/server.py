#!/usr/bin/env python3

import argparse
import logging
import random
import rpc_pb2 as rpc
import selectors
import socket
import sys
import threading
import types

from google.protobuf import text_format

class Server():
  """
  Receives connections and establishes handlers for the client and other servers.
  """

  def __init__(self, server_id, address, n):
    """
    Sets up this server to (1) connect to other servers and (2) connect to client
    """
    self.sel = selectors.DefaultSelector()
    self.logger = logging.getLogger('Server')
    logging.basicConfig(filename='test.log', level=logging.DEBUG)
    
    self.client_port : int = address[1]
    self.server_id : int = server_id
    self.server_port : int = 20000 + self.server_id
    
    # establish a listening TCP endpoint to client
    self.client_lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.client_lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # establish a listening TCP endpoint for other servers
    self.server_lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server_lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    self.n = n

    # bind to client-facing port; assumed guaranteed to be available
    while True:
      try:
        self.client_lsock.bind(address)
        break
      except:
        pass

    # bind to server-facing port; available by port assigning convention
    while True:
      try:
        self.server_lsock.bind(('localhost', self.server_port))
        break
      except:
        pass

    self.client_csock = None

    # map server IDs to sockets
    self.id_to_sock = {}
    
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

    # finish setting up our client listening socket
    self.client_lsock.listen(int(n))
    self.client_lsock.setblocking(False)
    self.sel.register(self.client_lsock, selectors.EVENT_READ, data=None)

    # finish setting up our server listening socket
    self.server_lsock.listen(int(n))
    self.server_lsock.setblocking(False)
    self.sel.register(self.server_lsock, selectors.EVENT_READ, data=None)

    # raft-specific persistent state on ALL servers
    self.current_term = 0
    self.voted_for = None # reset always when current term changes
    self.log = {} # log[index] = (cmd, term)

    # volatile state on ALL servers
    self.commit_index = 0
    self.last_applied = 0

    self.state = 'follower' # valid states: 'follower', 'leader', 'candidate'
    self.election_timeout = random.randint(150,300)
    self.election_timer = threading.Timer(self.election_timeout/1000, self.convert_to_candidate)
    self.heartbeat_timer = None
    self.leader = None

    # volatile state ONLY for leaders, None otherwise
    self.match_index = None
    self.next_index = None
    # TODO. array of queues for retrying indefinitely for servers that have failed
    self.pending_rpcs = None

    # state for candidates
    self.vote_count = 0 

    

  def crash(self):
    """
    Immediately crashes this server
    """
    sys.exit(0)

  def convert_to_follower(self):
  	if self.state == 'candidate':
  		pass
  	elif self.state == 'leader':
  		self.leader = None
  		self.pending_rpcs = None
  		self.match_index = None
  		self.next_index = None
  	elif self.state == 'follower':
  		pass
  	self.state = 'follower'


  def send(self, msg, sock):
    try:
    	sock.send((text_format.MessageToString(msg) + '*').encode('utf-8'))
    except Exception:
    	print('failure to send')
    	pass

  def convert_to_candidate(self):
  	self.state = 'candidate'
  	self.leader = None
  	self.start_election()

  def convert_to_leader(self):
  	self.election_timer.cancel()
  	self.state = 'leader'
  	self.leader = self.server_id
  	self.send_heartbeats()


  def reset_election_timer(self):
  	self.election_timer.cancel()
  	self.election_timer = threading.Timer(self.election_timeout/1000, self.convert_to_candidate)
	self.election_timer.start()

  def start_election(self):
  	self.current_term += 1
  	self.vote_count = 0
  	msg = rpc.Rpc()
    msg.type = rpc.Rpc.REQUEST_VOTE
    msg.voteReq.candidateTerm = self.current_term
    last_log_idx = max(self.log)
    msg.voteReq.lastLogIndex = last_log_idx
    msg.voteReq.lastLogTerm = self.log[last_log_idx][1]
    self.vote_count += 1
    for i in self.id_to_sock:
    	self.send(msg, self.id_to_sock[i])
    self.reset_election_timer()

  def handle_handshake_req(self, handshake_req, sock):
    self.id_to_sock[handshake_req.id] = sock
    print(self.server_id, 'got handshake req from', handshake_req.id)
    msg = rpc.Rpc()
    msg.type = rpc.Rpc.REQUEST_HANDSHAKE_RES
    msg.handshakeRes.id = self.server_id
    self.send(msg, sock)

  def handle_handshake_res(self, handshake_res, sock):
    self.id_to_sock[handshake_res.id] = sock
    print(self.server_id, 'got handshake res from', handshake_res.id)

  def handle_vote_req(self, vote_req, sock):
  	msg = rpc.Rpc()
    msg.type = rpc.Rpc.REQUEST_VOTE_RES
    msg.voteRes.id = self.server_id

    if vote_req.candidateTerm < self.current_term:
      msg.voteRes.voteGranted = False
    
    else:
    	if self.current_term < vote_req.candidateTerm:
    		self.convert_to_follower()
    		self.current_term = vote_req.candidateTerm
	    	self.voted_for = None
    	last_log_idx = max(self.log)
    	if (self.voted_for = None or self.voted_for == vote_req.candidateId) and log_comparison(vote_req.lastLogIndex, vote_req.lastLogTerm, last_log_idx, self.log[last_log_idx]) >= 0:
    		msg.voteRes.voteGranted = True
    		self.voted_for = vote_req.candidateId
    	else:
    		msg.voteRes.voteGranted = False
    	self.reset_election_timer() # only reset if vote is granted
    msg.voteRes.term = self.current_term
    self.send(msg, sock)

  def handle_vote_res(self, vote_res, sock):
    if vote_res.term > self.current_term:
    	self.current_term = vote_res.term
    	self.convert_to_follower()
    	return
    if vote_res.candidateTerm != self.current_term:
    	return
    self.vote_count += 1
    if self.vote_count >= int(self.n/2 + 1):
    	self.convert_to_leader()
    pass

  def send_heartbeats(self):
  	self.heartbeat_timer = threading.Timer(self.election_timeout/1000, self.send_heartbeats)
  	msg = rpc.Rpc()
    msg.type = rpc.Rpc.APPEND_ENTRIES
    msg.appendEntries.term = self.current_term
    msg.appendEntries.leaderId = self.server_id
    msg.appendEntries.prevLogIndex = 0 # TODO
    msg.appendEntries.prevLogTerm = 0 # TODO
    msg.appendEntries.entries = []
    msg.appendEntries.leaderCommit = self.commit_index

    for i in self.id_to_sock:
    	self.send(msg, self.id_to_sock[i])

  def handle_append_entries(self, append_entries, sock):
  	msg = rpc.Rpc()
    msg.type = rpc.Rpc.APPEND_ENTRIES_RES
    msg.appendEntriesRes.term = self.current_term

    if append_entries.term < self.current_term:
    	msg.appendEntriesRes.success = False
    	self.send(msg, sock)
    	return
    elif self.state == 'candidate':
    	self.convert_to_follower()
    	self.current_term = append_entries.term
    	# TODO FINISH PROCESSING AE
    	msg.appendEntriesRes.success = True
    	self.send(msg, sock)
    	self.reset_election_timer()
    self.leader = append_entries.leaderId
  
  def handle_append_entries_res(self, append_entries_res, sock):
  	if append_entries_res.term > self.current_term:
  		self.convert_to_follower()
  		return
  	if append_entries_res.leaderTerm != self.current_term:
  		return
  	# TODO FINISH PROCESSING AE



  def log_comparison(last_log_idx_1, last_log_term_1, last_log_idx_2, last_log_idx_2):
  """
  returns:
  	> 0 if log 1 is more up-to-date
  	0 if log 1 and 2 are equally up-to-date
  	< 0 otherwise
  """
    if last_log_term_1 > last_log_idx_2:
    	return 1
    elif last_log_term_1 < last_log_idx_2:
    	return -1
    return last_log_idx_1 - last_log_idx_2

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
    if self.client_csock is None and sock == self.client_lsock:
      self.client_csock = conn
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
          recv_buffer = recv_data.decode('utf-8')
          print(self.server_id, 'got data: ', recv_buffer)
          while len(recv_buffer) > 0:
            payload = recv_buffer

            if '*' in recv_buffer:
              payload = recv_buffer[:recv_buffer.index('*')]
              recv_buffer = recv_buffer[recv_buffer.index('*') + 1:]
              print('new recv buffer', recv_buffer)
            else:
              recv_buffer = ''

            # determine the requester
            from_client = (sock == self.client_csock)
            if from_client is True:
              cmd = payload.split()[0] 
              if cmd == 'crash':
                self.crash()
              pass
            else:
              msg = rpc.Rpc()
              text_format.Parse(payload, msg)
              if msg.type == rpc.Rpc.REQUEST_HANDSHAKE:
                self.handle_handshake_req(msg.handshakeReq, sock)
              elif msg.type == rpc.Rpc.REQUEST_HANDSHAKE_RES:
                self.handle_handshake_res(msg.handshakeRes, sock)
              elif msg.type == rpc.Rpc.REQUEST_VOTE:
                self.handle_vote_req(msg.voteReq, sock)
              elif msg.type == rpc.Rpc.REQUEST_HANDSHAKE_RES:
                self.handle_vote_res(msg.voteRes, sock)
              elif msg.type == rpc.Rpc.APPEND_ENTRIES:
              	self.handle_append_entries(msg.appendEntries, sock)

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

  parser = argparse.ArgumentParser(description='Process [pid] [n] [port]')
  parser.add_argument('pid', type=int, nargs='+',
                   help='the process ID')
  parser.add_argument('n', type=int, nargs='+',
                   help='the number of servers')
  parser.add_argument('port', type=int, nargs='+',
                   help='the server port') # 60000 + i

  logging.basicConfig(level=logging.DEBUG,
                      format='%(name)s: %(message)s',)

  args = parser.parse_args()

  address = ('localhost', args.port[0])
  server = Server(args.pid[0], address, args.n[0])
  server.start()