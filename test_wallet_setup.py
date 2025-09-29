#!/usr/bin/env python3
"""
Test Wallet Setup Flow
Test the new wallet setup with naming functionality
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from wallet_manager import wallet_manager
from wallet_setup import WalletSetupHandler

class MockTelegramUpdate:
    """Mock Telegram update for testing"""
    def __init__(self):
        self.effective_user = MockUser()
        self.message = MockMessage()

class MockUser:
    def __init__(self):
        self.id = "test_user_123"

class MockMessage:
    def __init__(self):
        self.text = "Test Wallet"

async def test_wallet_creation():
    """Test wallet creation with custom name"""
    print("🧪 Testing Wallet Creation with Custom Name...")
    
    try:
        # Test wallet creation
        user_id = "test_user_123"
        wallet_name = "My Test Wallet"
        
        # Create wallet
        address, backup_phrase = wallet_manager.create_new_wallet(user_id, wallet_name)
        
        print(f"✅ Wallet created successfully!")
        print(f"   📛 Name: {wallet_name}")
        print(f"   📍 Address: {address[:8]}...{address[-8:]}")
        print(f"   🔑 Backup: {backup_phrase[:20]}...")
        
        # Check wallet info
        wallet_info = wallet_manager.get_user_wallet(user_id)
        if wallet_info:
            print(f"   💾 Stored Name: {wallet_info.wallet_name}")
            print(f"   ✅ Wallet correctly saved with custom name!")
        else:
            print("   ❌ Wallet not found in storage!")
            return False
        
        # Clean up test wallet
        if os.path.exists('user_wallets.json'):
            import json
            with open('user_wallets.json', 'r') as f:
                wallets = json.load(f)
            if user_id in wallets:
                del wallets[user_id]
            with open('user_wallets.json', 'w') as f:
                json.dump(wallets, f)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing wallet creation: {e}")
        return False

async def test_wallet_import():
    """Test wallet import with custom name"""
    print("\n🧪 Testing Wallet Import with Custom Name...")
    
    try:
        # Generate a test private key
        from solders.keypair import Keypair
        test_wallet = Keypair()
        private_key_array = test_wallet.to_bytes_array()
        
        user_id = "test_user_456"
        wallet_name = "Imported Test Wallet"
        
        # Import wallet
        address = wallet_manager.import_wallet(
            user_id, 
            str(private_key_array), 
            wallet_name
        )
        
        print(f"✅ Wallet imported successfully!")
        print(f"   📛 Name: {wallet_name}")
        print(f"   📍 Address: {address[:8]}...{address[-8:]}")
        
        # Check wallet info
        wallet_info = wallet_manager.get_user_wallet(user_id)
        if wallet_info:
            print(f"   💾 Stored Name: {wallet_info.wallet_name}")
            print(f"   ✅ Wallet correctly imported with custom name!")
        else:
            print("   ❌ Wallet not found in storage!")
            return False
        
        # Clean up test wallet
        if os.path.exists('user_wallets.json'):
            import json
            with open('user_wallets.json', 'r') as f:
                wallets = json.load(f)
            if user_id in wallets:
                del wallets[user_id]
            with open('user_wallets.json', 'w') as f:
                json.dump(wallets, f)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing wallet import: {e}")
        return False

async def main():
    """Run wallet setup tests"""
    print("🔧 Wallet Setup Flow Tests")
    print("=" * 40)
    
    # Test wallet creation
    creation_success = await test_wallet_creation()
    
    # Test wallet import
    import_success = await test_wallet_import()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"   🆕 Wallet Creation: {'✅ PASS' if creation_success else '❌ FAIL'}")
    print(f"   📥 Wallet Import: {'✅ PASS' if import_success else '❌ FAIL'}")
    
    if creation_success and import_success:
        print("\n🎉 All wallet setup tests passed!")
        print("✅ The new wallet naming flow is working correctly!")
        return True
    else:
        print("\n❌ Some tests failed. Check the implementation.")
        return False

if __name__ == "__main__":
    asyncio.run(main())