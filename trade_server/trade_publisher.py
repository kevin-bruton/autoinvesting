import socket
from threading import Thread, current_thread, active_count
from time import sleep
from queue import Queue
import json
from trade_server.db import authenticate_user

HOST = 'localhost'
PORT = 5000
MAX_CLIENTS = 5

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind((HOST, PORT))

def format_msg(msg):
  return (msg + '\r\n').encode('utf-8')
def send(client, msg):
  client.sendall(format_msg(msg))

def handle_message(client, received_msg):
  print(f"Received: {addr} {received_msg}")
  msg = json.loads(received_msg)
  if msg['action'] == 'subscribe':
    subscriptions = authenticate_user(msg['token'], msg['account_type'], msg['account_number'])
    send(client, 'authorized:' + str(bool(subscriptions)).lower() + f'|subscribed:{subscriptions[1:-1]}')
  else:
    send(client, 'Got your message!\r\n').encode('utf-8')

def handle_client(client, addr):
  cur_thread = current_thread().name
  print(f"[NEW CONNECTION] {addr} connected. Num threads: {active_count()}. Current thread: {cur_thread}")
  response = ''
  while True:
    try:
      response += client.recv(1024).decode('utf-8')
    except ConnectionResetError:
      print('Connection reset')
      break
    if response == '':
      print('Socket reponse is empty')
      break
    if response:
      # print('response:', response)
      end_msg = response.find('\n')
      if end_msg != -1: # if message is complete
        msg = response[:end_msg]
        if msg == '':
          print('Empty message')
          break
        else:
          handle_message(client, msg)
        response = response[end_msg+1:]
    else:
      print('No response')

  client.close()
  print('Closed connection with client on thread', cur_thread)
    
print(f'Listening on {HOST}:{PORT} Max clients: {MAX_CLIENTS}...')
socket.listen(MAX_CLIENTS)
while True:
  client, addr = socket.accept()
  # print('Client:', client)
  Thread(target=handle_client, args=(client, addr)).start()
