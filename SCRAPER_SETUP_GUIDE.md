# Solana Telegram Contract Scraper Setup Guide

## Overview

The Solana Telegram Contract Scraper monitors Telegram groups for new Solana SPL token contract addresses and automatically extracts them with advanced confidence scoring. It's specifically optimized for Solana ecosystem tokens and can integrate with your trading bot for automatic execution.

## Features

- 🔍 **Real-time Monitoring**: Watches multiple Telegram groups simultaneously for Solana tokens
- 🤖 **AI Filtering**: Uses Solana-specific confidence scoring to filter high-quality contracts
- 💎 **Solana-Focused**: Specialized detection and validation for SPL tokens only
- 🎯 **Auto-trading**: Can automatically trade high-confidence Solana contracts
- 📊 **Analytics**: Tracks performance with Solana-specific metrics (decimals, authorities, etc.)
- 🔔 **Alerts**: Sends Solana contract notifications to your main trading bot

## Quick Start

### 1. Initial Setup

```bash
# Navigate to your bot directory
cd "/Users/carlsorensen/Documents/Trading Bots/TradingView-To Telegram-Autobuy:-sell"

# Make scripts executable
chmod +x scraper_manager.py telegram_scraper.py
```

### 2. Add Groups to Monitor

```bash
# Add a group by invite link
./venv/bin/python scraper_manager.py add-group "https://t.me/cryptosignals" --group-name "Crypto Signals"

# Add a group by username
./venv/bin/python scraper_manager.py add-group "@solanagemfinder" --group-name "Solana Gems"

# Add a private group (you must be a member)
./venv/bin/python scraper_manager.py add-group "https://t.me/+ABC123xyz" --group-name "Private Alpha"
```

### 3. Start the Scraper

```bash
# Start in foreground (for testing)
./venv/bin/python scraper_manager.py start

# Start in background (production)
nohup ./venv/bin/python telegram_scraper.py > scraper.log 2>&1 &
```

### 4. Monitor Results

```bash
# View found contracts
./venv/bin/python scraper_manager.py contracts

# View statistics
./venv/bin/python scraper_manager.py stats

# View monitored groups
./venv/bin/python scraper_manager.py list-groups
```

## Configuration

### Group Configuration

Edit `scraper_groups.json` to customize group settings:

```json
{
  "groups": [
    {
      "group_id": -1001234567890,
      "group_name": "Alpha Calls",
      "enabled": true,
      "auto_trade": false,
      "min_confidence": 0.8
    }
  ]
}
```

### Scraper Settings

Key configuration options:

- **min_confidence**: Minimum confidence score (0.0 - 1.0) to save contracts
- **auto_trade**: Enable automatic trading for high-confidence contracts
- **enabled**: Enable/disable monitoring for specific groups

## API Credentials

The scraper uses your Telegram API credentials:

- **API ID**: `24093084` (already configured)
- **API Hash**: `82fd0c45ae1987a6fcccf7248e7fc528` (already configured)

On first run, you'll need to:
1. Enter your phone number
2. Enter the verification code sent by Telegram
3. The session will be saved for future use

## Solana Contract Detection

The scraper automatically detects Solana SPL tokens:

### Solana Token Addresses
- Format: 32-44 character Base58 strings (typically 43-44 chars for tokens)
- Validation: Advanced Base58 character set validation
- Filtering: Excludes known program IDs and system accounts
- Example: `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` (USDC)

### Token Information Extraction
- **Symbols**: `$SYMBOL`, `CA: SYMBOL`, `SYMBOL mint/token`
- **Decimals**: Extracts decimal precision (defaults to 9 for Solana)
- **Technical Details**: Mint authority, freeze authority information
- **Context Analysis**: Detects launch announcements, presales, etc.

## Solana-Specific Confidence Scoring

Contracts are scored using Solana ecosystem indicators:

### Positive Indicators (+points)
- **Solana Keywords**: "solana", "spl token", "raydium", "jupiter" (+0.15)
- **Launch Terms**: "new token", "stealth launch", "fair launch", "mint address" (+0.1)
- **Technical Details**: "decimals", "supply", "liquidity pool", "mint authority" (+0.05)
- **Valid Symbol**: 2-6 character token symbol (+0.25)
- **Address Format**: 43-44 character Base58 addresses (+0.15)
- **Context**: "pump.fun", "dexscreener", "birdeye", "bonding curve" (+0.1)

### Negative Indicators (-points)
- **Major Red Flags**: "rug", "rugpull", "scam", "honeypot" (-0.4)
- **Warning Signs**: "dump", "frozen", "blacklist", "high tax" (-0.2)
- **Suspicious Patterns**: Too many repeated characters, non-Base58 chars

### Score Ranges (Solana-Optimized)
- **0.8-1.0**: High confidence Solana token (auto-trade eligible)
- **0.6-0.8**: Medium confidence (manual review recommended)
- **0.4-0.6**: Low confidence (proceed with caution)
- **0.0-0.4**: Very low confidence (likely false positive)

## Integration with Trading Bot

The scraper integrates with your main Telegram trading bot:

### Automatic Alerts
When high-confidence contracts are found, users with AI trading enabled receive:
```
🔍 New Contract Found

💎 Address: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
🏷️ Symbol: $GEMS  
🌐 Network: Solana
📍 Source: Alpha Calls
⭐ Confidence: 85%
🕒 Found: 14:30:25

💬 Context: "New gem launching! Contract: EPjF..."
```

### Auto-trading
For contracts with >80% confidence:
- Automatically executes buy orders
- Uses default amount (0.1 SOL)
- Only for users with auto-trade enabled
- Integrates with MEV protection

## File Structure

```
found_contracts.json     # Database of found contracts
scraper_groups.json      # Group configuration
scraper_session.session  # Telegram API session
telegram_scraper.py      # Main scraper script
scraper_manager.py       # Management interface
```

## Troubleshooting

### Common Issues

**"Flood wait" errors**
- Telegram rate limiting - wait and retry
- Reduce the number of groups monitored

**"Auth key unregistered"**
- Delete `scraper_session.session` file
- Re-authenticate with phone number

**No contracts found**
- Check group activity levels
- Verify groups are cryptocurrency-related
- Lower confidence threshold temporarily

**Import errors**
- Ensure virtual environment is activated
- Install missing dependencies: `pip install telethon`

### Logs and Debugging

```bash
# View scraper logs
tail -f telegram_scraper.log

# Debug mode
./venv/bin/python telegram_scraper.py --debug

# Check process status
./venv/bin/python process_manager.py status
```

## Advanced Usage

### Custom Filtering

Edit `telegram_scraper.py` to customize:
- Address validation patterns
- Symbol extraction rules  
- Confidence scoring algorithm
- Network support

### API Integration

The scraper can be extended to:
- Validate contracts using RPC calls
- Get token metadata automatically
- Check liquidity and market cap
- Integrate with additional APIs

### Performance Optimization

For high-volume monitoring:
- Use multiple scraper instances
- Implement database storage
- Add caching for repeated addresses
- Use async processing for API calls

## Security Considerations

- Store API credentials securely
- Monitor resource usage
- Set rate limits appropriately
- Review contracts before trading
- Never share session files

## Support

For issues or questions:
1. Check the logs first
2. Review this documentation
3. Test with a single group
4. Verify API credentials
5. Check network connectivity