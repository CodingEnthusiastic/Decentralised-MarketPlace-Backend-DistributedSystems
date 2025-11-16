# Client.py - Cristian's Algorithm (Time Client)
import socket
import time

def get_correct_time():
    s = socket.socket()
    start = time.time()

    s.connect(("localhost", 5000))

    server_time = float(s.recv(1024).decode())
    end = time.time()
    s.close()

    round_trip = end - start
    corrected_time = server_time + round_trip / 2

    print("Server Time       :", server_time)
    print("Round Trip Delay  :", round_trip)
    print("Corrected Time    :", corrected_time)

if __name__ == "__main__":
    get_correct_time()
