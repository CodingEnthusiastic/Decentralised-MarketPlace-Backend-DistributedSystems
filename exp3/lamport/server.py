# Server.py - Lamport Logical Clock Server
import socket
import json

lamport_clock = 0

def update_clock(received):
    global lamport_clock
    lamport_clock = max(lamport_clock, received) + 1
    return lamport_clock

def start_server():
    global lamport_clock

    s = socket.socket()
    s.bind(("localhost", 6000))
    s.listen(5)
    print("Lamport Server running on port 6000...")

    while True:
        client, addr = s.accept()

        data = json.loads(client.recv(1024).decode())
        received_ts = data["timestamp"]

        lamport_clock = update_clock(received_ts)

        response = json.dumps({"server_timestamp": lamport_clock})
        client.send(response.encode())
        client.close()

if __name__ == "__main__":
    start_server()
