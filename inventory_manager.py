#!/usr/bin/env python3
"""
Inventory Manager - Minecraft Bot Hub Inventory & Economy System
Handles bot inventories, game money, item transactions, and trading
"""

import json
import time
import uuid
import hashlib
import threading
from typing import Dict, List, Optional, Tuple, Set, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from pathlib import Path
import random
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Item:
    """Item definition and properties"""
    item_id: str
    name: str
    display_name: str
    type: str  # "block", "tool", "weapon", "armor", "food", "material", "special"
    stack_size: int
    durability: Optional[int]
    max_durability: Optional[int]
    enchantments: List[str]
    lore: List[str]
    rarity: str  # "common", "uncommon", "rare", "epic", "legendary"
    value: float  # Base market value
    craftable: bool
    tradeable: bool
    weight: float
    tags: List[str]

@dataclass
class InventorySlot:
    """Individual inventory slot"""
    slot_id: int
    item: Optional[Item]
    quantity: int
    durability: Optional[int]
    custom_name: Optional[str]
    last_updated: datetime

@dataclass
class PlayerInventory:
    """Player's complete inventory"""
    player_uuid: str
    inventory_type: str  # "player", "bot", "chest", "ender_chest"
    size: int
    slots: Dict[int, InventorySlot]
    max_weight: float
    current_weight: float
    last_updated: datetime
    is_locked: bool
    lock_reason: Optional[str]

@dataclass
class Transaction:
    """Item or money transaction record"""
    transaction_id: str
    timestamp: datetime
    transaction_type: str  # "trade", "gift", "purchase", "sale", "transfer"
    sender_uuid: str
    receiver_uuid: str
    items: List[Dict[str, any]]  # List of {item_id, quantity, durability}
    money_amount: float
    status: str  # "pending", "completed", "cancelled", "failed"
    notes: Optional[str]
    trade_id: Optional[str]

@dataclass
class TradeOffer:
    """Trade offer between players"""
    trade_id: str
    initiator_uuid: str
    target_uuid: str
    initiator_items: List[Dict[str, any]]
    target_items: List[Dict[str, any]]
    initiator_money: float
    target_money: float
    status: str  # "pending", "accepted", "declined", "cancelled", "expired"
    created_time: datetime
    expiry_time: datetime
    notes: Optional[str]

@dataclass
class EconomyAccount:
    """Player's economy account"""
    player_uuid: str
    balance: float
    total_earned: float
    total_spent: float
    transactions_count: int
    last_transaction: datetime
    account_type: str  # "player", "bot", "shop", "bank"
    interest_rate: float
    last_interest: datetime
    is_frozen: bool
    freeze_reason: Optional[str]

class InventoryManager:
    """
    Comprehensive inventory and economy management system for Minecraft Bot Hub
    Handles inventories, trading, economy, and item management
    """
    
    def __init__(self, config_file: str = "inventory_config.json"):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Core data structures
        self.items: Dict[str, Item] = {}
        self.inventories: Dict[str, PlayerInventory] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.trade_offers: Dict[str, TradeOffer] = {}
        self.economy_accounts: Dict[str, EconomyAccount] = {}
        
        # Server economy settings
        self.server_economy = {
            "currency_name": "Coins",
            "currency_symbol": "C",
            "starting_balance": 1000.0,
            "interest_rate": 0.05,  # 5% monthly interest
            "transaction_fee": 0.01,  # 1% transaction fee
            "max_transaction_amount": 1000000.0,
            "inflation_rate": 0.02,  # 2% monthly inflation
            "market_update_interval": 3600  # 1 hour
        }
        
        # Market prices (dynamic)
        self.market_prices: Dict[str, float] = {}
        self.price_history: Dict[str, List[Tuple[datetime, float]]] = {}
        
        # Threading and synchronization
        self.lock = threading.RLock()
        self.update_thread = None
        self.stop_updates = threading.Event()
        
        # Initialize the system
        self.load_config()
        self.initialize_default_items()
        self.initialize_default_inventories()
        self.start_background_tasks()
        
        logger.info("Inventory Manager initialized successfully")
    
    def load_config(self):
        """Load inventory configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    
                    # Load items
                    for item_data in config_data.get('items', []):
                        item = Item(**item_data)
                        self.items[item.item_id] = item
                    
                    # Load inventories
                    for inv_data in config_data.get('inventories', []):
                        inventory = PlayerInventory(**inv_data)
                        self.inventories[inventory.player_uuid] = inventory
                    
                    # Load economy accounts
                    for acc_data in config_data.get('economy_accounts', []):
                        account = EconomyAccount(**acc_data)
                        self.economy_accounts[account.player_uuid] = account
                    
                    logger.info(f"Loaded {len(self.items)} items, {len(self.inventories)} inventories, {len(self.economy_accounts)} accounts")
                    
            else:
                self.create_default_config()
                
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default inventory configuration"""
        logger.info("Creating default inventory configuration...")
        
        # Create default items
        self.initialize_default_items()
        
        # Create default economy accounts
        self.initialize_default_accounts()
        
        # Save configuration
        self.save_config()
    
    def save_config(self):
        """Save current configuration to file"""
        config_data = {
            "items": [asdict(item) for item in self.items.values()],
            "inventories": [asdict(inv) for inv in self.inventories.values()],
            "economy_accounts": [asdict(acc) for acc in self.economy_accounts.values()],
            "server_economy": self.server_economy,
            "market_prices": self.market_prices,
            "last_updated": datetime.now().isoformat()
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def initialize_default_items(self):
        """Initialize default Minecraft items"""
        default_items = [
            # Basic blocks
            {
                "item_id": "stone",
                "name": "stone",
                "display_name": "Stone",
                "type": "block",
                "stack_size": 64,
                "durability": None,
                "max_durability": None,
                "enchantments": [],
                "lore": ["A basic building block"],
                "rarity": "common",
                "value": 1.0,
                "craftable": True,
                "tradeable": True,
                "weight": 1.0,
                "tags": ["building", "mining"]
            },
            {
                "item_id": "diamond",
                "name": "diamond",
                "display_name": "Diamond",
                "type": "material",
                "stack_size": 64,
                "durability": None,
                "max_durability": None,
                "enchantments": [],
                "lore": ["A precious gem"],
                "rarity": "rare",
                "value": 100.0,
                "craftable": False,
                "tradeable": True,
                "weight": 0.5,
                "tags": ["valuable", "mining"]
            },
            {
                "item_id": "diamond_sword",
                "name": "diamond_sword",
                "display_name": "Diamond Sword",
                "type": "weapon",
                "stack_size": 1,
                "durability": 1561,
                "max_durability": 1561,
                "enchantments": [],
                "lore": ["A powerful weapon"],
                "rarity": "rare",
                "value": 500.0,
                "craftable": True,
                "tradeable": True,
                "weight": 2.0,
                "tags": ["weapon", "combat"]
            },
            {
                "item_id": "bread",
                "name": "bread",
                "display_name": "Bread",
                "type": "food",
                "stack_size": 64,
                "durability": None,
                "max_durability": None,
                "enchantments": [],
                "lore": ["Basic food item"],
                "rarity": "common",
                "value": 5.0,
                "craftable": True,
                "tradeable": True,
                "weight": 0.5,
                "tags": ["food", "farming"]
            },
            {
                "item_id": "iron_pickaxe",
                "name": "iron_pickaxe",
                "display_name": "Iron Pickaxe",
                "type": "tool",
                "stack_size": 1,
                "durability": 250,
                "max_durability": 250,
                "enchantments": [],
                "lore": ["A mining tool"],
                "rarity": "uncommon",
                "value": 150.0,
                "craftable": True,
                "tradeable": True,
                "weight": 1.5,
                "tags": ["tool", "mining"]
            }
        ]
        
        for item_data in default_items:
            item = Item(**item_data)
            self.items[item.item_id] = item
            self.market_prices[item.item_id] = item.value
        
        logger.info(f"Initialized {len(self.items)} default items")
    
    def initialize_default_accounts(self):
        """Initialize default economy accounts"""
        # This will be called when players are created
        pass
    
    def start_background_tasks(self):
        """Start background update tasks"""
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
        logger.info("Background update tasks started")
    
    def update_loop(self):
        """Main update loop for inventory management"""
        while not self.stop_updates.is_set():
            try:
                # Update market prices
                self.update_market_prices()
                
                # Process interest on accounts
                self.process_interest()
                
                # Clean up expired trade offers
                self.cleanup_expired_trades()
                
                # Update inventory weights
                self.update_inventory_weights()
                
                # Save configuration periodically
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    self.save_config()
                
                time.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                time.sleep(300)
    
    def update_market_prices(self):
        """Update market prices based on supply and demand"""
        current_time = datetime.now()
        
        for item_id, base_price in self.market_prices.items():
            # Simulate price fluctuations
            if random.random() < 0.1:  # 10% chance per hour
                fluctuation = random.uniform(0.9, 1.1)  # ±10%
                new_price = base_price * fluctuation
                
                # Apply inflation
                inflation_factor = 1 + (self.server_economy["inflation_rate"] / 30 / 24)  # Daily inflation
                new_price *= inflation_factor
                
                self.market_prices[item_id] = new_price
                
                # Record price history
                if item_id not in self.price_history:
                    self.price_history[item_id] = []
                
                self.price_history[item_id].append((current_time, new_price))
                
                # Keep only last 1000 price points
                if len(self.price_history[item_id]) > 1000:
                    self.price_history[item_id] = self.price_history[item_id][-1000:]
    
    def process_interest(self):
        """Process interest on economy accounts"""
        current_time = datetime.now()
        
        for account in self.economy_accounts.values():
            if account.is_frozen:
                continue
            
            # Check if interest should be applied (monthly)
            if (current_time - account.last_interest).days >= 30:
                interest_amount = account.balance * account.interest_rate
                account.balance += interest_amount
                account.total_earned += interest_amount
                account.last_interest = current_time
                
                logger.info(f"Applied interest to {account.player_uuid}: +{interest_amount:.2f}")
    
    def cleanup_expired_trades(self):
        """Clean up expired trade offers"""
        current_time = datetime.now()
        expired_trades = []
        
        for trade_id, trade in self.trade_offers.items():
            if current_time > trade.expiry_time:
                expired_trades.append(trade_id)
        
        for trade_id in expired_trades:
            trade.status = "expired"
            del self.trade_offers[trade_id]
            logger.info(f"Expired trade offer: {trade_id}")
    
    def update_inventory_weights(self):
        """Update inventory weights"""
        for inventory in self.inventories.values():
            total_weight = 0.0
            
            for slot in inventory.slots.values():
                if slot.item:
                    total_weight += slot.item.weight * slot.quantity
            
            inventory.current_weight = total_weight
    
    # Inventory Management Methods
    
    def create_inventory(self, player_uuid: str, inventory_type: str = "player", size: int = 36) -> str:
        """Create a new inventory for a player"""
        with self.lock:
            if player_uuid in self.inventories:
                return player_uuid
            
            # Create empty slots
            slots = {}
            for i in range(size):
                slots[i] = InventorySlot(
                    slot_id=i,
                    item=None,
                    quantity=0,
                    durability=None,
                    custom_name=None,
                    last_updated=datetime.now()
                )
            
            inventory = PlayerInventory(
                player_uuid=player_uuid,
                inventory_type=inventory_type,
                size=size,
                slots=slots,
                max_weight=1000.0,  # Default max weight
                current_weight=0.0,
                last_updated=datetime.now(),
                is_locked=False,
                lock_reason=None
            )
            
            self.inventories[player_uuid] = inventory
            
            # Create economy account
            self.create_economy_account(player_uuid)
            
            logger.info(f"Created inventory for {player_uuid}: {inventory_type} ({size} slots)")
            return player_uuid
    
    def add_item_to_inventory(self, player_uuid: str, item_id: str, quantity: int, 
                             slot_id: Optional[int] = None, durability: Optional[int] = None) -> bool:
        """Add items to a player's inventory"""
        with self.lock:
            if player_uuid not in self.inventories:
                self.create_inventory(player_uuid)
            
            if item_id not in self.items:
                logger.error(f"Item {item_id} not found")
                return False
            
            inventory = self.inventories[player_uuid]
            item = self.items[item_id]
            
            # Check if item can be stacked
            if item.stack_size > 1:
                # Try to find existing stack
                for slot in inventory.slots.values():
                    if (slot.item and slot.item.item_id == item_id and 
                        slot.durability == durability and slot.quantity < item.stack_size):
                        
                        space_left = item.stack_size - slot.quantity
                        to_add = min(quantity, space_left)
                        
                        slot.quantity += to_add
                        slot.last_updated = datetime.now()
                        quantity -= to_add
                        
                        if quantity <= 0:
                            break
                
                # If still have items, find empty slot
                if quantity > 0:
                    for slot in inventory.slots.values():
                        if slot.item is None:
                            to_add = min(quantity, item.stack_size)
                            slot.item = item
                            slot.quantity = to_add
                            slot.durability = durability
                            slot.last_updated = datetime.now()
                            quantity -= to_add
                            
                            if quantity <= 0:
                                break
            else:
                # Non-stackable item, find empty slot
                if slot_id is not None and slot_id in inventory.slots:
                    slot = inventory.slots[slot_id]
                    if slot.item is None:
                        slot.item = item
                        slot.quantity = 1
                        slot.durability = durability
                        slot.last_updated = datetime.now()
                        quantity -= 1
                    else:
                        logger.error(f"Slot {slot_id} is not empty")
                        return False
                else:
                    # Find any empty slot
                    for slot in inventory.slots.values():
                        if slot.item is None:
                            slot.item = item
                            slot.quantity = 1
                            slot.durability = durability
                            slot.last_updated = datetime.now()
                            quantity -= 1
                            
                            if quantity <= 0:
                                break
            
            if quantity > 0:
                logger.warning(f"Could not add {quantity} {item_id} to inventory (inventory full)")
            
            inventory.last_updated = datetime.now()
            self.update_inventory_weights()
            
            logger.info(f"Added {item.display_name} to {player_uuid}'s inventory")
            return True
    
    def remove_item_from_inventory(self, player_uuid: str, item_id: str, quantity: int, 
                                  slot_id: Optional[int] = None) -> bool:
        """Remove items from a player's inventory"""
        with self.lock:
            if player_uuid not in self.inventories:
                return False
            
            inventory = self.inventories[player_uuid]
            remaining_quantity = quantity
            
            if slot_id is not None and slot_id in inventory.slots:
                # Remove from specific slot
                slot = inventory.slots[slot_id]
                if slot.item and slot.item.item_id == item_id:
                    to_remove = min(remaining_quantity, slot.quantity)
                    slot.quantity -= to_remove
                    remaining_quantity -= to_remove
                    
                    if slot.quantity <= 0:
                        slot.item = None
                        slot.durability = None
                    
                    slot.last_updated = datetime.now()
            else:
                # Remove from any slot
                for slot in inventory.slots.values():
                    if remaining_quantity <= 0:
                        break
                    
                    if slot.item and slot.item.item_id == item_id:
                        to_remove = min(remaining_quantity, slot.quantity)
                        slot.quantity -= to_remove
                        remaining_quantity -= to_remove
                        
                        if slot.quantity <= 0:
                            slot.item = None
                            slot.durability = None
                        
                        slot.last_updated = datetime.now()
            
            inventory.last_updated = datetime.now()
            self.update_inventory_weights()
            
            if remaining_quantity > 0:
                logger.warning(f"Could not remove {remaining_quantity} {item_id} from inventory")
                return False
            
            logger.info(f"Removed {quantity} {item_id} from {player_uuid}'s inventory")
            return True
    
    def get_inventory_contents(self, player_uuid: str) -> Dict[str, any]:
        """Get complete inventory contents for a player"""
        if player_uuid not in self.inventories:
            return {"error": "Inventory not found"}
        
        inventory = self.inventories[player_uuid]
        contents = {
            "player_uuid": player_uuid,
            "inventory_type": inventory.inventory_type,
            "size": inventory.size,
            "max_weight": inventory.max_weight,
            "current_weight": inventory.current_weight,
            "is_locked": inventory.is_locked,
            "slots": {}
        }
        
        for slot_id, slot in inventory.slots.items():
            if slot.item:
                contents["slots"][slot_id] = {
                    "item_id": slot.item.item_id,
                    "name": slot.item.name,
                    "display_name": slot.item.display_name,
                    "quantity": slot.quantity,
                    "durability": slot.durability,
                    "max_durability": slot.item.max_durability,
                    "value": slot.item.value * slot.quantity,
                    "weight": slot.item.weight * slot.quantity
                }
        
        return contents
    
    # Economy Management Methods
    
    def create_economy_account(self, player_uuid: str, account_type: str = "player") -> str:
        """Create a new economy account for a player"""
        with self.lock:
            if player_uuid in self.economy_accounts:
                return player_uuid
            
            account = EconomyAccount(
                player_uuid=player_uuid,
                balance=self.server_economy["starting_balance"],
                total_earned=0.0,
                total_spent=0.0,
                transactions_count=0,
                last_transaction=datetime.now(),
                account_type=account_type,
                interest_rate=self.server_economy["interest_rate"],
                last_interest=datetime.now(),
                is_frozen=False,
                freeze_reason=None
            )
            
            self.economy_accounts[player_uuid] = account
            logger.info(f"Created economy account for {player_uuid}: {account_type}")
            return player_uuid
    
    def get_balance(self, player_uuid: str) -> float:
        """Get player's current balance"""
        if player_uuid not in self.economy_accounts:
            self.create_economy_account(player_uuid)
        
        return self.economy_accounts[player_uuid].balance
    
    def add_money(self, player_uuid: str, amount: float, reason: str = "deposit") -> bool:
        """Add money to player's account"""
        with self.lock:
            if player_uuid not in self.economy_accounts:
                self.create_economy_account(player_uuid)
            
            account = self.economy_accounts[player_uuid]
            
            if account.is_frozen:
                logger.error(f"Cannot add money to frozen account: {player_uuid}")
                return False
            
            account.balance += amount
            account.total_earned += amount
            account.transactions_count += 1
            account.last_transaction = datetime.now()
            
            # Record transaction
            transaction = Transaction(
                transaction_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                transaction_type="deposit",
                sender_uuid="system",
                receiver_uuid=player_uuid,
                items=[],
                money_amount=amount,
                status="completed",
                notes=reason,
                trade_id=None
            )
            
            self.transactions[transaction.transaction_id] = transaction
            
            logger.info(f"Added {amount} money to {player_uuid}: {reason}")
            return True
    
    def remove_money(self, player_uuid: str, amount: float, reason: str = "withdrawal") -> bool:
        """Remove money from player's account"""
        with self.lock:
            if player_uuid not in self.economy_accounts:
                return False
            
            account = self.economy_accounts[player_uuid]
            
            if account.is_frozen:
                logger.error(f"Cannot remove money from frozen account: {player_uuid}")
                return False
            
            if account.balance < amount:
                logger.error(f"Insufficient funds: {player_uuid} has {account.balance}, needs {amount}")
                return False
            
            account.balance -= amount
            account.total_spent += amount
            account.transactions_count += 1
            account.last_transaction = datetime.now()
            
            # Record transaction
            transaction = Transaction(
                transaction_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                transaction_type="withdrawal",
                sender_uuid=player_uuid,
                receiver_uuid="system",
                items=[],
                money_amount=amount,
                status="completed",
                notes=reason,
                trade_id=None
            )
            
            self.transactions[transaction.transaction_id] = transaction
            
            logger.info(f"Removed {amount} money from {player_uuid}: {reason}")
            return True
    
    def transfer_money(self, sender_uuid: str, receiver_uuid: str, amount: float, 
                      reason: str = "transfer") -> bool:
        """Transfer money between players"""
        with self.lock:
            # Check if both accounts exist
            if sender_uuid not in self.economy_accounts:
                self.create_economy_account(sender_uuid)
            if receiver_uuid not in self.economy_accounts:
                self.create_economy_account(receiver_uuid)
            
            sender_account = self.economy_accounts[sender_uuid]
            receiver_account = self.economy_accounts[receiver_uuid]
            
            # Check if accounts are frozen
            if sender_account.is_frozen or receiver_account.is_frozen:
                logger.error(f"Cannot transfer money: account frozen")
                return False
            
            # Check if sender has enough money
            if sender_account.balance < amount:
                logger.error(f"Insufficient funds for transfer: {sender_uuid} has {sender_account.balance}, needs {amount}")
                return False
            
            # Calculate transaction fee
            fee = amount * self.server_economy["transaction_fee"]
            total_cost = amount + fee
            
            # Remove money from sender
            sender_account.balance -= total_cost
            sender_account.total_spent += total_cost
            sender_account.transactions_count += 1
            sender_account.last_transaction = datetime.now()
            
            # Add money to receiver
            receiver_account.balance += amount
            receiver_account.total_earned += amount
            receiver_account.transactions_count += 1
            receiver_account.last_transaction = datetime.now()
            
            # Record transaction
            transaction = Transaction(
                transaction_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                transaction_type="transfer",
                sender_uuid=sender_uuid,
                receiver_uuid=receiver_uuid,
                items=[],
                money_amount=amount,
                status="completed",
                notes=f"{reason} (Fee: {fee})",
                trade_id=None
            )
            
            self.transactions[transaction.transaction_id] = transaction
            
            logger.info(f"Transferred {amount} money from {sender_uuid} to {receiver_uuid}: {reason}")
            return True
    
    # Trading Methods
    
    def create_trade_offer(self, initiator_uuid: str, target_uuid: str, 
                          initiator_items: List[Dict], target_items: List[Dict],
                          initiator_money: float = 0.0, target_money: float = 0.0,
                          notes: str = None) -> str:
        """Create a new trade offer"""
        with self.lock:
            trade_id = str(uuid.uuid4())
            
            trade_offer = TradeOffer(
                trade_id=trade_id,
                initiator_uuid=initiator_uuid,
                target_uuid=target_uuid,
                initiator_items=initiator_items,
                target_items=target_items,
                initiator_money=initiator_money,
                target_money=target_money,
                status="pending",
                created_time=datetime.now(),
                expiry_time=datetime.now() + timedelta(hours=24),  # 24 hour expiry
                notes=notes
            )
            
            self.trade_offers[trade_id] = trade_offer
            logger.info(f"Created trade offer {trade_id} from {initiator_uuid} to {target_uuid}")
            return trade_id
    
    def accept_trade(self, trade_id: str, accepter_uuid: str) -> bool:
        """Accept a trade offer"""
        with self.lock:
            if trade_id not in self.trade_offers:
                return False
            
            trade = self.trade_offers[trade_id]
            
            if trade.target_uuid != accepter_uuid:
                logger.error(f"Trade {trade_id} can only be accepted by {trade.target_uuid}")
                return False
            
            if trade.status != "pending":
                logger.error(f"Trade {trade_id} is not pending (status: {trade.status})")
                return False
            
            # Execute the trade
            if self.execute_trade(trade):
                trade.status = "accepted"
                logger.info(f"Trade {trade_id} accepted by {accepter_uuid}")
                return True
            else:
                trade.status = "failed"
                logger.error(f"Trade {trade_id} failed to execute")
                return False
    
    def execute_trade(self, trade: TradeOffer) -> bool:
        """Execute a trade between players"""
        try:
            # Transfer items from initiator to target
            for item_data in trade.initiator_items:
                if not self.remove_item_from_inventory(trade.initiator_uuid, 
                                                     item_data["item_id"], 
                                                     item_data["quantity"]):
                    return False
                
                if not self.add_item_to_inventory(trade.target_uuid, 
                                                 item_data["item_id"], 
                                                 item_data["quantity"]):
                    # Rollback
                    self.add_item_to_inventory(trade.initiator_uuid, 
                                             item_data["item_id"], 
                                             item_data["quantity"])
                    return False
            
            # Transfer items from target to initiator
            for item_data in trade.target_items:
                if not self.remove_item_from_inventory(trade.target_uuid, 
                                                     item_data["item_id"], 
                                                     item_data["quantity"]):
                    return False
                
                if not self.add_item_to_inventory(trade.initiator_uuid, 
                                                 item_data["item_id"], 
                                                 item_data["quantity"]):
                    # Rollback
                    self.add_item_to_inventory(trade.target_uuid, 
                                             item_data["item_id"], 
                                             item_data["quantity"])
                    return False
            
            # Transfer money
            if trade.initiator_money > 0:
                if not self.transfer_money(trade.initiator_uuid, trade.target_uuid, 
                                         trade.initiator_money, f"Trade {trade.trade_id}"):
                    return False
            
            if trade.target_money > 0:
                if not self.transfer_money(trade.target_uuid, trade.initiator_uuid, 
                                         trade.target_money, f"Trade {trade.trade_id}"):
                    return False
            
            # Record transaction
            transaction = Transaction(
                transaction_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                transaction_type="trade",
                sender_uuid=trade.initiator_uuid,
                receiver_uuid=trade.target_uuid,
                items=trade.initiator_items + trade.target_items,
                money_amount=trade.initiator_money + trade.target_money,
                status="completed",
                notes=f"Trade {trade.trade_id}",
                trade_id=trade.trade_id
            )
            
            self.transactions[transaction.transaction_id] = transaction
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing trade {trade.trade_id}: {e}")
            return False
    
    # Utility Methods
    
    def get_player_statistics(self, player_uuid: str) -> Dict[str, any]:
        """Get comprehensive player statistics"""
        stats = {
            "player_uuid": player_uuid,
            "inventory": {},
            "economy": {},
            "trades": {},
            "transactions": []
        }
        
        # Inventory stats
        if player_uuid in self.inventories:
            inventory = self.inventories[player_uuid]
            stats["inventory"] = {
                "type": inventory.inventory_type,
                "size": inventory.size,
                "used_slots": len([s for s in inventory.slots.values() if s.item]),
                "total_weight": inventory.current_weight,
                "max_weight": inventory.max_weight
            }
        
        # Economy stats
        if player_uuid in self.economy_accounts:
            account = self.economy_accounts[player_uuid]
            stats["economy"] = {
                "balance": account.balance,
                "total_earned": account.total_earned,
                "total_spent": account.total_spent,
                "transactions_count": account.transactions_count,
                "account_type": account.account_type
            }
        
        # Trade stats
        player_trades = [t for t in self.trade_offers.values() 
                        if t.initiator_uuid == player_uuid or t.target_uuid == player_uuid]
        stats["trades"] = {
            "total_trades": len(player_trades),
            "pending_trades": len([t for t in player_trades if t.status == "pending"]),
            "completed_trades": len([t for t in player_trades if t.status == "accepted"])
        }
        
        # Transaction history
        player_transactions = [t for t in self.transactions.values() 
                              if t.sender_uuid == player_uuid or t.receiver_uuid == player_uuid]
        stats["transactions"] = [{
            "id": t.transaction_id,
            "type": t.transaction_type,
            "amount": t.money_amount,
            "timestamp": t.timestamp.isoformat(),
            "status": t.status
        } for t in player_transactions[-10:]]  # Last 10 transactions
        
        return stats
    
    def get_market_info(self) -> Dict[str, any]:
        """Get current market information"""
        return {
            "currency": self.server_economy["currency_name"],
            "symbol": self.server_economy["currency_symbol"],
            "interest_rate": self.server_economy["interest_rate"],
            "transaction_fee": self.server_economy["transaction_fee"],
            "inflation_rate": self.server_economy["inflation_rate"],
            "prices": self.market_prices,
            "total_items": len(self.items),
            "total_transactions": len(self.transactions),
            "total_trades": len(self.trade_offers)
        }
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up Inventory Manager...")
        self.stop_updates.set()
        
        if self.update_thread:
            self.update_thread.join(timeout=5)
        
        self.save_config()
        logger.info("Inventory Manager cleanup completed")

# Example usage
if __name__ == "__main__":
    try:
        # Create inventory manager instance
        inventory_manager = InventoryManager()
        
        # Print market info
        print("=== Market Information ===")
        print(json.dumps(inventory_manager.get_market_info(), indent=2))
        
        # Create test players
        player1 = "test_player_1"
        player2 = "test_player_2"
        
        # Create inventories and accounts
        inventory_manager.create_inventory(player1)
        inventory_manager.create_inventory(player2)
        
        # Add some items
        inventory_manager.add_item_to_inventory(player1, "diamond", 5)
        inventory_manager.add_item_to_inventory(player1, "stone", 64)
        inventory_manager.add_item_to_inventory(player2, "bread", 10)
        
        # Add money
        inventory_manager.add_money(player1, 1000)
        inventory_manager.add_money(player2, 500)
        
        # Print player stats
        print(f"\n=== Player 1 Stats ===")
        print(json.dumps(inventory_manager.get_player_statistics(player1), indent=2))
        
        print(f"\n=== Player 2 Stats ===")
        print(json.dumps(inventory_manager.get_player_statistics(player2), indent=2))
        
        # Keep running for a while
        print("\n=== Running for 60 seconds to demonstrate functionality ===")
        time.sleep(60)
        
        # Cleanup
        inventory_manager.cleanup()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
        if 'inventory_manager' in locals():
            inventory_manager.cleanup()
    except Exception as e:
        print(f"Error: {e}")
        if 'inventory_manager' in locals():
            inventory_manager.cleanup()