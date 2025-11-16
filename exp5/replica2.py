import socket

PORT = 5002
data_store = {}

srv = socket.socket()
srv.bind(("localhost", PORT))
srv.listen(5)

print("[REPLICA2] Running...")

while True:
    conn, addr = srv.accept()
    msg = conn.recv(1024).decode()

    if msg.startswith("REPLICATE"):
        _, key, value = msg.split()
        data_store[key] = value
        print(f"[REPLICA2] Updated {key}={value}")

    conn.close()
