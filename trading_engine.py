"""
Enhanced Solana Trading Engine
Integrates with wallet manager for user wallets
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solana.rpc.types import TxOpts
from solana.transaction import Transaction
import aiohttp

# Import wallet manager
from wallet_manager import wallet_manager

import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

import requests
import aiohttp
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.rpc.types import TxOpts
import base64

from api_manager import api_manager, APIConfig

logger = logging.getLogger(__name__)

@dataclass
class TradeResult:
    success: bool
    tx_signature: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    gas_used: Optional[int] = None
    final_amount: Optional[float] = None

@dataclass
class TokenInfo:
    address: str
    symbol: str
    name: str
    decimals: int
    price_usd: float
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None

class EnhancedTradingEngine:
    """Advanced trading engine with full API integration"""
    
    def __init__(self):
        self.api_manager = api_manager
        self.config = APIConfig
        
        # Initialize RPC clients with failover
        self.primary_rpc = None
        self.backup_rpcs = []
        self._initialize_rpc_clients()
        
        # Jupiter API endpoints
        self.jupiter_endpoints = self.api_manager.get_jupiter_endpoints()
        
        # MEV protection
        self.mev_endpoints = self.api_manager.get_mev_endpoints()
        self.tip_accounts = self.api_manager.get_tip_accounts()
        
        # Performance tracking
        self.trade_stats = {
            'total_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_volume': 0.0,
            'average_execution_time': 0.0
        }
    
    def _initialize_rpc_clients(self):
        """Initialize RPC clients with failover support"""
        try:
            # Primary RPC (Shyft)
            primary_url = self.api_manager.get_rpc_url()
            self.primary_rpc = Client(primary_url, timeout=self.config.RPC_TIMEOUT)
            logger.info(f"✅ Primary RPC initialized: {primary_url}")
            
            # Backup RPCs
            backup_endpoints = ['publicnode_rpc', 'helius_rpc']
            for endpoint_key in backup_endpoints:
                endpoint = self.api_manager.endpoints.get(endpoint_key)
                if endpoint:
                    try:
                        if endpoint.api_key:
                            url = f"{endpoint.url}?api_key={endpoint.api_key}"
                        else:
                            url = endpoint.url
                        backup_client = Client(url, timeout=self.config.RPC_TIMEOUT)
                        self.backup_rpcs.append(backup_client)
                        logger.info(f"✅ Backup RPC added: {endpoint.name}")
                    except Exception as e:
                        logger.warning(f"⚠️  Failed to initialize backup RPC {endpoint.name}: {e}")
                        
        except Exception as e:
            logger.error(f"❌ Failed to initialize RPC clients: {e}")
            raise
    
    async def get_token_info(self, token_address: str) -> Optional[TokenInfo]:
        """Get comprehensive token information"""
        try:
            # Use Jupiter Token API for token search
            search_url = self.jupiter_endpoints['token_search']
            params = {'query': token_address}
            headers = self.api_manager.get_headers_for_endpoint('jupiter_token')
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        tokens = data.get('data', [])
                        
                        if tokens:
                            token = tokens[0]  # First match
                            
                            # Get price from Jupiter Price API
                            price = await self._get_token_price(token_address)
                            
                            return TokenInfo(
                                address=token.get('address', token_address),
                                symbol=token.get('symbol', 'UNKNOWN'),
                                name=token.get('name', 'Unknown Token'),
                                decimals=token.get('decimals', 9),
                                price_usd=price,
                                market_cap=token.get('market_cap'),
                                volume_24h=token.get('volume_24h')
                            )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting token info for {token_address}: {e}")
            return None
    
    async def _get_token_price(self, token_address: str) -> float:
        """Get current token price"""
        try:
            price_url = self.jupiter_endpoints['prices']
            params = {'ids': token_address}
            headers = self.api_manager.get_headers_for_endpoint('jupiter_price')
            
            async with aiohttp.ClientSession() as session:
                async with session.get(price_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        price_data = data.get('data', {}).get(token_address, {})
                        return float(price_data.get('price', 0.0))
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error getting price for {token_address}: {e}")
            return 0.0
    
    async def execute_trade(self, 
                           wallet: Keypair,
                           action: str,  # 'buy' or 'sell'
                           token_address: str,
                           amount: float,
                           slippage_bps: Optional[int] = None) -> TradeResult:
        """Execute a trade with full optimization and MEV protection"""
        
        start_time = time.time()
        
        try:
            # Input validation
            if action not in ['buy', 'sell']:
                return TradeResult(False, error="Invalid action. Must be 'buy' or 'sell'")
            
            if slippage_bps is None:
                slippage_bps = self.config.DEFAULT_SLIPPAGE_BPS
            
            # Get token info for better trade execution
            token_info = await self.get_token_info(token_address)
            
            # Configure trade parameters
            if action == 'buy':
                input_mint = "So11111111111111111111111111111111111111112"  # SOL
                output_mint = token_address
                trade_amount = int(amount * 1e9)  # Convert SOL to lamports
            else:
                input_mint = token_address
                output_mint = "So11111111111111111111111111111111111111112"  # SOL
                # For selling, amount should be in token units with proper decimals
                decimals = token_info.decimals if token_info else 9
                trade_amount = int(amount * (10 ** decimals))
            
            # Get optimal route from Jupiter
            route = await self._get_optimal_route(
                input_mint=input_mint,
                output_mint=output_mint,
                amount=trade_amount,
                slippage_bps=slippage_bps
            )
            
            if not route:
                return TradeResult(False, error="No trading route found")
            
            # Execute the swap with MEV protection
            tx_signature = await self._execute_swap_with_mev_protection(
                wallet=wallet,
                route=route
            )
            
            execution_time = time.time() - start_time
            
            # Update statistics
            self._update_trade_stats(True, execution_time, amount)
            
            # Calculate final amount received
            final_amount = float(route.get('outAmount', 0))
            if action == 'buy' and token_info:
                final_amount = final_amount / (10 ** token_info.decimals)
            elif action == 'sell':
                final_amount = final_amount / 1e9  # Convert lamports to SOL
            
            logger.info(f"✅ Trade executed successfully: {action} {token_address}")
            logger.info(f"📊 TX: {tx_signature}, Time: {execution_time:.2f}s")
            
            return TradeResult(
                success=True,
                tx_signature=tx_signature,
                execution_time=execution_time,
                final_amount=final_amount
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            logger.error(f"❌ Trade failed: {action} {token_address} - {error_msg}")
            
            # Update statistics
            self._update_trade_stats(False, execution_time, amount)
            
            return TradeResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )
    
    async def _get_optimal_route(self, input_mint: str, output_mint: str, 
                                amount: int, slippage_bps: int) -> Optional[Dict]:
        """Get optimal trading route from Jupiter with retry logic"""
        
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": str(amount),
            "slippageBps": slippage_bps,
            "swapMode": "ExactIn",
            "onlyDirectRoutes": False,
            "asLegacyTransaction": True
        }
        
        # Try Jupiter quote endpoint with retries
        for attempt in range(self.config.MAX_RETRIES):
            try:
                quote_url = self.jupiter_endpoints['quote']
                headers = self.api_manager.get_headers_for_endpoint('jupiter_swap')
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        quote_url, 
                        params=params, 
                        headers=headers,
                        timeout=self.config.API_TIMEOUT
                    ) as response:
                        
                        if response.status == 200:
                            data = await response.json()
                            routes = data.get('data', [])
                            
                            if routes:
                                # Return the best route (first one)
                                return routes[0]
                            else:
                                logger.warning("No routes found for trade")
                                return None
                        
                        elif response.status == 429:  # Rate limited
                            wait_time = (attempt + 1) * self.config.RETRY_DELAY
                            logger.warning(f"Rate limited, waiting {wait_time}s...")
                            await asyncio.sleep(wait_time)
                        
                        else:
                            error_text = await response.text()
                            logger.error(f"Jupiter API error {response.status}: {error_text}")
                            
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1}, retrying...")
                if attempt < self.config.MAX_RETRIES - 1:
                    await asyncio.sleep(self.config.RETRY_DELAY)
            
            except Exception as e:
                logger.error(f"Error getting route on attempt {attempt + 1}: {e}")
                if attempt < self.config.MAX_RETRIES - 1:
                    await asyncio.sleep(self.config.RETRY_DELAY)
        
        return None
    
    async def _execute_swap_with_mev_protection(self, wallet: Keypair, route: Dict) -> str:
        """Execute swap with MEV protection and optimal submission"""
        
        # Prepare swap transaction
        swap_data = {
            "route": route,
            "userPublicKey": str(wallet.pubkey()),
            "wrapUnwrapSOL": True,
            "feeAccount": None,
            "asLegacyTransaction": True
        }
        
        # Add compute budget for MEV protection
        if self.config.ENABLE_MEV_PROTECTION:
            swap_data.update({
                "computeUnitPriceMicroLamports": self.config.DEFAULT_COMPUTE_UNIT_PRICE,
                "computeUnitLimit": self.config.DEFAULT_COMPUTE_UNIT_LIMIT
            })
        
        # Get swap transaction from Jupiter
        swap_url = self.jupiter_endpoints['swap']
        headers = self.api_manager.get_headers_for_endpoint('jupiter_swap')
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                swap_url,
                json=swap_data,
                headers=headers,
                timeout=self.config.API_TIMEOUT
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Failed to get swap transaction: {error_text}")
                
                swap_response = await response.json()
        
        # Deserialize and sign transaction
        tx_base64 = swap_response["swapTransaction"]
        tx_bytes = base64.b64decode(tx_base64)
        tx = Transaction.deserialize(tx_bytes)
        tx.sign(wallet)
        
        # Submit transaction with MEV protection
        if self.config.ENABLE_MEV_PROTECTION and self.mev_endpoints:
            return await self._submit_with_mev_protection(tx)
        else:
            return await self._submit_to_rpc(tx)
    
    async def _submit_with_mev_protection(self, tx: Transaction) -> str:
        """Submit transaction through MEV protection services"""
        
        # Try MEV-protected submission first
        for mev_endpoint in self.mev_endpoints:
            try:
                if 'zeroslot' in mev_endpoint.name.lower():
                    return await self._submit_to_zeroslot(tx, mev_endpoint)
                elif 'nozomi' in mev_endpoint.name.lower():
                    return await self._submit_to_nozomi(tx, mev_endpoint)
                elif 'nextblock' in mev_endpoint.name.lower():
                    return await self._submit_to_nextblock(tx, mev_endpoint)
            
            except Exception as e:
                logger.warning(f"MEV submission failed for {mev_endpoint.name}: {e}")
                continue
        
        # Fallback to regular RPC
        logger.info("Falling back to regular RPC submission")
        return await self._submit_to_rpc(tx)
    
    async def _submit_to_zeroslot(self, tx: Transaction, endpoint) -> str:
        """Submit to ZeroSlot MEV protection"""
        url = f"{endpoint.url}?api_key={endpoint.api_key}"
        headers = self.api_manager.get_headers_for_endpoint('zeroslot_primary')
        
        tx_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendTransaction",
            "params": [
                base64.b64encode(tx.serialize()).decode('utf-8'),
                {"skipPreflight": True, "maxRetries": 0}
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=tx_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('result', '')
                else:
                    error_text = await response.text()
                    raise Exception(f"ZeroSlot submission failed: {error_text}")
    
    async def _submit_to_nozomi(self, tx: Transaction, endpoint) -> str:
        """Submit to Nozomi MEV protection"""
        url = f"{endpoint.url}?c={endpoint.api_key}"
        headers = self.api_manager.get_headers_for_endpoint('nozomi_primary')
        
        tx_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendTransaction",
            "params": [
                base64.b64encode(tx.serialize()).decode('utf-8'),
                {"skipPreflight": True}
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=tx_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('result', '')
                else:
                    error_text = await response.text()
                    raise Exception(f"Nozomi submission failed: {error_text}")
    
    async def _submit_to_nextblock(self, tx: Transaction, endpoint) -> str:
        """Submit to NextBlock"""
        headers = self.api_manager.get_headers_for_endpoint('nextblock')
        
        tx_data = {
            "transaction": base64.b64encode(tx.serialize()).decode('utf-8')
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint.url, json=tx_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('signature', '')
                else:
                    error_text = await response.text()
                    raise Exception(f"NextBlock submission failed: {error_text}")
    
    async def _submit_to_rpc(self, tx: Transaction) -> str:
        """Submit transaction to regular RPC with failover"""
        
        # Try primary RPC first
        try:
            result = self.primary_rpc.send_raw_transaction(
                tx.serialize(),
                opts=TxOpts(skip_preflight=True, max_retries=0)
            )
            return result.value
        
        except Exception as e:
            logger.warning(f"Primary RPC failed: {e}")
            
            # Try backup RPCs
            for backup_rpc in self.backup_rpcs:
                try:
                    result = backup_rpc.send_raw_transaction(
                        tx.serialize(),
                        opts=TxOpts(skip_preflight=True, max_retries=0)
                    )
                    return result.value
                
                except Exception as backup_error:
                    logger.warning(f"Backup RPC failed: {backup_error}")
                    continue
            
            raise Exception("All RPC endpoints failed")
    
    def _update_trade_stats(self, success: bool, execution_time: float, volume: float):
        """Update trading statistics"""
        self.trade_stats['total_trades'] += 1
        
        if success:
            self.trade_stats['successful_trades'] += 1
        else:
            self.trade_stats['failed_trades'] += 1
        
        self.trade_stats['total_volume'] += volume
        
        # Update average execution time
        total_time = (self.trade_stats['average_execution_time'] * 
                     (self.trade_stats['total_trades'] - 1) + execution_time)
        self.trade_stats['average_execution_time'] = total_time / self.trade_stats['total_trades']
    
    def get_performance_stats(self) -> Dict:
        """Get trading performance statistics"""
        total_trades = self.trade_stats['total_trades']
        
        if total_trades == 0:
            return {
                'total_trades': 0,
                'success_rate': 0.0,
                'total_volume': 0.0,
                'average_execution_time': 0.0
            }
        
        return {
            'total_trades': total_trades,
            'successful_trades': self.trade_stats['successful_trades'],
            'failed_trades': self.trade_stats['failed_trades'],
            'success_rate': (self.trade_stats['successful_trades'] / total_trades) * 100,
            'total_volume': self.trade_stats['total_volume'],
            'average_execution_time': self.trade_stats['average_execution_time']
        }
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all API endpoints"""
        health_status = {}
        
        # Check RPC endpoints
        try:
            # Test primary RPC
            slot = self.primary_rpc.get_slot()
            health_status['primary_rpc'] = bool(slot.value)
        except:
            health_status['primary_rpc'] = False
        
        # Check Jupiter API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.jupiter_endpoints['quote']}?inputMint=So11111111111111111111111111111111111111112&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=1000000",
                    timeout=5
                ) as response:
                    health_status['jupiter_api'] = response.status == 200
        except:
            health_status['jupiter_api'] = False
        
        # Check MEV endpoints
        for endpoint in self.mev_endpoints:
            try:
                if 'zeroslot' in endpoint.name.lower() and 'health' in self.api_manager.endpoints:
                    health_endpoint = self.api_manager.endpoints['zeroslot_health']
                    async with aiohttp.ClientSession() as session:
                        async with session.get(health_endpoint.url, timeout=5) as response:
                            health_status[f'mev_{endpoint.name.lower()}'] = response.status == 200
                else:
                    health_status[f'mev_{endpoint.name.lower()}'] = True  # Assume healthy if no health check
            except:
                health_status[f'mev_{endpoint.name.lower()}'] = False
        
        return health_status
    
    async def execute_user_trade(self, 
                                user_id: str,
                                action: str,  # 'buy' or 'sell'
                                token_address: str,
                                amount: float,
                                slippage_bps: Optional[int] = None) -> TradeResult:
        """Execute trade using user's wallet from wallet manager"""
        try:
            # Get user's keypair from wallet manager
            user_keypair = wallet_manager.get_user_keypair(user_id)
            if not user_keypair:
                return TradeResult(False, error="User wallet not found. Please set up your wallet first.")
            
            # Update wallet activity
            await wallet_manager.update_wallet_activity(user_id)
            
            # Execute the trade using the user's wallet
            result = await self.execute_trade(
                wallet=user_keypair,
                action=action,
                token_address=token_address,
                amount=amount,
                slippage_bps=slippage_bps
            )
            
            logger.info(f"User {user_id} {action} trade result: {result.success}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing user trade: {e}")
            return TradeResult(False, error=str(e))

# Global instance
trading_engine = EnhancedTradingEngine()

if __name__ == "__main__":
    # Test the trading engine
    import asyncio
    
    async def test_engine():
        print("🚀 Testing Enhanced Trading Engine")
        print("=" * 50)
        
        # Health check
        health = await trading_engine.health_check()
        print("🏥 Health Status:")
        for service, status in health.items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {service}")
        
        print("\n📊 Performance Stats:")
        stats = trading_engine.get_performance_stats()
        for key, value in stats.items():
            print(f"  • {key}: {value}")
        
        # Test token info
        print("\n🪙 Testing Token Info:")
        token_info = await trading_engine.get_token_info("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")  # USDC
        if token_info:
            print(f"  Token: {token_info.symbol} ({token_info.name})")
            print(f"  Price: ${token_info.price_usd}")
            print(f"  Decimals: {token_info.decimals}")
    
    asyncio.run(test_engine())