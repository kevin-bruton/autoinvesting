#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback

from connected_client import ConnectedClient

sel = selectors.DefaultSelector()


def accept_client(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    client = ConnectedClient(sel, conn, addr)
    sel.register(conn, selectors.EVENT_READ, data=client)


if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Avoid bind() exception: OSError: [Errno 48] Address already in use
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)
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
