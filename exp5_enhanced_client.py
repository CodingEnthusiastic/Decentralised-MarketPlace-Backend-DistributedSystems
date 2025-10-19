"""
Enhanced Client for Testing Data Consistency, Replication, and Load Balancing
Demonstrates all three features: fault tolerance, replication, and load balancing
"""

import socket
import json
import time
import threading
import random
from datetime import datetime

class EnhancedMarketplaceClient:
    def __init__(self):
        self.primary_address = ("localhost", 8000)
        self.backup_addresses = [("localhost", 8001), ("localhost", 8002)]
        self.current_server = self.primary_address
        self.client_id = f"client-{random.randint(1000, 9999)}"
        
    def connect_to_available_server(self):
        """Connect to any available server (primary or backup)"""
        servers_to_try = [self.primary_address] + self.backup_addresses
        
        for server in servers_to_try:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)  # Reduced timeout
                sock.connect(server)
                self.current_server = server
                print(f"Connected to server at {server[0]}:{server[1]}")
                return sock
            except Exception as e:
                continue
        
        raise Exception("No servers available")
    
    def send_request(self, request):
        """Send request to server with automatic failover"""
        max_retries = 3
        
        for attempt in range(max_retries):
            sock = None
            try:
                sock = self.connect_to_available_server()
                
                # Add client ID for load balancing
                request['client_id'] = self.client_id
                
                # Send request
                sock.send(json.dumps(request).encode('utf-8'))
                
                # Receive response
                response_data = sock.recv(2048).decode('utf-8')  # Smaller buffer
                response = json.loads(response_data)
                
                return response
                
            except Exception as e:
                print(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    print("Retrying with different server...")
                    time.sleep(0.5)  # Shorter retry delay
            finally:
                if sock:
                    try:
                        sock.close()
                    except:
                        pass
        
        return {'status': 'error', 'message': 'All servers unavailable'}
    
    def search_product(self, product):
        """Search for a product (load balanced read operation)"""
        request = {
            'type': 'search',
            'product': product
        }
        return self.send_request(request)
    
    def buy_product(self, area, shop, product, quantity=1):
        """Buy a product (write operation, goes to primary)"""
        request = {
            'type': 'buy',
            'area': area,
            'shop': shop,
            'product': product,
            'quantity': quantity
        }
        return self.send_request(request)
    
    def add_stock(self, area, shop, product, quantity):
        """Add stock to inventory (write operation, goes to primary)"""
        request = {
            'type': 'add_stock',
            'area': area,
            'shop': shop,
            'product': product,
            'quantity': quantity
        }
        return self.send_request(request)
    
    def get_server_status(self):
        """Get current server status"""
        request = {'type': 'get_status'}
        return self.send_request(request)
    
    def configure_load_balancer(self, algorithm):
        """Configure load balancing algorithm"""
        request = {
            'type': 'load_balancer_config',
            'algorithm': algorithm
        }
        return self.send_request(request)
    
    def get_load_balancer_stats(self):
        """Get load balancer statistics"""
        request = {'type': 'load_balancer_stats'}
        return self.send_request(request)

def test_load_balancing():
    """Test load balancing algorithms"""
    print("=== LOAD BALANCING TEST ===")
    
    client = EnhancedMarketplaceClient()
    
    # Test different load balancing algorithms
    algorithms = ['round_robin', 'weighted', 'least_connections', 'hash_based']
    
    for algorithm in algorithms:
        print(f"\n--- Testing {algorithm.upper()} Algorithm ---")
        
        # Configure load balancer
        config_response = client.configure_load_balancer(algorithm)
        print(f"Configuration: {config_response.get('message', 'Failed')}")
        
        if config_response.get('status') == 'success':
            # Perform multiple search operations
            search_results = []
            for i in range(10):
                result = client.search_product(random.choice(['apple', 'banana', 'milk', 'bread']))
                if result.get('status') == 'success':
                    served_by = result.get('served_by', 'unknown')
                    load_balanced = result.get('load_balanced', False)
                    response_time = result.get('response_time', 0)
                    
                    search_results.append({
                        'served_by': served_by,
                        'load_balanced': load_balanced,
                        'response_time': response_time
                    })
                    
                    print(f"Search {i+1}: Served by {served_by}, "
                          f"Load balanced: {load_balanced}, "
                          f"Response time: {response_time:.3f}s")
                
                time.sleep(0.5)
            
            # Show distribution
            distribution = {}
            for result in search_results:
                server = result['served_by']
                distribution[server] = distribution.get(server, 0) + 1
            
            print(f"\nRequest Distribution for {algorithm}:")
            for server, count in distribution.items():
                percentage = (count / len(search_results)) * 100
                print(f"  {server}: {count} requests ({percentage:.1f}%)")
    
    # Show final load balancer stats
    print("\n--- Final Load Balancer Statistics ---")
    stats_response = client.get_load_balancer_stats()
    if stats_response.get('status') == 'success':
        stats = {k: v for k, v in stats_response.items() if k != 'status'}
        print(json.dumps(stats, indent=2))

def test_fault_tolerance_with_load_balancing():
    """Test fault tolerance while load balancing is active"""
    print("=== FAULT TOLERANCE + LOAD BALANCING TEST ===")
    
    client = EnhancedMarketplaceClient()
    
    # Configure round-robin load balancing
    client.configure_load_balancer('round_robin')
    
    print("\n1. Testing normal operations with load balancing...")
    
    # Test normal operations
    for i in range(5):
        search_response = client.search_product("apple")
        print(f"Search {i+1}: {search_response.get('status')} - "
              f"Served by: {search_response.get('served_by', 'unknown')} - "
              f"Load balanced: {search_response.get('load_balanced', False)}")
        time.sleep(1)
    
    print("\n2. Simulating primary failure...")
    print("(Now manually stop the primary server and observe failover)")
    
    # Continue operations during failure
    time.sleep(5)
    
    print("\n3. Testing operations during failover...")
    
    # Try operations again
    for i in range(5):
        print(f"\nAttempt {i+1}:")
        
        # Search operation
        search_response = client.search_product("banana")
        print(f"Search: {search_response.get('status')} - "
              f"Served by: {search_response.get('served_by', 'unknown')}")
        
        # Buy operation
        buy_response = client.buy_product("borivali", "Fresh_Mart", "banana", 1)
        print(f"Buy: {buy_response.get('status')} - "
              f"Processed by: {buy_response.get('processed_by', 'unknown')}")
        
        # Status check
        status_response = client.get_server_status()
        if status_response.get('status') == 'success':
            print(f"Connected to: {status_response.get('node_id')} "
                  f"(Primary: {status_response.get('is_primary')})")
            
            # Show load balancer info if available
            lb_info = status_response.get('load_balancer')
            if lb_info:
                print(f"Load balancer algorithm: {lb_info.get('algorithm')}")
                print(f"Active nodes: {lb_info.get('active_nodes', [])}")
        
        time.sleep(3)

def test_replication_consistency():
    """Test data consistency across replicas with load balancing"""
    print("=== REPLICATION CONSISTENCY TEST ===")
    
    client = EnhancedMarketplaceClient()
    
    # Set to least connections for consistent testing
    client.configure_load_balancer('least_connections')
    
    print("1. Adding stock to test consistency...")
    add_response = client.add_stock("test_area", "test_shop", "test_product", 100)
    print(f"Add stock result: {add_response}")
    
    if add_response.get('status') == 'success':
        print(f"Version after add: {add_response.get('version')}")
    
    # Wait for replication
    time.sleep(2)
    
    print("\n2. Testing buy operations for consistency...")
    
    for i in range(5):
        buy_response = client.buy_product("test_area", "test_shop", "test_product", 10)
        print(f"Buy {i+1}: {buy_response.get('status')} - "
              f"Remaining: {buy_response.get('remaining_quantity')} - "
              f"Processed by: {buy_response.get('processed_by')}")
        
        if buy_response.get('status') == 'success':
            print(f"Version after buy: {buy_response.get('version')}")
        
        # Verify consistency with search
        search_response = client.search_product("test_product")
        if search_response.get('status') == 'success':
            results = search_response.get('results', [])
            for result in results:
                if result['area'] == 'test_area' and result['shop'] == 'test_shop':
                    print(f"Search confirms quantity: {result['quantity']} "
                          f"(Served by: {search_response.get('served_by')})")
                    break
        
        time.sleep(1)

def stress_test_with_load_balancing():
    """Stress test with concurrent clients and load balancing"""
    print("=== STRESS TEST WITH LOAD BALANCING ===")
    
    def worker_thread(thread_id, algorithm):
        client = EnhancedMarketplaceClient()
        client.client_id = f"stress-client-{thread_id}"
        
        # Configure load balancer (first thread only)
        if thread_id == 0:
            client.configure_load_balancer(algorithm)
            time.sleep(1)
        
        operations = [
            lambda: client.search_product(random.choice(["apple", "banana", "milk", "bread"])),
            lambda: client.buy_product("borivali", "Fresh_Mart", "apple", 1),
            lambda: client.add_stock("borivali", "Fresh_Mart", "apple", 5),
            lambda: client.get_server_status()
        ]
        
        results = []
        for i in range(10):
            operation = random.choice(operations)
            start_time = time.time()
            try:
                result = operation()
                response_time = time.time() - start_time
                
                status = result.get('status', 'unknown')
                served_by = result.get('served_by', result.get('processed_by', 'unknown'))
                load_balanced = result.get('load_balanced', False)
                
                results.append({
                    'thread': thread_id,
                    'operation': i+1,
                    'status': status,
                    'served_by': served_by,
                    'load_balanced': load_balanced,
                    'response_time': response_time
                })
                
                print(f"Thread {thread_id}, Op {i+1}: {status} - "
                      f"Served by: {served_by} - "
                      f"LB: {load_balanced} - "
                      f"Time: {response_time:.3f}s")
                
            except Exception as e:
                print(f"Thread {thread_id}, Op {i+1}: Error - {e}")
            
            time.sleep(random.uniform(0.5, 2.0))
        
        return results
    
    # Test with different algorithms
    for algorithm in ['round_robin', 'weighted']:
        print(f"\n--- Stress Testing with {algorithm.upper()} ---")
        
        # Start multiple threads
        threads = []
        thread_results = []
        
        for i in range(5):
            thread = threading.Thread(
                target=lambda tid=i: thread_results.append(worker_thread(tid, algorithm))
            )
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Analyze results
        all_results = []
        for result_list in thread_results:
            if result_list:
                all_results.extend(result_list)
        
        if all_results:
            # Calculate statistics
            total_requests = len(all_results)
            successful_requests = len([r for r in all_results if r['status'] == 'success'])
            load_balanced_requests = len([r for r in all_results if r['load_balanced']])
            avg_response_time = sum(r['response_time'] for r in all_results) / total_requests
            
            print(f"\nStress Test Results for {algorithm}:")
            print(f"  Total requests: {total_requests}")
            print(f"  Successful requests: {successful_requests} ({(successful_requests/total_requests)*100:.1f}%)")
            print(f"  Load balanced requests: {load_balanced_requests} ({(load_balanced_requests/total_requests)*100:.1f}%)")
            print(f"  Average response time: {avg_response_time:.3f}s")
            
            # Server distribution
            server_distribution = {}
            for result in all_results:
                server = result['served_by']
                server_distribution[server] = server_distribution.get(server, 0) + 1
            
            print(f"  Server distribution:")
            for server, count in server_distribution.items():
                percentage = (count / total_requests) * 100
                print(f"    {server}: {count} requests ({percentage:.1f}%)")

def interactive_client_with_load_balancing():
    """Interactive client with load balancing features"""
    client = EnhancedMarketplaceClient()
    
    print("=== ENHANCED INTERACTIVE MARKETPLACE CLIENT ===")
    print("Commands:")
    print("1. search <product>")
    print("2. buy <area> <shop> <product> [quantity]")
    print("3. add <area> <shop> <product> <quantity>")
    print("4. status")
    print("5. lb_config <algorithm>")
    print("6. lb_stats")
    print("7. test_lb")
    print("8. test_ft")
    print("9. test_consistency")
    print("10. exit")
    
    while True:
        try:
            command = input(f"\n[{client.client_id}] Enter command: ").strip().split()
            
            if not command:
                continue
            
            if command[0] == "search" and len(command) >= 2:
                product = command[1]
                response = client.search_product(product)
                print(json.dumps(response, indent=2))
            
            elif command[0] == "buy" and len(command) >= 4:
                area, shop, product = command[1], command[2], command[3]
                quantity = int(command[4]) if len(command) > 4 else 1
                response = client.buy_product(area, shop, product, quantity)
                print(json.dumps(response, indent=2))
            
            elif command[0] == "add" and len(command) >= 5:
                area, shop, product, quantity = command[1], command[2], command[3], int(command[4])
                response = client.add_stock(area, shop, product, quantity)
                print(json.dumps(response, indent=2))
            
            elif command[0] == "status":
                response = client.get_server_status()
                print(json.dumps(response, indent=2))
            
            elif command[0] == "lb_config" and len(command) >= 2:
                algorithm = command[1]
                response = client.configure_load_balancer(algorithm)
                print(json.dumps(response, indent=2))
            
            elif command[0] == "lb_stats":
                response = client.get_load_balancer_stats()
                print(json.dumps(response, indent=2))
            
            elif command[0] == "test_lb":
                test_load_balancing()
            
            elif command[0] == "test_ft":
                test_fault_tolerance_with_load_balancing()
            
            elif command[0] == "test_consistency":
                test_replication_consistency()
            
            elif command[0] == "exit":
                break
            
            else:
                print("Invalid command format")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    print("=== ENHANCED MARKETPLACE CLIENT WITH LOAD BALANCING ===")
    print("Choose test mode:")
    print("1. Interactive client")
    print("2. Load balancing test")
    print("3. Fault tolerance + Load balancing test")
    print("4. Replication consistency test")
    print("5. Stress test with load balancing")
    
    choice = input("Enter choice (1-5): ").strip()
    
    if choice == "1":
        interactive_client_with_load_balancing()
    elif choice == "2":
        test_load_balancing()
    elif choice == "3":
        test_fault_tolerance_with_load_balancing()
    elif choice == "4":
        test_replication_consistency()
    elif choice == "5":
        stress_test_with_load_balancing()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()