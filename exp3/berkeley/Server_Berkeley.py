# Server_Berkeley.py
import socket
import time
import json

def start_server():
    s = socket.socket()
    s.bind(("localhost", 7000))
    s.listen(5)
    print("Berkeley Time Server running on port 7000...")

    offsets = []

    while len(offsets) < 1:     # You can increase number of clients
        client, addr = s.accept()

        # Server time
        server_time = time.time()
        client.send(str(server_time).encode())

        # Receive client time
        client_time = float(client.recv(1024).decode())
        offset = client_time - server_time
        offsets.append(offset)

        client.close()

    # Calculate average offset
    avg_offset = sum(offsets) / len(offsets)

    print("Average Offset:", avg_offset)
    print("Server should adjust by:", avg_offset)

if __name__ == "__main__":
    start_server()
