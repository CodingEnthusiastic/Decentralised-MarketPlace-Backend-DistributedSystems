# Server.py - Cristian's Algorithm (Time Server)
import socket
import time

def start_server():
    s = socket.socket()
    s.bind(("localhost", 5000))
    s.listen(5)
    print("Time Server running on port 5000...")

    while True:
        client, addr = s.accept()

        server_time = time.time()   # current system time

        client.send(str(server_time).encode())
        client.close()

if __name__ == "__main__":
    start_server()
