import socket
from threading import Thread, current_thread, active_count
from time import sleep
from queue import Queue
import json
from trade_server.db import authenticate_user

active_clients = [] # a client: { client, client_id, subscriptions }

def send(client, msg):
  format_msg = lambda msg: (msg + '\r\n').encode('utf-8')
  client.sendall(format_msg(msg))

def handle_message(client, client_id, received_msg):
  global active_clients
  print(f"[PUBLISHER] Received from {client_id}: {received_msg}")
  try:
    msg = json.loads(received_msg)
    if msg['action'] == 'subscribe':
      subscriptions = authenticate_user(msg['token'], msg['account_type'], msg['account_number'])
      active_clients.append({ 'client': client, 'client_id': client_id, 'subscriptions': subscriptions })
      str_subscriptions = ','.join([str(s) for s in subscriptions])
      response = 'authorized:' + str(bool(len(subscriptions))).lower() + f'|subscribed:{str_subscriptions}'
      print('[PUBLISHER] Sending to ', client_id, ':', response)
      send(client, response)
  except Exception as e:
    send(client, 'Got your non-json message!')
    print(e)

def handle_client(client, client_id):
  global active_clients
  cur_thread = current_thread().name
  print(f"[PUBLISHER] [NEW CONNECTION] {client_id} connected. Num threads: {active_count()}. Current thread: {cur_thread}")

  response = ''
  while True:
    try:
      response += client.recv(1024).decode('utf-8')
    except ConnectionResetError:
      print('[PUBLISHER] Connection reset')
      break
    if response == '':
      print('[PUBLISHER] Socket reponse is empty')
      break
    if response:
      # print('response:', response)
      end_msg = response.find('\n')
      if end_msg != -1: # if message is complete
        msg = response[:end_msg]
        if msg == '':
          print('[PUBLISHER] Empty message')
          break
        else:
          handle_message(client, client_id, msg)
        response = response[end_msg+1:]
    else:
      print('[PUBLISHER] No response')

  client.close()
  # remove client from active_clients
  active_clients = [c for c in active_clients if c['client_id'] != client_id]
  print('[PUBLISHER] Closed connection with client on thread', cur_thread, 'Client_id:', client_id)

def send_trades(trades_queue):
  format_msg = lambda msg: (msg + '\r\n').encode('utf-8')
  while True:
    sleep(1)
    if not trades_queue.empty():
      t = trades_queue.get()
      # print('    **** Going to send this trade:', t)
      for active_client in active_clients:
        if t['magic'] in active_client['subscriptions']:
          size = t['size'] # TODO: Will have to calculate based on client's money management
          msg = f"{t['action']}|{t['direction']}|{t['symbol']}|{size}|{t['openPrice']}|{t['sl']}|{t['tp']}|{t['comment']}|{t['magic']}"
          print(f'[PUBLISHER] Sending trade to {active_client["client_id"]}: {msg}')
          active_client['client'].sendall(format_msg(msg))

def handle_connections_and_subscriptions():
  HOST = 'localhost'
  PORT = 3000
  MAX_CLIENTS = 5

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    sock.bind((HOST, PORT))
  except Exception as e:
    print('[PUBLISHER] Trade publisher could not bind to', HOST, PORT, e)
    quit()
  print(f'[PUBLISHER] Trade publisher listening on {HOST}:{PORT} Max clients: {MAX_CLIENTS}...')
  sock.listen(MAX_CLIENTS)
  while True:
    client, addr = sock.accept()
    client_id = f'{addr[0]}-{client.fileno()}'
    Thread(target=handle_client, args=(client, client_id)).start()

def run_publisher(trades_queue):
  Thread(target=handle_connections_and_subscriptions).start()
  Thread(target=send_trades, args=(trades_queue,)).start()
