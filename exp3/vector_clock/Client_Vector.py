# Client_Vector.py
import socket
import json

vector = [0, 0]   # vector clock: [Server, Client]

def send_event():
    global vector

    vector[1] += 1   # client event

    s = socket.socket()
    s.connect(("localhost", 8000))

    message = json.dumps({"vector": vector})
    s.send(message.encode())

    response = json.loads(s.recv(1024).decode())
    s.close()

    server_vector = response["vector"]
    print("Server Returned:", server_vector)

    # Merge vectors
    for i in range(2):
        vector[i] = max(vector[i], server_vector[i])
    vector[1] += 1

    print("Updated Client Vector:", vector)

if __name__ == "__main__":
    send_event()
