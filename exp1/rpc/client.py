# rpc_client.py
import socket
import json

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

# Example calls:
print("Calling add(10, 20)")
print(rpc_call("add", [10, 20]))

print("\nCalling multiply(5, 6)")
print(rpc_call("multiply", [5, 6]))

print("\nCalling a non-existing function:")
print(rpc_call("divide", [10, 5]))
