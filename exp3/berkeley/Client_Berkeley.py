# Client_Berkeley.py
import socket
import time

def client_sync():
    s = socket.socket()
    s.connect(("localhost", 7000))

    server_time = float(s.recv(1024).decode())
    local_time = time.time()

    s.send(str(local_time).encode())
    s.close()

    print("Server Time :", server_time)
    print("Local Time  :", local_time)
    print("Offset (client - server):", local_time - server_time)

if __name__ == "__main__":
    client_sync()
