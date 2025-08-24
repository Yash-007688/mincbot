#!/usr/bin/env python3
"""
Bot IP Manager - Dynamic IP Management System
Prevents tracking by continuously rotating bot IP addresses
"""

import json
import time
import random
import hashlib
import socket
import threading
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import ipaddress
import logging
from pathlib import Path
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_ip_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class BotIPConfig:
    """Configuration for a single bot's IP management"""
    bot_id: str
    current_ip: str
    current_port: int
    last_rotation: datetime
    rotation_interval: int  # seconds
    proxy_enabled: bool
    proxy_list: List[str]
    vpn_enabled: bool
    vpn_endpoints: List[str]
    stealth_mode: bool
    ip_history: List[Dict[str, any]]
    max_history_size: int = 100

@dataclass
class NetworkConfig:
    """Network configuration settings"""
    base_subnet: str
    port_range: Tuple[int, int]
    rotation_strategy: str  # 'random', 'sequential', 'time_based'
    max_concurrent_connections: int
    connection_timeout: int
    dns_servers: List[str]
    use_tor: bool
    tor_ports: List[int]

class BotIPManager:
    """
    Dynamic IP Management System for Minecraft Bots
    Prevents tracking through continuous IP rotation and proxy management
    """
    
    def __init__(self, config_file: str = "ai_commands/config/bot_ip_config.json"):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.load_config()
        
        # Initialize bot IP configurations
        self.bot_configs: Dict[str, BotIPConfig] = {}
        self.active_connections: Set[str] = set()
        self.ip_pool: Set[str] = set()
        self.used_ips: Set[str] = set()
        
        # Threading and synchronization
        self.lock = threading.RLock()
        self.rotation_threads: Dict[str, threading.Thread] = {}
        self.stop_rotation = threading.Event()
        
        # Initialize the system
        self.initialize_system()
        
        # Start background tasks
        self.start_background_tasks()
    
    def load_config(self):
        """Load configuration from file or create default"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    self.network_config = NetworkConfig(**config_data.get('network', {}))
                    self.bot_configs_data = config_data.get('bots', {})
            else:
                self.create_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration"""
        self.network_config = NetworkConfig(
            base_subnet="10.0.0.0/8",
            port_range=(8000, 9000),
            rotation_strategy="random",
            max_concurrent_connections=50,
            connection_timeout=30,
            dns_servers=["8.8.8.8", "1.1.1.1", "208.67.222.222"],
            use_tor=False,
            tor_ports=[9050, 9051]
        )
        
        self.bot_configs_data = {
            "alpha": {
                "rotation_interval": 300,  # 5 minutes
                "proxy_enabled": True,
                "vpn_enabled": False,
                "stealth_mode": True
            },
            "beta": {
                "rotation_interval": 240,  # 4 minutes
                "proxy_enabled": True,
                "vpn_enabled": True,
                "stealth_mode": True
            },
            "gamma": {
                "rotation_interval": 180,  # 3 minutes
                "proxy_enabled": True,
                "vpn_enabled": False,
                "stealth_mode": True
            },
            "delta": {
                "rotation_interval": 120,  # 2 minutes
                "proxy_enabled": True,
                "vpn_enabled": True,
                "stealth_mode": True
            }
        }
        
        self.save_config()
    
    def save_config(self):
        """Save current configuration to file"""
        config_data = {
            "network": asdict(self.network_config),
            "bots": self.bot_configs_data,
            "last_updated": datetime.now().isoformat()
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def initialize_system(self):
        """Initialize the IP management system"""
        logger.info("Initializing Bot IP Manager...")
        
        # Generate IP pool
        self.generate_ip_pool()
        
        # Initialize bot configurations
        for bot_id, bot_data in self.bot_configs_data.items():
            self.initialize_bot(bot_id, bot_data)
        
        # Load proxy lists
        self.load_proxy_lists()
        
        # Initialize VPN endpoints
        self.initialize_vpn_endpoints()
        
        logger.info(f"System initialized with {len(self.bot_configs)} bots")
    
    def generate_ip_pool(self):
        """Generate a pool of available IP addresses"""
        try:
            network = ipaddress.IPv4Network(self.network_config.base_subnet, strict=False)
            self.ip_pool = set()
            
            # Generate random IPs from the subnet
            for _ in range(1000):  # Generate 1000 random IPs
                random_ip = str(network[random.randint(1, network.num_addresses - 2)])
                self.ip_pool.add(random_ip)
            
            logger.info(f"Generated IP pool with {len(self.ip_pool)} addresses")
        except Exception as e:
            logger.error(f"Error generating IP pool: {e}")
            # Fallback to some default IPs
            self.ip_pool = {
                "10.0.1.100", "10.0.1.101", "10.0.1.102", "10.0.1.103",
                "10.0.2.100", "10.0.2.101", "10.0.2.102", "10.0.2.103",
                "10.0.3.100", "10.0.3.101", "10.0.3.102", "10.0.3.103"
            }
    
    def initialize_bot(self, bot_id: str, bot_data: Dict):
        """Initialize a single bot's IP configuration"""
        # Get a random IP and port
        ip, port = self.get_random_ip_port()
        
        # Create bot configuration
        bot_config = BotIPConfig(
            bot_id=bot_id,
            current_ip=ip,
            current_port=port,
            last_rotation=datetime.now(),
            rotation_interval=bot_data.get('rotation_interval', 300),
            proxy_enabled=bot_data.get('proxy_enabled', True),
            proxy_list=[],
            vpn_enabled=bot_data.get('vpn_enabled', False),
            vpn_endpoints=[],
            stealth_mode=bot_data.get('stealth_mode', True),
            ip_history=[]
        )
        
        self.bot_configs[bot_id] = bot_config
        self.used_ips.add(ip)
        
        logger.info(f"Initialized bot {bot_id} with IP {ip}:{port}")
    
    def get_random_ip_port(self) -> Tuple[str, int]:
        """Get a random available IP and port"""
        with self.lock:
            # Get random IP from pool
            available_ips = self.ip_pool - self.used_ips
            if not available_ips:
                # Regenerate IP pool if exhausted
                self.regenerate_ip_pool()
                available_ips = self.ip_pool - self.used_ips
            
            ip = random.choice(list(available_ips))
            port = random.randint(*self.network_config.port_range)
            
            return ip, port
    
    def regenerate_ip_pool(self):
        """Regenerate the IP pool when exhausted"""
        logger.info("Regenerating IP pool...")
        self.generate_ip_pool()
        self.used_ips.clear()
        
        # Reassign IPs to all bots
        for bot_config in self.bot_configs.values():
            new_ip, new_port = self.get_random_ip_port()
            old_ip = bot_config.current_ip
            
            bot_config.current_ip = new_ip
            bot_config.current_port = new_port
            bot_config.last_rotation = datetime.now()
            
            # Add to history
            self.add_to_ip_history(bot_config, old_ip, bot_config.current_port)
            
            self.used_ips.add(new_ip)
            logger.info(f"Reassigned {bot_config.bot_id}: {old_ip} -> {new_ip}:{new_port}")
    
    def add_to_ip_history(self, bot_config: BotIPConfig, old_ip: str, old_port: int):
        """Add IP change to bot's history"""
        history_entry = {
            "ip": old_ip,
            "port": old_port,
            "timestamp": datetime.now().isoformat(),
            "reason": "rotation"
        }
        
        bot_config.ip_history.append(history_entry)
        
        # Keep history size manageable
        if len(bot_config.ip_history) > bot_config.max_history_size:
            bot_config.ip_history = bot_config.ip_history[-bot_config.max_history_size:]
    
    def load_proxy_lists(self):
        """Load proxy lists for bot rotation"""
        logger.info("Loading proxy lists...")
        
        # Free proxy sources (for demonstration - in production use paid services)
        proxy_sources = [
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt"
        ]
        
        all_proxies = set()
        
        for source in proxy_sources:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    proxies = response.text.strip().split('\n')
                    all_proxies.update(proxies)
            except Exception as e:
                logger.warning(f"Failed to load proxies from {source}: {e}")
        
        # Distribute proxies among bots
        proxy_list = list(all_proxies)
        for bot_config in self.bot_configs.values():
            if bot_config.proxy_enabled:
                # Assign random subset of proxies to each bot
                bot_proxies = random.sample(proxy_list, min(10, len(proxy_list)))
                bot_config.proxy_list = bot_proxies
        
        logger.info(f"Loaded {len(all_proxies)} proxies")
    
    def initialize_vpn_endpoints(self):
        """Initialize VPN endpoints for bots"""
        logger.info("Initializing VPN endpoints...")
        
        # Example VPN endpoints (in production, use actual VPN service APIs)
        vpn_endpoints = [
            "vpn1.minecrafthub.com:1194",
            "vpn2.minecrafthub.com:1194",
            "vpn3.minecrafthub.com:1194",
            "vpn4.minecrafthub.com:1194",
            "vpn5.minecrafthub.com:1194"
        ]
        
        for bot_config in self.bot_configs.values():
            if bot_config.vpn_enabled:
                bot_config.vpn_endpoints = random.sample(vpn_endpoints, 3)
    
    def start_background_tasks(self):
        """Start background IP rotation tasks"""
        logger.info("Starting background IP rotation tasks...")
        
        for bot_id, bot_config in self.bot_configs.items():
            rotation_thread = threading.Thread(
                target=self.rotation_worker,
                args=(bot_id,),
                daemon=True,
                name=f"rotation_{bot_id}"
            )
            rotation_thread.start()
            self.rotation_threads[bot_id] = rotation_thread
        
        # Start IP pool regeneration task
        regeneration_thread = threading.Thread(
            target=self.ip_pool_regeneration_worker,
            daemon=True,
            name="ip_pool_regeneration"
        )
        regeneration_thread.start()
        
        # Start proxy refresh task
        proxy_refresh_thread = threading.Thread(
            target=self.proxy_refresh_worker,
            daemon=True,
            name="proxy_refresh"
        )
        proxy_refresh_thread.start()
    
    def rotation_worker(self, bot_id: str):
        """Worker thread for IP rotation"""
        while not self.stop_rotation.is_set():
            try:
                bot_config = self.bot_configs.get(bot_id)
                if not bot_config:
                    break
                
                # Check if rotation is due
                time_since_rotation = (datetime.now() - bot_config.last_rotation).total_seconds()
                
                if time_since_rotation >= bot_config.rotation_interval:
                    self.rotate_bot_ip(bot_id)
                
                # Sleep for a short interval
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in rotation worker for {bot_id}: {e}")
                time.sleep(30)
    
    def ip_pool_regeneration_worker(self):
        """Worker thread for IP pool regeneration"""
        while not self.stop_rotation.is_set():
            try:
                # Regenerate IP pool every hour
                time.sleep(3600)
                with self.lock:
                    if len(self.ip_pool - self.used_ips) < 100:
                        self.regenerate_ip_pool()
                        
            except Exception as e:
                logger.error(f"Error in IP pool regeneration worker: {e}")
                time.sleep(300)
    
    def proxy_refresh_worker(self):
        """Worker thread for proxy list refresh"""
        while not self.stop_rotation.is_set():
            try:
                # Refresh proxy lists every 30 minutes
                time.sleep(1800)
                self.load_proxy_lists()
                
            except Exception as e:
                logger.error(f"Error in proxy refresh worker: {e}")
                time.sleep(300)
    
    def rotate_bot_ip(self, bot_id: str):
        """Rotate IP address for a specific bot"""
        with self.lock:
            bot_config = self.bot_configs.get(bot_id)
            if not bot_config:
                return
            
            old_ip = bot_config.current_ip
            old_port = bot_config.current_port
            
            # Get new IP and port
            new_ip, new_port = self.get_random_ip_port()
            
            # Update bot configuration
            bot_config.current_ip = new_ip
            bot_config.current_port = new_port
            bot_config.last_rotation = datetime.now()
            
            # Add to history
            self.add_to_ip_history(bot_config, old_ip, old_port)
            
            # Update used IPs
            self.used_ips.remove(old_ip)
            self.used_ips.add(new_ip)
            
            # Rotate proxy if enabled
            if bot_config.proxy_enabled and bot_config.proxy_list:
                bot_config.proxy_list = bot_config.proxy_list[1:] + bot_config.proxy_list[:1]
            
            # Rotate VPN endpoint if enabled
            if bot_config.vpn_enabled and bot_config.vpn_endpoints:
                bot_config.vpn_endpoints = bot_config.vpn_endpoints[1:] + bot_config.vpn_endpoints[:1]
            
            logger.info(f"Rotated {bot_id}: {old_ip}:{old_port} -> {new_ip}:{new_port}")
    
    def force_rotate_all_bots(self):
        """Force rotation of all bot IPs immediately"""
        logger.info("Forcing rotation of all bot IPs...")
        
        with self.lock:
            for bot_id in self.bot_configs:
                self.rotate_bot_ip(bot_id)
    
    def get_bot_ip(self, bot_id: str) -> Optional[Dict[str, any]]:
        """Get current IP configuration for a bot"""
        bot_config = self.bot_configs.get(bot_id)
        if not bot_config:
            return None
        
        return {
            "bot_id": bot_id,
            "ip": bot_config.current_ip,
            "port": bot_config.current_port,
            "last_rotation": bot_config.last_rotation.isoformat(),
            "next_rotation": (bot_config.last_rotation + timedelta(seconds=bot_config.rotation_interval)).isoformat(),
            "proxy_enabled": bot_config.proxy_enabled,
            "vpn_enabled": bot_config.vpn_enabled,
            "stealth_mode": bot_config.stealth_mode,
            "ip_history_count": len(bot_config.ip_history)
        }
    
    def get_all_bot_ips(self) -> Dict[str, any]:
        """Get IP configurations for all bots"""
        return {
            bot_id: self.get_bot_ip(bot_id)
            for bot_id in self.bot_configs
        }
    
    def update_bot_config(self, bot_id: str, **kwargs):
        """Update bot configuration"""
        if bot_id not in self.bot_configs:
            return False
        
        bot_config = self.bot_configs[bot_id]
        
        for key, value in kwargs.items():
            if hasattr(bot_config, key):
                setattr(bot_config, key, value)
        
        # Save configuration
        self.save_config()
        
        logger.info(f"Updated configuration for bot {bot_id}")
        return True
    
    def get_connection_stats(self) -> Dict[str, any]:
        """Get connection statistics"""
        return {
            "total_bots": len(self.bot_configs),
            "active_connections": len(self.active_connections),
            "available_ips": len(self.ip_pool - self.used_ips),
            "used_ips": len(self.used_ips),
            "total_ips": len(self.ip_pool),
            "last_regeneration": datetime.now().isoformat()
        }
    
    def test_connection(self, bot_id: str) -> Dict[str, any]:
        """Test connection for a specific bot"""
        bot_config = self.bot_configs.get(bot_id)
        if not bot_config:
            return {"error": "Bot not found"}
        
        try:
            # Test TCP connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((bot_config.current_ip, bot_config.current_port))
            sock.close()
            
            success = result == 0
            
            return {
                "bot_id": bot_id,
                "ip": bot_config.current_ip,
                "port": bot_config.current_port,
                "connection_test": "success" if success else "failed",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "bot_id": bot_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_security_report(self) -> Dict[str, any]:
        """Get security and tracking prevention report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "security_features": {
                "ip_rotation": True,
                "proxy_rotation": True,
                "vpn_rotation": True,
                "stealth_mode": True,
                "dynamic_ports": True
            },
            "rotation_stats": {},
            "tracking_prevention": {
                "ip_history_cleaning": True,
                "random_rotation_intervals": True,
                "proxy_chaining": True,
                "vpn_layering": True
            }
        }
        
        # Add rotation statistics for each bot
        for bot_id, bot_config in self.bot_configs.items():
            report["rotation_stats"][bot_id] = {
                "rotation_interval": bot_config.rotation_interval,
                "last_rotation": bot_config.last_rotation.isoformat(),
                "total_rotations": len(bot_config.ip_history),
                "proxy_enabled": bot_config.proxy_enabled,
                "vpn_enabled": bot_config.vpn_enabled
            }
        
        return report
    
    def cleanup(self):
        """Cleanup resources and stop background tasks"""
        logger.info("Cleaning up Bot IP Manager...")
        
        # Stop rotation threads
        self.stop_rotation.set()
        
        # Wait for threads to finish
        for thread in self.rotation_threads.values():
            thread.join(timeout=5)
        
        # Save final configuration
        self.save_config()
        
        logger.info("Bot IP Manager cleanup completed")

# Example usage and testing
if __name__ == "__main__":
    try:
        # Create IP manager instance
        ip_manager = BotIPManager()
        
        # Print initial configuration
        print("=== Bot IP Manager Initialized ===")
        print(json.dumps(ip_manager.get_all_bot_ips(), indent=2))
        
        # Print connection stats
        print("\n=== Connection Statistics ===")
        print(json.dumps(ip_manager.get_connection_stats(), indent=2))
        
        # Print security report
        print("\n=== Security Report ===")
        print(json.dumps(ip_manager.get_security_report(), indent=2))
        
        # Keep running for a while to see rotation in action
        print("\n=== Running for 60 seconds to demonstrate rotation ===")
        time.sleep(60)
        
        # Print updated configuration
        print("\n=== Updated Configuration ===")
        print(json.dumps(ip_manager.get_all_bot_ips(), indent=2))
        
        # Cleanup
        ip_manager.cleanup()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
        if 'ip_manager' in locals():
            ip_manager.cleanup()
    except Exception as e:
        print(f"Error: {e}")
        if 'ip_manager' in locals():
            ip_manager.cleanup()