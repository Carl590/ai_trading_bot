# Advanced Solana Trading Bot with Telegram Scraper

A comprehensive Solana trading ecosystem with AI-powered automation, contract scraping, and professional-grade execution.

## 🌟 Key Features

### 🤖 AI Trading Bot
- **Maestro-style Dashboard**: Clean, inline interface
- **Real-time Portfolio**: Live PnL tracking and analytics  
- **MEV Protection**: Multiple protection services (ZeroSlot, Nozomi, NextBlock)
- **Multi-RPC Failover**: Automatic switching between Shyft, Helius, and public RPCs
- **Advanced Slippage**: Dynamic slippage management

### 🔍 Contract Scraper  
- **Multi-group Monitoring**: Monitor unlimited Telegram groups
- **AI Contract Detection**: Solana & Ethereum address extraction
- **Confidence Scoring**: Filter quality contracts (70%+ accuracy)
- **Auto-trading Integration**: Execute trades on high-confidence finds
- **Real-time Alerts**: Instant notifications for new contracts

### 📊 Analytics & Monitoring
- **Best Trades Tracker**: Monitor top-performing wallets
- **Performance Analytics**: Detailed success rate metrics
- **Health Monitoring**: System-wide health checks
- **Trading Statistics**: Comprehensive performance data

### 🌐 Professional Infrastructure
- **20+ API Integrations**: Jupiter, Shyft, Helius, MEV services
- **Production Deployment**: Full production management scripts
- **Process Management**: Advanced process monitoring and control
- **Comprehensive Testing**: Full system test suite

## 🚀 Quick Start

### 1. Installation
```bash
# Clone and setup
git clone <repository>
cd "TradingView-To Telegram-Autobuy:-sell"

# Run setup script
chmod +x setup.sh
./setup.sh
```

### 2. Configuration
```bash
# Configure your API keys in .env
cp .env.example .env
nano .env
```

Required environment variables:
```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=8482815083:AAHFqxiPCt0eZ6GjD8cahnAzXlA4ql3z9qk
TELEGRAM_GROUP_LINK=https://t.me/+idISjNudRgVhYzUy

# Webhook
WEBHOOK_SECRET_KEY=trading-bot-secure-key-2025

# Premium APIs
SHYFT_API_KEY=7Rt0hE2MGrr0R668
HELIUS_API_KEY=cd716db1-6133-46b4-9f2f-59f5b72c329b
```

### 3. Start Trading Bot
```bash
# Test the system
./venv/bin/python test_system.py

# Deploy single bot (recommended)
./venv/bin/python deploy.py single

# Or deploy full system
./venv/bin/python deploy.py full
```

### 4. Setup Contract Scraper
```bash
# Add groups to monitor
./venv/bin/python scraper_manager.py add-group "https://t.me/cryptosignals" --group-name "Crypto Signals"

# Start scraper
./venv/bin/python scraper_manager.py start
```

## 📱 Telegram Bot Usage

### Main Dashboard
Send `/start` to access your personal trading dashboard:

```
🤖 TRADING DASHBOARD

💰 Wallet Status: ✅ Connected  
🏦 Balance: 2.5432 SOL
🎯 AI Trading: 🟢 Active

📊 Quick Stats:
• Total Trades: 15
• Success Rate: 87%
• Total PnL: +1.23 SOL

🚀 Ready to trade!
```

### AI Trading Controls
- **🟢 Start AI**: Enable automatic trading
- **🔴 Stop AI**: Disable automatic trading  
- **📊 Monitor**: View trading activity
- **⚙️ Settings**: Configure parameters

### Contract Scraper Interface
- **📋 View Contracts**: See recently found contracts
- **📱 Manage Groups**: Add/remove monitored groups
- **⚙️ Settings**: Configure confidence thresholds
- **🚀 Start Scraper**: Launch monitoring

## 🔗 TradingView Integration

### Webhook Endpoint
```
POST https://your-domain.com/webhook
```

### Alert Format
```json
{
    "key": "trading-bot-secure-key-2025",
    "user_id": "YOUR_TELEGRAM_USER_ID",
    "msg": "buy EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
}
```

### Supported Actions
- `buy <contract_address>` - Execute buy order
- `sell <contract_address>` - Execute sell order  
- `buy <contract_address> <amount>` - Buy specific amount

## 🔍 Contract Scraper Features

### Automatic Detection
The scraper monitors Telegram groups and automatically detects:

**Solana Contracts** (32-44 chars)
```
EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
```

**Ethereum Contracts** (42 chars, 0x prefix)  
```
0xA0b86a33E6441b1008A5df7D78e36C2DCA0b7A7e
```

### Confidence Scoring
Contracts are scored 0-100% based on:
- **Positive signals**: "new token", "launch", "CA:", token symbols
- **Negative signals**: "scam", "rug", "fake", warnings
- **Context analysis**: Message relevance and formatting

### Auto-trading Thresholds
- **80%+**: Auto-trade eligible (if enabled)
- **70-79%**: High confidence (manual review)  
- **50-69%**: Medium confidence (caution)
- **<50%**: Low confidence (ignore)

## 🏗️ Architecture

### Core Components
```
📁 Trading Bot System
├── 🤖 telegram_bot.py          # Main bot interface
├── 🔍 telegram_scraper.py      # Contract monitoring  
├── 🚀 trading_engine.py        # Trade execution
├── 🌐 api_manager.py           # API management
├── 📊 best_trades_monitor.py   # Analytics
├── 🪝 webhook_handler.py       # TradingView integration
├── ⚙️ config_manager.py        # Configuration
└── 🎛️ deploy.py               # Production management
```

### API Integration (20+ Endpoints)
- **Jupiter Aggregator**: Swap routing and execution
- **Shyft API**: Premium RPC and analytics  
- **Helius API**: Enhanced RPC with gRPC
- **MEV Protection**: ZeroSlot, Nozomi, NextBlock
- **Public RPCs**: Fallback endpoints

### Database Files
```
📁 Data Storage
├── 📋 found_contracts.json     # Scraped contracts database
├── 🏆 best_trades.json         # Top performer tracking
├── ⚙️ scraper_groups.json      # Group configurations  
├── 👥 user_configs.json        # User wallet data
└── 📊 trading_stats.json       # Performance metrics
```

## 🛠️ Advanced Configuration

### Scraper Groups Setup
```json
{
  "groups": [
    {
      "group_id": -1001234567890,
      "group_name": "Alpha Calls", 
      "enabled": true,
      "auto_trade": true,
      "min_confidence": 0.8
    }
  ]
}
```

### Trading Engine Settings
```python
# MEV Protection
ENABLE_MEV_PROTECTION = True
DEFAULT_COMPUTE_UNIT_PRICE = 200000
DEFAULT_COMPUTE_UNIT_LIMIT = 200000

# Trading Parameters  
DEFAULT_SLIPPAGE_BPS = 300  # 3%
MAX_RETRIES = 3
API_TIMEOUT = 30
RPC_TIMEOUT = 30
```

### API Manager Configuration
All endpoints are centrally managed with:
- Automatic failover
- Rate limit handling  
- Health monitoring
- Performance tracking

## 📊 Management Commands

### System Management
```bash
# System health check
./venv/bin/python test_system.py

# Process management
./venv/bin/python process_manager.py status
./venv/bin/python process_manager.py clean

# Production deployment
./venv/bin/python deploy.py single
```

### Scraper Management
```bash
# View statistics
./venv/bin/python scraper_manager.py stats

# Manage groups
./venv/bin/python scraper_manager.py list-groups
./venv/bin/python scraper_manager.py add-group <link>

# View found contracts
./venv/bin/python scraper_manager.py contracts --limit 50
```

## 🔐 Security Features

### Authentication
- Telegram Bot API authentication
- Webhook secret key verification
- User wallet encryption
- Session management

### MEV Protection
- ZeroSlot integration  
- Nozomi MEV protection
- NextBlock submissions
- Priority fee optimization

### Rate Limiting
- API request throttling
- Telegram message limits
- Scraper flood protection
- Error handling and backoff

## 📈 Performance Optimization

### RPC Optimization
- Primary/backup RPC switching
- Connection pooling
- Timeout management  
- Health monitoring

### Trading Execution
- Jupiter route optimization
- Slippage minimization
- MEV protection
- Transaction prioritization

### Scraper Efficiency  
- Real-time event handling
- Duplicate filtering
- Confidence-based processing
- Resource management

## 🐛 Troubleshooting

### Common Issues

**Bot not responding**
```bash
# Check process status
./venv/bin/python process_manager.py status

# Clean and restart
./venv/bin/python process_manager.py clean
./venv/bin/python deploy.py single
```

**Scraper not finding contracts**
```bash
# Check groups
./venv/bin/python scraper_manager.py list-groups

# View logs  
tail -f telegram_scraper.log

# Test with lower confidence
# Edit scraper_groups.json, set min_confidence: 0.3
```

**Trading failures**
```bash
# Check API health
./venv/bin/python test_system.py

# Verify wallet setup in Telegram bot
# Check RPC endpoints in api_manager.py
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
./venv/bin/python telegram_bot.py --debug
./venv/bin/python telegram_scraper.py --debug
```

## 📋 Project Status

### ✅ Completed Features
- [x] Full Maestro-style Telegram bot
- [x] Advanced contract scraper with AI filtering  
- [x] Comprehensive API management (20+ endpoints)
- [x] MEV-protected trading execution
- [x] TradingView webhook integration
- [x] Group bot with auto-dashboard
- [x] Production deployment system
- [x] Complete monitoring and analytics

### 🔄 Current Status  
- System fully integrated and tested
- All major components operational
- Production-ready deployment
- Comprehensive documentation

### 🚀 Next Steps
1. **Deploy to Production**: Use `deploy.py` for full deployment
2. **Add Trading Groups**: Configure groups for scraper monitoring  
3. **Set Up Webhooks**: Connect TradingView alerts
4. **Monitor Performance**: Use analytics dashboard
5. **Scale as Needed**: Add more groups and users

## 📞 Support

For issues or questions:
1. Check logs: `tail -f *.log`
2. Run health check: `python test_system.py`  
3. Review documentation in `/docs`
4. Check configuration files
5. Verify API credentials and limits

## 📜 License

MIT License - feel free to use and modify for your trading needs.

---

**⚠️ Disclaimer**: This bot is for educational purposes. Always test with small amounts and understand the risks of automated trading. Cryptocurrency trading carries significant financial risk.