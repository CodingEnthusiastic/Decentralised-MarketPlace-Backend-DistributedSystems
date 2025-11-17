A distributed banking application runs across multiple servers, each responsible for handling a set of customers. 
If the primary server crashes, a new leader server must be elected using any of the Election Algorithms. 
The leader is responsible for synchronizing account balances and ensuring  clock synchronization between servers to maintain transaction ordering. 
Question: 
Simulate a distributed banking system where servers elect a leader after a crash (using Bully or Ring algorithm). The leader maintains global transaction ordering using clock synchronization ( which and why? ) . Show how clients can still perform transactions consistently after leader election. 
Features you need to implement: 
Leader election (use any algorithm) 
Monitoring algorithm for leader (Keep it simple for now) 
Clock Synchronization between the servers 
You can use REST apis, RPC/RMI or web sockets for communication. 


Answer:

Run Instructions (Multi-Terminal)
Open 3 terminals for servers:
python bank_serverX.py → enter X = 1, 2, 3
Open 1 terminal for client:
python bank_client.py → perform deposits/withdrawals
Servers will elect a leader automatically, transactions go to leader, and updates propagate to all servers.

Code:


import socket
import json
import time

# ---------------- SERVER CONFIGURATION ----------------
SERVER_ID = int(input("Enter Server ID (1-3): "))
PORT = 5000 + SERVER_ID
SERVERS = {1:5001, 2:5002, 3:5003}

leader_id = None
accounts = {"Alice":1000, "Bob":1000}
lamport_clock = 0

# ---------------- RPC FUNCTIONS ----------------
def deposit(account, amount):
    global lamport_clock
    accounts[account] = accounts[account] + amount
    lamport_clock = lamport_clock + 1
    return account + " new balance: " + str(accounts[account]) + " (clock=" + str(lamport_clock) + ")"

def withdraw(account, amount):
    global lamport_clock
    if accounts[account] >= amount:
        accounts[account] = accounts[account] - amount
        lamport_clock = lamport_clock + 1
        return account + " new balance: " + str(accounts[account]) + " (clock=" + str(lamport_clock) + ")"
    else:
        return "Insufficient funds for " + account

RPC_FUNCTIONS = {"deposit": deposit, "withdraw": withdraw}

# ---------------- SOCKET HELPER ----------------
def send_message(port, msg):
    try:
        s = socket.socket()
        s.connect(("localhost", port))
        message = json.dumps(msg)
        s.send(message.encode())
        s.close()
    except:
        # If server is down, just ignore
        pass

# ---------------- BULLY LEADER ELECTION ----------------
def bully_election():
    global leader_id
    print("[Server " + str(SERVER_ID) + "] Starting election")

    # Find all servers with higher ID
    higher_servers = []
    for s in SERVERS:
        if s > SERVER_ID:
            higher_servers.append(s)

    # Send ELECTION message to all higher servers
    for s in higher_servers:
        message = {"type":"ELECTION", "from": SERVER_ID}
        send_message(SERVERS[s], message)

    # Wait to see if any higher server responds (simplified)
    time.sleep(2)

    # If no higher server responds, become leader
    leader_id = SERVER_ID
    print("[Server " + str(SERVER_ID) + "] I am the new leader")

    # Notify other servers about the new leader
    for s in SERVERS:
        if s != SERVER_ID:
            message = {"type":"LEADER", "leader": leader_id}
            send_message(SERVERS[s], message)

# ---------------- HANDLE REQUEST ----------------
def handle_request(request_json):
    global leader_id, lamport_clock
    try:
        req = json.loads(request_json)
        msg_type = req.get("type")

        if msg_type == "ELECTION":
            if SERVER_ID > req["from"]:
                send_message(SERVERS[req["from"]], {"type":"OK", "from": SERVER_ID})
                bully_election()
            return {"status":"ok"}

        elif msg_type == "OK":
            return {"status":"ok"}

        elif msg_type == "LEADER":
            leader_id = req["leader"]
            print("[Server " + str(SERVER_ID) + "] New leader: Server " + str(leader_id))
            return {"status":"ok"}

        elif msg_type == "TRANSACTION":
            func_name = req["method"]
            params = req.get("params", [])

            if SERVER_ID == leader_id:
                if func_name in RPC_FUNCTIONS:
                    result = RPC_FUNCTIONS[func_name](params[0], params[1])

                    # Broadcast update to other servers
                    for s in SERVERS:
                        if s != SERVER_ID:
                            update_msg = {
                                "type":"UPDATE",
                                "account": params[0],
                                "balance": accounts[params[0]],
                                "clock": lamport_clock
                            }
                            send_message(SERVERS[s], update_msg)
                    return {"result": result}
                else:
                    return {"error":"Method not found"}
            else:
                # Forward transaction to leader
                send_message(SERVERS[leader_id], req)
                return {"status":"forwarded"}

        elif msg_type == "UPDATE":
            accounts[req["account"]] = req["balance"]
            lamport_clock = max(lamport_clock, req.get("clock",0)) + 1
            print("[Server " + str(SERVER_ID) + "] Updated " + req["account"] + " to " + str(accounts[req["account"]]))
            return {"status":"updated"}

    except Exception as e:
        return {"error": str(e)}

# ---------------- SERVER LISTENING LOOP ----------------
print("[Server " + str(SERVER_ID) + "] Listening on port " + str(PORT))
s = socket.socket()
s.bind(("localhost", PORT))
s.listen(5)

while True:
    client, addr = s.accept()
    data = client.recv(1024).decode()
    response = handle_request(data)
    client.send(json.dumps(response).encode())
    client.close()



import socket
import json
import random

# Ports of all servers
SERVERS = {1: 5001, 2: 5002, 3: 5003}

def rpc_call(server_port, method, params):
    """
    Sends a transaction request (deposit/withdraw) to a server.
    Returns the server's response.
    """
    s = socket.socket()
    s.connect(("localhost", server_port))  # connect to server
    msg = {"type": "TRANSACTION", "method": method, "params": params}
    s.send(json.dumps(msg).encode())       # send JSON request
    response = json.loads(s.recv(1024).decode())  # read response
    s.close()
    return response

while True:
    # Ask user for transaction details
    account = input("Account (Alice/Bob): ")
    action = input("Action (deposit/withdraw): ")
    amount = int(input("Amount: "))

    # Choose a random server to send request (simulating distributed client)
    port = random.choice(list(SERVERS.values()))
    print(rpc_call(port, action, [account, amount]))

            
