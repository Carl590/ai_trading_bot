#!/bin/bash

# Auto-Trading Setup Script
# This script helps configure auto-trading for the Solana bot

echo "🤖 Auto-Trading Setup for Solana Bot"
echo "====================================="
echo

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run setup.sh first."
    exit 1
fi

# Check if auto-trade template exists
if [ ! -f .env.autotrade ]; then
    echo "❌ Auto-trade template (.env.autotrade) not found."
    exit 1
fi

echo "📋 Auto-Trading Configuration Steps:"
echo "1. Create a dedicated wallet for auto-trading"
echo "2. Fund it with a small amount of SOL (recommended: 1-5 SOL)"
echo "3. Configure your private key and settings"
echo

read -p "Do you want to continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled."
    exit 0
fi

echo
echo "🔐 Wallet Configuration"
echo "======================"
echo "⚠️  SECURITY WARNING:"
echo "   - Use a separate wallet for auto-trading"
echo "   - Never share your private key"
echo "   - Start with small amounts"
echo

read -p "Enter your auto-trade wallet private key (hex format): " -s PRIVATE_KEY
echo
echo

if [ -z "$PRIVATE_KEY" ]; then
    echo "❌ Private key cannot be empty."
    exit 1
fi

echo "💰 Trading Configuration"
echo "========================"
read -p "Default buy amount per trade (SOL) [0.1]: " BUY_AMOUNT
BUY_AMOUNT=${BUY_AMOUNT:-0.1}

read -p "Daily trading limit (SOL) [1.0]: " DAILY_LIMIT
DAILY_LIMIT=${DAILY_LIMIT:-1.0}

read -p "Minimum confidence score (0.8-1.0) [0.8]: " MIN_CONFIDENCE
MIN_CONFIDENCE=${MIN_CONFIDENCE:-0.8}

read -p "Maximum slippage (%) [3]: " MAX_SLIPPAGE
MAX_SLIPPAGE=${MAX_SLIPPAGE:-3}
MAX_SLIPPAGE_BPS=$((MAX_SLIPPAGE * 100))

echo
echo "🔔 Notification Setup"
echo "===================="
read -p "Telegram chat ID for notifications (optional): " TELEGRAM_CHAT
read -p "Discord webhook URL (optional): " DISCORD_WEBHOOK

echo
echo "⚡ Performance Settings"
echo "======================"
read -p "Enable priority fees for faster execution? (y/n) [y]: " -n 1 -r PRIORITY_FEES
echo
PRIORITY_FEES=${PRIORITY_FEES:-y}

if [[ $PRIORITY_FEES =~ ^[Yy]$ ]]; then
    PRIORITY_ENABLED="true"
    read -p "Priority fee amount (lamports) [10000]: " PRIORITY_FEE
    PRIORITY_FEE=${PRIORITY_FEE:-10000}
else
    PRIORITY_ENABLED="false"
    PRIORITY_FEE="0"
fi

read -p "Enable MEV protection? (y/n) [y]: " -n 1 -r MEV_PROTECTION
echo
MEV_PROTECTION=${MEV_PROTECTION:-y}
if [[ $MEV_PROTECTION =~ ^[Yy]$ ]]; then
    MEV_ENABLED="true"
else
    MEV_ENABLED="false"
fi

echo
echo "💾 Saving Configuration"
echo "======================="

# Append auto-trading config to .env
echo "" >> .env
echo "# Auto-Trading Configuration (Generated $(date))" >> .env
echo "AUTO_TRADE_WALLET_PRIVATE_KEY=$PRIVATE_KEY" >> .env
echo "AUTO_TRADE_AMOUNT_SOL=$BUY_AMOUNT" >> .env
echo "AUTO_TRADE_DAILY_LIMIT_SOL=$DAILY_LIMIT" >> .env
echo "AUTO_TRADE_MIN_CONFIDENCE=$MIN_CONFIDENCE" >> .env
echo "AUTO_TRADE_MAX_SLIPPAGE_BPS=$MAX_SLIPPAGE_BPS" >> .env
echo "AUTO_TRADE_ENABLED=false" >> .env
echo "AUTO_TRADE_MAX_PER_HOUR=5" >> .env
echo "AUTO_TRADE_USE_PRIORITY_FEES=$PRIORITY_ENABLED" >> .env
echo "AUTO_TRADE_PRIORITY_FEE=$PRIORITY_FEE" >> .env
echo "AUTO_TRADE_MEV_PROTECTION=$MEV_ENABLED" >> .env

if [ ! -z "$TELEGRAM_CHAT" ]; then
    echo "AUTO_TRADE_NOTIFICATION_CHAT_ID=$TELEGRAM_CHAT" >> .env
fi

if [ ! -z "$DISCORD_WEBHOOK" ]; then
    echo "AUTO_TRADE_DISCORD_WEBHOOK=$DISCORD_WEBHOOK" >> .env
fi

echo "✅ Auto-trading configuration saved to .env"
echo

echo "🎯 Next Steps"
echo "============="
echo "1. Enable auto-trading in group configuration:"
echo "   ./venv/bin/python scraper_manager.py add-group <telegram_link> --auto-trade"
echo
echo "2. Set AUTO_TRADE_ENABLED=true in .env when ready"
echo
echo "3. Start the scraper:"
echo "   ./venv/bin/python scraper_manager.py start"
echo
echo "4. Monitor logs for auto-trade activity"
echo

echo "⚠️  Remember:"
echo "   - Start with small amounts"
echo "   - Monitor your wallet balance"
echo "   - Check auto-trade logs regularly"
echo "   - You can disable auto-trading anytime"
echo

echo "🚀 Auto-trading setup complete!"