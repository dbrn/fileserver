import socket
CMD_SIZE = 10


def get_command(client_socket_):
    filename = input("Insert filename: ")
    filename_length = len(filename)
    client_socket_.send(bytes(f"{filename_length:<{CMD_SIZE}}", "utf-8"))
    client_socket_.send(bytes(f"{filename}", "utf-8"))
    response = client_socket_.recv(CMD_SIZE)
    response = response.decode("utf-8").strip()
    if response == "END":
        print("File not found")
        return
    elif response == "OK":
        print("File transfer initiated")
        file = open(filename, "wb")
        response = ""
        while response != "END":
            response = client_socket_.recv(CMD_SIZE)
            response = response.decode("utf-8").strip()
            if response == "END":
                file.close()
                print("File transfer completed")
                continue
            length = int(response)
            response = client_socket_.recv(length)
            file.write(response)


def close_connection(client_socket_):
    client_socket_.close()
    print("Connection to server closed")


def list_command(client_socket_):
    response = ""
    while response != "END":
        response = client_socket_.recv(CMD_SIZE)
        response = response.decode("utf-8").strip()
        length = int(response)
        response = client_socket_.recv(length)
        response = response.decode("utf-8")
        if response == "END":
            continue
        print(response)


IP_PORT = (input("IP to connect to: "), 1234)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(IP_PORT)
message = client_socket.recv(CMD_SIZE)
if message.decode("utf-8") == "HELLO":
    client_socket.send(bytes("HELLO", "utf-8"))
    print(f"Connection to {IP_PORT[0]}:{IP_PORT[1]} established")
    while True:
        command = input(f"{IP_PORT[0]}:{IP_PORT[1]} > ")
        if len(command) > CMD_SIZE:
            print(f"{command} - command too long")
            continue
        client_socket.send(bytes(command, "utf-8"))
        message = client_socket.recv(CMD_SIZE)
        message = message.decode("utf-8")
        if message == "BYE":
            close_connection(client_socket)
            break
        elif message == "LIST":
            list_command(client_socket)
        elif message == "GET":
            get_command(client_socket)
        else:
            print(f"{message} - invalid response from server")
else:
    client_socket.close()
