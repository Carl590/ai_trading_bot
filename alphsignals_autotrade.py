"""
AlphaSignals AutoTrade Dashboard for Telegram Bot
Complete per-user signal trading with advanced controls
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
import logging
import asyncio
import json
import re
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
import aiofiles
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class AutoTradeSettings:
    """Per-user AutoTrade configuration"""
    user_id: int
    enabled: bool = False
    max_position_usd: float = 100.0
    stop_loss_pct: float = 0.20  # 20% stop loss
    take_profit_pct: float = 0.50  # 50% take profit
    auto_sell_delay_sec: int = 300  # 5 minutes default
    rug_check_enabled: bool = True
    trailing_stop_enabled: bool = True
    risk_limit_daily_usd: float = 500.0
    whitelist_channels: Set[str] = field(default_factory=set)
    blacklist_tokens: Set[str] = field(default_factory=set)
    duplicate_protection_hours: int = 24
    
    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "enabled": self.enabled,
            "max_position_usd": self.max_position_usd,
            "stop_loss_pct": self.stop_loss_pct,
            "take_profit_pct": self.take_profit_pct,
            "auto_sell_delay_sec": self.auto_sell_delay_sec,
            "rug_check_enabled": self.rug_check_enabled,
            "trailing_stop_enabled": self.trailing_stop_enabled,
            "risk_limit_daily_usd": self.risk_limit_daily_usd,
            "whitelist_channels": list(self.whitelist_channels),
            "blacklist_tokens": list(self.blacklist_tokens),
            "duplicate_protection_hours": self.duplicate_protection_hours
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AutoTradeSettings':
        settings = cls(user_id=data["user_id"])
        for key, value in data.items():
            if key in ["whitelist_channels", "blacklist_tokens"]:
                setattr(settings, key, set(value))
            else:
                setattr(settings, key, value)
        return settings

@dataclass 
class TradeSignal:
    """Parsed trade signal from channel"""
    token_address: str
    token_symbol: str
    channel_name: str
    signal_text: str
    confidence: float
    timestamp: datetime
    buy_price: Optional[float] = None
    target_price: Optional[float] = None
    market_cap: Optional[float] = None

@dataclass
class DuplicateTracker:
    """Track duplicate buys per user"""
    user_id: int
    recent_tokens: Dict[str, datetime] = field(default_factory=dict)
    
    def is_duplicate(self, token_addr: str, hours: int = 24) -> bool:
        """Check if token was recently bought"""
        if token_addr not in self.recent_tokens:
            return False
        
        cutoff = datetime.now() - timedelta(hours=hours)
        return self.recent_tokens[token_addr] > cutoff
    
    def mark_bought(self, token_addr: str):
        """Mark token as recently bought"""
        self.recent_tokens[token_addr] = datetime.now()
        
    def cleanup_old(self, hours: int = 48):
        """Remove old entries"""
        cutoff = datetime.now() - timedelta(hours=hours)
        self.recent_tokens = {
            addr: timestamp for addr, timestamp in self.recent_tokens.items()
            if timestamp > cutoff
        }

class AlphaSignalsAutotrade:
    """
    Complete AutoTrade system for AlphaSignals
    """
    
    def __init__(self):
        self.settings_file = Path("autotrade_settings.json")
        self.user_settings: Dict[int, AutoTradeSettings] = {}
        self.duplicate_trackers: Dict[int, DuplicateTracker] = {}
        self.active_trades: Dict[str, Dict] = {}  # trade_id -> trade_info
        
    async def initialize(self):
        """Initialize the autotrade system"""
        await self._load_settings()
        logger.info("AlphaSignals AutoTrade initialized")
    
    async def _load_settings(self):
        """Load user settings from file"""
        try:
            if self.settings_file.exists():
                async with aiofiles.open(self.settings_file, 'r') as f:
                    data = json.loads(await f.read())
                
                for user_id_str, settings_dict in data.items():
                    user_id = int(user_id_str)
                    self.user_settings[user_id] = AutoTradeSettings.from_dict(settings_dict)
                    self.duplicate_trackers[user_id] = DuplicateTracker(user_id)
                    
                logger.info(f"Loaded settings for {len(self.user_settings)} users")
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
    
    async def _save_settings(self):
        """Save user settings to file"""
        try:
            data = {
                str(user_id): settings.to_dict() 
                for user_id, settings in self.user_settings.items()
            }
            
            async with aiofiles.open(self.settings_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
                
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def get_user_settings(self, user_id: int) -> AutoTradeSettings:
        """Get or create user settings"""
        if user_id not in self.user_settings:
            self.user_settings[user_id] = AutoTradeSettings(user_id=user_id)
            self.duplicate_trackers[user_id] = DuplicateTracker(user_id)
        return self.user_settings[user_id]
    
    async def show_main_dashboard(self, update: Update, context: CallbackContext):
        """Show main AlphaSignals AutoTrade dashboard"""
        user_id = update.effective_user.id
        settings = self.get_user_settings(user_id)
        
        status = "🟢 ENABLED" if settings.enabled else "🔴 DISABLED"
        
        text = f"""
🤖 **AlphaSignals AutoTrade Dashboard**

**Status:** {status}
**Position Size:** ${settings.max_position_usd:,.0f}
**Stop Loss:** {settings.stop_loss_pct:.0%}
**Take Profit:** {settings.take_profit_pct:.0%}
**Daily Risk Limit:** ${settings.risk_limit_daily_usd:,.0f}

**Protection Settings:**
• Rug Check: {'✅' if settings.rug_check_enabled else '❌'}
• Trailing Stop: {'✅' if settings.trailing_stop_enabled else '❌'}
• Duplicate Protection: {settings.duplicate_protection_hours}h

**Channel Filters:**
• Whitelisted: {len(settings.whitelist_channels)} channels
• Blacklisted: {len(settings.blacklist_tokens)} tokens
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Toggle AutoTrade", callback_data=f"auto_toggle_{user_id}"),
                InlineKeyboardButton("⚙️ Settings", callback_data=f"auto_settings_{user_id}")
            ],
            [
                InlineKeyboardButton("📊 Position Settings", callback_data=f"auto_position_{user_id}"),
                InlineKeyboardButton("🛡️ Risk Settings", callback_data=f"auto_risk_{user_id}")
            ],
            [
                InlineKeyboardButton("📺 Channel Filters", callback_data=f"auto_channels_{user_id}"),
                InlineKeyboardButton("⚫ Token Blacklist", callback_data=f"auto_blacklist_{user_id}")
            ],
            [
                InlineKeyboardButton("📈 Active Trades", callback_data=f"auto_trades_{user_id}"),
                InlineKeyboardButton("📊 Statistics", callback_data=f"auto_stats_{user_id}")
            ],
            [InlineKeyboardButton("⬅️ Back to Main", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_toggle_autotrade(self, update: Update, context: CallbackContext):
        """Toggle AutoTrade on/off"""
        user_id = update.effective_user.id
        settings = self.get_user_settings(user_id)
        
        settings.enabled = not settings.enabled
        await self._save_settings()
        
        status = "🟢 ENABLED" if settings.enabled else "🔴 DISABLED"
        
        await update.callback_query.answer(f"AutoTrade {status}")
        await self.show_main_dashboard(update, context)
    
    async def show_position_settings(self, update: Update, context: CallbackContext):
        """Show position size and profit/loss settings"""
        user_id = update.effective_user.id
        settings = self.get_user_settings(user_id)
        
        text = f"""
📊 **Position Settings**

**Current Settings:**
• Position Size: ${settings.max_position_usd:,.0f}
• Stop Loss: {settings.stop_loss_pct:.0%}
• Take Profit: {settings.take_profit_pct:.0%}
• Auto-Sell Delay: {settings.auto_sell_delay_sec}s

Choose what to modify:
        """
        
        keyboard = [
            [
                InlineKeyboardButton("💰 Position Size", callback_data=f"set_position_size_{user_id}"),
                InlineKeyboardButton("🛑 Stop Loss", callback_data=f"set_stop_loss_{user_id}")
            ],
            [
                InlineKeyboardButton("🎯 Take Profit", callback_data=f"set_take_profit_{user_id}"),
                InlineKeyboardButton("⏱️ Sell Delay", callback_data=f"set_sell_delay_{user_id}")
            ],
            [InlineKeyboardButton("⬅️ Back", callback_data=f"auto_main_{user_id}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_risk_settings(self, update: Update, context: CallbackContext):
        """Show risk management settings"""
        user_id = update.effective_user.id
        settings = self.get_user_settings(user_id)
        
        text = f"""
🛡️ **Risk Management Settings**

**Current Settings:**
• Daily Risk Limit: ${settings.risk_limit_daily_usd:,.0f}
• Rug Check: {'✅ Enabled' if settings.rug_check_enabled else '❌ Disabled'}
• Trailing Stop: {'✅ Enabled' if settings.trailing_stop_enabled else '❌ Disabled'}
• Duplicate Protection: {settings.duplicate_protection_hours} hours

Choose what to modify:
        """
        
        keyboard = [
            [
                InlineKeyboardButton("💸 Daily Limit", callback_data=f"set_daily_limit_{user_id}"),
                InlineKeyboardButton("🔍 Rug Check", callback_data=f"toggle_rug_check_{user_id}")
            ],
            [
                InlineKeyboardButton("📈 Trailing Stop", callback_data=f"toggle_trailing_{user_id}"),
                InlineKeyboardButton("🔄 Duplicate Hours", callback_data=f"set_duplicate_hours_{user_id}")
            ],
            [InlineKeyboardButton("⬅️ Back", callback_data=f"auto_main_{user_id}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def parse_signal(self, message_text: str, channel_name: str) -> Optional[TradeSignal]:
        """Parse trading signal from channel message"""
        try:
            # Common patterns for Solana contract addresses
            solana_patterns = [
                r'[1-9A-HJ-NP-Za-km-z]{32,44}',  # Base58 pattern
                r'(?:Contract|CA|Token)[:=\s]+([1-9A-HJ-NP-Za-km-z]{32,44})',
                r'(?:Address|ADDR)[:=\s]+([1-9A-HJ-NP-Za-km-z]{32,44})'
            ]
            
            token_address = None
            for pattern in solana_patterns:
                match = re.search(pattern, message_text, re.IGNORECASE)
                if match:
                    potential_addr = match.group(1) if match.groups() else match.group(0)
                    if self._is_valid_solana_address(potential_addr):
                        token_address = potential_addr
                        break
            
            if not token_address:
                return None
            
            # Extract token symbol
            symbol_match = re.search(r'\$([A-Z]{2,10})', message_text, re.IGNORECASE)
            token_symbol = symbol_match.group(1) if symbol_match else "UNKNOWN"
            
            # Calculate confidence based on signal quality
            confidence = self._calculate_signal_confidence(message_text)
            
            # Extract additional data
            buy_price = self._extract_price(message_text, "buy|entry")
            target_price = self._extract_price(message_text, "target|tp|take.?profit")
            market_cap = self._extract_market_cap(message_text)
            
            return TradeSignal(
                token_address=token_address,
                token_symbol=token_symbol,
                channel_name=channel_name,
                signal_text=message_text,
                confidence=confidence,
                timestamp=datetime.now(),
                buy_price=buy_price,
                target_price=target_price,
                market_cap=market_cap
            )
            
        except Exception as e:
            logger.error(f"Failed to parse signal: {e}")
            return None
    
    def _is_valid_solana_address(self, address: str) -> bool:
        """Validate Solana address format"""
        try:
            if len(address) < 32 or len(address) > 44:
                return False
            
            # Try to decode as base58
            import base58
            decoded = base58.b58decode(address)
            return len(decoded) == 32
            
        except:
            return False
    
    def _calculate_signal_confidence(self, text: str) -> float:
        """Calculate signal confidence score 0-1"""
        confidence = 0.5  # Base confidence
        
        # Positive indicators
        positive_keywords = [
            'bullish', 'pump', 'moon', 'buy', 'long', 'gem', 'alpha',
            'target', 'breakout', 'surge', 'rocket', '🚀', '📈', '💎'
        ]
        
        # Negative indicators  
        negative_keywords = [
            'maybe', 'possibly', 'risky', 'dyor', 'nfa', 'speculation'
        ]
        
        text_lower = text.lower()
        
        for keyword in positive_keywords:
            if keyword in text_lower:
                confidence += 0.1
                
        for keyword in negative_keywords:
            if keyword in text_lower:
                confidence -= 0.1
        
        # Cap confidence between 0.1 and 1.0
        return max(0.1, min(1.0, confidence))
    
    def _extract_price(self, text: str, pattern: str) -> Optional[float]:
        """Extract price from text"""
        try:
            price_pattern = f'{pattern}[:\s]*\$?([0-9]+\.?[0-9]*)'
            match = re.search(price_pattern, text, re.IGNORECASE)
            return float(match.group(1)) if match else None
        except:
            return None
    
    def _extract_market_cap(self, text: str) -> Optional[float]:
        """Extract market cap from text"""
        try:
            mc_pattern = r'(?:mc|market.?cap)[:\s]*\$?([0-9]+\.?[0-9]*[kmb]?)'
            match = re.search(mc_pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1).lower()
                value = float(re.sub(r'[kmb]', '', value_str))
                
                if 'k' in value_str:
                    value *= 1000
                elif 'm' in value_str:
                    value *= 1000000
                elif 'b' in value_str:
                    value *= 1000000000
                    
                return value
        except:
            pass
        return None
    
    async def process_signal(self, signal: TradeSignal) -> Dict[str, Any]:
        """Process a trading signal for all eligible users"""
        results = {
            "signal": signal,
            "processed_users": [],
            "skipped_users": [],
            "errors": []
        }
        
        try:
            for user_id, settings in self.user_settings.items():
                if not settings.enabled:
                    results["skipped_users"].append({"user_id": user_id, "reason": "AutoTrade disabled"})
                    continue
                
                # Check channel whitelist
                if settings.whitelist_channels and signal.channel_name not in settings.whitelist_channels:
                    results["skipped_users"].append({"user_id": user_id, "reason": "Channel not whitelisted"})
                    continue
                
                # Check token blacklist
                if signal.token_address in settings.blacklist_tokens:
                    results["skipped_users"].append({"user_id": user_id, "reason": "Token blacklisted"})
                    continue
                
                # Check duplicate protection
                tracker = self.duplicate_trackers.get(user_id)
                if tracker and tracker.is_duplicate(signal.token_address, settings.duplicate_protection_hours):
                    results["skipped_users"].append({"user_id": user_id, "reason": "Recently bought"})
                    continue
                
                # Process trade for this user
                try:
                    trade_result = await self._execute_autotrade(user_id, signal, settings)
                    results["processed_users"].append(trade_result)
                    
                    # Mark as bought if successful
                    if trade_result.get("success") and tracker:
                        tracker.mark_bought(signal.token_address)
                        
                except Exception as e:
                    results["errors"].append({"user_id": user_id, "error": str(e)})
                    
        except Exception as e:
            logger.error(f"Failed to process signal: {e}")
            results["errors"].append({"global_error": str(e)})
        
        return results
    
    async def _execute_autotrade(self, user_id: int, signal: TradeSignal, settings: AutoTradeSettings) -> Dict[str, Any]:
        """Execute autotrade for a specific user"""
        try:
            # Import trading components
            from trading_engine import TradingEngine
            from rug_checker import quick_rug_check
            
            # Initialize trading engine for user
            trading_engine = TradingEngine()
            
            # Rug check if enabled
            if settings.rug_check_enabled:
                rug_result = await quick_rug_check(signal.token_address)
                if not rug_result.ok:
                    return {
                        "user_id": user_id,
                        "success": False,
                        "reason": f"Rug check failed: {rug_result.recommendation}",
                        "rug_check": rug_result.to_dict()
                    }
            
            # Execute buy order
            buy_result = await trading_engine.execute_buy(
                user_id=user_id,
                token_address=signal.token_address,
                amount_usd=settings.max_position_usd
            )
            
            if not buy_result.get("success"):
                return {
                    "user_id": user_id,
                    "success": False,
                    "reason": "Buy order failed",
                    "buy_result": buy_result
                }
            
            # Set up trailing stop if enabled
            if settings.trailing_stop_enabled:
                from trailing_stop import get_trailing_stop_manager
                ts_manager = get_trailing_stop_manager()
                await ts_manager.on_entry(
                    user_id=user_id,
                    token_addr=signal.token_address,
                    entry_price=buy_result.get("execution_price", 0),
                    trade_size_usd=settings.max_position_usd
                )
            
            # Schedule auto-sell if configured
            if settings.auto_sell_delay_sec > 0:
                asyncio.create_task(self._schedule_auto_sell(
                    user_id, signal.token_address, settings.auto_sell_delay_sec
                ))
            
            return {
                "user_id": user_id,
                "success": True,
                "signal": signal.token_symbol,
                "buy_result": buy_result,
                "position_usd": settings.max_position_usd
            }
            
        except Exception as e:
            logger.error(f"AutoTrade execution failed for user {user_id}: {e}")
            return {
                "user_id": user_id,
                "success": False,
                "reason": f"Execution error: {str(e)}"
            }
    
    async def _schedule_auto_sell(self, user_id: int, token_address: str, delay_seconds: int):
        """Schedule automatic sell after delay"""
        try:
            await asyncio.sleep(delay_seconds)
            
            from trading_engine import TradingEngine
            trading_engine = TradingEngine()
            
            # Execute sell order
            sell_result = await trading_engine.execute_sell(
                user_id=user_id,
                token_address=token_address,
                percentage=100  # Sell all
            )
            
            logger.info(f"Auto-sell completed for user {user_id}, token {token_address}: {sell_result}")
            
        except Exception as e:
            logger.error(f"Auto-sell failed for user {user_id}: {e}")

# Global instance
_autotrade_manager = None

async def get_autotrade_manager() -> AlphaSignalsAutotrade:
    """Get global autotrade manager"""
    global _autotrade_manager
    if _autotrade_manager is None:
        _autotrade_manager = AlphaSignalsAutotrade()
        await _autotrade_manager.initialize()
    return _autotrade_manager