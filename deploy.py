#!/usr/bin/env python3
"""
Production Deployment Script
Handles full system startup with monitoring
"""

import asyncio
import logging
import signal
import sys
import os
import time
from typing import Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class ProductionManager:
    """Manages production deployment and monitoring"""
    
    def __init__(self):
        self.running = True
        self.processes = {}
        self.start_time = datetime.now()
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.running = False
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive system health check"""
        try:
            from api_manager import api_manager
            from trading_engine import trading_engine
            from config_manager import config_manager
            
            health = {
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
                'status': 'healthy',
                'components': {}
            }
            
            # Check configuration
            config = config_manager.get_config()
            health['components']['config'] = {
                'bot_token': bool(config.telegram_bot_token),
                'webhook_key': bool(config.webhook_secret_key),
                'shyft_api': bool(config.shyft_api_key),
                'helius_api': bool(config.helius_api_key)
            }
            
            # Check API manager
            health['components']['api_manager'] = {
                'endpoints_loaded': len(api_manager.endpoints),
                'rpc_url': bool(api_manager.get_rpc_url()),
                'jupiter_endpoints': len(api_manager.get_jupiter_endpoints()),
                'mev_endpoints': len(api_manager.get_mev_endpoints())
            }
            
            # Check trading engine
            engine_health = await trading_engine.health_check()
            health['components']['trading_engine'] = engine_health
            
            # Overall status
            all_healthy = all(
                all(component.values()) if isinstance(component, dict) else component
                for component in health['components'].values()
            )
            
            if not all_healthy:
                health['status'] = 'degraded'
            
            return health
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def start_telegram_bot(self):
        """Start the main Telegram bot"""
        try:
            logger.info("🤖 Starting Telegram bot...")
            
            from telegram_bot import TelegramTradingBot
            from config_manager import config_manager
            
            config = config_manager.get_config()
            bot = TelegramTradingBot(config.telegram_bot_token)
            
            # Store bot instance
            self.processes['telegram_bot'] = bot
            
            # Start bot
            await bot.start()
            logger.info("✅ Telegram bot started successfully")
            
            # Keep bot running
            while self.running:
                await asyncio.sleep(1)
            
            # Stop bot
            await bot.stop()
            logger.info("🛑 Telegram bot stopped")
            
        except Exception as e:
            logger.error(f"❌ Telegram bot failed: {e}")
            raise
    
    async def start_group_bot(self):
        """Start the group bot for auto-dashboard"""
        try:
            logger.info("👥 Starting group bot...")
            
            from group_bot import GroupTradingBot
            from config_manager import config_manager
            
            config = config_manager.get_config()
            group_bot = GroupTradingBot(config.telegram_bot_token)
            
            # Store bot instance
            self.processes['group_bot'] = group_bot
            
            # Start group bot
            await group_bot.start()
            logger.info("✅ Group bot started successfully")
            
            # Keep running
            while self.running:
                await asyncio.sleep(1)
            
            # Stop bot
            await group_bot.stop()
            logger.info("🛑 Group bot stopped")
            
        except Exception as e:
            logger.error(f"❌ Group bot failed: {e}")
            raise
    
    async def start_webhook_server(self):
        """Start the Flask webhook server"""
        try:
            logger.info("🪝 Starting webhook server...")
            
            from webhook_handler import create_webhook_app
            from config_manager import config_manager
            
            app = create_webhook_app(config_manager)
            
            # Store app instance
            self.processes['webhook_server'] = app
            
            # Run Flask app
            app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
            logger.info("✅ Webhook server started on port 5000")
            
        except Exception as e:
            logger.error(f"❌ Webhook server failed: {e}")
            raise
    
    async def monitor_system(self):
        """Monitor system health and performance"""
        try:
            logger.info("📊 Starting system monitor...")
            
            while self.running:
                # Run health check every 30 seconds
                health = await self.health_check()
                
                # Log status
                status = health.get('status', 'unknown')
                uptime = health.get('uptime_seconds', 0)
                
                logger.info(f"🏥 System status: {status.upper()} | Uptime: {uptime:.0f}s")
                
                # Log component status
                for component, status_data in health.get('components', {}).items():
                    if isinstance(status_data, dict):
                        healthy_count = sum(1 for v in status_data.values() if v)
                        total_count = len(status_data)
                        logger.info(f"  📋 {component}: {healthy_count}/{total_count} healthy")
                    else:
                        logger.info(f"  📋 {component}: {'✅' if status_data else '❌'}")
                
                # Wait before next check
                await asyncio.sleep(30)
                
        except Exception as e:
            logger.error(f"❌ System monitor failed: {e}")
    
    async def deploy_single_bot(self):
        """Deploy only the main Telegram bot (recommended for single instance)"""
        logger.info("🚀 Deploying Single Bot Configuration")
        logger.info("=" * 60)
        
        try:
            # Run initial health check
            health = await self.health_check()
            logger.info(f"🏥 Initial health status: {health['status']}")
            
            # Start components concurrently
            tasks = []
            
            # Always start the main bot
            tasks.append(asyncio.create_task(self.start_telegram_bot()))
            
            # Start webhook server
            tasks.append(asyncio.create_task(self.start_webhook_server()))
            
            # Start monitoring
            tasks.append(asyncio.create_task(self.monitor_system()))
            
            logger.info("✅ All components started successfully")
            logger.info("🎯 Bot is ready to receive commands and webhooks")
            
            # Wait for tasks to complete or shutdown
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            raise
        finally:
            logger.info("🛑 Deployment shutdown complete")
    
    async def deploy_full_system(self):
        """Deploy full system with separate group bot"""
        logger.info("🚀 Deploying Full System Configuration")
        logger.info("=" * 60)
        
        try:
            # Run initial health check
            health = await self.health_check()
            logger.info(f"🏥 Initial health status: {health['status']}")
            
            # Start all components
            tasks = [
                asyncio.create_task(self.start_telegram_bot()),
                asyncio.create_task(self.start_group_bot()),
                asyncio.create_task(self.start_webhook_server()),
                asyncio.create_task(self.monitor_system())
            ]
            
            logger.info("✅ All components started successfully")
            logger.info("🎯 Full system is operational")
            
            # Wait for tasks to complete or shutdown
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ Full deployment failed: {e}")
            raise
        finally:
            logger.info("🛑 Full system shutdown complete")

async def main():
    """Main deployment entry point"""
    print("🚀 TRADING BOT PRODUCTION DEPLOYMENT")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Get deployment mode from command line
    deployment_mode = sys.argv[1] if len(sys.argv) > 1 else "single"
    
    if deployment_mode not in ["single", "full"]:
        print("❌ Invalid deployment mode. Use 'single' or 'full'")
        print("   • single: Main bot only (recommended)")
        print("   • full:   Main bot + Group bot (advanced)")
        sys.exit(1)
    
    print(f"🎯 Deployment Mode: {deployment_mode.upper()}")
    
    manager = ProductionManager()
    
    try:
        if deployment_mode == "single":
            await manager.deploy_single_bot()
        else:
            await manager.deploy_full_system()
    
    except KeyboardInterrupt:
        logger.info("👋 Received shutdown signal")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)
    
    print(f"\n🕐 Deployment ended at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("👋 Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())