# https://blog.csdn.net/weixin_39716043/article/details/110982437
# https://blog.csdn.net/SmartShepi/article/details/115405966

from socketserver import StreamRequestHandler
from socketserver import TCPServer, ThreadingTCPServer
from time import ctime
import threading
from queue import Queue
import json

class TCPRequestHandler(StreamRequestHandler):
  def setup(self) -> None:
    # print('\nSetup TCP request handler.')
    return super().setup()
    
  def handle(self) -> None:
    client_ip, client_port = self.client_address
    cur_thread = threading.current_thread().name
    socket = self.request
    connection_id = f'{client_ip}-{socket.fileno()}'
    # print('Listening to client:', connection_id)
    # The readline() function will return only when the client send a \n which is a new line character.
    # If the client do not send the \n character, then readline() mehtod will hang and never return.
    received_msg = self.rfile.readline().strip().decode('utf-8')
    if received_msg == '':
      print('End of connection with client', connection_id)
    else:
      print('Received message from', connection_id + ': "' + received_msg + '"')
      msg = json.loads(received_msg)
      if msg['action'] == 'subscribe':
        print('User has requested to subscribe')
        # Authenticate user
        # Get contracted subscriptions
        # Return authentication result and subscriptions if authentication successful
    # curr_time = ctime()
    # self.wfile.write((curr_time + ' - ' + client_send_data_line_str).encode('utf-8'))
    self.wfile.write('{ "authorized": true }\n'.encode('utf-8'))

  def finish(self) -> None:
    # print('Finish TCP request handler.\r\n')
    return super().finish()

def create_tcp_server():
  server_host = 'localhost'
  server_port_number = 5000
  tcp_server = ThreadingTCPServer((server_host, server_port_number), TCPRequestHandler)
  print('TCP server started on host \'' + server_host + ':' + str(server_port_number) + '\'\r\n')
  try:
    tcp_server.serve_forever()
  except KeyboardInterrupt:
    pass
  return tcp_server

def run_publisher(trades_queue, client_subscriptions):
  server = create_tcp_server()
  server.shutdown()
  print('\nSocket server has shutdown')


trades_queue = Queue()
client_subscriptions = [
  { 'username': 'kev7777', 'subscriptions': [220612001, 220612002], 'connection_id': None }
]
run_publisher(trades_queue, client_subscriptions)