import socket
import sys

PRIMARY_PORT = 5000

key = input("Key = ")
value = input("Value = ")

s = socket.socket()
s.connect(("localhost", PRIMARY_PORT))
s.send(f"WRITE {key} {value}".encode())
s.close()

print("[CLIENT] Write sent to PRIMARY")
