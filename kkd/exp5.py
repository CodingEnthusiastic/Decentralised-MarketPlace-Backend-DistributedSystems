Yes.
Your earlier RPC code (add + multiply) is exactly correct for Q5 — it already satisfies the requirements of:
✔ remote invocation
✔ marshalling (JSON encode/decode)
✔ socket-based RPC
✔ arithmetic service (add, subtract, multiply)
✔ client–server demonstration
You only need to add subtract() and maybe divide() if required.
I’ll give you the final cleaned-up Q5 version of your earlier code (easy to remember, same style, simple functions).
Use this directly in your assignment.

rpc_server.py (FINAL — FOR Q5)
import socket
import json

# --------------------------
# Arithmetic RPC Functions
# --------------------------

def add(a, b):
    return a + b

def sub(a, b):
    return a - b

def mul(a, b):
    return a * b

FUNCTIONS = {
    "add": add,
    "sub": sub,
    "mul": mul
}

# --------------------------
# Process incoming JSON RPC request
# --------------------------

def handle_request(req_json):
    try:
        req = json.loads(req_json)

        method = req["method"]
        params = req["params"]

        if method not in FUNCTIONS:
            return json.dumps({"error": "Method not found"})

        result = FUNCTIONS[method](*params)

        return json.dumps({"result": result})

    except Exception as e:
        return json.dumps({"error": str(e)})

# --------------------------
# RPC Server
# --------------------------

def start_server():
    server = socket.socket()
    server.bind(("localhost", 5000))
    server.listen(5)

    print("Arithmetic RPC Server running on port 5000...")

    while True:
        client, addr = server.accept()
        data = client.recv(1024).decode()

        response = handle_request(data)

        client.send(response.encode())
        client.close()


if __name__ == "__main__":
    start_server()


rpc_client.py (FINAL — FOR Q5)
import socket
import json

# --------------------------
# Make RPC call
# --------------------------

def rpc_call(method, params):
    s = socket.socket()
    s.connect(("localhost", 5000))

    request = json.dumps({
        "method": method,
        "params": params
    })

    s.send(request.encode())

    response = s.recv(1024).decode()
    s.close()

    return json.loads(response)

# --------------------------
# Test Remote Arithmetic
# --------------------------

print("add(10, 20)  ->", rpc_call("add", [10, 20]))
print("sub(50, 15)  ->", rpc_call("sub", [50, 15]))
print("mul(6, 7)    ->", rpc_call("mul", [6, 7]))

print("invalid method ->", rpc_call("divide", [5, 2]))


HOW TO RUN
Terminal 1 — Start server
python rpc_server.py

Terminal 2 — Run client
python rpc_client.py


✔ This fully satisfies Q5 requirements
RequirementSatisfied?Server exposes arithmetic RPC methods✔ add(), sub(), mul()Client invokes remote functions✔ rpc_call()Marshalling✔ JSON encoding/decodingReturn values✔ Sent back over socketRemote invocation✔ socket-based RPC

If you want
✓ multithreaded server
✓ more operations
✓ menu-driven client
Tell me — I will give the simplest possible version.
