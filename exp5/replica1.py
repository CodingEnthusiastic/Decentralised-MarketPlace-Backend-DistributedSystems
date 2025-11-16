import socket

PORT = 5001
data_store = {}

srv = socket.socket()
srv.bind(("localhost", PORT))
srv.listen(5)

print("[REPLICA1] Running...")

while True:
    conn, addr = srv.accept()
    msg = conn.recv(1024).decode()

    if msg.startswith("REPLICATE"):
        _, key, value = msg.split()
        data_store[key] = value
        print(f"[REPLICA1] Updated {key}={value}")

    conn.close()
