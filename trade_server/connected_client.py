import sys
import selectors
import json
import io
import struct

class ConnectedClient:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False
        self._recv_msg_len = None

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {mode!r}.")
        self.selector.modify(self.sock, events, data=self)
                
    def handle_json_request(self):
        action = self.request.get("action")
        if action == "subscribe":
            client_id = self.request.get("client_id")
            token = self.request.get("token")
            account_balance = self.request.get("account_balance")
            account_num = self.request.get("account_num")
            # authorize user credentials & make sure there isn't a conn_id already active(?)
            content = { "action": action, "success": True, "message": "subscribed to magics 001, 002, 003" }
        elif action == "search":
            content = { "action": action, "success": True, "message": "you are searching for " + self.request.get('value') }
        else:
            content = {"result": f"Error: invalid action '{action}'."}
        return json.dumps(content)

    def process_events(self, ev_type):
        if ev_type & selectors.EVENT_READ: # available for read
            self.read()
        if ev_type & selectors.EVENT_WRITE: # available for write
            self.write()

    def read(self):
        self._read_and_save_to_buffer()
        if self._recv_msg_len is None:
            self.process_header() # gets the header length and updates _recv_buffer
        if self._recv_msg_len:
            if self.request is None:
                self.process_request()

    def _read_and_save_to_buffer(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
            print('Got data:', data)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                # raise RuntimeError("Peer closed.")
                print('Remote client has closed')
                self.close()

    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response()
        self._write()
        self._set_selector_events_mask("r")

    def _write(self):
        if self._send_buffer:
            print(f"Sending {self._send_buffer!r} to {self.addr}")
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                # Close when the buffer is drained. The response has been sent.
                if sent and not self._send_buffer:
                    print('Message sent')
                    # self.close()

    def close(self):
        print(f"Closing connection to {self.addr}")
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                f"Error: selector.unregister() exception for "
                f"{self.addr}: {e!r}"
            )
        try:
            self.sock.close()
        except OSError as e:
            print(f"Error: socket.close() exception for {self.addr}: {e!r}")
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    def process_header(self):
        hdrlen = 4
        if len(self._recv_buffer) >= hdrlen:
            self._recv_msg_len = int(self._recv_buffer[:hdrlen])
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_request(self):
        content_len = self._recv_msg_len
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        self.request = json.loads(data)
        # Set selector to listen for write events, we're done reading.
        self._set_selector_events_mask("w")

    def _create_message(self, response):
        resp_len = str(len(response))
        while len(resp_len) < 4:
            resp_len = f'0{resp_len}'
        # print('Response to be sent. Length:', resp_len, '; Response:', response)
        message = f'{resp_len}{response}'
        return bytes(message, 'utf-8')

    def create_response(self):
        response = self.handle_json_request()
        self.response_created = True
        self._send_buffer += self._create_message(response)
