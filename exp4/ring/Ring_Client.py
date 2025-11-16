# Ring_Client.py
import socket
import json

def ring_election():
    # Node starting election = ID 1
    election_list = [1]

    print("Starting election with ID:", election_list)

    s = socket.socket()
    s.connect(("localhost", 9100))

    msg = json.dumps({"list": election_list})
    s.send(msg.encode())

    response = json.loads(s.recv(1024).decode())
    s.close()

    final_list = response["list"]
    print("Ring Completed:", final_list)

    coordinator = max(final_list)
    print("Chosen Coordinator:", coordinator)

if __name__ == "__main__":
    ring_election()
