"""
Telegram Group Trading Bot
Automatically shows dashboard when users join the group
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List

from telegram import (
    Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update, ChatMember
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler,
    ContextTypes, MessageHandler, filters, ChatMemberHandler
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class GroupTradingBot:
    def __init__(self, token: str, group_chat_id: str):
        self.token = token
        self.group_chat_id = group_chat_id
        self.application = Application.builder().token(token).build()
        
        # Store user sessions for the group
        self.user_sessions: Dict[int, Dict] = {}
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup all handlers for group interactions"""
        # Handle new group members
        self.application.add_handler(ChatMemberHandler(self.handle_new_member, ChatMemberHandler.CHAT_MEMBER))
        
        # Handle commands
        self.application.add_handler(CommandHandler("start", self.show_dashboard))
        self.application.add_handler(CommandHandler("dashboard", self.show_dashboard))
        self.application.add_handler(CommandHandler("trading", self.show_dashboard))
        
        # Handle callback queries (button presses)
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Handle text messages in group
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_group_message))
    
    async def handle_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle new members joining the group"""
        try:
            # Check if this is our target group
            if str(update.effective_chat.id) != self.group_chat_id.replace('@', '').replace('https://t.me/', ''):
                return
            
            chat_member_update = update.chat_member
            if chat_member_update.new_chat_member.status == ChatMember.MEMBER:
                user = chat_member_update.new_chat_member.user
                
                # Welcome the new user and show dashboard
                welcome_text = f"""
👋 **Welcome {user.first_name}!** 

🤖 **SOLANA TRADING BOT GROUP** 🤖

You've joined the ultimate Solana trading community! Here's what you can do:

✨ **Features Available:**
• 🤖 AI Auto Trading Bot
• 🏆 Best Trades Monitor  
• 👛 Wallet Management
• 📊 Real-time PnL Tracking
• 🔗 TradingView Integration

Click below to access your personal trading dashboard:
                """
                
                keyboard = [
                    [InlineKeyboardButton("🚀 Open Trading Dashboard", callback_data=f"dashboard_{user.id}")],
                    [InlineKeyboardButton("🏆 Best Trades", callback_data=f"best_trades_{user.id}")],
                    [InlineKeyboardButton("❓ Help & Guide", callback_data=f"help_{user.id}")]
                ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=welcome_text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
                
        except Exception as e:
            logger.error(f"Error handling new member: {e}")
    
    async def show_dashboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show the main trading dashboard"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        # Initialize user session if not exists
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'wallet_connected': False,
                'ai_trading_enabled': False,
                'balance': 0.0,
                'positions': []
            }
        
        session = self.user_sessions[user_id]
        
        # Dashboard content
        wallet_status = "✅ Connected" if session['wallet_connected'] else "❌ Not Connected"
        ai_status = "🟢 Active" if session['ai_trading_enabled'] else "🔴 Inactive"
        
        dashboard_text = f"""
🤖 **{user_name}'s TRADING DASHBOARD** 🤖

💰 **Wallet Status:** {wallet_status}
🏦 **Balance:** {session['balance']:.4f} SOL
🎯 **AI Trading:** {ai_status}
📊 **Active Positions:** {len(session['positions'])}

🚀 **Quick Stats:**
• Total PnL: +0.00% (Demo)
• Today's Trades: 0
• Win Rate: 0%

⚡ **Ready to start trading on Solana!**

Choose your action below:
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🤖 AI Trading", callback_data=f"ai_trading_{user_id}"),
                InlineKeyboardButton("🏆 Best Trades", callback_data=f"best_trades_{user_id}")
            ],
            [
                InlineKeyboardButton("👛 Wallet Setup", callback_data=f"wallet_{user_id}"),
                InlineKeyboardButton("📊 My Positions", callback_data=f"positions_{user_id}")
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data=f"settings_{user_id}"),
                InlineKeyboardButton("❓ Help", callback_data=f"help_{user_id}")
            ],
            [InlineKeyboardButton("🔄 Refresh Dashboard", callback_data=f"dashboard_{user_id}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=dashboard_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                text=dashboard_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def show_ai_trading(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Show AI Trading interface"""
        session = self.user_sessions.get(user_id, {})
        
        ai_status = "🟢 ACTIVE" if session.get('ai_trading_enabled', False) else "🔴 INACTIVE"
        
        text = f"""
🤖 **AI TRADING BOT** 🤖

**Status:** {ai_status}
**Webhook:** {'✅ Ready' if session.get('wallet_connected', False) else '❌ Setup Wallet First'}

📊 **HOW IT WORKS:**
1. Connect your TradingView alerts
2. Bot receives buy/sell signals
3. Automatically executes trades
4. Real-time PnL tracking

⚡ **Features:**
• Jupiter Aggregator Integration
• Risk Management Controls
• Real-time Notifications
• Profit/Loss Tracking

📈 **Performance:**
• Total Trades: 0
• Success Rate: 0%
• Best Trade: N/A
        """
        
        if not session.get('wallet_connected', False):
            keyboard = [
                [InlineKeyboardButton("👛 Setup Wallet First", callback_data=f"wallet_{user_id}")],
                [InlineKeyboardButton("🔙 Back to Dashboard", callback_data=f"dashboard_{user_id}")]
            ]
        else:
            toggle_text = "🛑 Stop AI Trading" if session.get('ai_trading_enabled', False) else "▶️ Start AI Trading"
            toggle_data = f"stop_ai_{user_id}" if session.get('ai_trading_enabled', False) else f"start_ai_{user_id}"
            
            keyboard = [
                [InlineKeyboardButton(toggle_text, callback_data=toggle_data)],
                [InlineKeyboardButton("⚙️ Trading Settings", callback_data=f"ai_settings_{user_id}")],
                [InlineKeyboardButton("📊 View Positions", callback_data=f"positions_{user_id}")],
                [InlineKeyboardButton("🔙 Back to Dashboard", callback_data=f"dashboard_{user_id}")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_best_trades(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Show best trades from Solana"""
        text = f"""
🏆 **TOP SOLANA TRADES (24H)** 🏆

📊 **Highest ROI Performers:**

1. **BONK** 🔥
   🎯 Wallet: `7xKX...9mNz`
   💰 PnL: +45.67 SOL
   📈 ROI: +1,247.3%

2. **WIF** ⚡
   🎯 Wallet: `3yHm...4kLp`  
   💰 PnL: +32.45 SOL
   📈 ROI: +892.1%

3. **POPCAT** 🚀
   🎯 Wallet: `9zRt...7qWx`
   💰 PnL: +28.91 SOL
   📈 ROI: +734.2%

4. **PEPE** 💎
   🎯 Wallet: `5mKj...2nVc`
   💰 PnL: +21.33 SOL
   📈 ROI: +567.8%

5. **DOGE** ⭐
   🎯 Wallet: `8vNx...6hBq`
   💰 PnL: +18.77 SOL
   📈 ROI: +445.6%

🔄 **Updated:** {datetime.now().strftime('%H:%M:%S')}
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh Data", callback_data=f"best_trades_{user_id}")],
            [InlineKeyboardButton("📊 Copy Strategy", callback_data=f"copy_wallet_{user_id}")],
            [InlineKeyboardButton("🔙 Back to Dashboard", callback_data=f"dashboard_{user_id}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_wallet_setup(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Show wallet setup interface"""
        session = self.user_sessions.get(user_id, {})
        
        wallet_connected = session.get('wallet_connected', False)
        status = "✅ **CONNECTED**" if wallet_connected else "❌ **NOT CONNECTED**"
        
        text = f"""
👛 **WALLET SETUP** 👛

**Status:** {status}

🔐 **Setup Your Solana Wallet:**

**Option 1:** Generate New Wallet
• Creates a brand new Solana wallet
• Gives you full private key control
• Ready for immediate use

**Option 2:** Import Existing Wallet
• Use your existing Solana wallet
• Support for Phantom, Solflare formats
• Keeps your current funds

⚠️ **Security Notice:**
• Private keys stored locally only
• Never shared or transmitted
• You maintain full control
        """
        
        if not wallet_connected:
            keyboard = [
                [InlineKeyboardButton("🆕 Generate New Wallet", callback_data=f"generate_wallet_{user_id}")],
                [InlineKeyboardButton("📥 Import Existing Wallet", callback_data=f"import_wallet_{user_id}")],
                [InlineKeyboardButton("❓ Wallet Help", callback_data=f"wallet_help_{user_id}")],
                [InlineKeyboardButton("🔙 Back to Dashboard", callback_data=f"dashboard_{user_id}")]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("💰 View Balance", callback_data=f"balance_{user_id}")],
                [InlineKeyboardButton("📤 Export Wallet", callback_data=f"export_wallet_{user_id}")],
                [InlineKeyboardButton("🗑️ Disconnect", callback_data=f"disconnect_{user_id}")],
                [InlineKeyboardButton("🔙 Back to Dashboard", callback_data=f"dashboard_{user_id}")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Show help information"""
        text = f"""
❓ **HELP & COMMANDS** ❓

🤖 **Getting Started:**
1. Setup your Solana wallet
2. Fund wallet with SOL
3. Enable AI Trading
4. Configure TradingView alerts
5. Start earning! 💰

🎯 **Commands:**
• `/dashboard` - Open trading dashboard
• `/start` - Show welcome message  
• `/trading` - Quick access to AI trading

🔗 **TradingView Setup:**
**Webhook URL:** `your-server:8080/webhook`
**Alert Format:**
```json
{{
  "key": "trading-bot-secure-key-2025",
  "user_id": {user_id},
  "msg": "buy TOKEN_ADDRESS_HERE"
}}
```

🛡️ **Risk Management:**
• Start with small amounts
• Set stop-loss limits
• Monitor positions regularly
• Never invest more than you can afford

💬 **Support:**
Need help? Ask in the group chat!
Our community is here to help! 🚀

📚 **Resources:**
• Solana Trading Guide
• TradingView Integration
• Wallet Security Tips
        """
        
        keyboard = [
            [InlineKeyboardButton("🎯 TradingView Guide", callback_data=f"tv_guide_{user_id}")],
            [InlineKeyboardButton("🛡️ Security Tips", callback_data=f"security_{user_id}")],
            [InlineKeyboardButton("💬 Ask Community", url="https://t.me/+idISjNudRgVhYzUy")],
            [InlineKeyboardButton("🔙 Back to Dashboard", callback_data=f"dashboard_{user_id}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        try:
            # Parse callback data
            if '_' in data:
                action, user_id_str = data.rsplit('_', 1)
                user_id = int(user_id_str)
            else:
                user_id = update.effective_user.id
                action = data
            
            # Route to appropriate handler
            if action == "dashboard":
                await self.show_dashboard(update, context)
            elif action == "ai_trading":
                await self.show_ai_trading(update, context, user_id)
            elif action == "best_trades":
                await self.show_best_trades(update, context, user_id)
            elif action == "wallet":
                await self.show_wallet_setup(update, context, user_id)
            elif action == "help":
                await self.show_help(update, context, user_id)
            elif action == "start_ai":
                await self.toggle_ai_trading(update, context, user_id, True)
            elif action == "stop_ai":
                await self.toggle_ai_trading(update, context, user_id, False)
            elif action in ["generate_wallet", "import_wallet", "balance", "export_wallet"]:
                await self.handle_wallet_action(update, context, user_id, action)
            else:
                await query.edit_message_text("🔧 Feature coming soon! Stay tuned...")
                
        except Exception as e:
            logger.error(f"Callback error: {e}")
            await query.edit_message_text("❌ An error occurred. Please try again.")
    
    async def toggle_ai_trading(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, enable: bool):
        """Toggle AI trading on/off"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {}
        
        session = self.user_sessions[user_id]
        
        if not session.get('wallet_connected', False):
            await update.callback_query.edit_message_text(
                "❌ **Wallet Required**\n\nPlease setup your wallet first before enabling AI trading.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("👛 Setup Wallet", callback_data=f"wallet_{user_id}"),
                    InlineKeyboardButton("🔙 Back", callback_data=f"dashboard_{user_id}")
                ]]),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        session['ai_trading_enabled'] = enable
        status = "🟢 **ENABLED**" if enable else "🔴 **DISABLED**"
        
        text = f"""
🤖 **AI Trading {status}**

{'🚀 Your bot is now actively monitoring TradingView alerts!' if enable else '⏸️ AI Trading has been paused.'}

**Next Steps:**
{'• Configure TradingView webhooks' if enable else '• Click "Start AI Trading" when ready'}
{'• Send test alerts to verify setup' if enable else '• Monitor your existing positions'}
{'• Start with small amounts' if enable else '• Review your trading strategy'}

**Status:** Ready for {'automated trading!' if enable else 'manual control.'}
        """
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to AI Trading", callback_data=f"ai_trading_{user_id}")],
            [InlineKeyboardButton("🏠 Dashboard", callback_data=f"dashboard_{user_id}")]
        ]
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_wallet_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, action: str):
        """Handle wallet-related actions"""
        if action == "generate_wallet":
            # Simulate wallet generation
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = {}
            
            self.user_sessions[user_id]['wallet_connected'] = True
            self.user_sessions[user_id]['balance'] = 0.0
            
            text = """
✅ **NEW WALLET GENERATED**

**Address:** `GxU7...h8Kp` (Demo)
**Private Key:** `[Generated - Save Securely]`

⚠️ **IMPORTANT:**
• Save your private key safely
• Never share it with anyone
• This is your only recovery method

💰 **Next Steps:**
1. Fund your wallet with SOL
2. Enable AI Trading
3. Configure TradingView alerts
            """
            
            keyboard = [
                [InlineKeyboardButton("✅ I Saved My Keys", callback_data=f"wallet_{user_id}")],
                [InlineKeyboardButton("🤖 Enable AI Trading", callback_data=f"ai_trading_{user_id}")]
            ]
        
        elif action == "balance":
            balance = self.user_sessions.get(user_id, {}).get('balance', 0.0)
            text = f"""
💰 **WALLET BALANCE**

**SOL Balance:** {balance:.4f} SOL
**USD Value:** ${balance * 140:.2f}

**Token Holdings:**
• No tokens detected

**Recent Activity:**
• No recent transactions
            """
            
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data=f"balance_{user_id}")],
                [InlineKeyboardButton("🔙 Back to Wallet", callback_data=f"wallet_{user_id}")]
            ]
        
        else:
            text = "🔧 Feature coming soon!"
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data=f"wallet_{user_id}")]]
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_group_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages in the group"""
        # You can add logic here to respond to specific keywords
        # or provide quick access to dashboard
        
        message_text = update.message.text.lower()
        
        if any(keyword in message_text for keyword in ['dashboard', 'trading', 'bot', 'help']):
            keyboard = [
                [InlineKeyboardButton("🚀 Open Trading Dashboard", 
                                    callback_data=f"dashboard_{update.effective_user.id}")]
            ]
            
            await update.message.reply_text(
                "🤖 Quick access to your trading dashboard:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    def run(self):
        """Start the group bot"""
        logger.info("Starting Group Trading Bot...")
        self.application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    # Configuration
    BOT_TOKEN = "8482815083:AAHFqxiPCt0eZ6GjD8cahnAzXlA4ql3z9qk"
    GROUP_CHAT_ID = "https://t.me/+idISjNudRgVhYzUy"  # Your group link
    
    # Create and start the group bot
    group_bot = GroupTradingBot(BOT_TOKEN, GROUP_CHAT_ID)
    group_bot.run()