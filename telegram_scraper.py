#!/usr/bin/env python3
"""
Telegram Contract Address Scraper
Monitors Telegram groups for contract addresses and potential trading opportunities
"""

import re
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
import json
import os
from telethon import TelegramClient, events
from telethon.tl.types import Message, Channel, Chat
# from config_manager import TradingBotConfig
# from api_manager import TradingBotAPIManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SolanaContractInfo:
    """Solana token contract information"""
    address: str
    symbol: Optional[str] = None
    name: Optional[str] = None
    decimals: Optional[int] = 9
    source_group: Optional[str] = None
    source_message: Optional[str] = None
    timestamp: Optional[datetime] = None
    confidence_score: float = 0.0
    mint_authority: Optional[str] = None
    freeze_authority: Optional[str] = None

@dataclass
class GroupConfig:
    """Group monitoring configuration"""
    group_id: int
    group_name: str
    enabled: bool = True
    auto_trade: bool = False
    min_confidence: float = 0.7

class SolanaTelegramScraper:
    """Advanced Telegram scraper for Solana token contracts"""
    
    def __init__(self):
        # Telegram API credentials
        self.api_id = 24093084
        self.api_hash = "82fd0c45ae1987a6fcccf7248e7fc528"
        
        # Initialize Telegram client
        self.client = TelegramClient('scraper_session', self.api_id, self.api_hash)
        
        # Solana contract address patterns (Base58 encoded, 32-44 chars)
        self.solana_pattern = re.compile(r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b')
        
        # Known Solana program IDs to exclude
        self.excluded_programs = {
            '11111111111111111111111111111111',  # System Program
            'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',  # Token Program
            'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL',  # Associated Token Program
            'So11111111111111111111111111111111111111112',   # Wrapped SOL
            'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',   # USDC
            'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB'    # USDT
        }
        
        # Solana token symbol patterns
        self.symbol_patterns = [
            re.compile(r'\$([A-Z][A-Z0-9]{1,10})\b'),  # $SYMBOL (starts with letter)
            re.compile(r'\b([A-Z][A-Z0-9]{1,10})\s*(?:token|coin|mint)\b', re.IGNORECASE),
            re.compile(r'(?:token|coin|mint|ca|contract):\s*([A-Z][A-Z0-9]{1,10})\b', re.IGNORECASE),
            re.compile(r'\bCA:\s*([A-Z][A-Z0-9]{1,10})\b', re.IGNORECASE)  # Common in Solana groups
        ]
        
        # Monitored groups
        self.monitored_groups: Dict[int, GroupConfig] = {}
        
        # Found contracts cache
        self.found_contracts: Set[str] = set()
        
        # Load configuration
        self.load_groups_config()
    
    def load_groups_config(self):
        """Load groups configuration from file"""
        config_file = 'scraper_groups.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    for group_data in data.get('groups', []):
                        config = GroupConfig(**group_data)
                        self.monitored_groups[config.group_id] = config
                logger.info(f"Loaded {len(self.monitored_groups)} group configurations")
            except Exception as e:
                logger.error(f"Error loading groups config: {e}")
        else:
            # Create default config
            self.create_default_config()
    
    def create_default_config(self):
        """Create default groups configuration"""
        default_config = {
            "groups": [
                {
                    "group_id": -1001234567890,  # Replace with actual group IDs
                    "group_name": "Crypto Signals",
                    "enabled": True,
                    "auto_trade": False,
                    "min_confidence": 0.7
                }
            ],
            "settings": {
                "check_interval": 1,
                "max_contracts_per_hour": 50,
                "enable_notifications": True
            }
        }
        
        with open('scraper_groups.json', 'w') as f:
            json.dump(default_config, f, indent=2)
        logger.info("Created default scraper configuration")
    
    async def start(self):
        """Start the scraper"""
        logger.info("Starting Telegram scraper...")
        
        try:
            # Connect to Telegram
            await self.client.start()
            logger.info("Connected to Telegram successfully")
            
            # Get user info
            me = await self.client.get_me()
            logger.info(f"Logged in as: {me.first_name} ({me.username})")
            
            # Set up event handlers
            self.setup_event_handlers()
            
            # Start monitoring
            logger.info("Scraper is now monitoring groups for contract addresses...")
            await self.client.run_until_disconnected()
            
        except Exception as e:
            logger.error(f"Error starting scraper: {e}")
            raise
    
    def setup_event_handlers(self):
        """Set up event handlers for message monitoring"""
        
        @self.client.on(events.NewMessage)
        async def handle_new_message(event):
            """Handle new messages in monitored groups"""
            try:
                message = event.message
                
                # Check if message is from a monitored group
                if hasattr(message.peer_id, 'channel_id'):
                    group_id = -message.peer_id.channel_id
                elif hasattr(message.peer_id, 'chat_id'):
                    group_id = -message.peer_id.chat_id
                else:
                    return
                
                if group_id not in self.monitored_groups:
                    return
                
                group_config = self.monitored_groups[group_id]
                if not group_config.enabled:
                    return
                
                # Process the message
                await self.process_message(message, group_config)
                
            except Exception as e:
                logger.error(f"Error handling message: {e}")
    
    async def process_message(self, message: Message, group_config: GroupConfig):
        """Process a message for contract addresses"""
        try:
            text = message.text or ""
            if not text:
                return
            
            # Find potential contract addresses
            contracts = self.extract_contract_addresses(text)
            
            for contract in contracts:
                if contract.address in self.found_contracts:
                    continue  # Skip duplicates
                
                # Add source information
                contract.source_group = group_config.group_name
                contract.source_message = text[:200]  # First 200 chars
                contract.timestamp = datetime.now()
                
                # Calculate confidence score
                contract.confidence_score = self.calculate_confidence_score(text, contract)
                
                if contract.confidence_score >= group_config.min_confidence:
                    self.found_contracts.add(contract.address)
                    await self.handle_found_contract(contract, group_config)
                    
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def extract_contract_addresses(self, text: str) -> List[SolanaContractInfo]:
        """Extract Solana contract addresses from text"""
        contracts = []
        
        # Find Solana addresses
        solana_matches = self.solana_pattern.findall(text)
        for address in solana_matches:
            if self.is_valid_solana_address(address):
                contract = SolanaContractInfo(address=address)
                
                # Try to extract symbol
                contract.symbol = self.extract_token_symbol(text, address)
                
                # Extract additional Solana-specific info from context
                contract.decimals = self.extract_decimals(text, address)
                
                contracts.append(contract)
        
        return contracts
    
    def is_valid_solana_address(self, address: str) -> bool:
        """Enhanced validation for Solana addresses"""
        # Check length (Solana addresses are typically 32-44 characters)
        if len(address) < 32 or len(address) > 44:
            return False
        
        # Skip known program addresses and common tokens
        if address in self.excluded_programs:
            return False
        
        # Check for valid Base58 characters only
        base58_chars = set('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz')
        if not all(c in base58_chars for c in address):
            return False
        
        # Check for common non-address patterns
        invalid_patterns = [
            'twitter', 'telegram', 'website', 'medium', 'github', 'discord', 
            'youtube', 'instagram', 'http', 'www', '.com', '.org', '.io',
            'pump', 'fun', 'raydium', 'jupiter'  # Common but not contract addresses
        ]
        
        address_lower = address.lower()
        for pattern in invalid_patterns:
            if pattern in address_lower:
                return False
        
        # Additional checks for suspicious patterns
        if address.count('1') > len(address) * 0.7:  # Too many 1s
            return False
        if len(set(address)) < 8:  # Too few unique characters
            return False
            
        return True
    
    def extract_token_symbol(self, text: str, address: str) -> Optional[str]:
        """Extract token symbol from message text"""
        # Look for symbols near the address
        address_index = text.find(address)
        if address_index == -1:
            return None
        
        # Check text around the address (±100 characters)
        start = max(0, address_index - 100)
        end = min(len(text), address_index + len(address) + 100)
        context = text[start:end]
        
        for pattern in self.symbol_patterns:
            matches = pattern.findall(context)
            if matches:
                return matches[0].upper()
        
        return None
    
    def calculate_confidence_score(self, text: str, contract: SolanaContractInfo) -> float:
        """Calculate confidence score for a Solana contract"""
        score = 0.0
        text_lower = text.lower()
        
        # Solana-specific positive indicators
        positive_keywords = [
            'new token', 'launch', 'presale', 'fair launch', 'stealth launch',
            'contract address', 'ca:', 'token address', 'mint address',
            'buy now', 'gem', 'moonshot', 'alpha', 'solana', 'spl token',
            'raydium', 'jupiter', 'pump.fun', 'dexscreener', 'birdeye',
            'bonding curve', 'liquidity', 'mcap', 'market cap'
        ]
        
        for keyword in positive_keywords:
            if keyword in text_lower:
                if keyword in ['solana', 'spl token', 'raydium', 'jupiter']:
                    score += 0.15  # Higher weight for Solana-specific terms
                else:
                    score += 0.1
        
        # Has symbol (important for tokens)
        if contract.symbol:
            score += 0.25
            # Bonus for reasonable symbol length
            if 2 <= len(contract.symbol) <= 6:
                score += 0.1
        
        # Address format bonus (Solana addresses are typically 43-44 chars)
        if 43 <= len(contract.address) <= 44:
            score += 0.15
        elif 40 <= len(contract.address) <= 42:
            score += 0.1
        
        # Context indicators
        context_indicators = [
            'just launched', 'new mint', 'fresh token', 'stealth',
            '0 tax', 'no tax', 'renounced', 'burned', 'locked'
        ]
        
        for indicator in context_indicators:
            if indicator in text_lower:
                score += 0.08
        
        # Negative indicators (Solana-specific)
        negative_keywords = [
            'scam', 'rug', 'fake', 'honeypot', 'warning', 'avoid', 'lost', 'hacked',
            'dump', 'dumped', 'rugpull', 'exit scam', 'mint disabled', 'frozen',
            'blacklist', 'tax', 'high tax', 'sell tax', 'anti bot'
        ]
        
        for keyword in negative_keywords:
            if keyword in text_lower:
                if keyword in ['rug', 'rugpull', 'scam', 'honeypot']:
                    score -= 0.4  # Heavy penalty for major red flags
                else:
                    score -= 0.2
        
        # Bonus for technical details (suggests legitimacy)
        technical_terms = [
            'decimals', 'supply', 'total supply', 'max supply',
            'liquidity pool', 'lp', 'mint authority', 'freeze authority'
        ]
        
        for term in technical_terms:
            if term in text_lower:
                score += 0.05
        
        return min(1.0, max(0.0, score))
    
    async def handle_found_contract(self, contract: SolanaContractInfo, group_config: GroupConfig):
        """Handle a found contract address"""
        logger.info(f"Found contract: {contract.address} (${contract.symbol}) "
                   f"from {group_config.group_name} (confidence: {contract.confidence_score:.2f})")
        
        # Save to file
        self.save_contract_to_file(contract)
        
        # Send to main bot if configured
        # if hasattr(self.config, 'TELEGRAM_BOT_TOKEN'):
        await self.notify_main_bot(contract)
        
        # Auto-trade if enabled
        if group_config.auto_trade and contract.confidence_score >= 0.8:
            await self.execute_auto_trade(contract)
    
    def save_contract_to_file(self, contract: SolanaContractInfo):
        """Save Solana contract to JSON file"""
        contracts_file = 'found_solana_contracts.json'
        
        # Load existing contracts
        contracts = []
        if os.path.exists(contracts_file):
            try:
                with open(contracts_file, 'r') as f:
                    contracts = json.load(f)
            except:
                contracts = []
        
        # Add new contract
        contract_data = {
            'address': contract.address,
            'symbol': contract.symbol,
            'name': contract.name,
            'decimals': contract.decimals,
            'network': 'solana',
            'source_group': contract.source_group,
            'source_message': contract.source_message,
            'timestamp': contract.timestamp.isoformat() if contract.timestamp else None,
            'confidence_score': contract.confidence_score,
            'mint_authority': contract.mint_authority,
            'freeze_authority': contract.freeze_authority
        }
        
        contracts.append(contract_data)
        
        # Keep only last 1000 contracts
        contracts = contracts[-1000:]
        
        # Save back to file
        with open(contracts_file, 'w') as f:
            json.dump(contracts, f, indent=2)
    
    async def notify_main_bot(self, contract: SolanaContractInfo):
        """Notify the main trading bot about the found contract"""
        try:
            from telegram_bot import send_contract_alert
            
            message = f"🔍 **New Contract Found**\n\n"
            message += f"💎 **Address:** `{contract.address}`\n"
            if contract.symbol:
                message += f"🏷️ **Symbol:** ${contract.symbol}\n"
            message += f"🌐 **Network:** {contract.network.capitalize()}\n"
            message += f"📍 **Source:** {contract.source_group}\n"
            message += f"⭐ **Confidence:** {contract.confidence_score:.0%}\n"
            message += f"🕒 **Found:** {contract.timestamp.strftime('%H:%M:%S')}\n\n"
            if contract.source_message:
                message += f"💬 **Context:** {contract.source_message[:100]}..."
            
            await send_contract_alert(message)
            
        except Exception as e:
            logger.error(f"Error notifying main bot: {e}")
    
    async def execute_auto_trade(self, contract: SolanaContractInfo):
        """Execute automatic trade for high-confidence contracts"""
        try:
            logger.info(f"Executing auto-trade for {contract.address}")
            
            # Import trading engine
            from trading_engine import SolanaTradingEngine
            from solana.keypair import Keypair
            
            # Initialize trading engine
            trading_engine = SolanaTradingEngine()
            
            # Get default wallet for auto-trading (you'll need to configure this)
            # For security, this should be loaded from encrypted config
            auto_trade_wallet = os.getenv('AUTO_TRADE_WALLET_PRIVATE_KEY')
            if not auto_trade_wallet:
                logger.warning("Auto-trade wallet not configured. Skipping trade.")
                return
            
            # Create wallet from private key
            wallet = Keypair.from_secret_key(bytes.fromhex(auto_trade_wallet))
            
            # Default buy amount (configurable)
            buy_amount_sol = float(os.getenv('AUTO_TRADE_AMOUNT_SOL', '0.1'))
            
            # Execute buy order
            result = await trading_engine.execute_trade(
                wallet=wallet,
                action='buy',
                token_address=contract.address,
                amount=buy_amount_sol,
                slippage_bps=300  # 3% slippage for auto-trades
            )
            
            if result.success:
                logger.info(f"✅ Auto-trade successful: {contract.symbol} ({contract.address})")
                logger.info(f"TX: {result.tx_signature}")
                
                # Notify main bot of successful trade
                await self.notify_trade_success(contract, result)
            else:
                logger.error(f"❌ Auto-trade failed: {result.error}")
                
        except Exception as e:
            logger.error(f"Error in auto-trade: {e}")
    
    async def notify_trade_success(self, contract: SolanaContractInfo, trade_result):
        """Notify main bot of successful auto-trade"""
        try:
            # This would send a notification to your main trading bot
            message = f"🤖 AUTO-TRADE EXECUTED\n\n"
            message += f"💎 Token: ${contract.symbol}\n"
            message += f"📍 Address: {contract.address}\n"
            message += f"🎯 Confidence: {contract.confidence_score:.2f}\n"
            message += f"✅ Status: Success\n"
            message += f"🔗 TX: {trade_result.tx_signature}\n"
            message += f"⏱️ Execution: {trade_result.execution_time:.2f}s"
            
            logger.info(f"Trade notification: {message}")
            # Add actual notification logic here (Telegram, Discord, etc.)
            
        except Exception as e:
            logger.error(f"Error sending trade notification: {e}")
    
    async def add_group(self, group_identifier: str, group_name: str = None, auto_trade: bool = False, min_confidence: float = 0.8) -> bool:
        """Add a group to monitor"""
        try:
            # Get group entity
            entity = await self.client.get_entity(group_identifier)
            
            if isinstance(entity, (Channel, Chat)):
                group_id = entity.id
                if hasattr(entity, 'broadcast') and entity.broadcast:
                    group_id = -entity.id  # Channel ID should be negative
                
                group_config = GroupConfig(
                    group_id=group_id,
                    group_name=group_name or getattr(entity, 'title', 'Unknown Group'),
                    enabled=True,
                    auto_trade=auto_trade,
                    min_confidence=min_confidence
                )
                
                self.monitored_groups[group_id] = group_config
                self.save_groups_config()
                
                logger.info(f"Added group: {group_config.group_name} (ID: {group_id})")
                return True
            
        except Exception as e:
            logger.error(f"Error adding group {group_identifier}: {e}")
        
        return False
    
    def save_groups_config(self):
        """Save groups configuration to file"""
        config_data = {
            "groups": [
                {
                    "group_id": config.group_id,
                    "group_name": config.group_name,
                    "enabled": config.enabled,
                    "auto_trade": config.auto_trade,
                    "min_confidence": config.min_confidence
                }
                for config in self.monitored_groups.values()
            ]
        }
        
        with open('scraper_groups.json', 'w') as f:
            json.dump(config_data, f, indent=2)
    
    async def list_groups(self) -> List[Dict]:
        """List all monitored groups"""
        groups_info = []
        for group_config in self.monitored_groups.values():
            groups_info.append({
                'id': group_config.group_id,
                'name': group_config.group_name,
                'enabled': group_config.enabled,
                'auto_trade': group_config.auto_trade,
                'min_confidence': group_config.min_confidence
            })
        return groups_info
    
    async def stop(self):
        """Stop the scraper"""
        logger.info("Stopping Telegram scraper...")
        await self.client.disconnect()

async def main():
    """Main function"""
    scraper = SolanaTelegramScraper()
    
    try:
        await scraper.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Scraper error: {e}")
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())