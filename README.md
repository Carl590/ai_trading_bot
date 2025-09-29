# 🤖 AI Trading Bot - Solana Edition

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Solana](https://img.shields.io/badge/Solana-Network-purple.svg)](https://solana.com/)

> **Professional Telegram Trading Bot for Solana - Your Complete Automated Trading Solution**

![Trading Bot Dashboard](./assets/logo.png)

Transform your Solana trading with our cutting-edge AI-powered bot that delivers institutional-grade automation through a simple Telegram interface. From TradingView webhook integration to intelligent signal processing, this bot handles everything automatically while you maintain full control.

## 🎯 **How It Works**

Start the bot with `/start` and access your **Personal Trading Dashboard** with five powerful sections:

### 🤖 **AI Trading** - TradingView Automation
> *Fully automated TradingView webhook trading*

- **🎯 One-Click Setup**: Connect your TradingView alerts directly to the bot
- **⚡ Instant Execution**: Webhooks trigger immediate buy/sell orders
- **💰 Customizable Amounts**: Set your preferred SOL trade amounts (0.1, 0.5, 1.0, 5.0 SOL)
- **🛡️ Risk Management**: Built-in slippage protection and transaction optimization
- **📊 Real-time Monitoring**: Live position tracking and PnL updates

**Perfect for**: Traders who want to automate their TradingView strategies without manual intervention

### 🚀 **AlphaSignals AutoTrade** - Intelligent Signal Trading
> *AI-powered contract discovery with exclusive trailing stop technology*

- **🔍 Smart Signal Detection**: Automatically scans Telegram groups for Solana contract addresses
- **🧠 AI Filtering**: Advanced algorithms identify high-potential tokens
- **📈 Exclusive Trailing Stops**: Revolutionary liquidity-based trailing stop loss system
  - Calculates optimal stops based on entry liquidity
  - Adapts to market volatility in real-time
  - Maximizes profits while protecting capital
- **⚙️ Per-User Settings**: Customize position sizes, risk limits, and channel filters
- **🛡️ Rug Protection**: Comprehensive token safety analysis before every trade

**Perfect for**: Alpha hunters who want to catch the best signals with intelligent risk management

### 🏆 **Best Trades** - Market Intelligence
> *Discover the most profitable Solana trades in real-time*

- **📊 24-Hour Winners**: Top performing tokens by ROI in the last 24 hours
- **🎯 Smart Wallets**: Track and copy strategies from successful traders
- **💎 Gem Discovery**: Identify emerging opportunities before they explode
- **📈 Performance Analytics**: Detailed metrics on winning trades and strategies
- **🔄 Live Updates**: Real-time data refresh for up-to-the-minute insights

**Perfect for**: Traders who want to learn from the market's best performers and spot trending opportunities

### � **Wallet Setup** - Secure & Simple
> *Military-grade wallet management through Telegram*

- **🔐 Custom Naming**: Give your wallets personalized names for easy management
- **🔑 Secure Import**: Import using private keys with Fernet encryption
- **💰 Multi-Wallet Support**: Manage multiple wallets from one interface
- **📱 QR Code Deposits**: Generate QR codes for easy funding
- **🛡️ Maximum Security**: All private keys encrypted and stored locally

**Perfect for**: Everyone - secure wallet setup is your gateway to automated trading

### ❓ **Help & Support** - Complete Guidance
> *Everything you need to master the bot*

- **📚 Command Reference**: Complete list of bot commands and features
- **🎥 Setup Guides**: Step-by-step tutorials for each feature
- **🔧 Troubleshooting**: Common issues and solutions
- **📞 Support Channels**: Direct access to help and community
- **📖 Best Practices**: Trading tips and security recommendations

**Perfect for**: New users getting started and experienced traders optimizing their setup

## 🚀 **Getting Started in 3 Minutes**

### **Step 1: Quick Installation**
```bash
# Clone and setup
git clone https://github.com/Carl590/ai_trading_bot.git
cd ai_trading_bot
./setup.sh

# Configure your environment
cp .env.example .env
# Edit .env with your Telegram bot token
```

### **Step 2: Launch Your Bot**
```bash
# Start the bot
python telegram_bot.py

# Or run in background
nohup python telegram_bot.py &
```

### **Step 3: Setup Your Wallet**
```
1. Message your bot with /start
2. Click "👛 Wallet Setup"
3. Choose "Import Wallet"
4. Name your wallet (e.g., "Main Trading")
5. Paste your private key
6. Start trading! 🚀
```

## 💡 **Real-World Usage Examples**

### **Scenario 1: TradingView Automation**
*"I want my TradingView Pine Script alerts to automatically buy tokens"*

1. Go to **🤖 AI Trading**
2. Set your trade amount (e.g., 1 SOL)
3. Copy the webhook URL
4. Add it to your TradingView alert
5. Every alert = automatic trade execution!

### **Scenario 2: Alpha Signal Hunting**
*"I want to catch profitable signals from Telegram channels with smart exits"*

1. Go to **🚀 AlphaSignals AutoTrade**
2. Add trusted Telegram channels to whitelist
3. Enable the exclusive trailing stop system
4. Set your max position size
5. Bot automatically buys good signals and exits optimally!

### **Scenario 3: Learning from Winners**
*"I want to see what the best traders are buying"*

1. Check **🏆 Best Trades** daily
2. Analyze top ROI tokens from last 24 hours
3. Copy successful wallet strategies
4. Discover gems before they moon!

## 🎛️ **Dashboard Deep Dive**

### **Main Menu Navigation**
Access everything from one central hub:
```
/start
├── 🤖 AI Trading (TradingView webhooks)
├── 🚀 AlphaSignals AutoTrade (Signal automation)
├── 🏆 Best Trades (Market intelligence)
├── 👛 Wallet Setup (Secure management)
├── ❓ Help (Complete guidance)
└── 🔄 Refresh (Update all data)
```

### **🤖 AI Trading Dashboard**
Your TradingView automation headquarters:
- **Trade Size Selection**: Choose 0.1, 0.5, 1.0, or 5.0 SOL per trade
- **Webhook Management**: Generate and manage your webhook URLs
- **Live Monitoring**: See active positions and PnL in real-time
- **Settings**: Configure slippage, MEV protection, and safety limits
- **Performance**: Track success rate and total profits

### **🚀 AlphaSignals AutoTrade Dashboard**
The most advanced signal trading system:
- **AutoTrade Toggle**: Enable/disable automated signal trading
- **Position Settings**: Set max trade size and profit targets
- **Risk Management**: Configure stop losses and daily limits
- **Channel Filters**: Whitelist trusted sources, blacklist scams
- **Trailing Stops**: Exclusive liquidity-based exit strategy
- **Live Trades**: Monitor active positions and performance

### **🏆 Best Trades Dashboard**
Your market intelligence center:
- **24H Winners**: Top performing tokens by ROI
- **Smart Wallets**: Most profitable traders to follow
- **Trending Tokens**: Emerging opportunities
- **Performance Metrics**: Detailed analytics and insights
- **Copy Trading**: One-click strategy replication

### **👛 Wallet Setup Dashboard**
Secure wallet management made simple:
- **Create New**: Generate a new Solana wallet
- **Import Existing**: Add your existing wallet with custom name
- **Balance View**: Check SOL and token balances
- **QR Codes**: Generate deposit addresses
- **Security**: Export, backup, or disconnect wallets

## 🔥 **Exclusive Features**

### **⚡ Lightning-Fast Execution**
- **Sub-second latency** from signal detection to trade execution
- **MEV protection** ensures optimal transaction ordering
- **Multi-RPC failover** guarantees 99.9% uptime

### **🧠 AI-Powered Intelligence**
- **Rug detection** prevents trading scam tokens
- **Liquidity analysis** ensures tradeable positions
- **Confidence scoring** filters low-quality signals

### **📈 Exclusive Trailing Stops**
The industry's most advanced trailing stop system:
- **Liquidity-Based Calculations**: Stops adjust based on available liquidity
- **Volatility Adaptation**: Tighter stops in stable markets, wider in volatile
- **Real-Time Optimization**: Continuous adjustment as market conditions change
- **Maximum Profit Protection**: Locks in gains while allowing for continued upside

## ⚙️ **Quick Installation & Setup**

### **1. Install & Configure**
```bash
# Clone and setup
git clone https://github.com/Carl590/ai_trading_bot.git
cd ai_trading_bot
chmod +x setup.sh && ./setup.sh

# Configure environment
cp .env.example .env
# Add your Telegram bot token to .env file
```

### **2. Start Your Bot**
```bash
# Launch the bot
./venv/bin/python telegram_bot.py

# Or run in background
nohup ./venv/bin/python telegram_bot.py &
```

### **3. Setup Your First Wallet**
```
1. Message your bot: /start
2. Click: � Wallet Setup
3. Choose: Import Wallet
4. Name it: "Main Trading Wallet"
5. Paste your private key
6. Start trading! 🚀
```

## 🔧 **Configuration**

### **Environment Setup**
```bash
# Required in .env file
TELEGRAM_BOT_TOKEN=your_bot_token_here
WEBHOOK_SECRET_KEY=your_webhook_secret

# Optional API enhancements
SHYFT_API_KEY=your_shyft_key
HELIUS_API_KEY=your_helius_key
```

### **TradingView Webhook Configuration**
```javascript
// TradingView Alert Message Format
{
    "user_id": "YOUR_TELEGRAM_USER_ID",
    "action": "buy",
    "token": "CONTRACT_ADDRESS",
    "amount": 1.0
}
```

## � **Performance & Analytics**

### **Real-Time Monitoring**
- **Live P&L**: Instant profit/loss updates
- **Success Rates**: Win percentage tracking
- **Volume Analytics**: Total trading volume
- **Performance Metrics**: ROI and risk analysis

### **Advanced Analytics**
- **Best Performing Tokens**: 24-hour ROI leaders
- **Trending Signals**: Most active channels
- **Market Intelligence**: Emerging opportunities
- **Risk Assessment**: Portfolio health checks

## 🛡️ **Security & Safety**

### **Wallet Security**
- ✅ **Dedicated Trading Wallets**: Use separate wallets for automated trading
- ✅ **Small Start Amounts**: Begin with 0.1-0.5 SOL to test the system
- ✅ **Military-Grade Encryption**: All private keys encrypted with Fernet
- ✅ **Secure Backup**: Always keep offline backups of your keys
- ✅ **Regular Monitoring**: Check your positions and performance daily

### **Trading Safety**
- ✅ **Rug Protection**: Comprehensive token safety analysis before trades
- ✅ **Position Limits**: Set maximum position sizes to control risk
- ✅ **Daily Limits**: Protect against runaway losses with daily caps
- ✅ **Trailing Stops**: Use exclusive liquidity-based stop loss system
- ✅ **Signal Filtering**: Whitelist only trusted Telegram channels

### **Bot Security**
- ✅ **Private Bot Token**: Never share your Telegram bot token
- ✅ **Webhook Protection**: Use secret keys to prevent unauthorized access
- ✅ **Regular Updates**: Keep bot software updated for security patches
- ✅ **Activity Monitoring**: Watch logs for any suspicious activity
- ✅ **Environment Security**: Keep API keys and configs private

## 🎯 **FAQ & Troubleshooting**

### **Common Questions**

**Q: How much SOL do I need to start?**
A: Minimum 0.1 SOL recommended for testing. 1-5 SOL for active trading.

**Q: Is my private key safe?**
A: Yes! All keys are encrypted with military-grade Fernet encryption and stored locally.

**Q: Can I use multiple wallets?**
A: Absolutely! You can set up and name multiple wallets for different strategies.

**Q: How does the trailing stop work?**
A: Our exclusive system calculates optimal stops based on entry liquidity and market volatility.

**Q: What if the bot goes offline?**
A: The bot automatically saves state and resumes operations when restarted.

### **Getting Help**

- 📚 **In-Bot Help**: Use the ❓ Help section for complete guidance
- 💬 **Community Support**: Join our Telegram community
- 🐛 **Report Issues**: Use GitHub issues for bug reports
- 📧 **Direct Support**: Contact us for personalized assistance

## 🚀 **Advanced Usage**

### **Power User Features**
- **Multiple Strategy Wallets**: Separate wallets for different trading approaches
- **Custom Signal Sources**: Add your own trusted Telegram channels
- **API Integration**: Connect external tools and analytics
- **Performance Analytics**: Track detailed metrics and optimize strategies

### **Professional Trading**
- **Risk Management**: Advanced position sizing and stop-loss strategies
- **Market Intelligence**: Leverage Best Trades data for alpha discovery
- **Automation**: Full TradingView integration for strategy automation
- **Monitoring**: Real-time alerts and performance tracking

---

## 📄 **License & Support**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### **Support the Project**
If you find this bot useful, consider:
- ⭐ Starring the GitHub repository
- 🐛 Reporting bugs and issues
- 💡 Suggesting new features
- 🤝 Contributing code improvements

### **Disclaimer**
This bot is for educational and research purposes. Cryptocurrency trading involves substantial risk of loss. Always do your own research and never trade with funds you cannot afford to lose.

---

**🤖 Start your automated Solana trading journey today!**

**Ready to trade like a pro? Get started in 3 minutes:**
1. Clone the repo and run setup
2. Configure your bot token
3. Import your wallet and start trading!

*Transform your Solana trading with AI-powered automation.* 🚀
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

### **AlphaSignals AutoTrade Setup**
1. **Access Dashboard**
   ```
   /start → 🤖 AlphaSignals AutoTrade
   ```

2. **Configure Settings**
   ```
   Position Settings: Set trade size and profit targets
   Risk Settings: Configure rug check and trailing stops
   Channel Filters: Whitelist trusted signal channels
   ```

3. **Enable AutoTrade**
   ```
   Toggle AutoTrade → 🟢 ENABLED
   ```

### **AI Features Usage**
```python
# Manual Rug Check
from rug_checker import quick_rug_check

result = await quick_rug_check("TOKEN_ADDRESS")
if result.ok:
    print(f"✅ {result.recommendation}")
else:
    print(f"❌ Failed: {result.hard_fail_reasons}")

# AI Trading with Features
from trading_engine import TradingEngine, TradeOptions

options = TradeOptions(
    enable_rug_check=True,
    enable_trailing_stop=True,
    max_slippage_pct=0.01
)

result = await engine.execute_buy_with_ai(
    user_id="123456",
    token_address="TOKEN_ADDRESS", 
    amount_usd=100.0,
    options=options
)
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

## 🧠 **AI Features Deep Dive**

### **🔍 Rug Check System**
The comprehensive rug check system analyzes tokens for safety before trading:

```python
# Configuration
RugCheckConfig:
  max_tax_pct: 0.10             # Maximum buy/sell tax
  max_top10_pct: 0.35           # Maximum top 10 holder concentration
  require_lp_locked_or_burned: True  # LP must be locked/burned
  require_mint_revoked: True     # Mint authority must be revoked
  require_freeze_revoked: True   # Freeze authority must be revoked
  min_24h_volume_usd: 50000.0   # Minimum daily volume
  min_liquidity_usd: 100000.0   # Minimum liquidity
```

**Hard Requirements (Must Pass):**
- Mint authority revoked
- Freeze authority revoked
- LP tokens locked or burned
- Buy/sell tax below threshold
- No blacklist functionality
- Trading cannot be paused

**Soft Warnings (Risk Score):**
- Low liquidity or volume
- High holder concentration
- Very new token
- Suspicious patterns

### **📈 AI Trailing Stop Loss**
Advanced trailing stop system with liquidity awareness:

```python
# Configuration
TrailingStopConfig:
  z: 1.65                    # Confidence interval (1.65 = 90%)
  alpha: 1.8                 # Liquidity sensitivity
  beta: 1.0                  # Volatility weight
  floor_pct: 0.06           # Minimum stop (6%)
  ceiling_pct: 0.40         # Maximum stop (40%)
```

**Features:**
- Dynamic stop adjustment based on volatility
- Liquidity-aware calculations
- Real-time price monitoring
- Automatic position management
- State persistence across restarts

### **🤖 AlphaSignals AutoTrade**
Complete per-user automated trading system:

```python
# User Settings
AutoTradeSettings:
  max_position_usd: 100.0        # Maximum position size
  stop_loss_pct: 0.20           # 20% stop loss
  take_profit_pct: 0.50         # 50% take profit
  auto_sell_delay_sec: 300      # Auto-sell after 5 minutes
  rug_check_enabled: True       # Enable rug checking
  trailing_stop_enabled: True   # Enable trailing stops
  risk_limit_daily_usd: 500.0   # Daily risk limit
```

**Features:**
- Per-user configuration
- Signal parsing from channels
- Duplicate protection
- Channel whitelisting/blacklisting
- Risk management
- Real-time dashboard

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