import sys
import socket
import selectors
import traceback
from threading import Thread

from trade_server.connected_client import ConnectedClient

def send_trade (lsock):
  pass

def listen_to_clients (lsock):

  def accept_client(sock):
      conn, addr = sock.accept()  # Should be ready to read
      print(f"Accepted connection from {addr}")
      conn.setblocking(False)
      client = ConnectedClient(sel, conn, addr)
      sel.register(conn, selectors.EVENT_READ, data=client)

  sel = selectors.DefaultSelector()
  sel.register(lsock, selectors.EVENT_READ, data=None)


  try:
      while True:
          events = sel.select(timeout=None) # waits here for a client to connect or send a msg
          for key, ev_type in events:
              if key.data is None:
                  accept_client(key.fileobj)
              else:
                  client = key.data
                  try:
                      client.process_events(ev_type)
                  except Exception:
                      print(
                          f"Main: Error: Exception for {client.addr}:\n"
                          f"{traceback.format_exc()}"
                      )
                      client.close()
  except KeyboardInterrupt:
      print("Caught keyboard interrupt, exiting")
  finally:
      sel.close()


def run_publisher (trade_queue):

  """ if len(sys.argv) != 3:
      print(f"Usage: {sys.argv[0]} <host> <port>")
      sys.exit(1) """

  host, port = '127.0.0.1', 5000
  lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # Avoid bind() exception: OSError: [Errno 48] Address already in use
  lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  lsock.bind((host, port))
  lsock.listen()
  print(f"Listening on {(host, port)}")
  lsock.setblocking(False)

  listen_to_clients_thread = Thread(target=listen_to_clients, args=(lsock,))
  send_trades_thread = Thread(target=send_trade, args=(lsock,))

  listen_to_clients_thread.start()
  send_trades_thread.start()