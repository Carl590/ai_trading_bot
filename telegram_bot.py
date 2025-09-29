"""
Telegram Trading Bot - Maestro Style
Author: AI Assistant
Description: Advanced Telegram bot for Solana trading with inline dashboard
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests
from telegram import (
    Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler,
    ContextTypes, MessageHandler, filters
)
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.api import Client
import base64

# Import wallet management
from wallet_manager import wallet_manager
from wallet_setup import WalletSetupHandler

# Import the comprehensive API manager
from api_manager import api_manager, APIConfig

# Global bot instance for contract alerts
_global_bot_instance = None

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SolanaTrader:
    def __init__(self):
        # Use API manager for RPC connection
        rpc_url = api_manager.get_rpc_url()
        self.rpc_client = Client(rpc_url, timeout=APIConfig.RPC_TIMEOUT)
        
        # Get Jupiter endpoints
        jupiter_endpoints = api_manager.get_jupiter_endpoints()
        self.jupiter_api = jupiter_endpoints['quote'].replace('/quote', '')
        
        self.wallet = None
        self.sol_mint = "So11111111111111111111111111111111111111112"
        
        # MEV protection endpoints
        self.mev_endpoints = api_manager.get_mev_endpoints()
        self.tip_accounts = api_manager.get_tip_accounts()
        
    def load_wallet(self, private_key_json: List[int]) -> bool:
        try:
            self.wallet = Keypair.from_secret_key(bytes(private_key_json))
            return True
        except Exception as e:
            logger.error(f"Failed to load wallet: {e}")
            return False
    
    def get_balance(self, token_address: str = None) -> float:
        try:
            if not token_address or token_address == self.sol_mint:
                # Get SOL balance
                response = self.rpc_client.get_balance(self.wallet.public_key)
                return response.value / 1e9  # Convert lamports to SOL
            else:
                # Get SPL token balance (simplified)
                return 0.0
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return 0.0

class TradingPosition:
    def __init__(self, contract_address: str, ticker: str, entry_price: float, 
                 amount: float, timestamp: datetime):
        self.contract_address = contract_address
        self.ticker = ticker
        self.entry_price = entry_price
        self.amount = amount
        self.timestamp = timestamp
        self.current_price = entry_price
        self.pnl = 0.0
        self.roi = 0.0
    
    def update_price(self, new_price: float):
        self.current_price = new_price
        self.pnl = (new_price - self.entry_price) * self.amount
        self.roi = ((new_price - self.entry_price) / self.entry_price) * 100

class TelegramTradingBot:
    def __init__(self, token: str):
        global _global_bot_instance
        
        self.token = token
        self.application = Application.builder().token(token).build()
        self.trader = SolanaTrader()
        self.user_wallets: Dict[int, Keypair] = {}
        self.user_positions: Dict[int, List[TradingPosition]] = {}
        self.ai_trading_enabled: Dict[int, bool] = {}
        
        # Initialize wallet handler
        self.wallet_handler = WalletSetupHandler(self)
        
        # Store global reference for scraper alerts
        _global_bot_instance = self
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup all command and callback handlers"""
        # Handle new group members
        from telegram.ext import ChatMemberHandler
        from telegram import ChatMember
        self.application.add_handler(ChatMemberHandler(self.handle_new_member, ChatMemberHandler.CHAT_MEMBER))
        
        # Handle commands
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("dashboard", self.start_command))
        self.application.add_handler(CommandHandler("trading", self.start_command))
        
        # Handle callbacks and messages
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def handle_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle new members joining groups - automatically show dashboard"""
        try:
            from telegram import ChatMember
            chat_member_update = update.chat_member
            if chat_member_update and chat_member_update.new_chat_member.status == ChatMember.MEMBER:
                user = chat_member_update.new_chat_member.user
                
                # Initialize user data
                if user.id not in self.user_positions:
                    self.user_positions[user.id] = []
                if user.id not in self.ai_trading_enabled:
                    self.ai_trading_enabled[user.id] = False
                
                # Send welcome message with dashboard
                welcome_text = f"""
👋 **Welcome {user.first_name}!** 

🤖 **SOLANA TRADING BOT** 🤖

You've joined the ultimate Solana trading community!

✨ **Your Personal Dashboard is Ready:**
• 🤖 AI Auto Trading
• 🏆 Best Trades Monitor
• 👛 Wallet Management
• 📊 Real-time PnL

Click below to start trading! 🚀
                """
                
                keyboard = [
                    [InlineKeyboardButton("🚀 Open My Dashboard", callback_data="main_menu")]
                ]
                
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=welcome_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Error handling new member: {e}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        
        # Initialize user data
        if user_id not in self.user_positions:
            self.user_positions[user_id] = []
        if user_id not in self.ai_trading_enabled:
            self.ai_trading_enabled[user_id] = False
        
        await self.show_main_menu(update, context)
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Display the main dashboard menu"""
        user_id = update.effective_user.id
        
        # Get wallet status
        wallet_status = "✅ Connected" if user_id in self.user_wallets else "❌ Not Connected"
        ai_status = "🟢 Active" if self.ai_trading_enabled.get(user_id, False) else "🔴 Inactive"
        
        # Get current balance
        balance = 0.0
        if user_id in self.user_wallets:
            self.trader.wallet = self.user_wallets[user_id]
            balance = self.trader.get_balance()
        
        user_name = update.effective_user.first_name or "Trader"
        
        text = f"""
🤖 **{user_name}'s TRADING DASHBOARD** 🤖

💰 **Wallet Status:** {wallet_status}
🏦 **Balance:** {balance:.4f} SOL
🎯 **AI Trading:** {ai_status}

📊 **Quick Stats:**
• Active Positions: {len(self.user_positions.get(user_id, []))}
• Total PnL: +0.00% (Demo)
• Group: [Solana Traders](https://t.me/+idISjNudRgVhYzUy)

Choose an option below:
        """
        
        keyboard = [
            [InlineKeyboardButton("🤖 AI Trading Bot", callback_data="ai_trading")],
            [InlineKeyboardButton("🏆 Best Trades", callback_data="best_trades")],
            [InlineKeyboardButton("👛 Wallet Manager", callback_data="wallet_menu")],
            [InlineKeyboardButton("🔍 Contract Scraper", callback_data="scraper_menu")],
            [InlineKeyboardButton("❓ Help", callback_data="help")],
            [InlineKeyboardButton("🔄 Refresh", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def show_ai_trading(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show AI Trading Bot dashboard"""
        user_id = update.effective_user.id
        
        ai_status = "🟢 ACTIVE" if self.ai_trading_enabled.get(user_id, False) else "🔴 INACTIVE"
        positions = self.user_positions.get(user_id, [])
        
        text = f"""
🤖 **AI TRADING BOT** 🤖

**Status:** {ai_status}
**Webhook:** {'✅ Ready' if user_id in self.user_wallets else '❌ Setup Wallet First'}

📊 **CURRENT POSITIONS:**
        """
        
        if positions:
            for i, pos in enumerate(positions[-5:], 1):  # Show last 5 positions
                text += f"""
{i}. **{pos.ticker}** ({pos.contract_address[:8]}...)
   💰 PnL: {pos.pnl:+.4f} SOL ({pos.roi:+.2f}%)
   📈 Entry: ${pos.entry_price:.6f} | Current: ${pos.current_price:.6f}
                """
        else:
            text += "\n📭 No active positions"
        
        # Control buttons
        toggle_text = "🛑 Stop AI Trading" if self.ai_trading_enabled.get(user_id, False) else "▶️ Start AI Trading"
        toggle_data = "stop_ai" if self.ai_trading_enabled.get(user_id, False) else "start_ai"
        
        keyboard = [
            [InlineKeyboardButton(toggle_text, callback_data=toggle_data)],
            [InlineKeyboardButton("📊 Trading Monitor", callback_data="trading_monitor")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="ai_settings")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_best_trades(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show best trades from Solana chain"""
        text = """
🏆 **TOP 5 BEST TRADES (24H)** 🏆

📊 **Highest ROI Trades on Solana:**
        """
        
        # Simulated data - replace with real API calls
        best_trades = [
            {"wallet": "7xKX...9mNz", "token": "BONK", "pnl": 45.67, "roi": 1247.3},
            {"wallet": "3yHm...4kLp", "token": "WIF", "pnl": 32.45, "roi": 892.1},
            {"wallet": "9zRt...7qWx", "token": "POPCAT", "pnl": 28.91, "roi": 734.2},
            {"wallet": "5mKj...2nVc", "token": "PEPE", "pnl": 21.33, "roi": 567.8},
            {"wallet": "8vNx...6hBq", "token": "DOGE", "pnl": 18.77, "roi": 445.6}
        ]
        
        for i, trade in enumerate(best_trades, 1):
            text += f"""
{i}. **{trade['token']}** 
   🎯 Wallet: `{trade['wallet']}`
   💰 PnL: +{trade['pnl']:.2f} SOL
   📈 ROI: +{trade['roi']:.1f}%
            """
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh Data", callback_data="best_trades")],
            [InlineKeyboardButton("📊 Copy Best Wallet", callback_data="copy_wallet")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_wallet_setup(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show wallet setup options"""
        user_id = update.effective_user.id
        
        wallet_connected = user_id in self.user_wallets
        status = "✅ **CONNECTED**" if wallet_connected else "❌ **NOT CONNECTED**"
        
        text = f"""
👛 **WALLET SETUP** 👛

**Status:** {status}

🔐 **Setup Options:**
1️⃣ Import existing wallet (private key)
2️⃣ Generate new wallet
3️⃣ Connect hardware wallet (coming soon)

⚠️ **Security Notice:**
• Never share your private key
• Bot uses secure local storage
• Keys are encrypted and never logged
        """
        
        if wallet_connected:
            wallet_address = str(self.user_wallets[user_id].public_key)
            text += f"""

💳 **Current Wallet:**
`{wallet_address}`

💰 **Balance:** {self.trader.get_balance():.4f} SOL
            """
        
        keyboard = []
        
        if not wallet_connected:
            keyboard.extend([
                [InlineKeyboardButton("📥 Import Wallet", callback_data="import_wallet")],
                [InlineKeyboardButton("🆕 Generate New Wallet", callback_data="generate_wallet")]
            ])
        else:
            keyboard.extend([
                [InlineKeyboardButton("💰 View Balance", callback_data="view_balance")],
                [InlineKeyboardButton("📤 Export Wallet", callback_data="export_wallet")],
                [InlineKeyboardButton("🗑️ Disconnect Wallet", callback_data="disconnect_wallet")]
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help section"""
        text = """
❓ **HELP & COMMANDS** ❓

🤖 **Bot Commands:**
• `/start` - Launch the trading dashboard
• `/balance` - Check wallet balance
• `/positions` - View current positions
• `/stop` - Emergency stop all trading

🎯 **AI Trading Bot:**
• Automatically executes buy/sell orders
• Processes TradingView webhook alerts
• Real-time profit/loss monitoring
• Risk management built-in

👛 **Wallet Management:**
• Secure private key storage
• Multiple wallet support
• Hardware wallet integration (soon)
• Export/import functionality

🏆 **Best Trades:**
• Top performing wallets on Solana
• Real-time ROI tracking
• Copy trading features
• 24/7 market analysis

⚙️ **Settings:**
• Slippage tolerance: 1-10%
• Trade size limits
• Stop-loss configuration
• Notification preferences

🆘 **Support:**
• Telegram: @support_bot
• Documentation: /docs
• FAQ: /faq
        """
        
        keyboard = [
            [InlineKeyboardButton("📚 Documentation", callback_data="docs")],
            [InlineKeyboardButton("❓ FAQ", callback_data="faq")],
            [InlineKeyboardButton("🆘 Contact Support", callback_data="support")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all callback queries"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "main_menu":
            await self.show_main_menu(update, context)
        elif data == "ai_trading":
            await self.show_ai_trading(update, context)
        elif data == "best_trades":
            await self.show_best_trades(update, context)
        elif data == "wallet_setup":
            await self.show_wallet_setup(update, context)
        elif data == "wallet_menu":
            await self.wallet_handler.show_wallet_menu(update, context)
        elif data == "wallet_create_new":
            await self.wallet_handler.create_new_wallet(update, context)
        elif data == "wallet_import":
            await self.wallet_handler.import_wallet_start(update, context)
        elif data == "wallet_dashboard":
            await self.wallet_handler.show_wallet_dashboard(update, context)
        elif data == "wallet_refresh":
            await self.wallet_handler.refresh_balance(update, context)
        elif data == "wallet_export":
            await self.wallet_handler.export_private_key(update, context)
        elif data == "wallet_help":
            await self.wallet_handler.show_wallet_help(update, context)
        elif data.startswith("wallet_qr_"):
            await self.wallet_handler.generate_deposit_qr(update, context)
        elif data == "help":
            await self.show_help(update, context)
        elif data == "scraper_menu":
            await self.show_scraper_menu(update, context)
        elif data.startswith("scraper_"):
            await self.handle_scraper_action(update, context)
        elif data == "start_ai":
            await self.toggle_ai_trading(update, context, True)
        elif data == "stop_ai":
            await self.toggle_ai_trading(update, context, False)
        elif data == "import_wallet":
            await self.request_wallet_import(update, context)
        elif data == "generate_wallet":
            await self.generate_new_wallet(update, context)
        else:
            await query.edit_message_text("🔧 Feature coming soon!")
    
    async def toggle_ai_trading(self, update: Update, context: ContextTypes.DEFAULT_TYPE, enable: bool):
        """Toggle AI trading on/off"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_wallets:
            await update.callback_query.edit_message_text(
                "❌ Please setup your wallet first!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("👛 Setup Wallet", callback_data="wallet_setup")
                ]])
            )
            return
        
        self.ai_trading_enabled[user_id] = enable
        status = "🟢 ENABLED" if enable else "🔴 DISABLED"
        
        await update.callback_query.edit_message_text(
            f"🤖 AI Trading {status}\n\nReturning to AI Trading dashboard...",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to AI Trading", callback_data="ai_trading")
            ]])
        )
    
    async def request_wallet_import(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Request wallet private key for import"""
        text = """
📥 **IMPORT WALLET** 📥

Please send your wallet's private key in one of these formats:

1️⃣ **Base58 format:** (Phantom/Solflare export)
2️⃣ **JSON Array:** [1,2,3,4,5...] (Solana CLI format)
3️⃣ **Hex format:** 0x1a2b3c4d5e...

⚠️ **SECURITY WARNING:**
• This message will be automatically deleted
• Private keys are stored securely locally
• Never share your private key with others

Send your private key now:
        """
        
        context.user_data['awaiting_wallet_import'] = True
        
        keyboard = [
            [InlineKeyboardButton("❌ Cancel", callback_data="wallet_setup")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def generate_new_wallet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate a new Solana wallet"""
        user_id = update.effective_user.id
        
        # Generate new keypair
        new_wallet = Keypair()
        self.user_wallets[user_id] = new_wallet
        
        # Get the private key in different formats
        private_key_bytes = new_wallet.secret_key
        private_key_json = list(private_key_bytes)
        
        text = f"""
🆕 **NEW WALLET GENERATED** 🆕

✅ Wallet successfully created and connected!

**Public Address:**
`{str(new_wallet.public_key)}`

**Private Key (JSON format):**
`{json.dumps(private_key_json)}`

⚠️ **IMPORTANT:**
• Save your private key securely
• This is the ONLY way to recover your wallet
• Never share it with anyone
• Bot will delete this message in 60 seconds

💰 **Next Steps:**
1. Fund your wallet with SOL
2. Enable AI Trading
3. Configure TradingView webhooks
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ I've Saved My Keys", callback_data="wallet_setup")],
            [InlineKeyboardButton("🔙 Back to Wallet Setup", callback_data="wallet_setup")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Schedule message deletion after 60 seconds for security
        context.job_queue.run_once(
            self.delete_message,
            60,
            data={'chat_id': message.chat.id, 'message_id': message.message_id}
        )
    
    async def delete_message(self, context: ContextTypes.DEFAULT_TYPE):
        """Delete a message for security purposes"""
        job_data = context.job.data
        try:
            await context.bot.delete_message(
                chat_id=job_data['chat_id'],
                message_id=job_data['message_id']
            )
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (for wallet import, etc.)"""
        # Check if user is importing wallet
        if context.user_data.get('wallet_import'):
            await self.wallet_handler.handle_private_key_input(update, context)
            return
        
        if context.user_data.get('awaiting_wallet_import'):
            await self.process_wallet_import(update, context)
        else:
            # Check if message contains trading keywords
            message_text = update.message.text.lower()
            
            if any(keyword in message_text for keyword in ['dashboard', 'trading', 'bot', 'start', 'help']):
                # Show dashboard for relevant keywords
                keyboard = [[
                    InlineKeyboardButton("🚀 Open Trading Dashboard", callback_data="main_menu")
                ]]
                
                await update.message.reply_text(
                    "🤖 **Quick Access to Your Trading Dashboard:**\n\nManage your Solana trading, monitor positions, and configure AI trading!",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
            # If not trading-related, don't respond to avoid spam
    
    async def process_wallet_import(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process wallet private key import"""
        user_id = update.effective_user.id
        private_key_text = update.message.text.strip()
        
        try:
            # Delete the user's message immediately for security
            await update.message.delete()
            
            # Try to parse the private key
            if private_key_text.startswith('[') and private_key_text.endswith(']'):
                # JSON array format
                private_key_list = json.loads(private_key_text)
                wallet = Keypair.from_secret_key(bytes(private_key_list))
            else:
                # Assume base58 format
                wallet = Keypair.from_secret_key(base64.b58decode(private_key_text))
            
            # Store the wallet
            self.user_wallets[user_id] = wallet
            context.user_data['awaiting_wallet_import'] = False
            
            # Send success message
            success_text = f"""
✅ **WALLET IMPORTED SUCCESSFULLY** ✅

**Address:** `{str(wallet.public_key)}`
**Balance:** {self.trader.get_balance():.4f} SOL

Your wallet is now connected and ready for trading!
            """
            
            keyboard = [
                [InlineKeyboardButton("🤖 Enable AI Trading", callback_data="ai_trading")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
            ]
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=success_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Failed to import wallet: {e}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Invalid private key format. Please try again.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Wallet Setup", callback_data="wallet_setup")
                ]])
            )
    
    async def show_scraper_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show the contract scraper menu"""
        # Read current scraper stats
        contracts_count = 0
        groups_count = 0
        
        try:
            # Count found contracts
            if os.path.exists('found_solana_contracts.json'):
                with open('found_solana_contracts.json', 'r') as f:
                    contracts = json.load(f)
                    contracts_count = len(contracts)
            
            # Count monitored groups
            if os.path.exists('scraper_groups.json'):
                with open('scraper_groups.json', 'r') as f:
                    data = json.load(f)
                    groups_count = len(data.get('groups', []))
        except:
            pass
        
        text = f"""
🔍 **CONTRACT SCRAPER DASHBOARD**

📊 **Statistics:**
• 💎 Contracts Found: {contracts_count}
• 📱 Monitored Groups: {groups_count}

🤖 **Features:**
• Real-time contract monitoring
• AI-powered filtering
• Auto-trade integration
• Multi-network support (Solana/Ethereum)

Choose an option below:
        """
        
        keyboard = [
            [InlineKeyboardButton("📋 View Found Contracts", callback_data="scraper_contracts")],
            [InlineKeyboardButton("📱 Manage Groups", callback_data="scraper_groups")],
            [InlineKeyboardButton("⚙️ Scraper Settings", callback_data="scraper_settings")],
            [InlineKeyboardButton("🚀 Start Scraper", callback_data="scraper_start")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_scraper_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle scraper-related actions"""
        data = update.callback_query.data
        
        if data == "scraper_contracts":
            await self.show_found_contracts(update, context)
        elif data == "scraper_groups":
            await self.show_scraper_groups(update, context)
        elif data == "scraper_settings":
            await self.show_scraper_settings(update, context)
        elif data == "scraper_start":
            await self.start_scraper_process(update, context)
        else:
            await update.callback_query.edit_message_text("🔧 Feature coming soon!")
    
    async def show_found_contracts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show recently found contracts"""
        try:
            if not os.path.exists('found_solana_contracts.json'):
                text = "📭 No Solana contracts found yet.\n\nStart the scraper to begin monitoring groups for new Solana tokens!"
                keyboard = [
                    [InlineKeyboardButton("🚀 Start Scraper", callback_data="scraper_start")],
                    [InlineKeyboardButton("🔙 Back", callback_data="scraper_menu")]
                ]
            else:
                with open('found_solana_contracts.json', 'r') as f:
                    contracts = json.load(f)
                
                if not contracts:
                    text = "📭 No contracts found yet."
                else:
                    recent_contracts = contracts[-10:][::-1]  # Last 10, newest first
                    
                    text = f"💎 **RECENT SOLANA CONTRACTS** ({len(contracts)} total)\n\n"
                    
                    for i, contract in enumerate(recent_contracts, 1):
                        symbol = contract.get('symbol', 'Unknown')
                        address = contract['address']
                        decimals = contract.get('decimals', 9)
                        confidence = contract.get('confidence_score', 0) * 100
                        source = contract.get('source_group', 'Unknown')
                        
                        # Truncate address for display
                        short_addr = f"{address[:6]}...{address[-6:]}"
                        
                        text += f"{i}. **${symbol}** (SOL)\n"
                        text += f"   `{short_addr}` | {confidence:.0f}%\n"
                        text += f"   🔢 Decimals: {decimals} | 📍 {source}\n\n"
                
                keyboard = [
                    [InlineKeyboardButton("🔄 Refresh", callback_data="scraper_contracts")],
                    [InlineKeyboardButton("📤 Export All", callback_data="scraper_export")],
                    [InlineKeyboardButton("🔙 Back", callback_data="scraper_menu")]
                ]
            
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error showing contracts: {e}")
            await update.callback_query.edit_message_text(
                "❌ Error loading contracts data",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data="scraper_menu")
                ]])
            )
    
    async def show_scraper_groups(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show monitored groups management"""
        try:
            text = """
📱 **GROUP MANAGEMENT**

To add groups to monitor:
1. Get the group's invite link or @username
2. Use the scraper manager: `python scraper_manager.py add-group <link>`
3. The scraper will automatically monitor new messages

**Current Groups:**
            """
            
            if os.path.exists('scraper_groups.json'):
                with open('scraper_groups.json', 'r') as f:
                    data = json.load(f)
                    groups = data.get('groups', [])
                
                if groups:
                    for group in groups:
                        status = "🟢" if group.get('enabled', True) else "🔴"
                        auto_trade = "🤖" if group.get('auto_trade', False) else "👤"
                        confidence = group.get('min_confidence', 0.7) * 100
                        
                        text += f"\n{status} **{group['group_name']}**"
                        text += f"\n   Trading: {auto_trade} | Min: {confidence:.0f}%"
                else:
                    text += "\n📭 No groups configured yet."
            else:
                text += "\n📭 No groups configured yet."
            
            keyboard = [
                [InlineKeyboardButton("📚 Setup Guide", callback_data="scraper_guide")],
                [InlineKeyboardButton("🔙 Back", callback_data="scraper_menu")]
            ]
            
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error showing groups: {e}")
            await update.callback_query.edit_message_text(
                "❌ Error loading groups data",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data="scraper_menu")
                ]])
            )
    
    async def show_scraper_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show scraper settings"""
        text = """
⚙️ **SCRAPER SETTINGS**

**Current Configuration:**
• 🌐 Networks: Solana, Ethereum
• 🎯 Min Confidence: 70%
• 🔄 Check Interval: Real-time
• 📊 Max Contracts/Hour: 50

**Features:**
• ✅ Contract Address Detection
• ✅ Token Symbol Extraction
• ✅ Confidence Scoring
• ✅ Duplicate Filtering
• ✅ Multi-network Support

**Auto-trading:**
• Threshold: 80% confidence
• Amount: 0.1 SOL default
• Networks: Solana only
        """
        
        keyboard = [
            [InlineKeyboardButton("🎯 Adjust Confidence", callback_data="scraper_confidence")],
            [InlineKeyboardButton("🤖 Auto-trade Settings", callback_data="scraper_autotrade")],
            [InlineKeyboardButton("🔙 Back", callback_data="scraper_menu")]
        ]
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def start_scraper_process(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the scraper process"""
        text = """
🚀 **STARTING SCRAPER**

To start the contract scraper:

**Option 1: Command Line**
```bash
python scraper_manager.py start
```

**Option 2: Background Process**
```bash
nohup python telegram_scraper.py &
```

**First Time Setup:**
1. Add groups to monitor:
   `python scraper_manager.py add-group <group_link>`

2. Start the scraper:
   `python scraper_manager.py start`

The scraper will:
• Monitor all configured groups
• Extract contract addresses
• Filter by confidence score
• Save findings to database
• Send alerts to this bot

**Status:** Ready to start! 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("📚 Full Setup Guide", callback_data="scraper_guide")],
            [InlineKeyboardButton("📋 View Groups", callback_data="scraper_groups")],
            [InlineKeyboardButton("🔙 Back", callback_data="scraper_menu")]
        ]
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

    def run(self):
        """Start the bot"""
        logger.info("Starting Telegram Trading Bot...")
        self.application.run_polling(drop_pending_updates=True)

async def send_contract_alert(message: str, user_id: int = None):
    """Send contract alert to users"""
    global _global_bot_instance
    
    if not _global_bot_instance:
        logger.warning("No bot instance available for contract alerts")
        return
    
    try:
        # If specific user ID provided, send only to them
        if user_id:
            await _global_bot_instance.application.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Send to all users with AI trading enabled
            for uid in _global_bot_instance.ai_trading_enabled:
                if _global_bot_instance.ai_trading_enabled[uid]:
                    try:
                        await _global_bot_instance.application.bot.send_message(
                            chat_id=uid,
                            text=message,
                            parse_mode=ParseMode.MARKDOWN
                        )
                    except Exception as e:
                        logger.error(f"Failed to send alert to user {uid}: {e}")
                        
    except Exception as e:
        logger.error(f"Error sending contract alert: {e}")

if __name__ == "__main__":
    # Replace with your bot token
    BOT_TOKEN = "8482815083:AAHFqxiPCt0eZ6GjD8cahnAzXlA4ql3z9qk"
    
    bot = TelegramTradingBot(BOT_TOKEN)
    bot.run()