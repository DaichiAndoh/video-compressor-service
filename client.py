import json
import os
import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9999
BUFFER_SIZE = 1400
RECEIVED_FILES_DIR = "client_received_files/"

class Client:
    def __init__(self):
        self.tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.tcp_client_socket.connect((SERVER_HOST, SERVER_PORT))
            print("[*] connected to the server\n")
        except socket.error as err:
            print(err)
            sys.exit(1)

    def run(self):
        file_type, file_path, file_size = self.get_file_info()
        compression_ratio = self.get_compression_ratio()

        result = self.send_request_data(file_type, file_path, file_size, compression_ratio)
        if not result:
            self.tcp_client_socket.close()
            return

        self.receive_response_data(file_type)
        self.tcp_client_socket.close()

    def get_file_info(self):
        file_type = None
        while file_type is None:
            entered_value = input("[-] enter file type to upload (mp4, mp3, json, avi...): ")
            # TODO: entered_value validation
            if True:
                file_type = entered_value

        file_path = ""
        file_size = 0
        while file_path == "" and file_size == 0:
            file_path = input("[-] enter path to the file: ")

            try:
                file_size = os.path.getsize(file_path)
                print(f"[*] file size: {file_size} bytes")
            except FileNotFoundError:
                print("[!] file not found")
                file_path = ""
                file_size = 0

        return file_type, file_path, file_size

    def get_compression_ratio(self):
        compression_ratio = None
        while compression_ratio is None:
            entered_value = input("[-] enter compression ratio (0-51): ")

            try:
                compression_ratio = int(entered_value)
                if compression_ratio >= 0 and compression_ratio <= 51:
                    return compression_ratio
                else:
                    raise Exception
            except:
                compression_ratio = None
                print("[!] please enter compression ratio in the range of 0 to 51")

    def send_request_data(self, file_type, file_path, file_size, compression_ratio):
        try:
            config_data = json.dumps({
                "compression_ratio": compression_ratio,
            })

            request_data_excluding_payload = \
                len(config_data).to_bytes(16, "big") + \
                len(file_type).to_bytes(1, "big") + \
                file_size.to_bytes(47, "big") + \
                config_data.encode("utf-8") + \
                file_type.encode("utf-8")
            self.tcp_client_socket.sendall(request_data_excluding_payload)

            with open(file_path, "rb") as f:
                while True:
                    file_data = f.read(BUFFER_SIZE)
                    if not file_data:
                        break
                    self.tcp_client_socket.sendall(file_data)

            print("[*] request data send success")
            return True
        except:
            print("[!] error occurred: request data send failure")
            return False

    def receive_response_data(self, file_type):
        try:
            compressed_file_size = int.from_bytes(self.tcp_client_socket.recv(47), "big")
            if compressed_file_size == 0:
                print("[!] file compression is faild")
            else:
                received_bytes = 0
                with open(f"{RECEIVED_FILES_DIR}received_file.{file_type}", "wb") as f:
                    while received_bytes < compressed_file_size:
                        file_data = self.tcp_client_socket.recv(BUFFER_SIZE)
                        if not file_data:
                            break
                        f.write(file_data)
                        received_bytes += len(file_data)

                print("[*] response data reception success")
        except:
            print("[!] error occurred: response data reception failure")

if __name__ == "__main__":
    client = Client()
    client.run()
