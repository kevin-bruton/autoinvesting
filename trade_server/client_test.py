# https://blog.csdn.net/weixin_39716043/article/details/110982437
# https://blog.csdn.net/SmartShepi/article/details/115405966

from time import ctime
import socket

def create_tcp_client():
    server_host = 'localhost'
    server_port_number = 5000
    buffer_size = 10
    print("Input the data send to server:")
    while True:
        tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_client.connect((server_host, server_port_number))
        client_data = input(">")
        if client_data == 'bye':
            break
        # Add the '\r\n' character at the end of the sent data, because the TCP server handler will call the readline() function 
        # to get client send data, if the client does not send the '\n' character ( new line character ) then the server readline() 
        # function will hang and do not receive client send data.
        tcp_client.sendall((client_data + '\r\n').encode('utf-8'))
        server_data_all = ''
        server_data = tcp_client.recv(buffer_size).decode('utf-8').strip()
        while len(server_data) > 0:
            server_data_all += server_data
            server_data = tcp_client.recv(buffer_size).decode('utf-8').strip()
        print('Message from server: ' + server_data_all)
    tcp_client.close()

if __name__ == '__main__':
    create_tcp_client()
