"""
Main Application - Telegram Trading Bot with TradingView Integration
Combines Telegram Bot, Webhook Handler, and Trading Features
"""

import asyncio
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
import signal
import sys

from telegram_bot import TelegramTradingBot
from webhook_handler import webhook_app, initialize_webhook_handler
from best_trades_monitor import best_trades_monitor

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TradingBotApplication:
    def __init__(self, telegram_token: str, webhook_port: int = 8080):
        self.telegram_token = telegram_token
        self.webhook_port = webhook_port
        self.telegram_bot = None
        self.webhook_thread = None
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.running = False
        
    def start(self):
        """Start the complete trading bot application"""
        logger.info("🚀 Starting Telegram Trading Bot Application...")
        
        try:
            # Initialize Telegram Bot
            logger.info("🤖 Initializing Telegram Bot...")
            self.telegram_bot = TelegramTradingBot(self.telegram_token)
            
            # Initialize Webhook Handler
            logger.info("🔗 Initializing Webhook Handler...")
            initialize_webhook_handler(self.telegram_bot)
            
            # Start webhook server in a separate thread
            logger.info(f"🌐 Starting Webhook Server on port {self.webhook_port}...")
            self.webhook_thread = threading.Thread(
                target=self._run_webhook_server,
                daemon=True
            )
            self.webhook_thread.start()
            
            # Update best trades monitor with telegram bot reference
            self._setup_best_trades_integration()
            
            # Setup graceful shutdown
            self._setup_signal_handlers()
            
            self.running = True
            logger.info("✅ All services started successfully!")
            logger.info("🔥 Trading Bot is now LIVE and ready for action!")
            logger.info(f"📡 Webhook endpoint: http://localhost:{self.webhook_port}/webhook")
            logger.info("📱 Telegram bot is running... Send /start to begin trading!")
            
            # Start Telegram Bot (this will block)
            self.telegram_bot.run()
            
        except Exception as e:
            logger.error(f"❌ Failed to start application: {e}")
            self.stop()
    
    def _run_webhook_server(self):
        """Run Flask webhook server"""
        try:
            webhook_app.run(
                host="0.0.0.0",
                port=self.webhook_port,
                debug=False,
                use_reloader=False
            )
        except Exception as e:
            logger.error(f"Webhook server error: {e}")
    
    def _setup_best_trades_integration(self):
        """Setup integration with best trades monitor"""
        # You can add periodic updates here
        pass
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown on SIGINT/SIGTERM"""
        def signal_handler(sig, frame):
            logger.info("🛑 Received shutdown signal...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def stop(self):
        """Stop all services gracefully"""
        logger.info("⏹️ Stopping Trading Bot Application...")
        
        self.running = False
        
        if self.telegram_bot:
            logger.info("🤖 Stopping Telegram Bot...")
            try:
                self.telegram_bot.application.stop()
            except:
                pass
        
        if self.executor:
            logger.info("🔧 Shutting down thread executor...")
            self.executor.shutdown(wait=True)
        
        logger.info("✅ Application stopped successfully!")

def main():
    """Main entry point"""
    # Configuration
    TELEGRAM_BOT_TOKEN = "8482815083:AAHFqxiPCt0eZ6GjD8cahnAzXlA4ql3z9qk"  # Replace with your bot token
    WEBHOOK_PORT = 8080
    
    # Validate configuration
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        logger.error("❌ Please set your Telegram Bot Token in the configuration!")
        logger.info("📝 Get your bot token from @BotFather on Telegram")
        return
    
    # Create and start application
    app = TradingBotApplication(
        telegram_token=TELEGRAM_BOT_TOKEN,
        webhook_port=WEBHOOK_PORT
    )
    
    try:
        app.start()
    except KeyboardInterrupt:
        logger.info("👋 Received keyboard interrupt...")
    except Exception as e:
        logger.error(f"💥 Application crashed: {e}")
    finally:
        app.stop()

if __name__ == "__main__":
    # Display startup banner
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                  🤖 TELEGRAM TRADING BOT 🤖                  ║
    ║                                                              ║
    ║                    Maestro Style Dashboard                   ║
    ║                  TradingView Integration                     ║
    ║                   Solana Auto Trading                       ║
    ║                                                              ║
    ║  Features:                                                   ║
    ║  ✅ AI Auto Trading                                          ║
    ║  ✅ Best Trades Monitor                                      ║
    ║  ✅ Wallet Management                                        ║
    ║  ✅ Real-time PnL Tracking                                   ║
    ║  ✅ TradingView Webhooks                                     ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)
    
    main()