#!/usr/bin/env python3

import argparse
import logging
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

    self.id_to_sock[self.server_id] = None
    
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
    self.voted_for = None
    self.log = []

    # volatile state on ALL servers
    self.commit_index = 0
    self.last_applied = 0

    # volatile state ONLY for leaders, None otherwise
    self.match_index = None
    self.next_index = None

    # TODO. array of queues for retrying indefinitely for servers that have failed
    self.pending_rpcs = None

  def crash(self):
    """
    Immediately crashes this server
    """
    sys.exit(0)

  def handle_handshake_req(self, handshake_req, sock):
    self.id_to_sock[handshake_req.id] = sock
    print(self.server_id, 'got handshake req from', handshake_req.id)
    msg = rpc.Rpc()
    msg.type = rpc.Rpc.REQUEST_HANDSHAKE_RES
    msg.handshakeRes.id = self.server_id
    sock.send((text_format.MessageToString(msg) + '*').encode('utf-8'))

  def handle_handshake_res(self, handshake_res, sock):
    self.id_to_sock[handshake_res.id] = sock
    print(self.server_id, 'got handshake res from', handshake_res.id)

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
        conn.send((text_format.MessageToString(msg) + '*').encode('utf-8'))
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
        else:
          self.process_connection_fail(sock)
      except ConnectionError:
        self.process_connection_fail(sock)

  def start(self):
    """
    Starts the server
    """
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