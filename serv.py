import socket
import threading

SERVER_HOST = socket.gethostname()
SERVER_PORT = 8000

# dictionary to keep track of connected clients and their addresses
clients = {}

# create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to a specific address and port
server_socket.bind((SERVER_HOST, SERVER_PORT))

# listen for incoming connections
server_socket.listen()

def handle_client(client_socket, client_address):
    """Thread function to handle a client connection"""

    # add the client to the dictionary
    clients[client_address] = client_socket

    gameStarter = "W"

    if len(clients.values()) == 2:
        for address, socket in clients.items():
            socket.send(gameStarter.encode('utf-8'))
            gameStarter = "B"

    # receive messages from the client and broadcast to other clients
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break
        for address, socket in clients.items():
            if address != client_address:
                print("SAAAA")
                socket.send(message.encode('utf-8'))

    # remove the client from the dictionary and close the socket
    del clients[client_address]
    client_socket.close()

# accept incoming connections and spawn a new thread to handle each one
while True:
    client_socket, client_address = server_socket.accept()
    print("Connected!", client_address)
    thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    thread.start()
    if len(clients.values()) == 2:
        break