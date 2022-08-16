import threading
import socket
import json
from time import sleep

class SocketServer:
  def __init__(self, send, receive, address = '127.0.0.1', port = 9090):
    self.send_cb = send
    self.receive_cb = receive
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.bind((address, port))
    self.resp_to_wait_for = None
    self.ev_client_connected = threading.Event()
    self.ev_stop_listening = threading.Event()
    self.ev_got_response = threading.Event()
    self.response = ''

  def start(self):
    threading.Thread(target=self.receiver).start()
    print('Waiting for clients to connect...')
    self.ev_client_connected.wait()

  def receiver(self):
    self.sock.listen()
    self.conn, self.addr = self.sock.accept()
    if self.conn:
      print('A client has connected via host', self.addr[0], 'and port', self.addr[1])
      self.ev_client_connected.set()
    data = self.conn.recv(16384).decode("utf-8")
    while not self.ev_stop_listening.is_set() and data:
      if data:
        try:
          split_msg = data.split('|')
          for msg_str in split_msg:
            if msg_str:
              msg = json.loads(msg_str)
              self.handle_incoming_msg(msg)
        except Exception as e:
          print('\nTradeServer.__receiver: Msg received does not have a valid json structure:', e, 'Raw data:', data, '\n')
      try:
        data = self.conn.recv(16384).decode("utf-8")
      except Exception as e:
        print('Error while reading from socket:', e)
    print('Stopped communication with client')
    self.close()
          
  def raw_send(self, data):
    """ data must be json-convertible """
    json_data = ""
    try:
      json_data = json.dumps(data) + '|'
    except:
      print('Data provided to send to socket client cannot be converted to a json string')
    self.conn.sendall(json_data.encode())
    # self.ev_got_response.wait()

  def send(self, msg):
    print('\nSending:', msg)
    self.resp_to_wait_for = msg['action']
    self.raw_send(msg)
    self.ev_got_response.wait()
    response = self.response
    self.response = None
    print('Got response:', response)
    return response

  def handle_incoming_msg(self, msg):
    if msg['msg_type'] == 'RESPONSE':
      if self.resp_to_wait_for == msg['action']:
        print('Response waited for:', msg, '\n')
        self.response = msg
        self.resp_to_wait_for = None
        if self.resp_to_wait_for == msg['action']:
          self.ev_got_response.set()
      else:
        print('Response not waited for:', msg, '\n')
    elif msg['msg_type'] == 'TRADE_PERFORMED':
      self.trade_performed()
    elif msg['msg_type'] == 'ON_DEINIT':
      self.on_deinit()
    else: print(f'\nTradeServer.handle_incoming_msg: msg_type not recognized: "{msg["msg_type"]}"\n')

  def close(self):
    self.ev_stop_listening.set()
    try:
      self.sock.shutdown(socket.SHUT_RDWR)
    except:
      pass
    self.sock.close()
    print('Socket has been closed')

  def trade_performed(self):
    threading.Thread(target=self.callbacks['trade_performed']).start()

  def on_deinit(self):
    print('TradeServer.on_deinit')
    threading.Thread(target=self.callbacks['on_deinit']).start()
    self.close()
    