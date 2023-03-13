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

def log(accountId, msg):
  time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  with open(f"logs/client-{accountId}.log", 'a') as f:
    f.write(f"{time_str} {msg}\n")

def handle_auth_request (client, client_id, msg):
  print(f"[PUBLISHER] RECEIVED AUTH REQUEST FROM {client_id}: {msg}")
  accountSubscriptions = db.authenticate_mt_client(msg['token'], msg['account_number'], msg['account_type'])
  print('[PUBLISHER]   Result from user authentication:', accountSubscriptions)
  if accountSubscriptions == None:
    account_id = db.get_account_id(msg['account_number'])
    send(client, f"authorization_failed")
    client.close()
    print('[PUBLISHER]   Authorization failed. Closed connection with client. Client_id:', client_id, 'Account Id:', account_id)
    log(account_id, 'Attempted authorization failed. Closed connection')
  else:
    account_id, subscriptions = accountSubscriptions
    active_clients.append({ 'client': client, 'client_id': client_id, 'accountId': account_id, 'subscriptions': subscriptions })
    str_subscriptions = ','.join([str(s) for s in subscriptions])
    response = f"authorized|{str_subscriptions}"
    print('[PUBLISHER]   Sending to ', client_id, 'with account id', account_id, ':', response)
    send(client, response)
    log(account_id, f"Successful authentication. Subscriptions: {str_subscriptions}")

def handle_get_subscriptions (client, account_id, msg):
  print(f"[PUBLISHER] RECEIVED GET SUBSCRIPTIONS REQUEST FROM {account_id}: {msg}")
  subscriptions = db.get_accounts_subscriptions(account_id)
  str_subscriptions = ','.join([str(s) for s in subscriptions])
  response = f"got_subscriptions|{str_subscriptions}"
  print('[PUBLISHER]    Sending to client with account id', account_id, ':', response)
  send(client, response)

def handle_heartbeat (account_id):
  print(f"[PUBLISHER] RECEIVED HEARTBEAT FROM {account_id}")
  db.register_heartbeat(account_id)
  
def handle_place_order_response (account_id, msg):
  print(f"[PUBLISHER] RECEIVED PLACE ORDER REPORT FROM {account_id}: {msg}")
  if msg['status'] == 'placed' or msg['status'] == 'open':
    order = Order(msg['orderId'],msg['masterOrderId'],account_id,msg['magic'],msg['symbol'],msg['orderType'],msg['openTime'],msg['openPrice'],msg['size'],msg['comment'],msg['sl'],msg['tp'],msg['status'])
    db.save_order(order)
    log(account_id, f"CREATE ORDER. RESULT: {msg['status']} {order}")
  else:
    log(account_id, f"CREATE ORDER. RESULT: FAILED! REASON: {msg['reason']}; DETAILS: {msg}")

def handle_close_position_response (account_id, msg):
  print(f"[PUBLISHER] RECEIVED CLOSE POSITION REPORT FROM {account_id}: {msg}")
  if msg['status'] == 'closed':
    order = db.get_order(msg['orderId'])
    db.delete_order(msg['orderId'])
    trade = Trade(msg['orderId'],order['masterOrderId'],account_id,order['magic'],order['symbol'],order['orderType'],order['openTime'],msg['closeTime'],order['openPrice'],msg['closePrice'],order['size'],msg['profit'],msg['balance'],msg['closeType'],msg['comment'],order['sl'],order['tp'],msg['swap'],msg['commission'])
    db.save_trade(trade)
    log(account_id, f"CLOSED POSITION {trade}")
  else:
    log(account_id, f"FAILED TO CLOSE POSITION {msg}")

def handle_cancel_order_response (account_id, msg):
  print(f"[PUBLISHER] RECEIVED CANCEL ORDER REPORT FROM {account_id} **** NOT IMPLEMENTED YET ****: {msg}")

def handle_message(client, client_id, received_msg):
  # print(f"[PUBLISHER] RECEIVED MSG {client_id}: {received_msg}")
  global active_clients
  try:
    msg = json.loads(received_msg)
  except Exception as e:
    print('[PUBLISHER] MESSAGE NOT A VALID JSON', repr(e), 'MESSAGE:', received_msg)
    send(client, 'Got your non-json message!')
    return
  
  account_id = None if msg['action'] == 'subscribe' \
    else [c['accountId'] for c in active_clients if c['client_id'] == client_id][0]
  
  if 'action' not in msg:
    return
  if msg['action'] == 'subscribe':        handle_auth_request(client, client_id, msg)
  elif msg['action'] == 'get_subscriptions': handle_get_subscriptions(client, account_id, msg)
  elif msg['action'] == 'heatbeat':       handle_heartbeat(account_id)
  elif msg['action'] == 'place_order':    handle_place_order_response(account_id, msg)
  elif msg['action'] == 'close_position': handle_close_position_response(account_id, msg)
  elif msg['action'] == 'cancel_order':   handle_cancel_order_response(account_id, msg)

def handle_msgs_from_master(trades_queue):
  """ Receives trades performed by the Master
      It looks for all accounts that have subscribed to that strategy
      If the subscribed client is connected, the message is sent to that client for it to be performed there
      If the subscribed client is not connected, then an entry is added to the log to register this event
  """
  format_msg = lambda msg: (msg + '\r\n').encode('utf-8')
  while True:
    sleep(1)
    if not trades_queue.empty():
      t = trades_queue.get()
      # get all accountIds that are subscribed to the strategy
      # send the trade to them if they are in active_clients and log
      # if not connected, just log the fact in their account log
      size = t['size'] # TODO: Will have to calculate based on client's money management
      account_ids = db.get_accounts_subscribed_to_magic(t['magic'])
      for account_id in account_ids:
        is_account_connected = account_id in [c['accountId'] for c in active_clients]
        # get client's corresponding orderId so it knows which one to cancel == get orderId with masterOrderId and accountId from Orders
        client_order_id = db.get_corresponding_orderid(t['orderId'], account_id)
        msg = format_msg(f"{t['action']}|{t['direction']}|{t['symbol']}|{size}|{t['openPrice']}|{t['sl']}|{t['tp']}|{t['comment']}|{t['magic']}|{t['orderId']}|{client_order_id}")
        if is_account_connected:
          connection = [c for c in active_clients if account_id == c['accountId']][0]
          print(f"[PUBLISHER] SENDING MSG TO CLIENT WITH ACCOUNTID {account_id} MSG: {msg}")
          connection['client'].sendall(msg)
        else:
          print(f"[PUBLISHER] ERROR: CLIENT {account_id} NOT CONNECTED. TRIED TO SEND MESSAGE: {msg}")
          log(account_id, f"ERROR: CLIENT NOT CONNECTED. TRIED TO SEND MESSAGE: {msg}")

def handle_client(client, client_id):
  def get_response ():
    try:
      response = client.recv(1024).decode('utf-8')
    except ConnectionResetError:
      print('[PUBLISHER] Connection reset')
      return False
    except Exception as e:
      print('[PUBLISHER] ERROR receiving from client')
      return False
    if response == '':
      print('[PUBLISHER] Socket reponse is empty')
      return False
    return response
  def has_an_end_of_message(response):
    return response.find('\n') != -1
  def get_end_msg_position(response):
    return response.find('\n')

  global active_clients
  cur_thread = current_thread().name
  print(f"[PUBLISHER] [NEW CONNECTION] {client_id} connected. Num threads: {active_count()}. Current thread: {cur_thread}")

  response = ''
  msg = ''
  while True:
    response = get_response()
    if response == False:
      print('[PUBLISHER] No longer listening to clients')
      break
    if has_an_end_of_message(response): # if there is a complete message
      end_msg_position = get_end_msg_position(response)
      msg += response[:end_msg_position]
      if msg == '':
        print('[PUBLISHER] Empty message')
        break
      else:
        handle_message(client, client_id, msg)
      response = response[end_msg_position+1:]
      msg = ''
    else:
      msg += response
      response = ''

  client.close()
  # remove client from active_clients
  active_clients = [c for c in active_clients if c['client_id'] != client_id]
  print('[PUBLISHER] Closed connection with client on thread', cur_thread, 'Client_id:', client_id)

def handle_connections_and_subscriptions():
  sock = bind_to_socket()
  while True:
    client, addr = sock.accept()
    client_id = f'{addr[0]}-{client.fileno()}'
    Thread(target=handle_client, args=(client, client_id)).start()

def bind_to_socket ():
  def bind (host, port, bind_attempt):
    try:
      sock.bind((host, port))
      return True
    except Exception as e:
      print('[PUBLISHER] ERROR: Trade publisher could not bind to', host, port, e, ' Attempt', bind_attempt)
      return False

  HOST = 'localhost'
  PORT = 3000
  MAX_CLIENTS = 5
  bind_attempt = 1

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  bound = bind(HOST, PORT, bind_attempt)
  while not bound:
    sleep(10)
    bind_attempt += 1
    bound = bind(HOST, PORT, bind_attempt)
  print(f'[PUBLISHER] Trade publisher listening on {HOST}:{PORT} Max clients: {MAX_CLIENTS}...')
  sock.listen(MAX_CLIENTS)
  return sock


def run_publisher(trades_queue):
  Thread(target=handle_connections_and_subscriptions).start()
  Thread(target=handle_msgs_from_master, args=(trades_queue,)).start()
