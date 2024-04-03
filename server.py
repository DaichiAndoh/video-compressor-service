import json
import os
import socket
import subprocess

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9999
BUFFER_SIZE = 1400
MAX_RECEIVED_BYTES = 10000000
RECEIVED_FILES_DIR = "server_received_files/"
COMPRESSED_FILES_DIR = "server_compressed_files/"
COMMAND_LOGS_DIR = "server_command_logs/"

class VideoCompressor:
    def __init__(self):
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server_socket.bind((SERVER_HOST, SERVER_PORT))
        self.tcp_server_socket.listen(1)
        print("[*] server is listening...")

    def run_server(self):
        while True:
            connection, client_address = self.tcp_server_socket.accept()
            client_port = str(client_address[1])
            print("\n[*] connected")

            # receive request data
            received_file_path, crf_value = self.receive_request_data(
                connection,
                client_port,
            )

            if received_file_path == "":
                # send error response
                self.send_response_data(connection, "", 0)
            else:
                # compress file
                compressed_file_path, compressed_file_size = self.compress_file(
                    received_file_path,
                    str(crf_value),
                    client_port,
                )
                # send success response
                self.send_response_data(connection, compressed_file_path, compressed_file_size)
                # delete received file and compressed file
                self.delete_files(received_file_path, compressed_file_path)

            print("[*] disconnected")

    def receive_request_data(self, connection, client_port):
        try:
            config_data_size = int.from_bytes(connection.recv(16), "big")
            file_type_size = int.from_bytes(connection.recv(1), "big")
            file_size = int.from_bytes(connection.recv(47))
            config_data = json.loads(connection.recv(config_data_size).decode())
            file_type = connection.recv(file_type_size).decode()
            crf_value = config_data["crf_value"]

            received_bytes = 0
            received_file_path = f"{RECEIVED_FILES_DIR}received_{client_port}.{file_type}"
            with open(received_file_path, "wb") as f:
                while received_bytes < file_size:
                    file_data = connection.recv(BUFFER_SIZE)
                    if not file_data:
                        break
                    f.write(file_data)
                    received_bytes += len(file_data)

            print(f"[*] received file size: {file_size} bytes")
            return received_file_path, crf_value
        except:
            print("[!] error occurred: request data reception failure")
            return "", 0

    def send_response_data(self, connection, compressed_file_path, compressed_file_size):
        try:
            connection.sendall(compressed_file_size.to_bytes(47, "big"))

            if compressed_file_path != "":
                with open(compressed_file_path, "rb") as f:
                    while True:
                        file_data = f.read(BUFFER_SIZE)
                        if not file_data:
                            break
                        connection.sendall(file_data)
        except:
            print("[!] error occurred: response data send failure")
        finally:
            connection.close()

    def compress_file(self, received_file_path, crf_value, client_port):
        try:
            print("[*] compressing file...")

            compressed_file_path = f"{COMPRESSED_FILES_DIR}compressed_{client_port}.mp4"
            command = ["ffmpeg", "-i", received_file_path, "-crf", crf_value, compressed_file_path]

            with open(f"{COMMAND_LOGS_DIR}logs_{client_port}.txt", "w") as log_file:
                subprocess.run(command, stdout=log_file, stderr=subprocess.STDOUT)

            compressed_file_size = os.path.getsize(compressed_file_path)
            print(f"[*] compressed file size: {compressed_file_size} bytes")

            return compressed_file_path, compressed_file_size
        except:
            print("[!] error occurred: file compression failure")
            return "", 0

    def delete_files(self, received_file_path, compressed_file_path):
        if received_file_path:
            os.remove(received_file_path)
        if compressed_file_path:
            os.remove(compressed_file_path)

if __name__ == "__main__":
    video_compressor = VideoCompressor()
    video_compressor.run_server()
