import socket
from _thread import *
import conf




server = "127.0.0.1"
port = 5555

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server_socket.bind((server, port))
except socket.error as e:
    str(e)

print("Waiting for a connection, Server Started")

idCount = 0
connections = []
BLACK = 1
WHITE = 0


def threaded_client(connection, color):
    connection.send(str.encode(str(color)))
    while True:
        try:
            data = connection.recv(4096)
            if color == conf.WHITE:
                connections[BLACK].send(data)
            elif color == conf.BLACK:
                connections[WHITE].send(data)
        except Exception:
            break


server_socket.listen(2)
while True:
    conn, addr = server_socket.accept()
    connections.append(conn)
    print("Connected to:", addr)

    idCount += 1
    player_color = conf.WHITE
    if idCount == 1:
        print("Creating a new game...")
    else:
        player_color = conf.BLACK

    start_new_thread(threaded_client, (conn, player_color))


