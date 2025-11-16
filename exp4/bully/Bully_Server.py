# Bully_Server.py
import socket

def start_server():
    s = socket.socket()
    s.bind(("localhost", 9000))
    s.listen(5)
    print("Highest ID Node Running (Coordinator)")

    while True:
        client, addr = s.accept()
        msg = client.recv(1024).decode()

        if msg == "ELECTION":
            print("Received election message")
            client.send("OK".encode())

        elif msg == "COORDINATOR?":
            client.send("I_AM_COORDINATOR".encode())

        client.close()

if __name__ == "__main__":
    start_server()
