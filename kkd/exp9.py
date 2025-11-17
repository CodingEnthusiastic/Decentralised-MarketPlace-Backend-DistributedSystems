Here is the MOST EASY POSSIBLE CODE for eventual consistency key-value store, using:

✔ sockets
✔ json
✔ no threads
✔ no classes
✔ no complex parsing
✔ simple functions
✔ 4 short files
✔ fully exam-friendly

This is the absolute simplest readable version.

1) master.py — MAIN SERVER
import socket
import json
import time

replicas = [6001, 6002, 6003]
store = {}

def send_to_replica(port, key, value, delay):
    time.sleep(delay)          # delay only for eventual consistency
    s = socket.socket()
    s.connect(("localhost", port))
    msg = {"key": key, "value": value}
    s.send(json.dumps(msg).encode())
    s.close()

def handle(req):
    key = req["key"]
    value = req["value"]
    mode = req["mode"]         # "strong" or "eventual"

    store[key] = value

    # strong = send immediately
    if mode == "strong":
        for r in replicas:
            send_to_replica(r, key, value, 0)

    # eventual = send after delay
    if mode == "eventual":
        for r in replicas:
            send_to_replica(r, key, value, 3)

    return {"status": "ok"}

def start():
    s = socket.socket()
    s.bind(("localhost", 6000))
    s.listen(5)
    print("MASTER READY")

    while True:
        c, _ = s.accept()
        data = c.recv(1024).decode()
        req = json.loads(data)
        res = handle(req)
        c.send(json.dumps(res).encode())
        c.close()

start()

2) replica.py — REPLICA SERVER (same file reused)

Run this same file three times after modifying the port.

import socket
import json

store = {}

def start(port):
    s = socket.socket()
    s.bind(("localhost", port))
    s.listen(5)
    print("REPLICA", port, "READY")

    while True:
        c, _ = s.accept()
        data = c.recv(1024).decode()
        req = json.loads(data)

        key = req["key"]
        value = req["value"]
        store[key] = value

        print("Replica", port, "updated:", key, "=", value)

        c.close()

# Make 3 files like below:
# replica1.py → start(6001)
# replica2.py → start(6002)
# replica3.py → start(6003)

start(6001)


Just change the last line for replicas 2 and 3.

3) client.py
import socket
import json

def put(k, v, mode):
    s = socket.socket()
    s.connect(("localhost", 6000))
    msg = {"key": k, "value": v, "mode": mode}
    s.send(json.dumps(msg).encode())
    print("Response:", s.recv(1024).decode())
    s.close()

print("Strong:")
put("x", "10", "strong")

print("\nEventual:")
put("y", "20", "eventual")

HOW TO RUN (4 terminals)
T1 → python master.py
T2 → python replica1.py
T3 → python replica2.py
T4 → python replica3.py
T5 → python client.py

OUTPUT (Strong Consistency)
Replica 6001 updated: x = 10
Replica 6002 updated: x = 10
Replica 6003 updated: x = 10

OUTPUT (Eventual Consistency)

(after 3 seconds)

Replica 6001 updated: y = 20
Replica 6002 updated: y = 20
Replica 6003 updated: y = 20


If you want, I can give:

✔ even shorter code
✔ exam-style explanation (4–5 lines)
✔ same program with strong consistency only
