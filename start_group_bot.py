#!/usr/bin/env python3
"""
Group Bot Launcher
Starts the Telegram bot for group interactions with automatic dashboard
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Launch the group trading bot"""
    
    print("🚀 Starting Group Trading Bot...")
    print("📱 Features:")
    print("  • Automatic dashboard for new members")
    print("  • Inline trading interface")
    print("  • Group-optimized interactions")
    print("  • No message spam")
    print()
    
    try:
        # Import and run the group bot
        from group_bot import GroupTradingBot
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        group_id = "https://t.me/+idISjNudRgVhYzUy"
        
        if not bot_token:
            print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env file")
            return False
        
        print(f"✅ Bot Token: {bot_token[:20]}...")
        print(f"✅ Group: {group_id}")
        print()
        print("🎯 Bot Features Active:")
        print("  • New member welcome with dashboard")
        print("  • /start, /dashboard, /trading commands")
        print("  • Inline buttons for all interactions")
        print("  • AI trading controls")
        print("  • Wallet management")
        print("  • Best trades monitor")
        print()
        print("📋 Setup Instructions:")
        print("1. Add your bot to the group as admin")
        print("2. Give it permission to:")
        print("   - Read messages")
        print("   - Send messages") 
        print("   - Manage group members")
        print("3. New members will automatically see the dashboard!")
        print()
        print("🛑 Press Ctrl+C to stop the bot")
        print("="*50)
        
        # Create and start bot
        group_bot = GroupTradingBot(bot_token, group_id)
        group_bot.run()
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   ./venv/bin/pip install python-telegram-bot")
        return False
    except KeyboardInterrupt:
        print("\n👋 Group bot stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)