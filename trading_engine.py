"""
Enhanced Solana Trading Engine with AI Features
Integrates with wallet manager, rug checker, and trailing stops
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

# Import components
from wallet_manager import wallet_manager
from api_manager import api_manager, APIConfig

# Import new AI features
from rug_checker import quick_rug_check, RugCheckResult
from trailing_stop import get_trailing_stop_manager

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
    execution_price: Optional[float] = None
    rug_check_result: Optional[RugCheckResult] = None
    
@dataclass
class TradeOptions:
    """Options for trade execution"""
    enable_rug_check: bool = True
    enable_trailing_stop: bool = True
    max_slippage_pct: float = 0.01
    priority_fee_lamports: int = 1000
    use_mev_protection: bool = True
    stop_loss_pct: Optional[float] = None
    take_profit_pct: Optional[float] = None

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
    
    async def execute_buy_with_ai(self, 
                                 user_id: str,
                                 token_address: str, 
                                 amount_usd: float,
                                 options: Optional[TradeOptions] = None) -> TradeResult:
        """
        Execute buy order with AI features (rug check, trailing stops)
        """
        if options is None:
            options = TradeOptions()
        
        start_time = time.time()
        
        try:
            # Get user's wallet
            user_keypair = wallet_manager.get_user_keypair(user_id)
            if not user_keypair:
                return TradeResult(
                    success=False, 
                    error="User wallet not found. Please set up your wallet first."
                )
            
            # Rug check if enabled
            rug_result = None
            if options.enable_rug_check:
                logger.info(f"Running rug check for token: {token_address}")
                rug_result = await quick_rug_check(token_address)
                
                if not rug_result.ok:
                    return TradeResult(
                        success=False,
                        error=f"Rug check failed: {', '.join(rug_result.hard_fail_reasons)}",
                        rug_check_result=rug_result,
                        execution_time=time.time() - start_time
                    )
                
                logger.info(f"Rug check passed: {rug_result.recommendation}")
            
            # Execute the buy trade
            buy_result = await self.execute_user_trade(
                user_id=user_id,
                action='buy',
                token_address=token_address,
                amount=amount_usd,
                slippage_bps=int(options.max_slippage_pct * 10000)
            )
            
            if not buy_result.success:
                return TradeResult(
                    success=False,
                    error=buy_result.error,
                    execution_time=time.time() - start_time,
                    rug_check_result=rug_result
                )
            
            # Set up trailing stop if enabled
            if options.enable_trailing_stop and buy_result.execution_price:
                try:
                    ts_manager = await get_trailing_stop_manager()
                    await ts_manager.on_entry(
                        user_id=user_id,
                        token_addr=token_address,
                        entry_price=buy_result.execution_price,
                        trade_size_usd=amount_usd
                    )
                    logger.info(f"Trailing stop activated for {user_id} on {token_address}")
                except Exception as e:
                    logger.error(f"Failed to set up trailing stop: {e}")
            
            # Update stats
            execution_time = time.time() - start_time
            self._update_trade_stats(True, execution_time, amount_usd)
            
            return TradeResult(
                success=True,
                tx_signature=buy_result.tx_signature,
                execution_time=execution_time,
                execution_price=buy_result.execution_price,
                final_amount=buy_result.final_amount,
                rug_check_result=rug_result
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._update_trade_stats(False, execution_time, amount_usd)
            
            logger.error(f"AI buy failed for user {user_id}: {e}")
            return TradeResult(
                success=False,
                error=str(e),
                execution_time=execution_time,
                rug_check_result=rug_result
            )
    
    async def execute_sell_with_ai(self,
                                  user_id: str,
                                  token_address: str,
                                  percentage: float = 100.0,
                                  options: Optional[TradeOptions] = None) -> TradeResult:
        """
        Execute sell order with AI features
        """
        if options is None:
            options = TradeOptions()
        
        start_time = time.time()
        
        try:
            # Remove trailing stop if exists
            if options.enable_trailing_stop:
                try:
                    ts_manager = await get_trailing_stop_manager()
                    await ts_manager.remove_trailing_stop(user_id, token_address)
                    logger.info(f"Trailing stop removed for {user_id} on {token_address}")
                except Exception as e:
                    logger.warning(f"Failed to remove trailing stop: {e}")
            
            # Execute the sell trade
            sell_result = await self.execute_user_trade(
                user_id=user_id,
                action='sell',
                token_address=token_address,
                amount=percentage,  # Percentage to sell
                slippage_bps=int(options.max_slippage_pct * 10000)
            )
            
            execution_time = time.time() - start_time
            
            if sell_result.success:
                self._update_trade_stats(True, execution_time, 0)  # No USD amount for sells
            else:
                self._update_trade_stats(False, execution_time, 0)
            
            return TradeResult(
                success=sell_result.success,
                tx_signature=sell_result.tx_signature,
                error=sell_result.error,
                execution_time=execution_time,
                execution_price=sell_result.execution_price,
                final_amount=sell_result.final_amount
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._update_trade_stats(False, execution_time, 0)
            
            logger.error(f"AI sell failed for user {user_id}: {e}")
            return TradeResult(
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    async def get_token_price_and_liquidity(self, token_address: str) -> Dict[str, Any]:
        """Get token price and liquidity info for AI features"""
        try:
            # Use Jupiter API to get price info
            quote_url = self.jupiter_endpoints['quote']
            params = {
                'inputMint': 'So11111111111111111111111111111111111111112',  # SOL
                'outputMint': token_address,
                'amount': 1000000000,  # 1 SOL in lamports
                'slippageBps': 50  # 0.5%
            }
            
            headers = self.api_manager.get_headers_for_endpoint('jupiter_quote')
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    quote_url,
                    params=params,
                    headers=headers,
                    timeout=self.config.API_TIMEOUT
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract price info
                        in_amount = int(data.get('inAmount', 0))
                        out_amount = int(data.get('outAmount', 0))
                        
                        if in_amount > 0 and out_amount > 0:
                            # Calculate price (tokens per SOL)
                            tokens_per_sol = out_amount / in_amount
                            price_usd = 0  # Would need SOL price to calculate
                            
                            return {
                                'price_per_sol': tokens_per_sol,
                                'price_usd': price_usd,
                                'liquidity_available': True,
                                'slippage_for_1_sol': data.get('priceImpactPct', 0),
                                'route_plan': data.get('routePlan', [])
                            }
            
            return {
                'price_per_sol': 0,
                'price_usd': 0,
                'liquidity_available': False,
                'slippage_for_1_sol': 100,
                'route_plan': []
            }
            
        except Exception as e:
            logger.error(f"Failed to get token info for {token_address}: {e}")
            return {
                'price_per_sol': 0,
                'price_usd': 0,
                'liquidity_available': False,
                'slippage_for_1_sol': 100,
                'route_plan': []
            }
    
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

# Global trading engine instance
_trading_engine = None

async def get_trading_engine():
    """Get global trading engine instance"""
    global _trading_engine
    if _trading_engine is None:
        _trading_engine = EnhancedTradingEngine()
    return _trading_engine

# Alias for backward compatibility
TradingEngine = EnhancedTradingEngine