"""
Wallet Setup Integration for Telegram Bot
Maestro-style wallet management interface
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import logging
from wallet_manager import wallet_manager
import qrcode
import io
import base64

logger = logging.getLogger(__name__)

class WalletSetupHandler:
    """Handle wallet setup and management through Telegram"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
    
    async def show_wallet_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main wallet management menu"""
        user_id = str(update.effective_user.id)
        
        # Check if user has a wallet
        wallet_info = wallet_manager.get_user_wallet(user_id)
        
        if wallet_info:
            # User has wallet - show wallet dashboard
            await self.show_wallet_dashboard(update, context)
        else:
            # No wallet - show setup options
            await self.show_wallet_setup_options(update, context)
    
    async def show_wallet_setup_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show wallet setup options for new users"""
        text = """
🔐 **WALLET SETUP**

Choose how you want to set up your trading wallet:

**🆕 Create New Wallet**
• Generate a fresh Solana wallet
• Get backup phrase for recovery
• Recommended for new users

**📥 Import Existing Wallet**
• Use your existing Solana wallet
• Import via private key
• Keep your current funds

**⚠️ Security Notice:**
Your private keys are encrypted and stored securely. Never share your private key with anyone!
        """
        
        keyboard = [
            [InlineKeyboardButton("🆕 Create New Wallet", callback_data="wallet_create_new")],
            [InlineKeyboardButton("📥 Import Existing Wallet", callback_data="wallet_import")],
            [InlineKeyboardButton("❓ Wallet Help", callback_data="wallet_help")],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
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
    
    async def show_wallet_dashboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show wallet dashboard for existing users"""
        user_id = str(update.effective_user.id)
        wallet_info = wallet_manager.get_user_wallet(user_id)
        
        if not wallet_info:
            await self.show_wallet_setup_options(update, context)
            return
        
        # Get current balance
        try:
            balance = await wallet_manager.get_wallet_balance(user_id)
        except:
            balance = 0.0
        
        # Format wallet address for display
        address = wallet_info.wallet_address
        short_address = f"{address[:8]}...{address[-8:]}"
        
        text = f"""
💼 **YOUR WALLET**

**{wallet_info.wallet_name}**
`{address}`

💰 **Balance:** {balance:.4f} SOL
📊 **Trades:** {wallet_info.total_trades}
📅 **Created:** {wallet_info.created_at[:10]}

**🔐 Security Status:** ✅ Encrypted
**📱 Status:** {'🟢 Active' if wallet_info.is_active else '🔴 Inactive'}
        """
        
        keyboard = [
            [
                InlineKeyboardButton("💰 Refresh Balance", callback_data="wallet_refresh"),
                InlineKeyboardButton("📤 Deposit", callback_data="wallet_deposit")
            ],
            [
                InlineKeyboardButton("🔄 Trade History", callback_data="wallet_history"),
                InlineKeyboardButton("⚙️ Settings", callback_data="wallet_settings")
            ],
            [
                InlineKeyboardButton("🔑 Export Private Key", callback_data="wallet_export"),
                InlineKeyboardButton("❌ Delete Wallet", callback_data="wallet_delete_confirm")
            ],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
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
    
    async def create_new_wallet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create a new wallet for the user"""
        user_id = str(update.effective_user.id)
        
        # Check if user already has a wallet
        if wallet_manager.get_user_wallet(user_id):
            await update.callback_query.answer("You already have a wallet configured!")
            return
        
        try:
            # Create new wallet
            address, backup_phrase = wallet_manager.create_new_wallet(user_id)
            
            # Show success message with backup info
            text = f"""
✅ **WALLET CREATED SUCCESSFULLY!**

**🏦 Wallet Address:**
`{address}`

**🔑 Backup Information:**
⚠️ **IMPORTANT:** Save this backup securely!

`{backup_phrase}`

**Next Steps:**
1. Copy your wallet address
2. Send SOL to this address to fund your wallet
3. Start trading with the AI bot!

**🔐 Security:**
• Your private key is encrypted and stored securely
• Never share your backup phrase with anyone
• This message will be deleted in 5 minutes for security
            """
            
            keyboard = [
                [InlineKeyboardButton("💰 View Wallet Dashboard", callback_data="wallet_dashboard")],
                [InlineKeyboardButton("📤 Get Deposit QR Code", callback_data=f"wallet_qr_{address}")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Schedule message deletion for security
            context.job_queue.run_once(
                self.delete_sensitive_message,
                300,  # 5 minutes
                data={
                    'chat_id': update.effective_chat.id,
                    'message_id': update.callback_query.message.message_id
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating wallet: {e}")
            await update.callback_query.edit_message_text(
                "❌ Error creating wallet. Please try again later.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data="wallet_menu")
                ]])
            )
    
    async def import_wallet_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start wallet import process"""
        text = """
📥 **IMPORT EXISTING WALLET**

Send your private key in one of these formats:

**🔢 Array Format:**
`[123,45,67,89,...]`

**🔤 Hex Format:**
`abcd1234ef567890...`

**📝 Base58 Format:**
`5Kb8kLf4o7K...`

**⚠️ Security:**
• Your message will be deleted immediately
• Private key will be encrypted and stored securely
• Never share your private key publicly

**Send your private key now:**
        """
        
        keyboard = [
            [InlineKeyboardButton("❌ Cancel Import", callback_data="wallet_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Set conversation state
        context.user_data['wallet_import'] = True
    
    async def handle_private_key_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle private key input for import"""
        if not context.user_data.get('wallet_import'):
            return
        
        user_id = str(update.effective_user.id)
        private_key = update.message.text.strip()
        
        # Delete the message immediately for security
        try:
            await update.message.delete()
        except:
            pass
        
        try:
            # Import the wallet
            address = wallet_manager.import_wallet(user_id, private_key)
            
            # Clear import state
            context.user_data['wallet_import'] = False
            
            # Show success message
            text = f"""
✅ **WALLET IMPORTED SUCCESSFULLY!**

**🏦 Wallet Address:**
`{address}`

Your wallet is now ready for trading with the AI bot!

**🔐 Security:**
• Your private key has been encrypted and stored securely
• Original private key has been deleted from memory
• You can now use this wallet for all trading operations
            """
            
            keyboard = [
                [InlineKeyboardButton("💰 View Wallet Dashboard", callback_data="wallet_dashboard")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send success message
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error importing wallet: {e}")
            
            # Clear import state
            context.user_data['wallet_import'] = False
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Error importing wallet. Please check your private key format and try again.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄 Try Again", callback_data="wallet_import"),
                    InlineKeyboardButton("🔙 Back", callback_data="wallet_menu")
                ]])
            )
    
    async def generate_deposit_qr(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate QR code for wallet deposit"""
        callback_data = update.callback_query.data
        
        if callback_data.startswith("wallet_qr_"):
            address = callback_data[10:]  # Remove "wallet_qr_" prefix
            
            try:
                # Generate QR code
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(address)
                qr.make(fit=True)
                
                # Create QR code image
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Convert to bytes
                bio = io.BytesIO()
                img.save(bio, 'PNG')
                bio.seek(0)
                
                # Send QR code
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=bio,
                    caption=f"""
💰 **DEPOSIT TO YOUR WALLET**

**Address:** `{address}`

Scan this QR code or copy the address above to deposit SOL to your trading wallet.

**⚠️ Important:**
• Only send SOL to this address
• Minimum deposit: 0.01 SOL
• Funds will be available immediately
                    """,
                    parse_mode=ParseMode.MARKDOWN
                )
                
            except Exception as e:
                logger.error(f"Error generating QR code: {e}")
                await update.callback_query.answer("Error generating QR code")
    
    async def export_private_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Export user's private key"""
        user_id = str(update.effective_user.id)
        
        try:
            # Export in array format (most compatible)
            private_key = wallet_manager.export_private_key(user_id, "array")
            
            if private_key:
                text = f"""
🔑 **PRIVATE KEY EXPORT**

**⚠️ CRITICAL SECURITY WARNING:**
• Never share this private key with anyone
• Store it in a secure location
• This message will be deleted in 2 minutes

**Your Private Key:**
`{private_key}`

**Alternative Formats:**
                """
                
                # Also provide hex format
                hex_key = wallet_manager.export_private_key(user_id, "hex")
                if hex_key:
                    text += f"\n**Hex:** `{hex_key}`"
                
                keyboard = [
                    [InlineKeyboardButton("✅ I've Saved It Securely", callback_data="wallet_dashboard")]
                ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                message = await update.callback_query.edit_message_text(
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
                
                # Schedule deletion for security
                context.job_queue.run_once(
                    self.delete_sensitive_message,
                    120,  # 2 minutes
                    data={
                        'chat_id': update.effective_chat.id,
                        'message_id': message.message_id
                    }
                )
                
            else:
                await update.callback_query.answer("Error exporting private key")
                
        except Exception as e:
            logger.error(f"Error exporting private key: {e}")
            await update.callback_query.answer("Error exporting private key")
    
    async def delete_sensitive_message(self, context: ContextTypes.DEFAULT_TYPE):
        """Delete sensitive messages for security"""
        job_data = context.job.data
        try:
            await context.bot.delete_message(
                chat_id=job_data['chat_id'],
                message_id=job_data['message_id']
            )
        except:
            # Message might already be deleted
            pass
    
    async def refresh_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Refresh wallet balance"""
        user_id = str(update.effective_user.id)
        
        try:
            balance = await wallet_manager.get_wallet_balance(user_id)
            await update.callback_query.answer(f"Balance updated: {balance:.4f} SOL")
            
            # Refresh dashboard
            await self.show_wallet_dashboard(update, context)
            
        except Exception as e:
            logger.error(f"Error refreshing balance: {e}")
            await update.callback_query.answer("Error refreshing balance")
    
    async def show_wallet_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show wallet help information"""
        text = """
❓ **WALLET HELP**

**🔐 What is a wallet?**
A Solana wallet stores your SOL and tokens. It consists of:
• **Public Address**: Like a bank account number (safe to share)
• **Private Key**: Like your password (NEVER share this!)

**🆕 Create New vs Import**
• **Create New**: Generate a fresh wallet with new keys
• **Import**: Use an existing wallet you already have

**💰 Funding Your Wallet**
1. Get your wallet address from the dashboard
2. Send SOL from an exchange or another wallet
3. Minimum: 0.01 SOL for trading

**🛡️ Security Best Practices**
• Never share your private key
• Save your backup phrase securely
• Use small amounts for testing first
• Enable all security features

**📱 Supported Formats**
• Phantom wallet export
• Solflare wallet export
• Raw private key (array/hex/base58)

**🤖 Trading Integration**
Your wallet automatically works with:
• Auto-trading features
• Manual buy/sell orders
• TradingView alerts
• Contract scraper purchases
        """
        
        keyboard = [
            [InlineKeyboardButton("🆕 Create New Wallet", callback_data="wallet_create_new")],
            [InlineKeyboardButton("📥 Import Wallet", callback_data="wallet_import")],
            [InlineKeyboardButton("🔙 Back to Wallet Menu", callback_data="wallet_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )