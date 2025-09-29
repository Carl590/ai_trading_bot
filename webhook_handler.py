"""
TradingView Webhook Handler for Telegram Bot
Processes incoming alerts and executes trades
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any

import requests
from flask import Flask, request, jsonify
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.rpc.types import TxOpts
import base64

from telegram_bot import TelegramTradingBot, TradingPosition
from trading_engine import trading_engine, TradeResult
from api_manager import api_manager, APIConfig
from api_manager import api_manager, APIConfig

logger = logging.getLogger(__name__)

class WebhookTradeExecutor:
    def __init__(self, telegram_bot: TelegramTradingBot):
        self.bot = telegram_bot
        
        # Use API manager for all endpoints
        self.jupiter_endpoints = api_manager.get_jupiter_endpoints()
        self.rpc_client = Client(api_manager.get_rpc_url(), timeout=APIConfig.RPC_TIMEOUT)
        self.sol_mint = "So11111111111111111111111111111111111111112"
        
        # MEV protection
        self.mev_endpoints = api_manager.get_mev_endpoints()
        self.tip_accounts = api_manager.get_tip_accounts()
        
    async def process_tradingview_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming TradingView alert and execute trade"""
        try:
            # Extract alert information
            message = alert_data.get('msg', '').lower()
            user_id = alert_data.get('user_id')  # Should be passed in webhook
            
            if not user_id or user_id not in self.bot.user_wallets:
                return {"status": "error", "message": "User not found or wallet not connected"}
            
            if not self.bot.ai_trading_enabled.get(user_id, False):
                return {"status": "error", "message": "AI trading not enabled for user"}
            
            # Parse the message for action and token address
            action = None
            token_address = None
            
            # Look for buy/sell keywords
            if 'buy' in message:
                action = 'buy'
            elif 'sell' in message:
                action = 'sell'
            
            # Extract contract address (basic pattern matching)
            # Looking for Solana addresses (base58, 32-44 characters)
            import re
            address_pattern = r'[1-9A-HJ-NP-Za-km-z]{32,44}'
            addresses = re.findall(address_pattern, message)
            
            if addresses:
                token_address = addresses[0]  # Take the first address found
            
            if not action or not token_address:
                return {"status": "error", "message": "Could not parse buy/sell action or token address"}
            
            # Execute the trade
            result = await self.execute_trade(user_id, action, token_address)
            
            # Send notification to user
            await self.notify_user(user_id, action, token_address, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing alert: {e}")
            return {"status": "error", "message": str(e)}
    
    async def execute_trade(self, user_id: str, action: str, token_address: str, amount: float = None) -> Dict[str, Any]:
        """Execute a trading transaction using enhanced trading engine"""
        try:
            logger.info(f"Executing {action} for user {user_id}, token {token_address}")
            
            # Get user wallet from config
            user_config = self.config_manager.get_user_config(user_id)
            if not user_config or not user_config.get('wallet_private_key'):
                return {
                    'success': False,
                    'error': 'Wallet not configured for user'
                }
            
            # Initialize wallet
            wallet = Keypair.from_secret_key(user_config['wallet_private_key'])
            
            # Use enhanced trading engine for execution
            if action.lower() == 'buy':
                amount = amount or 0.1  # Default buy amount in SOL
                result = await trading_engine.execute_trade(
                    wallet=wallet,
                    action='buy',
                    token_address=token_address,
                    amount=amount
                )
            elif action.lower() == 'sell':
                if amount is None:
                    return {'success': False, 'error': 'Amount required for sell orders'}
                result = await trading_engine.execute_trade(
                    wallet=wallet,
                    action='sell',
                    token_address=token_address,
                    amount=amount
                )
            else:
                return {
                    'success': False,
                    'error': f'Unknown action: {action}'
                }
            
            # Convert TradeResult to dictionary
            return {
                'success': result.success,
                'tx_signature': result.tx_signature,
                'error': result.error,
                'execution_time': result.execution_time,
                'final_amount': result.final_amount
            }
        
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_swap_route(self, input_mint: str, output_mint: str, amount: int):
        """Get optimal swap route from Jupiter"""
        try:
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount),
                "slippageBps": APIConfig.DEFAULT_SLIPPAGE_BPS,
                "swapMode": "ExactIn"
            }
            
            # Use API manager for Jupiter quote endpoint
            quote_url = self.jupiter_endpoints['quote']
            headers = api_manager.get_headers_for_endpoint('jupiter_swap')
            
            response = requests.get(quote_url, params=params, headers=headers, timeout=APIConfig.API_TIMEOUT)
            response.raise_for_status()
            
            quote_data = response.json()
            routes = quote_data.get("data", [])
            
            if not routes:
                raise Exception("No swap route found")
            
            return routes[0]  # Return best route
            
        except Exception as e:
            logger.error(f"Failed to get swap route: {e}")
            raise
    
    async def execute_swap(self, wallet: Keypair, route: Dict) -> str:
        """Execute the swap transaction"""
        try:
        # Get swap transaction from Jupiter using API manager
        swap_url = self.jupiter_endpoints['swap']
        headers = api_manager.get_headers_for_endpoint('jupiter_swap')
        
        swap_data = {
            "route": route,
            "userPublicKey": str(wallet.public_key),
            "wrapUnwrapSOL": True,
            "feeAccount": None,
            "asLegacyTransaction": True
        }
        
        # Add MEV protection if enabled
        if APIConfig.ENABLE_MEV_PROTECTION and self.tip_accounts:
            swap_data["computeUnitPriceMicroLamports"] = APIConfig.DEFAULT_COMPUTE_UNIT_PRICE
            swap_data["computeUnitLimit"] = APIConfig.DEFAULT_COMPUTE_UNIT_LIMIT
        
        swap_response = requests.post(
            swap_url,
            json=swap_data,
            headers=headers,
            timeout=APIConfig.API_TIMEOUT
        )            swap_response.raise_for_status()
            swap_data = swap_response.json()
            
            # Deserialize and sign transaction
            tx_base64 = swap_data["swapTransaction"]
            tx_bytes = base64.b64decode(tx_base64)
            tx = Transaction.deserialize(tx_bytes)
            tx.sign(wallet)
            
            # Send transaction
            result = self.rpc_client.send_raw_transaction(
                tx.serialize(),
                opts=TxOpts(skip_preflight=True)
            )
            
            return result["result"]
            
        except Exception as e:
            logger.error(f"Swap execution failed: {e}")
            raise
    
    async def get_token_symbol(self, token_address: str) -> str:
        """Get token symbol from address (simplified)"""
        try:
            # In a real implementation, you would query token metadata
            # For now, return a simplified format
            return f"TOKEN_{token_address[:4].upper()}"
        except:
            return "UNKNOWN"
    
    async def notify_user(self, user_id: int, action: str, token_address: str, result: Dict):
        """Send trade notification to user via Telegram"""
        try:
            if result["status"] == "success":
                action_emoji = "🟢" if action == "buy" else "🔴"
                message = f"""
{action_emoji} **TRADE EXECUTED** {action_emoji}

**Action:** {action.upper()}
**Token:** `{token_address[:8]}...{token_address[-8:]}`
**Status:** ✅ SUCCESS
**TX:** `{result.get('tx_signature', 'N/A')[:8]}...`

**Amount:** {result.get('amount', 0) / 1e6:.4f}
**Time:** {datetime.now().strftime('%H:%M:%S')}
                """
            else:
                message = f"""
❌ **TRADE FAILED** ❌

**Action:** {action.upper()}
**Token:** `{token_address[:8]}...{token_address[-8:]}`
**Error:** {result.get('message', 'Unknown error')}
**Time:** {datetime.now().strftime('%H:%M:%S')}
                """
            
            # Send notification (would need to integrate with telegram bot instance)
            # await self.bot.send_message_to_user(user_id, message)
            logger.info(f"Trade notification for user {user_id}: {message}")
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

# Flask webhook endpoint
webhook_app = Flask(__name__)
trade_executor = None

@webhook_app.route("/webhook", methods=["POST"])
def tradingview_webhook():
    """Handle TradingView webhook"""
    try:
        # Verify the request (basic security)
        whitelisted_ips = ['52.89.214.238', '34.212.75.30', '54.218.53.128', '52.32.178.7']
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        if client_ip not in whitelisted_ips:
            return jsonify({'message': 'Unauthorized'}), 401
        
        data = request.get_json()
        
        # Verify security key (if configured)
        if data.get("key") != "YOUR_SECURITY_KEY":  # Replace with actual key
            return jsonify({'message': 'Unauthorized'}), 401
        
        # Process the alert asynchronously
        if trade_executor:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                trade_executor.process_tradingview_alert(data)
            )
            loop.close()
            
            return jsonify(result)
        else:
            return jsonify({'message': 'Trade executor not initialized'}), 500
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'message': 'Error processing webhook'}), 400

def initialize_webhook_handler(telegram_bot: TelegramTradingBot):
    """Initialize the webhook handler with telegram bot instance"""
    global trade_executor
    trade_executor = WebhookTradeExecutor(telegram_bot)

if __name__ == "__main__":
    # For testing the webhook endpoint
    webhook_app.run(host="0.0.0.0", port=8080, debug=True)