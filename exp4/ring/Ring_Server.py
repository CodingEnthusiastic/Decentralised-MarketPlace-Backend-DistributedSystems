# Ring_Server.py
import socket
import json

def start_server():
    s = socket.socket()
    s.bind(("localhost", 9100))
    s.listen(5)
    print("Ring Server Ready")

    while True:
        client, addr = s.accept()
        data = json.loads(client.recv(1024).decode())
        election_list = data["list"]
        print("Received:", election_list)

        # Add own ID (server = ID 3)
        election_list.append(3)

        # Send back updated list
        response = json.dumps({"list": election_list})
        client.send(response.encode())
        client.close()

if __name__ == "__main__":
    start_server()
