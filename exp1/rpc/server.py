# rpc_server.py
import socket
import json

# RPC functions
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

# Function registry
FUNCTIONS = {
    "add": add,
    "multiply": multiply
}

def handle_request(request_json):
    try:
        req = json.loads(request_json)
        func_name = req["method"]
        args = req.get("params", [])

        if func_name not in FUNCTIONS:
            return json.dumps({"error": "Method not found"})

        result = FUNCTIONS[func_name](*args)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})

def start_server():
    s = socket.socket()
    s.bind(("localhost", 5000))
    s.listen(5)
    print("RPC Server running on port 5000...")

    while True:
        client, addr = s.accept()
        data = client.recv(1024).decode()
        response = handle_request(data)
        client.send(response.encode())
        client.close()

if __name__ == "__main__":
    start_server()
