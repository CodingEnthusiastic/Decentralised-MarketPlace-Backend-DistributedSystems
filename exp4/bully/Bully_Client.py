# Bully_Client.py
import socket
import time

def bully_election():
    s = socket.socket()

    try:
        s.connect(("localhost", 9000))
        print("Sending election message to higher ID node...")
        s.send("ELECTION".encode())

        response = s.recv(1024).decode()
        print("Response:", response)

        if response == "OK":
            print("Higher node alive → It becomes coordinator")

    except:
        print("No response from higher node → I am the coordinator")

    s.close()

    time.sleep(1)

    # Check coordinator
    try:
        s = socket.socket()
        s.connect(("localhost", 9000))
        s.send("COORDINATOR?".encode())
        reply = s.recv(1024).decode()
        print("Coordinator says:", reply)

    except:
        print("No coordinator alive!")

if __name__ == "__main__":
    bully_election()
