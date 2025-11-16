# Client.py - Lamport Logical Clock Client
import socket
import json

lamport_clock = 1  # starts from 1

def lamport_send():
    global lamport_clock
    lamport_clock += 1

    s = socket.socket()
    s.connect(("localhost", 6000))

    message = json.dumps({"timestamp": lamport_clock})
    s.send(message.encode())

    response = json.loads(s.recv(1024).decode())
    s.close()

    server_ts = response["server_timestamp"]
    lamport_clock = max(lamport_clock, server_ts) + 1

    print("Client Sent Timestamp:", lamport_clock - 1)
    print("Server Timestamp     :", server_ts)
    print("Updated Client Clock :", lamport_clock)

if __name__ == "__main__":
    lamport_send()
