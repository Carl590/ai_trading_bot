# 🤖 Advanced Telegram Trading Bot - Maestro Style

> **Professional Solana Trading Bot with TradingView Integration & Maestro-Style Dashboard**

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Solana](https://img.shields.io/badge/blockchain-Solana-purple.svg)
![Telegram](https://img.shields.io/badge/platform-Telegram-blue.svg)

## 🌟 Features

### 🎯 **Core Features**
- **🤖 AI Auto Trading** - Automated buy/sell based on TradingView alerts
- **📊 Real-time Dashboard** - Maestro-style inline interface (no spam messages)
- **💰 Wallet Management** - Secure wallet import/generation with encryption
- **🏆 Best Trades Monitor** - Track top performing wallets on Solana
- **📈 PnL Tracking** - Real-time profit/loss monitoring
- **🔗 TradingView Integration** - Direct webhook processing

### 🛡️ **Security & Risk Management**
- **🔐 Secure Key Storage** - Encrypted private key management
- **⚠️ Risk Controls** - Daily loss limits, position size controls
- **🚨 Emergency Stop** - Instant trading halt functionality
- **🔑 Access Control** - User whitelist and rate limiting

### 📊 **Trading Features**
- **⚡ Jupiter Integration** - Optimal swap routing
- **📱 Mobile Friendly** - Complete control via Telegram
- **🎚️ Customizable Settings** - Slippage, trade amounts, risk levels
- **📊 Position Monitoring** - Track all active positions
- **🔄 Auto-refresh** - Real-time price and PnL updates

## 🚀 Quick Start

### 1. **Clone & Setup**
```bash
git clone <your-repo-url>
cd "TradingView-To Telegram-Autobuy:-sell"
./setup.sh install
```

### 2. **Configure Bot Token**
```bash
# Edit .env file
nano .env

# Add your Telegram Bot Token (get from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here
WEBHOOK_SECRET_KEY=your_secret_key_123
```

### 3. **Start Trading**
```bash
source venv/bin/activate
python main_app.py
```

### 4. **Setup TradingView Webhooks**
- **Webhook URL:** `http://your-server:8080/webhook`
- **Alert Message Format:**
```json
{
  "key": "your_secret_key_123",
  "user_id": YOUR_TELEGRAM_USER_ID,
  "msg": "buy So11111111111111111111111111111111111111112"
}
```

## 📱 Bot Interface

### 🏠 **Main Dashboard**
```
🤖 SOLANA TRADING BOT DASHBOARD 🤖

💰 Wallet Status: ✅ Connected
🏦 Balance: 1.2345 SOL
🎯 AI Trading: 🟢 Active

📊 Quick Stats:
• Active Positions: 3
• Total PnL: +15.67%

[🤖 AI Trading Bot] [🏆 Best Trades]
[👛 Wallet Setup]   [❓ Help]
```

### 🤖 **AI Trading Dashboard**
```
🤖 AI TRADING BOT 🤖

Status: 🟢 ACTIVE
Webhook: ✅ Ready

📊 CURRENT POSITIONS:
1. BONK (EPjF...YmNz)
   💰 PnL: +0.0234 SOL (+23.4%)
   📈 Entry: $0.000012 | Current: $0.000015

[🛑 Stop AI Trading] [📊 Trading Monitor]
[⚙️ Settings]       [🔙 Back to Menu]
```

### 🏆 **Best Trades Monitor**
```
🏆 TOP 5 BEST TRADES (24H) 🏆

1. BONK
   🎯 Wallet: 7xKX...9mNz
   💰 PnL: +45.67 SOL
   📈 ROI: +1247.3%

[🔄 Refresh Data] [📊 Copy Best Wallet]
```

### 👛 **Wallet Setup**
```
👛 WALLET SETUP 👛

Status: ✅ CONNECTED

Current Wallet:
GxU7...h8Kp

💰 Balance: 1.2345 SOL

[💰 View Balance] [📤 Export Wallet]
[🗑️ Disconnect]   [🔙 Back to Menu]
```

## ⚙️ Configuration

### **Environment Variables (.env)**
```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here
WEBHOOK_SECRET_KEY=your_secret_key

# Trading Settings
DEFAULT_TRADE_AMOUNT_SOL=0.01
DEFAULT_SLIPPAGE_BPS=100
MAX_TRADE_AMOUNT_SOL=1.0

# Risk Management
DAILY_LOSS_LIMIT_SOL=0.1
EMERGENCY_STOP_LOSS_PERCENT=-50.0

# API Keys (Optional)
BIRDEYE_API_KEY=your_api_key
DEXSCREENER_API_KEY=your_api_key
```

### **TradingView Alert Setup**

1. **Create Alert in TradingView**
2. **Set Webhook URL:** `http://your-server:8080/webhook`
3. **Alert Message:**
```json
{
  "key": "{{strategy.key}}",
  "user_id": YOUR_TELEGRAM_USER_ID,
  "msg": "{{strategy.order.action}} {{ticker}}"
}
```

Example messages:
- **Buy:** `"msg": "buy So11111111111111111111111111111111111111112"`
- **Sell:** `"msg": "sell EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"`

## 🔧 Advanced Features

### **Multi-User Support**
```bash
# In .env file, specify allowed users (comma-separated)
TELEGRAM_ALLOWED_USERS=123456789,987654321
```

### **Custom Trading Strategies**
- Position sizing based on win rate
- Dynamic slippage adjustment
- Portfolio rebalancing
- Copy trading from successful wallets

### **Monitoring & Alerts**
- Real-time PnL notifications
- Daily trading summaries
- Error alerts and system status
- Performance analytics

## 📊 API Integration

### **Supported APIs**
- **Jupiter Aggregator** - Optimal swap routing
- **Birdeye API** - Token prices and analytics
- **DexScreener** - Market data and trending tokens
- **Solana RPC** - Blockchain interactions
- **CoinGecko** - Price data and market info

### **Webhook Security**
- IP whitelisting (TradingView IPs)
- Secret key validation
- Rate limiting
- Request logging and monitoring

## 🛠️ Development

### **Project Structure**
```
├── main_app.py              # Main application entry point
├── telegram_bot.py          # Telegram bot interface
├── webhook_handler.py       # TradingView webhook processing
├── best_trades_monitor.py   # Top trades analysis
├── config_manager.py        # Configuration management
├── setup.sh                 # Installation script
├── requirements_full.txt    # Python dependencies
├── .env.example            # Environment template
└── SOLANA_AUTO_TRADER_GUIDE.md
```

### **Running in Development**
```bash
# Install dependencies
./setup.sh install

# Test configuration
./setup.sh test

# Start development server
source venv/bin/activate
python main_app.py
```

### **Running in Production**
```bash
# Using systemd service
sudo cp trading-bot.service /etc/systemd/system/
sudo systemctl enable trading-bot
sudo systemctl start trading-bot

# Or using screen/tmux
screen -S trading-bot
source venv/bin/activate
python main_app.py
```

## 📈 Performance Optimization

### **Recommended VPS Specs**
- **CPU:** 2+ cores
- **RAM:** 4GB+ 
- **Storage:** 20GB+ SSD
- **Network:** 100+ Mbps
- **OS:** Ubuntu 20.04+ / Debian 11+

### **RPC Optimization**
```bash
# Use premium RPC for better performance
SOLANA_RPC_URL=https://your-premium-rpc.com
SOLANA_RPC_TIMEOUT=10
```

## 🔒 Security Best Practices

### **Wallet Security**
- Never share private keys
- Use hardware wallets for large amounts
- Regular security audits
- Backup strategies

### **Server Security**
- Use SSL/TLS certificates
- Regular system updates
- Firewall configuration
- Log monitoring

### **Bot Security**
- Strong webhook secret keys
- User access controls
- Rate limiting
- Error handling

## 🆘 Support & Troubleshooting

### **Common Issues**
```bash
# Bot not responding
./setup.sh test  # Check configuration

# Webhook not working
# Check TradingView IP whitelist and secret key

# Trading errors
# Verify wallet balance and RPC connection

# Performance issues
# Use premium RPC and optimize VPS specs
```

### **Logs & Monitoring**
```bash
# View logs
tail -f trading_bot.log

# Check system status
python -c "from config_manager import *; print_config_summary()"
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**IMPORTANT:** This software is for educational purposes only. Trading cryptocurrencies involves significant risk and can result in financial loss. Always:

- ✅ Test with small amounts first
- ✅ Never invest more than you can afford to lose
- ✅ Do your own research (DYOR)
- ✅ Monitor your bot regularly
- ✅ Understand the risks involved

The developers are not responsible for any financial losses incurred through the use of this software.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⭐ Support

If you find this project helpful, please give it a star! ⭐

For support, join our [Telegram Group](https://t.me/+idISjNudRgVhYzUy) or open an issue.

---

**Built with ❤️ for the Solana community**