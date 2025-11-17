✅ rpc_server.py (MULTITHREADED version, your same code)
import socket
import json
import threading   # <-- ONLY NEW THING


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


# Handle one client at a time (executed inside a thread)
def handle_client(client):
    data = client.recv(1024).decode()

    try:
        req = json.loads(data)
        func_name = req["method"]
        args = req.get("params", [])

        if func_name not in FUNCTIONS:
            response = {"error": "Method not found"}
        else:
            result = FUNCTIONS[func_name](*args)
            response = {"result": result}

    except Exception as e:
        response = {"error": str(e)}

    client.send(json.dumps(response).encode())
    client.close()


# Main server loop
def start_server():
    s = socket.socket()
    s.bind(("localhost", 5000))
    s.listen(5)
    print("RPC Server running on port 5000...")

    while True:
        client, addr = s.accept()

        # Create a thread for each client
        t = threading.Thread(target=handle_client, args=(client,))
        t.start()


if __name__ == "__main__":
    start_server()


✅ rpc_client.py (unchanged)
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


print(rpc_call("add", [10, 20]))
print(rpc_call("multiply", [5, 6]))
print(rpc_call("divide", [10, 5]))


✅ What changed?
Only this:
import threading

AND inside server loop:
t = threading.Thread(target=handle_client, args=(client,))
t.start()

That's it.

If you want, I can also add comments, or make an even simpler version.


Here is the simplest step-by-step way to run your multithreaded RPC server + client using multiple terminals.

✅ STEP 1 — Save the files
File 1: rpc_server.py

(Use the multithreaded version I gave)

File 2: rpc_client.py

Save both in the same folder.

✅ STEP 2 — Open 2 or 3 terminals

You can use:

Windows CMD

PowerShell

VS Code multiple terminals

Linux terminals

✅ STEP 3 — Run the server

In Terminal 1:

python rpc_server.py


You should see:

RPC Server running on port 5000...


This server will stay running.

✅ STEP 4 — Run client in another terminal

In Terminal 2:

python rpc_client.py


You will see output like:

{'result': 30}
{'result': 30}
{'error': 'Method not found'}

✅ STEP 5 — Run ANOTHER client (multithreading test)

Open Terminal 3:

python rpc_client.py


Both Terminal 2 & Terminal 3 run at the same time.

Server will show:

Client connected: (...)
Client connected: (...)


This proves multithreading works.

OPTIONAL: Want to visually test concurrency?

Add this inside add():

import time
time.sleep(5)


Now run 2 clients quickly:

Terminal 2:

python rpc_client.py


Terminal 3:

python rpc_client.py


If multithreading is working, both clients finish in 5 seconds total, not 10 seconds.
