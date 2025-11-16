import threading
import time
import random

# ---------------------------------------------------------
# SERVER (Shared Coordinator for All Nodes)
# ---------------------------------------------------------

class Server:
    def __init__(self):
        # Lock ensures mutual exclusion when multiple threads
        # try to write to shared log at the same time
        self.lock = threading.Lock()

        # Shared resource accessed by all nodes
        self.log = []

    def receive_message(self, node_id, message):
        # Only one thread is allowed to execute this block at a time
        # Prevents race conditions
        with self.lock:
            entry = f"Node {node_id}: {message}"
            self.log.append(entry)

            # Display message received from the node
            print(f"[SERVER] Received → {entry}")

    def show_log(self):
        # Prints the complete log after all threads finish execution
        print("\n--- FINAL SERVER LOG ---")
        for entry in self.log:
            print(entry)


# ---------------------------------------------------------
# NODE (Represents a distributed node running in parallel)
# ---------------------------------------------------------

class Node(threading.Thread):
    """
    Each Node acts like an independent distributed system node.
    It runs in parallel using Python's threading.Thread.
    """
    def __init__(self, node_id, server):
        # Initialize the thread properly
        super().__init__()

        # Node's ID for identification
        self.node_id = node_id

        # Reference to the central server for communication
        self.server = server

    def run(self):
        """
        This is the main function executed by each thread.
        Simulates the node performing 3 independent tasks.
        """
        for task_no in range(3):
            # Random sleep to simulate different node speeds
            time.sleep(random.uniform(0.5, 1.5))

            # Create task completion message
            message = f"Task {task_no + 1} completed"

            # Send message to server (shared resource)
            self.server.receive_message(self.node_id, message)

        # After finishing tasks, notify the server
        self.server.receive_message(self.node_id, "Node Finished Execution")


# ---------------------------------------------------------
# MAIN FUNCTION (Creates and runs all distributed nodes)
# ---------------------------------------------------------

if __name__ == "__main__":
    # Create a central server for coordination
    server = Server()

    # Create 5 Node threads (Node 1 to Node 5)
    nodes = [Node(node_id=i, server=server) for i in range(1, 6)]

    # Start all node threads (parallel execution begins)
    for node in nodes:
        node.start()

    # Wait for all nodes to finish execution
    # join() ensures main thread waits for threads to complete
    for node in nodes:
        node.join()

    # After all nodes finish, print the final log
    server.show_log()
