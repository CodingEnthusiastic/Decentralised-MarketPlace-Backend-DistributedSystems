# Server_Vector.py
import socket
import json

vector = [0, 0]   # vector clock: [Server, Client]

def update(received):
    global vector
    for i in range(2):
        vector[i] = max(vector[i], received[i])
    vector[0] += 1
    return vector

def start_server():
    global vector

    s = socket.socket()
    s.bind(("localhost", 8000))
    s.listen(5)
    print("Vector Clock Server running on port 8000...")

    while True:
        client, addr = s.accept()

        data = json.loads(client.recv(1024).decode())
        received_clock = data["vector"]

        print("\nReceived Vector:", received_clock)

        updated = update(received_clock)

        response = json.dumps({"vector": updated})
        client.send(response.encode())
        client.close()

        print("Updated Server Vector:", updated)

if __name__ == "__main__":
    start_server()
