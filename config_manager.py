"""
Configuration Management for Telegram Trading Bot
"""

import os
from typing import Optional
from pydantic import Field
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class TradingBotConfig(BaseSettings):
    """Configuration settings for the trading bot"""
    
    # Telegram Bot Settings
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    telegram_allowed_users: list = Field(default=[], env="TELEGRAM_ALLOWED_USERS")
    
    # Webhook Settings
    webhook_host: str = Field(default="0.0.0.0", env="WEBHOOK_HOST")
    webhook_port: int = Field(default=8080, env="WEBHOOK_PORT")
    webhook_secret_key: str = Field(default="", env="WEBHOOK_SECRET_KEY")
    
    # Solana RPC Settings (now managed by API Manager)
    solana_rpc_url: str = Field(
        default="https://rpc.shyft.to?api_key=7Rt0hE2MGrr0R668",
        env="SOLANA_RPC_URL"
    )
    solana_rpc_timeout: int = Field(default=30, env="SOLANA_RPC_TIMEOUT")
    
    # Jupiter Aggregator Settings
    jupiter_api_url: str = Field(
        default="https://quote-api.jup.ag/v6",
        env="JUPITER_API_URL"
    )
    
    # API Keys for premium services
    shyft_api_key: str = Field(default="7Rt0hE2MGrr0R668", env="SHYFT_API_KEY")
    helius_api_key: str = Field(default="cd716db1-6133-46b4-9f2f-59f5b72c329b", env="HELIUS_API_KEY")
    
    # MEV Protection Settings
    enable_mev_protection: bool = Field(default=True, env="ENABLE_MEV_PROTECTION")
    zeroslot_api_key: str = Field(default="ca6fc089f334462e90d47012d2a17b9c", env="ZEROSLOT_API_KEY")
    nozomi_uuid: str = Field(default="4516a74a-ad06-4faf-9de4-10cce6e37f6b", env="NOZOMI_UUID")
    
    # Trading Settings
    default_slippage_bps: int = Field(default=100, env="DEFAULT_SLIPPAGE_BPS")  # 1%
    default_trade_amount_sol: float = Field(default=0.01, env="DEFAULT_TRADE_AMOUNT_SOL")
    max_trade_amount_sol: float = Field(default=1.0, env="MAX_TRADE_AMOUNT_SOL")
    min_trade_amount_sol: float = Field(default=0.001, env="MIN_TRADE_AMOUNT_SOL")
    
    # Risk Management
    daily_loss_limit_sol: float = Field(default=0.1, env="DAILY_LOSS_LIMIT_SOL")
    max_positions_per_user: int = Field(default=10, env="MAX_POSITIONS_PER_USER")
    emergency_stop_loss_percent: float = Field(default=-50.0, env="EMERGENCY_STOP_LOSS_PERCENT")
    
    # API Keys for external services
    birdeye_api_key: Optional[str] = Field(default=None, env="BIRDEYE_API_KEY")
    dexscreener_api_key: Optional[str] = Field(default=None, env="DEXSCREENER_API_KEY")
    coingecko_api_key: Optional[str] = Field(default=None, env="COINGECKO_API_KEY")
    
    # Database Settings (for user data persistence)
    database_url: str = Field(
        default="sqlite:///trading_bot.db",
        env="DATABASE_URL"
    )
    
    # Logging Settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="trading_bot.log", env="LOG_FILE")
    
    # Security Settings
    rate_limit_per_minute: int = Field(default=30, env="RATE_LIMIT_PER_MINUTE")
    session_timeout_hours: int = Field(default=24, env="SESSION_TIMEOUT_HOURS")
    
    # Notification Settings
    send_trade_notifications: bool = Field(default=True, env="SEND_TRADE_NOTIFICATIONS")
    send_error_notifications: bool = Field(default=True, env="SEND_ERROR_NOTIFICATIONS")
    send_daily_summary: bool = Field(default=True, env="SEND_DAILY_SUMMARY")
    
    # Performance Settings
    price_update_interval_seconds: int = Field(default=30, env="PRICE_UPDATE_INTERVAL_SECONDS")
    best_trades_refresh_minutes: int = Field(default=5, env="BEST_TRADES_REFRESH_MINUTES")
    
    # Feature Flags
    enable_ai_trading: bool = Field(default=True, env="ENABLE_AI_TRADING")
    enable_best_trades: bool = Field(default=True, env="ENABLE_BEST_TRADES")
    enable_copy_trading: bool = Field(default=False, env="ENABLE_COPY_TRADING")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global configuration instance
config = TradingBotConfig()

def get_config() -> TradingBotConfig:
    """Get the global configuration instance"""
    return config

def validate_config() -> list:
    """Validate configuration and return list of errors if any"""
    errors = []
    
    # Required fields validation
    if not config.telegram_bot_token or config.telegram_bot_token == "YOUR_TELEGRAM_BOT_TOKEN":
        errors.append("❌ TELEGRAM_BOT_TOKEN is required! Get it from @BotFather")
    
    if config.webhook_secret_key == "":
        errors.append("⚠️  WEBHOOK_SECRET_KEY is not set - webhook will be less secure")
    
    # Range validations
    if config.default_slippage_bps < 1 or config.default_slippage_bps > 1000:
        errors.append("❌ DEFAULT_SLIPPAGE_BPS must be between 1 and 1000")
    
    if config.default_trade_amount_sol <= 0:
        errors.append("❌ DEFAULT_TRADE_AMOUNT_SOL must be positive")
    
    if config.max_trade_amount_sol < config.min_trade_amount_sol:
        errors.append("❌ MAX_TRADE_AMOUNT_SOL must be >= MIN_TRADE_AMOUNT_SOL")
    
    # URL validations
    if not config.solana_rpc_url.startswith(("http://", "https://")):
        errors.append("❌ SOLANA_RPC_URL must be a valid HTTP/HTTPS URL")
    
    if not config.jupiter_api_url.startswith(("http://", "https://")):
        errors.append("❌ JUPITER_API_URL must be a valid HTTP/HTTPS URL")
    
    return errors

def print_config_summary():
    """Print a summary of the current configuration"""
    print("🔧 Configuration Summary:")
    print(f"  📱 Telegram Bot: {'✅ Configured' if config.telegram_bot_token else '❌ Missing Token'}")
    print(f"  🌐 Webhook Port: {config.webhook_port}")
    print(f"  🔗 Solana RPC: {config.solana_rpc_url}")
    print(f"  💰 Default Trade: {config.default_trade_amount_sol} SOL")
    print(f"  📊 Slippage: {config.default_slippage_bps/100:.1f}%")
    print(f"  🛡️  Daily Loss Limit: {config.daily_loss_limit_sol} SOL")
    print(f"  🚨 Emergency Stop: {config.emergency_stop_loss_percent}%")
    print(f"  📈 AI Trading: {'✅ Enabled' if config.enable_ai_trading else '❌ Disabled'}")
    print(f"  🏆 Best Trades: {'✅ Enabled' if config.enable_best_trades else '❌ Disabled'}")

if __name__ == "__main__":
    # Test configuration loading
    print("Testing Configuration...")
    
    errors = validate_config()
    if errors:
        print("❌ Configuration Errors:")
        for error in errors:
            print(f"  {error}")
    else:
        print("✅ Configuration is valid!")
    
    print_config_summary()