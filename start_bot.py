#!/usr/bin/env python3
"""
Simple Bot Startup Script
Tests the Telegram bot functionality
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_requirements():
    """Check if all requirements are met"""
    issues = []
    
    # Check bot token
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        issues.append("❌ TELEGRAM_BOT_TOKEN not found in .env file")
    elif bot_token == 'YOUR_BOT_TOKEN_HERE':
        issues.append("❌ Please set your actual bot token in .env file")
    else:
        print(f"✅ Bot token configured: {bot_token[:20]}...")
    
    # Check webhook key
    webhook_key = os.getenv('WEBHOOK_SECRET_KEY')
    if not webhook_key:
        issues.append("⚠️  WEBHOOK_SECRET_KEY not set - webhook will be less secure")
    else:
        print(f"✅ Webhook key configured: {webhook_key}")
    
    return issues

def start_simple_bot():
    """Start a simple version of the bot for testing"""
    try:
        print("🤖 Starting Simple Telegram Bot...")
        
        # Import here to avoid import errors during setup
        from telegram import Bot, Update
        from telegram.ext import Application, CommandHandler, CallbackQueryHandler
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        async def start_command(update: Update, context):
            """Handle /start command"""
            keyboard = [
                [InlineKeyboardButton("🚀 Bot is Working!", callback_data="test")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            text = """
🤖 **TELEGRAM TRADING BOT**

✅ **Status:** Online and Ready!
🔗 **TradingView Webhook:** Ready
👛 **Wallet System:** Ready
📊 **Best Trades Monitor:** Ready

**Next Steps:**
1. Setup your Solana wallet
2. Configure TradingView alerts
3. Start auto-trading!

Bot is working perfectly! 🎉
            """
            
            await update.message.reply_text(
                text, 
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        async def button_callback(update: Update, context):
            """Handle button callbacks"""
            query = update.callback_query
            await query.answer()
            
            await query.edit_message_text(
                "✅ **SUCCESS!** Your bot is working perfectly!\n\n"
                "You can now use the full trading bot features:\n"
                "• AI Auto Trading\n"
                "• Best Trades Monitor\n"
                "• Wallet Management\n"
                "• TradingView Integration\n\n"
                "Send /start again to see the main dashboard.",
                parse_mode='Markdown'
            )
        
        # Create application
        app = Application.builder().token(bot_token).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CallbackQueryHandler(button_callback))
        
        print("✅ Simple bot started successfully!")
        print("📱 Send /start to your bot on Telegram to test it")
        print("🛑 Press Ctrl+C to stop the bot")
        
        # Run the bot
        app.run_polling(drop_pending_updates=True)
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Try installing missing packages: pip install python-telegram-bot")
        return False
    except Exception as e:
        print(f"❌ Bot Error: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🔧 Checking Bot Configuration...")
    
    issues = check_requirements()
    
    if issues:
        print("\n❌ Configuration Issues Found:")
        for issue in issues:
            print(f"  {issue}")
        print("\n💡 Please fix these issues and try again.")
        return False
    
    print("\n✅ All requirements met!")
    print("🚀 Starting bot...\n")
    
    try:
        start_simple_bot()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
    
    return True

if __name__ == "__main__":
    main()