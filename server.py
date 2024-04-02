import json
import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9999
BUFFER_SIZE = 1400
MAX_RECEIVED_BYTES = 10000000

class VideoCompressor:
    def __init__(self):
        self.total_received_bytes = 0
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server_socket.bind((SERVER_HOST, SERVER_PORT))
        self.tcp_server_socket.listen(1)
        print("server is listening...\n")

    def run_server(self):
        while True:
            connection, client_address = self.tcp_server_socket.accept()
            print("\nprocessing...")
            result = self.receive_request_data(connection, str(client_address[1]))
            self.send_response_data(connection, result)

    def receive_request_data(self, connection, client_port):
        try:
            file_size_bytes = connection.recv(32)
            file_size = int(file_size_bytes.decode())
            print(f"[*] file size: {file_size} bytes")

            self.total_received_bytes += file_size
            if self.total_received_bytes >= MAX_RECEIVED_BYTES:
                raise Exception

            received_bytes = 0
            with open("received_movies/received_file_{}.mp4".format(client_port), "wb") as f:
                while received_bytes < file_size:
                    file_data = connection.recv(BUFFER_SIZE)
                    if not file_data:
                        break
                    f.write(file_data)
                    received_bytes += len(file_data)

            print("[*] file received successfully")
            return True
        except:
            print("[!] error")
            return False

    def send_response_data(self, connection, isSuccess):
        response_data = "200: file received successfully"
        if not isSuccess:
            response_data = "500: error"

        connection.sendall(json.dumps(response_data).encode())
        connection.close()

if __name__ == "__main__":
    video_compressor = VideoCompressor()
    video_compressor.run_server()
