Below is the **cleanest possible RPC-style vector clock simulation**, matching your earlier RPC logic pattern:

✔ 4 files (1 global server + 3 local processes)
✔ Only sockets
✔ No threads
✔ Each local process calls the global server with its vector clock
✔ Global compares and returns updated vector
✔ Each local process prints updated vector clock
✔ Easy to memorize

We only simulate **update_time(vector_from_local)** instead of add/multiply etc.

---

## GLOBAL SERVER → `global_server.py`

```python
# global_server.py
import socket
import json

GLOBAL_VECTOR = [0, 0, 0]   # P1, P2, P3

s = socket.socket()
s.bind(("localhost", 8000))
s.listen(5)
print("Global Server running on port 8000")

while True:
    conn, addr = s.accept()
    data = conn.recv(1024).decode()
    
    local_vec = json.loads(data)
    print("Received vector from process:", local_vec)

    # update global vector clock
    for i in range(3):
        GLOBAL_VECTOR[i] = max(GLOBAL_VECTOR[i], local_vec[i])

    conn.send(json.dumps(GLOBAL_VECTOR).encode())
    print("Updated Global VC:", GLOBAL_VECTOR)
    conn.close()
```

---

## LOCAL PROCESS 1 → `p1.py`

```python
# p1.py
import socket, json, time

VC = [0, 0, 0]   # vector clock for P1

def send_to_global():
    global VC
    s = socket.socket()
    s.connect(("localhost", 8000))
    s.send(json.dumps(VC).encode())
    updated = json.loads(s.recv(1024).decode())
    VC = updated
    s.close()

print("P1 started")

# simulate events
for i in range(3):
    VC[0] += 1               # internal event
    print("P1 local event →", VC)

    send_to_global()
    print("P1 updated from Global →", VC)

    time.sleep(2)
```

---

## LOCAL PROCESS 2 → `p2.py`

```python
# p2.py
import socket, json, time

VC = [0, 0, 0]

def send_to_global():
    global VC
    s = socket.socket()
    s.connect(("localhost", 8000))
    s.send(json.dumps(VC).encode())
    updated = json.loads(s.recv(1024).decode())
    VC = updated
    s.close()

print("P2 started")

for i in range(3):
    VC[1] += 1
    print("P2 local event →", VC)

    send_to_global()
    print("P2 updated from Global →", VC)

    time.sleep(3)
```

---

## LOCAL PROCESS 3 → `p3.py`

```python
# p3.py
import socket, json, time

VC = [0, 0, 0]

def send_to_global():
    global VC
    s = socket.socket()
    s.connect(("localhost", 8000))
    s.send(json.dumps(VC).encode())
    updated = json.loads(s.recv(1024).decode())
    VC = updated
    s.close()

print("P3 started")

for i in range(3):
    VC[2] += 1
    print("P3 local event →", VC)

    send_to_global()
    print("P3 updated from Global →", VC)

    time.sleep(4)
```

---

## HOW TO RUN (Open 4 Terminals)

**Terminal 1:**

```
python global_server.py
```

**Terminal 2:**

```
python p1.py
```

**Terminal 3:**

```
python p2.py
```

**Terminal 4:**

```
python p3.py
```

---

## SIMULATION EXPLANATION

• Each process increments only its own index → internal event
• Then sends its 3-size vector to global server
• Server takes **max** of each entry (vector clock rule)
• Sends updated VC back
• Local process updates and prints

You get perfect event ordering using vector timestamps.

---

If you want, I can also give:

✔ version with message passing between processes
✔ version without JSON
✔ version with 4 processes
✔ C++ socket version
