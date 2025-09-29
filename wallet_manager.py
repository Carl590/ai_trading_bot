"""
Wallet Management System for AI Trading Bot
Similar to Maestro Trading Bot - User wallet integration
"""

import os
import json
import base64
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

@dataclass
class WalletInfo:
    """User wallet information"""
    user_id: str
    wallet_address: str
    encrypted_private_key: str
    wallet_name: str
    created_at: str
    last_used: Optional[str] = None
    is_active: bool = True
    balance_sol: float = 0.0
    total_trades: int = 0
    
class WalletEncryption:
    """Handle wallet encryption/decryption"""
    
    def __init__(self, master_key: Optional[str] = None):
        if master_key:
            self.key = master_key.encode()
        else:
            # Generate from environment or create new
            self.key = os.getenv('WALLET_ENCRYPTION_KEY', self._generate_key()).encode()
        
        # Create Fernet instance for encryption
        key_hash = hashlib.sha256(self.key).digest()
        self.fernet = Fernet(base64.urlsafe_b64encode(key_hash[:32]))
    
    def _generate_key(self) -> str:
        """Generate a new encryption key"""
        return base64.urlsafe_b64encode(os.urandom(32)).decode()
    
    def encrypt_private_key(self, private_key: bytes) -> str:
        """Encrypt private key"""
        return self.fernet.encrypt(private_key).decode()
    
    def decrypt_private_key(self, encrypted_key: str) -> bytes:
        """Decrypt private key"""
        return self.fernet.decrypt(encrypted_key.encode())

class WalletManager:
    """Comprehensive wallet management system"""
    
    def __init__(self, rpc_url: str = None):
        self.wallets_file = 'user_wallets.json'
        self.encryption = WalletEncryption()
        self.rpc_url = rpc_url or os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
        self.client = AsyncClient(self.rpc_url, commitment=Commitment("confirmed"))
        self.user_wallets: Dict[str, WalletInfo] = {}
        self.load_wallets()
    
    def load_wallets(self):
        """Load user wallets from file"""
        try:
            if os.path.exists(self.wallets_file):
                with open(self.wallets_file, 'r') as f:
                    data = json.load(f)
                    
                for user_id, wallet_data in data.items():
                    self.user_wallets[user_id] = WalletInfo(**wallet_data)
                    
                logger.info(f"Loaded {len(self.user_wallets)} user wallets")
        except Exception as e:
            logger.error(f"Error loading wallets: {e}")
            self.user_wallets = {}
    
    def save_wallets(self):
        """Save user wallets to file"""
        try:
            data = {}
            for user_id, wallet in self.user_wallets.items():
                data[user_id] = asdict(wallet)
            
            with open(self.wallets_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Saved {len(self.user_wallets)} user wallets")
        except Exception as e:
            logger.error(f"Error saving wallets: {e}")
    
    def create_new_wallet(self, user_id: str, wallet_name: str = "Main Wallet") -> Tuple[str, str]:
        """Create a new wallet for user"""
        try:
            # Generate new keypair
            keypair = Keypair()
            
            # Encrypt private key
            encrypted_key = self.encryption.encrypt_private_key(bytes(keypair))
            
            # Create wallet info
            wallet_info = WalletInfo(
                user_id=user_id,
                wallet_address=str(keypair.public_key),
                encrypted_private_key=encrypted_key,
                wallet_name=wallet_name,
                created_at=datetime.now().isoformat()
            )
            
            # Store wallet
            self.user_wallets[user_id] = wallet_info
            self.save_wallets()
            
            logger.info(f"Created new wallet for user {user_id}: {keypair.public_key}")
            
            # Return address and mnemonic-style backup
            return str(keypair.pubkey()), self._create_backup_phrase(bytes(keypair))
            
        except Exception as e:
            logger.error(f"Error creating wallet: {e}")
            raise
    
    def import_wallet(self, user_id: str, private_key: str, wallet_name: str = "Imported Wallet") -> str:
        """Import existing wallet from private key"""
        try:
            # Handle different private key formats
            if private_key.startswith('[') and private_key.endswith(']'):
                # Array format: [1,2,3,...]
                key_bytes = bytes(json.loads(private_key))
            elif len(private_key) == 128:
                # Hex format
                key_bytes = bytes.fromhex(private_key)
            elif len(private_key) == 88:
                # Base58 format
                import base58
                key_bytes = base58.b58decode(private_key)
            else:
                raise ValueError("Unsupported private key format")
            
            # Create keypair
            keypair = Keypair.from_bytes(key_bytes)
            
            # Encrypt private key
            encrypted_key = self.encryption.encrypt_private_key(bytes(keypair))
            
            # Create wallet info
            wallet_info = WalletInfo(
                user_id=user_id,
                wallet_address=str(keypair.pubkey()),
                encrypted_private_key=encrypted_key,
                wallet_name=wallet_name,
                created_at=datetime.now().isoformat()
            )
            
            # Store wallet
            self.user_wallets[user_id] = wallet_info
            self.save_wallets()
            
            logger.info(f"Imported wallet for user {user_id}: {keypair.pubkey()}")
            return str(keypair.pubkey())
            
        except Exception as e:
            logger.error(f"Error importing wallet: {e}")
            raise
    
    def get_user_wallet(self, user_id: str) -> Optional[WalletInfo]:
        """Get user's wallet info"""
        return self.user_wallets.get(user_id)
    
    def get_user_keypair(self, user_id: str) -> Optional[Keypair]:
        """Get user's keypair for trading"""
        try:
            wallet_info = self.user_wallets.get(user_id)
            if not wallet_info:
                return None
            
            # Decrypt private key
            private_key = self.encryption.decrypt_private_key(wallet_info.encrypted_private_key)
            
            # Create keypair
            return Keypair.from_bytes(private_key)
            
        except Exception as e:
            logger.error(f"Error getting keypair for user {user_id}: {e}")
            return None
    
    async def get_wallet_balance(self, user_id: str) -> float:
        """Get wallet SOL balance"""
        try:
            wallet_info = self.user_wallets.get(user_id)
            if not wallet_info:
                return 0.0
            
            # Get balance from blockchain
            pubkey = Pubkey.from_string(wallet_info.wallet_address)
            response = await self.client.get_balance(pubkey)
            
            if response.value is not None:
                balance = response.value / 1e9  # Convert lamports to SOL
                
                # Update stored balance
                wallet_info.balance_sol = balance
                self.save_wallets()
                
                return balance
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error getting balance for user {user_id}: {e}")
            return 0.0
    
    async def update_wallet_activity(self, user_id: str):
        """Update last used timestamp and trade count"""
        try:
            wallet_info = self.user_wallets.get(user_id)
            if wallet_info:
                wallet_info.last_used = datetime.now().isoformat()
                wallet_info.total_trades += 1
                self.save_wallets()
        except Exception as e:
            logger.error(f"Error updating wallet activity: {e}")
    
    def delete_wallet(self, user_id: str) -> bool:
        """Delete user wallet (irreversible)"""
        try:
            if user_id in self.user_wallets:
                del self.user_wallets[user_id]
                self.save_wallets()
                logger.info(f"Deleted wallet for user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting wallet: {e}")
            return False
    
    def export_private_key(self, user_id: str, format_type: str = "array") -> Optional[str]:
        """Export private key in various formats"""
        try:
            wallet_info = self.user_wallets.get(user_id)
            if not wallet_info:
                return None
            
            # Decrypt private key
            private_key = self.encryption.decrypt_private_key(wallet_info.encrypted_private_key)
            
            if format_type == "array":
                return str(list(private_key))
            elif format_type == "hex":
                return private_key.hex()
            elif format_type == "base58":
                import base58
                return base58.b58encode(private_key).decode()
            else:
                return str(list(private_key))  # Default to array
                
        except Exception as e:
            logger.error(f"Error exporting private key: {e}")
            return None
    
    def _create_backup_phrase(self, private_key: bytes) -> str:
        """Create a backup phrase (simplified - in production use BIP39)"""
        # This is a simplified backup - in production, implement proper BIP39 mnemonic
        key_hex = private_key.hex()
        # Split into chunks and create pseudo-mnemonic
        chunks = [key_hex[i:i+8] for i in range(0, len(key_hex), 8)]
        return " ".join(chunks[:12])  # First 12 chunks as backup
    
    def get_wallet_stats(self) -> Dict:
        """Get overall wallet statistics"""
        total_wallets = len(self.user_wallets)
        active_wallets = len([w for w in self.user_wallets.values() if w.is_active])
        total_trades = sum(w.total_trades for w in self.user_wallets.values())
        
        return {
            "total_wallets": total_wallets,
            "active_wallets": active_wallets,
            "total_trades": total_trades,
            "encryption_enabled": True
        }
    
    async def validate_wallet(self, user_id: str) -> Tuple[bool, str]:
        """Validate user wallet"""
        try:
            wallet_info = self.user_wallets.get(user_id)
            if not wallet_info:
                return False, "Wallet not found"
            
            # Check if we can decrypt the private key
            try:
                private_key = self.encryption.decrypt_private_key(wallet_info.encrypted_private_key)
                keypair = Keypair.from_secret_key(private_key)
                
                # Verify address matches
                if str(keypair.pubkey()) != wallet_info.wallet_address:
                    return False, "Address mismatch"
                
                # Check if wallet exists on blockchain
                pubkey = Pubkey.from_string(wallet_info.wallet_address)
                response = await self.client.get_account_info(pubkey)
                
                return True, "Wallet valid"
                
            except Exception as e:
                return False, f"Decryption failed: {e}"
                
        except Exception as e:
            return False, f"Validation error: {e}"

# Global wallet manager instance
wallet_manager = WalletManager()