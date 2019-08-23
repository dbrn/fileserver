import socket
import glob
import time
CMD_LENGTH = 10
FILE_FOLDER = "./ext/"
SLEEP = 0.0001


def command_get(client_socket_, address):
    client_socket_.send(bytes("GET", "utf-8"))
    filename_len = client_socket_.recv(CMD_LENGTH)
    filename_len = int(filename_len.decode("utf-8"))
    filename = client_socket_.recv(filename_len)
    filename = filename.decode("utf-8")
    print(f"{filename} requested from {address[0]}")
    try:
        file = open(FILE_FOLDER + filename, "rb")
    except FileNotFoundError:
        print(f"{filename} not found, sending END command")
        client_socket_.send(bytes("END", "utf-8"))
        return
    print(f"{filename} found, sending OK command")
    client_socket_.send(bytes("OK", "utf-8"))
    time.sleep(SLEEP)
    file_lines = file.readlines()
    for line in file_lines:
        line_len = len(line)
        client_socket_.send(bytes(f"{line_len:<{CMD_LENGTH}}", "utf-8"))
        time.sleep(SLEEP)
        client_socket_.send(line)
        time.sleep(SLEEP)
    client_socket_.send(bytes("END", "utf-8"))
    time.sleep(SLEEP)
    file.close()
    print(f"{filename} successfully sent to {address[0]}")


def command_list(client_socket_, address):
    client_socket_.send(bytes("LIST", "utf-8"))
    time.sleep(SLEEP)
    files_list = glob.glob(FILE_FOLDER + "*.*")
    for file in files_list:
        client_socket_.send(bytes(f"{len(file[len(FILE_FOLDER):]):<{CMD_LENGTH}}", "utf-8"))
        time.sleep(SLEEP)
        client_socket_.send(bytes(file[len(FILE_FOLDER):], "utf-8"))
        time.sleep(SLEEP)
    client_socket_.send(bytes(f"{len('END'):<{CMD_LENGTH}}", "utf-8"))
    time.sleep(SLEEP)
    client_socket_.send(bytes("END", "utf-8"))
    time.sleep(SLEEP)
    print(f"List sent to {address[0]}")


def command_bye(client_socket_, address):
    client_socket_.send(bytes("BYE", "utf-8"))
    time.sleep(SLEEP)
    client_socket_.close()
    print(f"Socket with {address[0]} closed")


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
IP_PORT = ("192.168.1.11", 1234)
server_socket.bind(IP_PORT)
while True:
    server_socket.listen()
    client_socket, client_address_port = server_socket.accept()
    client_socket.send(bytes("HELLO", "utf-8"))
    response = client_socket.recv(CMD_LENGTH)
    if response.decode("utf-8") == "HELLO":
        print(f"Connection to {client_address_port[0]}:{client_address_port[1]} established")
        while True:
            command = client_socket.recv(CMD_LENGTH)
            command = command.decode("utf-8")
            print(f"{command} received from {client_address_port[0]}")
            if command == "LIST":
                command_list(client_socket, client_address_port)
            elif command == "GET":
                command_get(client_socket, client_address_port)
            elif command == "BYE":
                command_bye(client_socket, client_address_port)
                break
            else:
                print(f"{command} - invalid command from {client_address_port[0]}")
                client_socket.send(bytes("INV", "utf-8"))
    else:
        client_socket.close()
