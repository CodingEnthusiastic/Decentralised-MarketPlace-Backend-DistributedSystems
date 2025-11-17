Here is the simplest possible multi-terminal style simulation of Round Robin Load Balancing using Python sockets (NO threads inside servers, only separate terminals).
Each backend server is run in a separate terminal, and the load balancer runs in another terminal.
Very easy code. No complex functions.

TERMINAL 1 → Backend Server 1
# server1.py
import socket

s = socket.socket()
s.bind(("localhost", 9001))
s.listen(1)
print("Server 1 ready on port 9001")

while True:
    conn, addr = s.accept()
    data = conn.recv(1024).decode()
    print("Server1 got:", data)
    reply = "Server1 processed: " + data
    conn.send(reply.encode())
    conn.close()


TERMINAL 2 → Backend Server 2
# server2.py
import socket

s = socket.socket()
s.bind(("localhost", 9002))
s.listen(1)
print("Server 2 ready on port 9002")

while True:
    conn, addr = s.accept()
    data = conn.recv(1024).decode()
    print("Server2 got:", data)
    reply = "Server2 processed: " + data
    conn.send(reply.encode())
    conn.close()


TERMINAL 3 → Load Balancer (Round Robin)
# load_balancer.py
import socket

servers = [("localhost", 9001), ("localhost", 9002)]
index = 0

lb = socket.socket()
lb.bind(("localhost", 8000))
lb.listen(5)

print("Load Balancer listening on 8000")

while True:
    conn, addr = lb.accept()
    data = conn.recv(1024).decode()
    print("Received request:", data)

    # pick server using round robin
    host, port = servers[index]
    index = (index + 1) % len(servers)

    # connect to selected backend
    backend = socket.socket()
    backend.connect((host, port))
    backend.send(data.encode())
    reply = backend.recv(1024).decode()
    backend.close()

    conn.send(reply.encode())
    conn.close()


TERMINAL 4 → Client
# client.py
import socket

for i in range(1, 7):
    s = socket.socket()
    s.connect(("localhost", 8000))
    msg = "Request " + str(i)
    s.send(msg.encode())
    reply = s.recv(1024).decode()
    print(reply)
    s.close()


HOW TO RUN (4 TERMINALS):
Terminal 1:
python server1.py

Terminal 2:
python server2.py

Terminal 3:
python load_balancer.py

Terminal 4:
python client.py


OUTPUT (Round Robin):
Server1: handles Request 1, 3, 5
Server2: handles Request 2, 4, 6
Load balancer alternates 9001 → 9002 → 9001 → 9002 …

If you want, I can give even simpler code, or version with 3 servers, or load balancing with weights.
