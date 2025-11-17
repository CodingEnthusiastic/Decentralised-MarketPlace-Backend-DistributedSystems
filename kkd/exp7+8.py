⭐ PART 1 — BULLY ALGORITHM (SOCKET BASED, SUPER SIMPLE)

You run N terminals, each running the server code with a different ID.

bully_node.py
import socket
import json
import time

# ---------------------------------------------------------
# ASK USER WHICH PROCESS THIS IS
# ---------------------------------------------------------
my_id = int(input("Enter process ID: "))
my_port = 5000 + my_id

# define fixed ports for all processes
process_ports = {
    1: 5001,
    2: 5002,
    3: 5003,
    4: 5004
}

alive = True               # this process is alive
coordinator = None         # current leader


# ---------------------------------------------------------
# SEND MESSAGE TO OTHER PROCESS
# ---------------------------------------------------------
def send_message(target_port, message_dict):
    try:
        s = socket.socket()
        s.connect(("localhost", target_port))

        message_json = json.dumps(message_dict)
        s.send(message_json.encode())

        s.close()
    except:
        # if target process is dead or not started
        pass


# ---------------------------------------------------------
# BULLY ELECTION START
# ---------------------------------------------------------
def start_election():
    global coordinator

    print("\nProcess", my_id, "is starting an ELECTION")

    higher_processes = []
    for pid in process_ports:
        if pid > my_id:
            higher_processes.append(pid)

    any_alive = False

    for hp in higher_processes:
        # send ELECTION message
        message = {"type": "ELECTION", "from": my_id}
        send_message(process_ports[hp], message)
        print("Sent ELECTION to", hp)
        any_alive = True

    # wait to see if someone responds
    time.sleep(2)

    # if no higher process responded → become coordinator
    if coordinator is None:
        coordinator = my_id
        print("Process", my_id, "BECOMES LEADER")

        # announce to all
        for pid in process_ports:
            if pid != my_id:
                msg = {"type": "LEADER", "leader": my_id}
                send_message(process_ports[pid], msg)
    else:
        print("Higher process already took over election")


# ---------------------------------------------------------
# HANDLE Incoming Requests
# ---------------------------------------------------------
def handle_request(request_json):
    global coordinator

    try:
        data = json.loads(request_json)
        msg_type = data["type"]

        # someone started an election
        if msg_type == "ELECTION":
            sender = data["from"]
            print("Received ELECTION from", sender)

            # send OK back
            ok_message = {"type": "OK", "from": my_id}
            send_message(process_ports[sender], ok_message)

            # start own election
            start_election()

        elif msg_type == "OK":
            print("Received OK from higher process")
            # mark that someone higher is alive
            coordinator = -1

        elif msg_type == "LEADER":
            coordinator = data["leader"]
            print("Coordinator is now:", coordinator)

    except:
        pass


# ---------------------------------------------------------
# SERVER LOOP TO RECEIVE MESSAGES
# ---------------------------------------------------------
print("Process", my_id, "listening on port", my_port)
server = socket.socket()
server.bind(("localhost", my_port))
server.listen(5)

# automatically start election after 1 sec for demo
time.sleep(1)
start_election()

while True:
    client, addr = server.accept()
    data = client.recv(1024).decode()
    handle_request(data)
    client.close()

HOW TO RUN BULLY ALGO

Open 4 terminals:

Terminal 1:
python bully_node.py
Enter process ID: 1

Terminal 2:
python bully_node.py
Enter process ID: 2

Terminal 3:
python bully_node.py
Enter process ID: 3

Terminal 4:
python bully_node.py
Enter process ID: 4


If you close the window of process 4, process 3 will become leader.

⭐ PART 2 — RING ALGORITHM (SOCKET BASED SIMPLE)

Each node only talks to the next node in ring
Super easy to memorise.

ring_node.py
import socket
import json
import time

# ---------------------------------------------------------
# ASK USER FOR PROCESS ID
# ---------------------------------------------------------
my_id = int(input("Enter process ID: "))
my_port = 6000 + my_id

# ring order
ring = [1, 2, 3, 4]
next_process = None

# find next process
pos = ring.index(my_id)
next_process = ring[(pos + 1) % len(ring)]

# next process port
next_port = 6000 + next_process

leader = None


# ---------------------------------------------------------
# SEND MESSAGE
# ---------------------------------------------------------
def send_message(port, msg):
    try:
        s = socket.socket()
        s.connect(("localhost", port))
        s.send(json.dumps(msg).encode())
        s.close()
    except:
        pass


# ---------------------------------------------------------
# START ELECTION
# ---------------------------------------------------------
def start_election():
    print("\nProcess", my_id, "starting ring election")

    # send own ID to next process
    msg = {"type": "ELECTION", "ids": [my_id]}
    send_message(next_port, msg)


# ---------------------------------------------------------
# HANDLE REQUEST
# ---------------------------------------------------------
def handle_request(request_json):
    global leader

    try:
        data = json.loads(request_json)
        msg_type = data["type"]

        if msg_type == "ELECTION":
            id_list = data["ids"]

            if my_id not in id_list:
                id_list.append(my_id)

            print("Process", my_id, "received IDs:", id_list)

            # If message came back to starter
            if id_list[0] == my_id:
                # highest ID is leader
                leader = max(id_list)
                print("New LEADER =", leader)

                # start announcement
                announce_msg = {"type": "ANNOUNCE", "leader": leader}
                send_message(next_port, announce_msg)
            else:
                # forward election
                send_message(next_port, {"type": "ELECTION", "ids": id_list})

        elif msg_type == "ANNOUNCE":
            leader = data["leader"]
            print("Process", my_id, "acknowledges leader", leader)

            # continue passing if not back to starter
            if leader != my_id:
                send_message(next_port, data)

    except:
        pass


# ---------------------------------------------------------
# SERVER LOOP
# ---------------------------------------------------------
print("Process", my_id, "listening on port", my_port)
server = socket.socket()
server.bind(("localhost", my_port))
server.listen(5)

# auto start election
time.sleep(1)
start_election()

while True:
    client, addr = server.accept()
    data = client.recv(1024).decode()
    handle_request(data)
    client.close()

HOW TO RUN RING ALGO

Open 4 terminals:

Terminal 1:
python ring_node.py
Enter process ID: 1

Terminal 2:
python ring_node.py
Enter process ID: 2

Terminal 3:
python ring_node.py
Enter process ID: 3

Terminal 4:
python ring_node.py
Enter process ID: 4


Output example:

Process 1 starting ring election
Process 2 received IDs: [1,2]
Process 3 received IDs: [1,2,3]
Process 4 received IDs: [1,2,3,4]
Process 1 received IDs: [1,2,3,4]
New LEADER = 4

✔ You get:
Bully Algorithm (socket based) — Beginner friendly
Ring Algorithm (socket based) — Beginner friendly
No threads
No advanced logic
No one-liners
Easy to write in exam
