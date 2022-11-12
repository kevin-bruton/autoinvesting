import socket
from threading import Thread, current_thread, active_count
from time import sleep
from datetime import datetime
from queue import Queue
import json
import back.db as db
from back.db import Order, Trade

active_clients = [] # a client: { client, client_id, subscriptions }

def send(client, msg):
  format_msg = lambda msg: (msg + '\r\n').encode('utf-8')
  client.sendall(format_msg(msg))

def handle_message(client, client_id, received_msg):
  global active_clients
  try:
    msg = json.loads(received_msg)
  except Exception as e:
    send(client, 'Got your non-json message!')
    print(e)
    return
  if msg['action'] == 'subscribe':
    print(f"[PUBLISHER] RECEIVED AUTH REQUEST FROM {client_id}: {received_msg}")
    accountSubscriptions = db.authenticate_mt_client(msg['token'], msg['account_number'], msg['account_type'])
    print('[PUBLISHER]   Result from user authentication:', accountSubscriptions)
    if accountSubscriptions == None:
      send(client, f"authorization_failed")
      client.close()
      print('[PUBLISHER]   Authorization failed. Closed connection with client. Client_id:', client_id)
    else:
      active_clients.append({ 'client': client, 'client_id': client_id, 'accountId': accountSubscriptions.accountId, 'subscriptions': accountSubscriptions.subscriptions })
      str_subscriptions = ','.join([str(s) for s in accountSubscriptions.subscriptions])
      response = f"authorized|{str_subscriptions}"
      print('[PUBLISHER]   Sending to ', client_id, ':', response)
      send(client, response)
  elif msg['action'] == 'create_order':
    account_id = [c['accountId'] for c in active_clients if c['client_id'] == client_id][0]
    print(f"[PUBLISHER] RECEIVED CREATE ORDER REPORT FROM {account_id}: {received_msg}")
    if msg['status'] == 'order_placed' or msg['status'] == 'position_opened':
      order = Order(msg['orderId'],msg['masterOrderId'],account_id,msg['magic'],msg['symbol'],msg['orderType'],msg['openTime'],msg['openPrice'],msg['size'],msg['comment'],msg['sl'],msg['tp'],msg['status'])
      db.save_order(order)
      log(account_id, 'CREATE ORDER. RESULT:', msg['status'], order)
    else:
      log(account_id, 'CREATE ORDER. RESULT: FAILED! REASON:', msg['reason'],'; DETAILS:',order)

def send_trades(trades_queue):
  format_msg = lambda msg: (msg + '\r\n').encode('utf-8')
  while True:
    sleep(1)
    if not trades_queue.empty():
      t = trades_queue.get()
      # get all accountIds that are subscribed to the strategy
      # send the trade to them if they are in active_clients and log
      # if not connected, just log the fact in their account log
      size = t['size'] # TODO: Will have to calculate based on client's money management
      msg = format_msg(f"{t['action']}|{t['direction']}|{t['symbol']}|{size}|{t['openPrice']}|{t['sl']}|{t['tp']}|{t['comment']}|{t['magic']}|{t['orderId']}")
      accountIds = db.get_accounts_subscribed_to_magic(t['magic'])
      for accountId in accountIds:
        is_account_connected = accountId in [c['accountId'] for c in active_clients]
        if is_account_connected:
          connection = [c for c in active_clients if accountId == c['accountId']][0]
          print(f"SENDING MSG TO CLIENT WITH ACCOUNTID {accountId} MSG: {msg}")
          connection['client'].sendall(msg)
        else:
          print(accountId, f"ERROR: CLIENT NOT CONNECTED. TRIED TO SEND MESSAGE: {msg}")
          log(accountId, f"ERROR: CLIENT NOT CONNECTED. TRIED TO SEND MESSAGE: {msg}")

def log(accountId, msg):
  time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  with open(f"logs/client-{accountId}.log", 'a') as f:
    f.write(f"{time_str} {msg}\n")

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

def handle_connections_and_subscriptions():
  HOST = 'localhost'
  PORT = 3000
  MAX_CLIENTS = 5

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    sock.bind((HOST, PORT))
  except Exception as e:
    print('[PUBLISHER] ***** ERROR: Trade publisher could not bind to', HOST, PORT, e, ' *****')
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
