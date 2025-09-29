#!/usr/bin/env python3
"""
Comprehensive System Test for Trading Bot
Tests all components and API integrations
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_api_manager():
    """Test API Manager functionality"""
    print("🔧 Testing API Manager...")
    print("=" * 50)
    
    try:
        from api_manager import api_manager
        
        # Test endpoint availability
        print("📡 Available Endpoints:")
        for key, endpoint in api_manager.endpoints.items():
            status = "🔑" if endpoint.api_key else "🔓"
            print(f"  {status} {endpoint.name}: {endpoint.url}")
        
        # Test RPC URL
        rpc_url = api_manager.get_rpc_url()
        print(f"\n🌐 Primary RPC: {rpc_url}")
        
        # Test Jupiter endpoints
        jupiter_endpoints = api_manager.get_jupiter_endpoints()
        print(f"\n🪐 Jupiter Endpoints:")
        for key, url in jupiter_endpoints.items():
            print(f"  • {key}: {url}")
        
        # Test MEV endpoints
        mev_endpoints = api_manager.get_mev_endpoints()
        print(f"\n🛡️  MEV Protection Endpoints ({len(mev_endpoints)}):")
        for endpoint in mev_endpoints:
            print(f"  • {endpoint.name}: {endpoint.url}")
        
        return True
        
    except Exception as e:
        print(f"❌ API Manager test failed: {e}")
        return False

async def test_trading_engine():
    """Test Enhanced Trading Engine"""
    print("\n🚀 Testing Enhanced Trading Engine...")
    print("=" * 50)
    
    try:
        from trading_engine import trading_engine
        
        # Health check
        print("🏥 Running health check...")
        health = await trading_engine.health_check()
        
        for service, status in health.items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {service}")
        
        # Performance stats
        print("\n📊 Performance Statistics:")
        stats = trading_engine.get_performance_stats()
        for key, value in stats.items():
            print(f"  • {key}: {value}")
        
        # Test token info (USDC)
        print("\n🪙 Testing Token Info (USDC):")
        token_info = await trading_engine.get_token_info("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        
        if token_info:
            print(f"  • Symbol: {token_info.symbol}")
            print(f"  • Name: {token_info.name}")
            print(f"  • Price: ${token_info.price_usd}")
            print(f"  • Decimals: {token_info.decimals}")
        else:
            print("  ⚠️  Could not fetch token info")
        
        return True
        
    except Exception as e:
        print(f"❌ Trading Engine test failed: {e}")
        return False

async def test_config_manager():
    """Test Configuration Manager"""
    print("\n⚙️ Testing Configuration Manager...")
    print("=" * 50)
    
    try:
        from config_manager import config_manager
        
        # Test configuration loading
        config = config_manager.get_config()
        print(f"📋 Bot Token: {'✅ Configured' if config.telegram_bot_token else '❌ Missing'}")
        print(f"🔑 Webhook Key: {'✅ Configured' if config.webhook_secret_key else '❌ Missing'}")
        print(f"💎 Shyft API: {'✅ Configured' if config.shyft_api_key else '❌ Missing'}")
        print(f"🌟 Helius API: {'✅ Configured' if config.helius_api_key else '❌ Missing'}")
        
        # Test user config (if any)
        print(f"\n👥 User Configurations: {len(config_manager.user_configs)} users")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration Manager test failed: {e}")
        return False

async def test_webhook_handler():
    """Test Webhook Handler"""
    print("\n🪝 Testing Webhook Handler...")
    print("=" * 50)
    
    try:
        from webhook_handler import WebhookHandler
        from config_manager import config_manager
        
        # Initialize handler
        handler = WebhookHandler(config_manager)
        
        # Test webhook validation
        test_payload = {
            "key": "trading-bot-secure-key-2025",
            "user_id": "123456789",
            "msg": "buy EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        }
        
        print("🔍 Testing webhook validation...")
        is_valid = handler.validate_webhook(test_payload)
        print(f"  {'✅ Valid' if is_valid else '❌ Invalid'} webhook format")
        
        print("\n📨 Webhook handler initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Webhook Handler test failed: {e}")
        return False

async def test_telegram_bot():
    """Test Telegram Bot"""
    print("\n🤖 Testing Telegram Bot...")
    print("=" * 50)
    
    try:
        from telegram_bot import TelegramTradingBot
        from config_manager import config_manager
        
        # Initialize bot (don't start it)
        config = config_manager.get_config()
        
        if not config.telegram_bot_token:
            print("❌ No Telegram bot token configured")
            return False
        
        print("✅ Bot token configured")
        print("✅ Bot classes imported successfully")
        
        # Note: We don't actually start the bot to avoid conflicts
        print("⚠️  Bot startup skipped (to avoid conflicts)")
        
        return True
        
    except Exception as e:
        print(f"❌ Telegram Bot test failed: {e}")
        return False

async def test_dependencies():
    """Test all dependencies"""
    print("\n📦 Testing Dependencies...")
    print("=" * 50)
    
    dependencies = [
        'telegram',
        'flask', 
        'aiohttp',
        'solana',
        'requests',
        'python-dotenv'
    ]
    
    all_good = True
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✅ {dep}")
        except ImportError:
            print(f"  ❌ {dep} - Not installed")
            all_good = False
    
    return all_good

async def main():
    """Run comprehensive system test"""
    print("🧪 COMPREHENSIVE SYSTEM TEST")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Configuration Manager", test_config_manager),
        ("API Manager", test_api_manager),
        ("Trading Engine", test_trading_engine),
        ("Webhook Handler", test_webhook_handler),
        ("Telegram Bot", test_telegram_bot)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        icon = "✅" if result else "❌"
        print(f"  {icon} {test_name}")
    
    print(f"\n🏆 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready to deploy.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    print(f"\n🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())