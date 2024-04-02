import json
import os
import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9999
BUFFER_SIZE = 1400

class Client:
    def __init__(self):
        self.tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.tcp_client_socket.connect((SERVER_HOST, SERVER_PORT))
            print("connected to the server\n")
        except socket.error as err:
            print(err)
            sys.exit(1)

    def run(self):
        file_path = ""
        file_size = 0
        while file_path == "" and file_size == 0:
            file_path, file_size = self.get_file_path()

        result = self.send_request_data(file_path, file_size)
        if not result:
            self.tcp_client_socket.close()
            return

        self.receive_response_data()
        self.tcp_client_socket.close()

    def get_file_path(self):
        file_path = input("enter path to the mp4 file to upload: ")

        try:
            file_size = os.path.getsize(file_path)
            print(f"[*] file size: {file_size} bytes")
            return file_path, file_size
        except FileNotFoundError:
            print("[!] file not found")
            return "", 0

    def send_request_data(self, file_path, file_size):
        try:
            self.tcp_client_socket.send(str(file_size).encode().ljust(32))
            with open(file_path, 'rb') as f:
                while True:
                    file_data = f.read(BUFFER_SIZE)
                    if not file_data:
                        break
                    self.tcp_client_socket.sendall(file_data)
            print("[*] file sent successfully")
            return True
        except:
            print("[!] file sent unsuccessfully")
            return False

    def receive_response_data(self):
        response_data = self.tcp_client_socket.recv(32).decode()
        print(f"[*] server response: {response_data}")

if __name__ == "__main__":
    client = Client()
    client.run()
