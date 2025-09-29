#!/usr/bin/env python3
"""
Quick test to verify wallet import callback is working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_callback_handlers():
    """Test that all wallet callback handlers are properly mapped"""
    
    print("🧪 Testing Wallet Import Callback Handlers...")
    
    # Test cases for callback data
    test_cases = [
        "import_wallet",      # Old wallet setup menu
        "wallet_import",      # New wallet setup menu  
        "wallet_create_new",  # Create wallet
        "wallet_menu",        # Wallet menu
    ]
    
    print("✅ Callback handlers to test:")
    for callback in test_cases:
        print(f"   📋 {callback}")
    
    print("\n🔍 Checking telegram_bot.py for handlers...")
    
    # Read the bot file to check handlers
    with open('telegram_bot.py', 'r') as f:
        bot_content = f.read()
    
    # Check if handlers exist
    missing_handlers = []
    found_handlers = []
    
    for callback in test_cases:
        if f'data == "{callback}"' in bot_content:
            found_handlers.append(callback)
            print(f"   ✅ {callback}")
        else:
            missing_handlers.append(callback)
            print(f"   ❌ {callback}")
    
    print(f"\n📊 Results:")
    print(f"   ✅ Found: {len(found_handlers)}")
    print(f"   ❌ Missing: {len(missing_handlers)}")
    
    if missing_handlers:
        print(f"\n🚨 Missing handlers for: {missing_handlers}")
        return False
    else:
        print(f"\n🎉 All wallet callback handlers are properly configured!")
        return True

if __name__ == "__main__":
    success = test_callback_handlers()
    if success:
        print("\n✅ Wallet import should now work correctly!")
        print("📱 Try clicking 'Import Wallet' in your Telegram bot")
    else:
        print("\n❌ Some callback handlers are missing")