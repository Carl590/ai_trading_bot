# 🤖 AI Trading Bot - Solana Edition

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Solana](https://img.shields.io/badge/Solana-Network-purple.svg)](https://solana.com/)

> **Advanced Telegram Trading Bot for Solana with AI-Powered Contract Discovery, Maestro-Style Wallet Management, and Automated Trading**

![Trading Bot Dashboard](./assets/logo.png)

## 🌟 **Key Features**

### 🔐 **Secure Wallet Management**
- **Maestro-Style Interface**: Complete wallet setup through Telegram
- **Military-Grade Encryption**: Fernet encryption for all private keys
- **Multi-Format Support**: Import from Phantom, Solflare, or raw keys
- **QR Code Deposits**: Easy funding with generated QR codes

### 🤖 **AI-Powered Trading**
- **Smart Contract Discovery**: AI filters for high-confidence Solana tokens
- **Auto-Trading**: Automatic execution on detected opportunities
- **TradingView Integration**: Webhook alerts execute trades instantly
- **MEV Protection**: Advanced transaction optimization

### 💎 **Solana Ecosystem Focus**
- **SPL Token Specialist**: Optimized for Solana token trading
- **Jupiter Integration**: Best swap routes and pricing
- **Raydium Support**: Direct DEX interactions
- **Real-Time Analytics**: Live market data and trends

### 📊 **Professional Features**
- **Portfolio Tracking**: Real-time balance and performance monitoring
- **Risk Management**: Configurable slippage and safety limits
- **Group Monitoring**: Scrape multiple Telegram channels
- **Performance Analytics**: Detailed trading statistics

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.9 or higher
- Telegram Bot Token
- Solana RPC endpoint access

### **Installation**

1. **Clone the repository**
   ```bash
   git clone https://github.com/Carl590/ai_trading_bot.git
   cd ai_trading_bot
   ```

2. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure your environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Start the bot**
   ```bash
   ./venv/bin/python telegram_bot.py
   ```

### **First Time Setup**

1. **Start your bot on Telegram**
   - Send `/start` to your bot
   - Click "💼 Wallet Manager"
   - Choose "🆕 Create New Wallet" or "📥 Import Existing"

2. **Fund your wallet**
   - Get your wallet address from the dashboard
   - Send SOL to fund your trading operations
   - Minimum recommended: 0.1 SOL

3. **Configure trading**
   - Set up auto-trading parameters
   - Add Telegram groups to monitor
   - Configure risk management settings

## 📱 **How to Access Dashboard**

### **Via Telegram Commands**
```bash
/start      # Main dashboard
/dashboard  # Alternative access
/trading    # Trading interface
```

### **Dashboard Features**
- 🗺️ **Portfolio**: View holdings and performance
- 🔄 **Quick Trade**: Manual buy/sell operations
- 📊 **Analytics**: Market trends and statistics
- 🚀 **Trending**: Hot tokens and opportunities
- 💎 **Contract Scraper**: AI-powered token discovery
- 💼 **Wallet Manager**: Secure wallet operations
- ⚙️ **Settings**: Bot configuration
- ℹ️ **Help**: Documentation and support

## 🔧 **Configuration**

### **Environment Variables**

Create a `.env` file with the following:

```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
WEBHOOK_SECRET_KEY=your_webhook_secret

# Solana Configuration
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
JUPITER_API_URL=https://quote-api.jup.ag/v6

# Trading Configuration
DEFAULT_SLIPPAGE_BPS=300
MAX_TRADE_AMOUNT_SOL=1.0
AUTO_TRADE_ENABLED=false

# Wallet Encryption
WALLET_ENCRYPTION_KEY=auto_generated_on_first_run

# Auto-Trading Configuration (Optional)
AUTO_TRADE_WALLET_PRIVATE_KEY=your_dedicated_trading_wallet
AUTO_TRADE_AMOUNT_SOL=0.1
AUTO_TRADE_MIN_CONFIDENCE=0.8
```

### **Auto-Trading Setup**

1. **Run the auto-trade configuration**
   ```bash
   ./setup_autotrade.sh
   ```

2. **Add groups to monitor**
   ```bash
   ./venv/bin/python scraper_manager.py add-group "https://t.me/solana_gems" --group-name "Solana Gems" --auto-trade
   ```

3. **Start the scraper**
   ```bash
   ./venv/bin/python scraper_manager.py start
   ```

## 🏗️ **Architecture**

### **Core Components**

```
├── telegram_bot.py          # Main Telegram interface
├── wallet_manager.py        # Secure wallet management
├── trading_engine.py        # Jupiter-integrated trading
├── telegram_scraper.py      # AI contract discovery
├── webhook_handler.py       # TradingView integration
├── api_manager.py          # RPC and API management
└── scraper_manager.py      # Group monitoring CLI
```

### **Security Features**

- **🔐 End-to-End Encryption**: All private keys encrypted at rest
- **🛡️ Message Auto-Deletion**: Sensitive data automatically removed
- **🔑 Secure Key Derivation**: Cryptographically secure wallet generation
- **📱 Session Management**: Secure Telegram session handling

### **Trading Pipeline**

```
Market Signal → AI Analysis → Risk Assessment → Wallet Verification → Trade Execution → Results Tracking
```

## 💡 **Usage Examples**

### **Manual Trading**
```bash
# Send to your bot on Telegram:
/start
# Click "🔄 Quick Trade"
# Select token and amount
# Confirm transaction
```

### **Auto-Trading Setup**
```bash
# Configure auto-trading
./setup_autotrade.sh

# Add monitoring groups
./venv/bin/python scraper_manager.py add-group "https://t.me/alpha_calls" --auto-trade

# Start monitoring
./venv/bin/python scraper_manager.py start
```

### **TradingView Integration**
```javascript
// TradingView Alert Webhook
{
    "user_id": "123456789",
    "action": "buy",
    "token": "CONTRACT_ADDRESS",
    "amount": 0.1
}
```

## 📊 **Monitoring & Analytics**

### **Contract Discovery**
- **AI Filtering**: 80%+ confidence threshold for auto-trades
- **Multi-Network**: Solana SPL token focus
- **Real-Time**: Instant detection and analysis
- **Group Monitoring**: Multiple Telegram channels

### **Performance Tracking**
- **Portfolio Value**: Real-time SOL and USD values
- **Trade History**: Complete transaction records
- **Success Rate**: Win/loss analytics
- **Risk Metrics**: Drawdown and volatility tracking

### **Available Commands**
```bash
# Scraper Management
./venv/bin/python scraper_manager.py stats
./venv/bin/python scraper_manager.py contracts
./venv/bin/python scraper_manager.py list-groups

# System Monitoring
./venv/bin/python test_system.py
```

## 🔒 **Security Best Practices**

### **Wallet Security**
- ✅ Use dedicated wallets for auto-trading
- ✅ Start with small amounts for testing
- ✅ Keep backup phrases in secure locations
- ✅ Never share private keys or backup phrases
- ✅ Monitor wallet activity regularly

### **Bot Security**
- ✅ Use environment variables for sensitive data
- ✅ Enable webhook secret validation
- ✅ Monitor bot logs for suspicious activity
- ✅ Keep dependencies updated
- ✅ Use HTTPS for webhook endpoints

### **Trading Security**
- ✅ Set reasonable slippage limits (3-5%)
- ✅ Configure daily trading limits
- ✅ Monitor auto-trading performance
- ✅ Use stop-losses where appropriate
- ✅ Diversify trading strategies

## 🛠️ **Development**

### **Project Structure**
```
ai_trading_bot/
├── README.md
├── requirements.txt
├── .env.example
├── setup.sh
├── Dockerfile
├── docker-compose.yml
├── assets/
│   ├── logo.png
│   └── bmac.png
├── .github/
│   └── workflows/
└── src/
    ├── telegram_bot.py
    ├── wallet_manager.py
    ├── trading_engine.py
    ├── telegram_scraper.py
    ├── webhook_handler.py
    ├── api_manager.py
    └── utils/
```

### **Contributing**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### **Testing**
```bash
# Run system tests
./venv/bin/python test_system.py

# Test wallet functionality
./venv/bin/python -c "from wallet_manager import wallet_manager; print(wallet_manager.get_wallet_stats())"

# Test trading engine
./venv/bin/python -c "from trading_engine import trading_engine; print('Trading engine ready')"
```

## 🚀 **Deployment**

### **Docker Deployment**
```bash
# Build and run with Docker
docker-compose up -d

# View logs
docker-compose logs -f
```

### **Manual Deployment**
```bash
# Set up production environment
./setup.sh

# Start with process manager
./venv/bin/python process_manager.py start

# Monitor with logs
tail -f telegram_scraper.log
```

### **Environment Setup**
- **Development**: Use `.env` with test tokens
- **Production**: Use environment variables or encrypted config
- **Staging**: Separate bot tokens and minimal funds

## 📈 **Performance Optimization**

### **RPC Configuration**
- Multiple RPC endpoints for redundancy
- Load balancing for high availability
- Custom timeout and retry settings
- MEV protection endpoints

### **Trading Optimization**
- Jupiter API for best swap routes
- Priority fee optimization
- Slippage protection
- Gas fee estimation

### **Memory & CPU**
- Efficient async operations
- Connection pooling
- Garbage collection optimization
- Resource monitoring

## ❓ **Troubleshooting**

### **Common Issues**

#### **Bot Not Responding**
```bash
# Check if bot is running
ps aux | grep python | grep telegram_bot

# Restart bot
./venv/bin/python telegram_bot.py
```

#### **Wallet Issues**
```bash
# Test wallet system
./venv/bin/python -c "from wallet_manager import wallet_manager; print(wallet_manager.get_wallet_stats())"

# Reset wallet data (⚠️ This will delete all wallets)
rm user_wallets.json
```

#### **Trading Errors**
```bash
# Check RPC connectivity
./venv/bin/python -c "from api_manager import api_manager; print(api_manager.get_rpc_url())"

# Test trading engine
./venv/bin/python test_system.py
```

### **Log Analysis**
```bash
# View recent logs
tail -100 telegram_scraper.log

# Search for errors
grep ERROR telegram_scraper.log

# Monitor live
tail -f telegram_scraper.log
```

## 📞 **Support**

### **Documentation**
- **Setup Guide**: See installation section above
- **API Reference**: Check individual module docstrings
- **Configuration**: Review `.env.example` file

### **Community**
- **Issues**: [GitHub Issues](https://github.com/Carl590/ai_trading_bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Carl590/ai_trading_bot/discussions)
- **Updates**: Follow repository for latest updates

### **Professional Support**
For enterprise deployment or custom modifications, contact through GitHub.

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ **Disclaimer**

**Trading cryptocurrencies involves substantial risk of loss. This bot is for educational and experimental purposes. Never trade with funds you cannot afford to lose. Always do your own research and understand the risks involved.**

- Past performance does not guarantee future results
- The bot operates autonomously based on programmed criteria
- Market conditions can change rapidly
- Smart contract risks exist in DeFi protocols
- Always test with small amounts first

## 🚀 **Get Started Now**

1. **Clone the repo**: `git clone https://github.com/Carl590/ai_trading_bot.git`
2. **Run setup**: `./setup.sh`
3. **Configure**: Edit `.env` with your settings
4. **Start trading**: `./venv/bin/python telegram_bot.py`

**Happy Trading! 🎯**

---

**⭐ Star this repo if you found it useful!**