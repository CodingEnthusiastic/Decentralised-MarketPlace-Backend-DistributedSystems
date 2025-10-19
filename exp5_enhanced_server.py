"""
Enhanced Distributed Marketplace with Load Balancing
Adds Round-Robin and Weighted Load Balancing to the replication system
"""

import socket
import threading
import json
import time
import sys
import os
import logging
import random
import hashlib
from datetime import datetime
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('marketplace_replication.log'),
        logging.StreamHandler()
    ]
)

class LoadBalancer:
    """Load Balancer for distributing read requests across backup nodes"""
    
    def __init__(self):
        self.algorithms = {
            'round_robin': self.round_robin,
            'weighted': self.weighted_round_robin,
            'least_connections': self.least_connections,
            'hash_based': self.hash_based
        }
        self.current_algorithm = 'round_robin'
        self.round_robin_index = 0
        self.node_weights = {}
        self.node_connections = defaultdict(int)
        self.node_response_times = defaultdict(list)
        self.active_nodes = []
        self.lock = threading.Lock()
    
    def set_active_nodes(self, nodes):
        """Set list of active backup nodes for load balancing"""
        with self.lock:
            self.active_nodes = nodes
            # Initialize weights (higher is better)
            for node in nodes:
                if node not in self.node_weights:
                    self.node_weights[node] = 1.0
    
    def set_algorithm(self, algorithm):
        """Set the load balancing algorithm"""
        if algorithm in self.algorithms:
            self.current_algorithm = algorithm
            return True
        return False
    
    def get_next_node(self, client_id=None):
        """Get next node based on current algorithm"""
        with self.lock:
            if not self.active_nodes:
                return None
            
            return self.algorithms[self.current_algorithm](client_id)
    
    def round_robin(self, client_id=None):
        """Round-robin load balancing"""
        if not self.active_nodes:
            return None
        
        node = self.active_nodes[self.round_robin_index]
        self.round_robin_index = (self.round_robin_index + 1) % len(self.active_nodes)
        return node
    
    def weighted_round_robin(self, client_id=None):
        """Weighted round-robin based on node performance"""
        if not self.active_nodes:
            return None
        
        # Calculate total weight
        total_weight = sum(self.node_weights.get(node, 1.0) for node in self.active_nodes)
        
        # Generate random number for weighted selection
        rand_val = random.uniform(0, total_weight)
        cumulative_weight = 0
        
        for node in self.active_nodes:
            cumulative_weight += self.node_weights.get(node, 1.0)
            if rand_val <= cumulative_weight:
                return node
        
        # Fallback to first node
        return self.active_nodes[0]
    
    def least_connections(self, client_id=None):
        """Least connections load balancing"""
        if not self.active_nodes:
            return None
        
        # Find node with minimum connections
        min_connections = min(self.node_connections.get(node, 0) for node in self.active_nodes)
        candidates = [node for node in self.active_nodes 
                     if self.node_connections.get(node, 0) == min_connections]
        
        return random.choice(candidates)
    
    def hash_based(self, client_id=None):
        """Hash-based load balancing for session affinity"""
        if not self.active_nodes or not client_id:
            return self.round_robin()
        
        # Hash client ID to select node
        hash_val = int(hashlib.md5(str(client_id).encode()).hexdigest(), 16)
        node_index = hash_val % len(self.active_nodes)
        return self.active_nodes[node_index]
    
    def update_node_metrics(self, node, response_time, success=True):
        """Update node performance metrics"""
        with self.lock:
            # Update response times
            self.node_response_times[node].append(response_time)
            # Keep only last 10 response times
            if len(self.node_response_times[node]) > 10:
                self.node_response_times[node] = self.node_response_times[node][-10:]
            
            # Update weights based on performance
            avg_response_time = sum(self.node_response_times[node]) / len(self.node_response_times[node])
            
            # Lower response time = higher weight
            if avg_response_time > 0:
                self.node_weights[node] = 1.0 / avg_response_time
            
            # Adjust weight based on success rate
            if not success:
                self.node_weights[node] *= 0.9  # Reduce weight for failed requests
    
    def increment_connections(self, node):
        """Increment connection count for a node"""
        with self.lock:
            self.node_connections[node] += 1
    
    def decrement_connections(self, node):
        """Decrement connection count for a node"""
        with self.lock:
            if self.node_connections[node] > 0:
                self.node_connections[node] -= 1
    
    def get_stats(self):
        """Get load balancer statistics"""
        with self.lock:
            return {
                'algorithm': self.current_algorithm,
                'active_nodes': self.active_nodes,
                'node_weights': dict(self.node_weights),
                'node_connections': dict(self.node_connections),
                'node_response_times': {k: v[-5:] for k, v in self.node_response_times.items()}
            }

class EnhancedMarketplaceNode:
    def __init__(self, node_id, port, is_primary=False):
        self.node_id = node_id
        self.port = port
        self.is_primary = is_primary
        self.is_backup = not is_primary
        self.is_active = True
        
        # Data storage
        self.inventory = self.load_initial_data()
        self.transaction_log = []
        self.version_number = 0
        self.last_heartbeat = time.time()
        
        # Load balancer (only for primary)
        self.load_balancer = LoadBalancer() if is_primary else None
        
        # Network configuration
        self.primary_port = 8000 if is_primary else None
        self.backup_ports = [8001, 8002] if is_primary else []
        self.primary_address = ("localhost", 8000) if not is_primary else None
        
        # Performance metrics
        self.request_count = 0
        self.average_response_time = 0
        self.cpu_usage = 0
        self.memory_usage = 0
        
        # Threading locks
        self.data_lock = threading.Lock()
        self.log_lock = threading.Lock()
        self.metrics_lock = threading.Lock()
        
        # Socket setup
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("localhost", self.port))
        
        self.logger = logging.getLogger(f"Node-{self.node_id}")
        self.logger.info(f"{'Primary' if is_primary else 'Backup'} node initialized on port {port}")
        
        # Initialize load balancer for primary
        if self.is_primary and self.load_balancer:
            # Start with empty active nodes - will be populated by health checks
            self.load_balancer.set_active_nodes([])
    
    def load_initial_data(self):
        """Load initial marketplace data"""
        return {
            "areas": {
                "borivali": {
                    "shops": {
                        "Fresh_Mart": {"apple": 50, "banana": 30, "milk": 25, "bread": 20},
                        "Daily_Needs": {"rice": 100, "oil": 20, "sugar": 40, "salt": 15}
                    }
                },
                "andheri": {
                    "shops": {
                        "Tech_Store": {"laptop": 5, "phone": 10, "charger": 50, "headphones": 25},
                        "Food_Corner": {"pizza": 15, "burger": 20, "fries": 25, "coke": 30}
                    }
                },
                "goregaon": {
                    "shops": {
                        "Veggie_World": {"tomato": 60, "potato": 80, "onion": 45, "carrot": 35},
                        "Bakery_House": {"bread": 40, "cake": 8, "cookies": 30, "pastry": 12}
                    }
                },
                "bhayandar": {
                    "shops": {
                        "Farm_Fresh": {"mango": 25, "apple": 30, "banana": 40, "grapes": 20},
                        "Kitchen_Needs": {"spices": 50, "salt": 25, "sugar": 35, "flour": 45}
                    }
                }
            }
        }
    
    def start_server(self):
        """Start the server and handle client connections"""
        self.server_socket.listen(10)
        self.logger.info(f"Server listening on port {self.port}")
        
        # Start background threads
        if self.is_primary:
            threading.Thread(target=self.heartbeat_sender, daemon=True).start()
            threading.Thread(target=self.backup_monitor, daemon=True).start()
            threading.Thread(target=self.load_balancer_monitor, daemon=True).start()
        else:
            threading.Thread(target=self.heartbeat_monitor, daemon=True).start()
            threading.Thread(target=self.performance_monitor, daemon=True).start()
        
        try:
            while self.is_active:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    ).start()
                except Exception as e:
                    if self.is_active:
                        self.logger.error(f"Error accepting connections: {e}")
        except KeyboardInterrupt:
            self.logger.info("Server shutdown requested")
        finally:
            self.shutdown()
    
    def handle_client(self, client_socket, client_address):
        """Handle individual client requests with load balancing"""
        start_time = time.time()
        
        try:
            client_socket.settimeout(5)  # Set client socket timeout
            data = client_socket.recv(2048).decode('utf-8')
            if not data:
                return
                
            request = json.loads(data)
            
            # Add client info for load balancing
            request['client_id'] = f"{client_address[0]}:{client_address[1]}"
            request['request_time'] = start_time
            
            response = self.process_request(request)
            
            # Update metrics
            response_time = time.time() - start_time
            self.update_metrics(response_time, response.get('status') == 'success')
            
            client_socket.send(json.dumps(response).encode('utf-8'))
                
        except socket.timeout:
            self.logger.warning(f"Client {client_address} timed out")
        except Exception as e:
            self.logger.error(f"Error handling client {client_address}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def process_request(self, request):
        """Process client requests with load balancing for read operations"""
        request_type = request.get('type')
        client_id = request.get('client_id')
        
        # Route read operations through load balancer
        if self.is_primary and request_type == 'search' and self.load_balancer:
            return self.handle_load_balanced_read(request)
        
        # Handle other operations normally
        if request_type == 'search':
            return self.search_product(request.get('product'))
        elif request_type == 'buy':
            return self.buy_product(request.get('area'), request.get('shop'), 
                                  request.get('product'), request.get('quantity', 1))
        elif request_type == 'add_stock':
            return self.add_stock(request.get('area'), request.get('shop'), 
                                request.get('product'), request.get('quantity'))
        elif request_type == 'get_status':
            return self.get_node_status()
        elif request_type == 'sync_request':
            return self.handle_sync_request(request)
        elif request_type == 'replicate':
            return self.handle_replication(request)
        elif request_type == 'load_balancer_config':
            return self.configure_load_balancer(request)
        elif request_type == 'load_balancer_stats':
            return self.get_load_balancer_stats()
        else:
            return {'status': 'error', 'message': 'Invalid request type'}
    
    def handle_load_balanced_read(self, request):
        """Handle read operations with load balancing"""
        client_id = request.get('client_id')
        
        # Get next node from load balancer
        selected_node = self.load_balancer.get_next_node(client_id)
        
        if not selected_node:
            # No backup nodes available, handle locally
            return self.search_product(request.get('product'))
        
        # Extract port from node identifier
        try:
            port = int(selected_node.split('-')[1])
            return self.forward_read_request(port, request)
        except (ValueError, IndexError):
            # Fallback to local processing
            return self.search_product(request.get('product'))
    
    def forward_read_request(self, target_port, request):
        """Forward read request to backup node"""
        start_time = time.time()
        node_id = f"backup-{target_port}"
        
        try:
            # Update connection count
            self.load_balancer.increment_connections(node_id)
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)  # Reduced timeout
                sock.connect(("localhost", target_port))
                
                # Remove load balancing fields to avoid recursion
                clean_request = {k: v for k, v in request.items() 
                               if k not in ['client_id', 'request_time']}
                
                sock.send(json.dumps(clean_request).encode('utf-8'))
                response_data = sock.recv(2048).decode('utf-8')  # Smaller buffer
                response = json.loads(response_data)
                
                # Update metrics
                response_time = time.time() - start_time
                success = response.get('status') == 'success'
                self.load_balancer.update_node_metrics(node_id, response_time, success)
                
                # Add load balancing info to response
                response['load_balanced'] = True
                response['served_by'] = node_id
                response['response_time'] = response_time
                
                return response
                
        except socket.timeout:
            self.logger.warning(f"Load balancing failed for {node_id}: timed out")
            # Remove unresponsive node from active list
            if self.load_balancer and node_id in self.load_balancer.active_nodes:
                self.load_balancer.active_nodes.remove(node_id)
            
            # Fallback to local processing
            response = self.search_product(request.get('product'))
            response['load_balanced'] = False
            response['fallback_reason'] = 'backup_timeout'
            return response
            
        except Exception as e:
            self.logger.warning(f"Load balancing failed for {node_id}: {e}")
            # Update metrics for failed request
            response_time = time.time() - start_time
            self.load_balancer.update_node_metrics(node_id, response_time, False)
            
            # Fallback to local processing
            response = self.search_product(request.get('product'))
            response['load_balanced'] = False
            response['fallback_reason'] = str(e)
            return response
            
        finally:
            # Decrement connection count
            self.load_balancer.decrement_connections(node_id)
    
    def configure_load_balancer(self, request):
        """Configure load balancing algorithm"""
        if not self.is_primary or not self.load_balancer:
            return {'status': 'error', 'message': 'Load balancer not available'}
        
        algorithm = request.get('algorithm')
        if self.load_balancer.set_algorithm(algorithm):
            self.logger.info(f"Load balancing algorithm changed to: {algorithm}")
            return {
                'status': 'success',
                'message': f'Load balancing algorithm set to {algorithm}',
                'available_algorithms': list(self.load_balancer.algorithms.keys())
            }
        else:
            return {
                'status': 'error',
                'message': f'Invalid algorithm: {algorithm}',
                'available_algorithms': list(self.load_balancer.algorithms.keys())
            }
    
    def get_load_balancer_stats(self):
        """Get load balancer statistics"""
        if not self.is_primary or not self.load_balancer:
            return {'status': 'error', 'message': 'Load balancer not available'}
        
        stats = self.load_balancer.get_stats()
        stats['status'] = 'success'
        return stats
    
    def search_product(self, product):
        """Search for a product across all areas"""
        with self.data_lock:
            results = []
            for area, area_data in self.inventory['areas'].items():
                for shop, items in area_data['shops'].items():
                    if product in items and items[product] > 0:
                        results.append({
                            'area': area,
                            'shop': shop,
                            'quantity': items[product],
                            'node': self.node_id
                        })
            
            return {
                'status': 'success',
                'product': product,
                'results': results,
                'timestamp': datetime.now().isoformat(),
                'version': self.version_number,
                'served_by': self.node_id
            }
    
    def buy_product(self, area, shop, product, quantity):
        """Buy a product with strong consistency"""
        if not self.is_primary and self.primary_address:
            # Forward to primary if this is a backup
            return self.forward_to_primary({
                'type': 'buy',
                'area': area,
                'shop': shop,
                'product': product,
                'quantity': quantity
            })
        
        with self.data_lock:
            try:
                # Check if product exists and has sufficient quantity
                if (area in self.inventory['areas'] and 
                    shop in self.inventory['areas'][area]['shops'] and
                    product in self.inventory['areas'][area]['shops'][shop]):
                    
                    current_qty = self.inventory['areas'][area]['shops'][shop][product]
                    
                    if current_qty >= quantity:
                        # Create transaction
                        transaction = {
                            'type': 'buy',
                            'area': area,
                            'shop': shop,
                            'product': product,
                            'quantity': quantity,
                            'timestamp': datetime.now().isoformat(),
                            'transaction_id': self.generate_transaction_id(),
                            'version': self.version_number + 1
                        }
                        
                        # Update inventory
                        self.inventory['areas'][area]['shops'][shop][product] -= quantity
                        self.version_number += 1
                        
                        # Log transaction
                        with self.log_lock:
                            self.transaction_log.append(transaction)
                        
                        # Replicate to backups
                        if self.is_primary:
                            self.replicate_to_backups(transaction)
                        
                        self.logger.info(f"Purchase successful: {quantity} {product} from {shop}")
                        
                        return {
                            'status': 'success',
                            'message': f'Purchased {quantity} {product} from {shop}',
                            'transaction_id': transaction['transaction_id'],
                            'remaining_quantity': self.inventory['areas'][area]['shops'][shop][product],
                            'version': self.version_number,
                            'processed_by': self.node_id
                        }
                    else:
                        return {
                            'status': 'error',
                            'message': f'Insufficient quantity. Available: {current_qty}, Requested: {quantity}'
                        }
                else:
                    return {
                        'status': 'error',
                        'message': f'Product {product} not found in {shop}, {area}'
                    }
            
            except Exception as e:
                self.logger.error(f"Error in buy_product: {e}")
                return {'status': 'error', 'message': str(e)}
    
    def add_stock(self, area, shop, product, quantity):
        """Add stock to inventory"""
        if not self.is_primary and self.primary_address:
            return self.forward_to_primary({
                'type': 'add_stock',
                'area': area,
                'shop': shop,
                'product': product,
                'quantity': quantity
            })
        
        with self.data_lock:
            try:
                # Ensure area and shop exist
                if area not in self.inventory['areas']:
                    self.inventory['areas'][area] = {'shops': {}}
                if shop not in self.inventory['areas'][area]['shops']:
                    self.inventory['areas'][area]['shops'][shop] = {}
                
                # Add or update product
                if product in self.inventory['areas'][area]['shops'][shop]:
                    self.inventory['areas'][area]['shops'][shop][product] += quantity
                else:
                    self.inventory['areas'][area]['shops'][shop][product] = quantity
                
                self.version_number += 1
                
                # Create transaction
                transaction = {
                    'type': 'add_stock',
                    'area': area,
                    'shop': shop,
                    'product': product,
                    'quantity': quantity,
                    'timestamp': datetime.now().isoformat(),
                    'transaction_id': self.generate_transaction_id(),
                    'version': self.version_number
                }
                
                with self.log_lock:
                    self.transaction_log.append(transaction)
                
                # Replicate to backups
                if self.is_primary:
                    self.replicate_to_backups(transaction)
                
                return {
                    'status': 'success',
                    'message': f'Added {quantity} {product} to {shop}',
                    'new_quantity': self.inventory['areas'][area]['shops'][shop][product],
                    'version': self.version_number,
                    'processed_by': self.node_id
                }
            
            except Exception as e:
                self.logger.error(f"Error in add_stock: {e}")
                return {'status': 'error', 'message': str(e)}
    
    def replicate_to_backups(self, transaction):
        """Replicate transaction to backup nodes"""
        replication_message = {
            'type': 'replicate',
            'transaction': transaction,
            'full_state': self.inventory,
            'version': self.version_number
        }
        
        for backup_port in self.backup_ports:
            threading.Thread(
                target=self.send_to_backup,
                args=(backup_port, replication_message),
                daemon=True
            ).start()
    
    def send_to_backup(self, backup_port, message):
        """Send replication message to a backup node"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                sock.connect(("localhost", backup_port))
                sock.send(json.dumps(message).encode('utf-8'))
                
                response = sock.recv(1024).decode('utf-8')
                response_data = json.loads(response)
                
                if response_data.get('status') == 'success':
                    self.logger.info(f"Successfully replicated to backup on port {backup_port}")
                else:
                    self.logger.warning(f"Replication failed to backup on port {backup_port}")
                    
        except Exception as e:
            self.logger.error(f"Failed to replicate to backup {backup_port}: {e}")
    
    def handle_replication(self, request):
        """Handle replication request from primary"""
        if self.is_primary:
            return {'status': 'error', 'message': 'Primary cannot receive replication'}
        
        try:
            transaction = request.get('transaction')
            full_state = request.get('full_state')
            new_version = request.get('version')
            
            with self.data_lock:
                # Update state
                self.inventory = full_state
                self.version_number = new_version
                
                # Log transaction
                with self.log_lock:
                    self.transaction_log.append(transaction)
                
                self.logger.info(f"Applied replication: {transaction['type']} - Version {new_version}")
                
                return {'status': 'success', 'version': self.version_number}
        
        except Exception as e:
            self.logger.error(f"Error handling replication: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def forward_to_primary(self, request):
        """Forward request to primary node"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(10)
                sock.connect(self.primary_address)
                sock.send(json.dumps(request).encode('utf-8'))
                
                response = sock.recv(4096).decode('utf-8')
                return json.loads(response)
                
        except Exception as e:
            self.logger.error(f"Failed to forward to primary: {e}")
            return {'status': 'error', 'message': 'Primary node unavailable'}
    
    def heartbeat_sender(self):
        """Send heartbeat to backup nodes (Primary only)"""
        while self.is_active and self.is_primary:
            heartbeat_message = {
                'type': 'heartbeat',
                'timestamp': time.time(),
                'version': self.version_number,
                'primary_id': self.node_id,
                'load_balancer_stats': self.load_balancer.get_stats() if self.load_balancer else {}
            }
            
            active_backups = []
            for backup_port in self.backup_ports:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(2)
                        sock.connect(("localhost", backup_port))
                        sock.send(json.dumps(heartbeat_message).encode('utf-8'))
                        active_backups.append(f"backup-{backup_port}")
                except:
                    pass  # Backup might be down
            
            # Update load balancer with active nodes
            if self.load_balancer:
                self.load_balancer.set_active_nodes(active_backups)
            
            time.sleep(3)  # Send heartbeat every 3 seconds
    
    def heartbeat_monitor(self):
        """Monitor heartbeat from primary (Backup only)"""
        heartbeat_timeout = 10  # 10 seconds timeout
        
        while self.is_active and not self.is_primary:
            current_time = time.time()
            
            if current_time - self.last_heartbeat > heartbeat_timeout:
                self.logger.warning("Primary heartbeat timeout - initiating failover")
                self.initiate_failover()
                break
            
            time.sleep(2)
    
    def initiate_failover(self):
        """Initiate failover process when primary fails"""
        self.logger.info("Starting failover process")
        
        # Promote this backup to primary
        self.is_primary = True
        self.is_backup = False
        self.primary_port = self.port
        self.backup_ports = [p for p in [8001, 8002] if p != self.port]
        
        # Initialize load balancer
        self.load_balancer = LoadBalancer()
        backup_nodes = [f"backup-{port}" for port in self.backup_ports]
        self.load_balancer.set_active_nodes(backup_nodes)
        
        # Start primary services
        threading.Thread(target=self.heartbeat_sender, daemon=True).start()
        threading.Thread(target=self.backup_monitor, daemon=True).start()
        threading.Thread(target=self.load_balancer_monitor, daemon=True).start()
        
        self.logger.info(f"Failover complete - Node {self.node_id} is now PRIMARY with load balancing")
    
    def load_balancer_monitor(self):
        """Monitor load balancer performance (Primary only)"""
        while self.is_active and self.is_primary and self.load_balancer:
            try:
                stats = self.load_balancer.get_stats()
                self.logger.debug(f"Load balancer stats: {stats}")
                
                # Auto-adjust algorithm based on performance
                if len(stats['active_nodes']) > 1:
                    # Switch to weighted algorithm if nodes have different performance
                    response_times = stats.get('node_response_times', {})
                    if response_times and len(set(len(times) for times in response_times.values())) > 1:
                        if stats['algorithm'] == 'round_robin':
                            self.load_balancer.set_algorithm('weighted')
                            self.logger.info("Auto-switched to weighted load balancing")
                
            except Exception as e:
                self.logger.error(f"Load balancer monitoring error: {e}")
            
            time.sleep(10)  # Monitor every 10 seconds
    
    def backup_monitor(self):
        """Monitor backup nodes health (Primary only)"""
        while self.is_active and self.is_primary:
            active_nodes = []
            for backup_port in self.backup_ports:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(2)  # Shorter timeout
                        sock.connect(("localhost", backup_port))
                        
                        status_request = {'type': 'get_status'}
                        sock.send(json.dumps(status_request).encode('utf-8'))
                        
                        response = sock.recv(1024).decode('utf-8')
                        status = json.loads(response)
                        
                        # Add to active nodes if responsive
                        node_id = f"backup-{backup_port}"
                        active_nodes.append(node_id)
                        
                        if status.get('version', 0) < self.version_number:
                            # Backup is behind, trigger sync
                            self.sync_backup(backup_port)
                            
                except Exception as e:
                    self.logger.warning(f"Backup {backup_port} health check failed: {e}")
            
            # Update load balancer active nodes
            if self.load_balancer:
                self.load_balancer.set_active_nodes(active_nodes)
            
            time.sleep(5)
    
    def performance_monitor(self):
        """Monitor node performance metrics (Backup only)"""
        while self.is_active and not self.is_primary:
            try:
                # Simulate CPU and memory monitoring
                self.cpu_usage = random.uniform(10, 90)
                self.memory_usage = random.uniform(20, 80)
                
                # Log performance metrics
                self.logger.debug(f"Performance - CPU: {self.cpu_usage:.1f}%, Memory: {self.memory_usage:.1f}%")
                
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
            
            time.sleep(15)  # Monitor every 15 seconds
    
    def sync_backup(self, backup_port):
        """Synchronize backup node with current state"""
        sync_message = {
            'type': 'sync_request',
            'full_state': self.inventory,
            'transaction_log': self.transaction_log[-50:],  # Last 50 transactions
            'version': self.version_number
        }
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(10)
                sock.connect(("localhost", backup_port))
                sock.send(json.dumps(sync_message).encode('utf-8'))
                
                response = sock.recv(1024).decode('utf-8')
                result = json.loads(response)
                
                if result.get('status') == 'success':
                    self.logger.info(f"Successfully synced backup {backup_port}")
                    
        except Exception as e:
            self.logger.error(f"Failed to sync backup {backup_port}: {e}")
    
    def handle_sync_request(self, request):
        """Handle synchronization request from primary"""
        try:
            with self.data_lock:
                self.inventory = request.get('full_state')
                self.version_number = request.get('version')
                
                # Update transaction log
                with self.log_lock:
                    new_transactions = request.get('transaction_log', [])
                    self.transaction_log.extend(new_transactions)
                    # Keep only last 100 transactions
                    self.transaction_log = self.transaction_log[-100:]
                
                self.last_heartbeat = time.time()  # Update heartbeat
                
                return {'status': 'success', 'version': self.version_number}
                
        except Exception as e:
            self.logger.error(f"Error handling sync request: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def update_metrics(self, response_time, success):
        """Update node performance metrics"""
        with self.metrics_lock:
            self.request_count += 1
            
            # Update average response time
            if self.average_response_time == 0:
                self.average_response_time = response_time
            else:
                # Exponential moving average
                alpha = 0.1
                self.average_response_time = (alpha * response_time + 
                                            (1 - alpha) * self.average_response_time)
    
    def get_node_status(self):
        """Get current node status including load balancing info"""
        with self.metrics_lock:
            status = {
                'status': 'success',
                'node_id': self.node_id,
                'port': self.port,
                'is_primary': self.is_primary,
                'version': self.version_number,
                'transaction_count': len(self.transaction_log),
                'last_heartbeat': self.last_heartbeat,
                'timestamp': time.time(),
                'request_count': self.request_count,
                'average_response_time': self.average_response_time,
                'cpu_usage': getattr(self, 'cpu_usage', 0),
                'memory_usage': getattr(self, 'memory_usage', 0)
            }
            
            # Add load balancer info for primary
            if self.is_primary and self.load_balancer:
                status['load_balancer'] = self.load_balancer.get_stats()
            
            return status
    
    def generate_transaction_id(self):
        """Generate unique transaction ID"""
        data = f"{self.node_id}_{time.time()}_{self.version_number}"
        return hashlib.md5(data.encode()).hexdigest()[:16]
    
    def shutdown(self):
        """Gracefully shutdown the node"""
        self.is_active = False
        self.server_socket.close()
        self.logger.info("Node shutdown complete")

def main():
    if len(sys.argv) != 4:
        print("Usage: python exp5_enhanced_server.py <node_id> <port> <is_primary>")
        print("Example: python exp5_enhanced_server.py node1 8000 True")
        sys.exit(1)
    
    node_id = sys.argv[1]
    port = int(sys.argv[2])
    is_primary = sys.argv[3].lower() == 'true'
    
    node = EnhancedMarketplaceNode(node_id, port, is_primary)
    
    try:
        node.start_server()
    except KeyboardInterrupt:
        print("\nShutting down...")
        node.shutdown()

if __name__ == "__main__":
    main()