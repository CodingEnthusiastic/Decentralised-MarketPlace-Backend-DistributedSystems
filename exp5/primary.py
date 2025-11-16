import socket

PRIMARY_PORT = 5000
REPLICAS = [("localhost", 5001), ("localhost", 5002)]  # replica ports

data_store = {}

def send_to_replica(msg):
    for host, port in REPLICAS:
        try:
            s = socket.socket()
            s.connect((host, port))
            s.send(msg.encode())
            s.close()
        except:
            print(f"[PRIMARY] Replica {port} not reachable")

srv = socket.socket()
srv.bind(("localhost", PRIMARY_PORT))
srv.listen(5)

print("[PRIMARY] Running... waiting for WRITE commands")

while True:
    conn, addr = srv.accept()
    msg = conn.recv(1024).decode()
    
    if msg.startswith("WRITE"):
        _, key, value = msg.split()
        data_store[key] = value
        print(f"[PRIMARY] Applied WRITE {key}={value}")

        # replicate
        send_to_replica(f"REPLICATE {key} {value}")
        print(f"[PRIMARY] Replicated to all replicas")

    conn.close()
