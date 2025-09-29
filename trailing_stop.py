"""
AI Trailing Stop Loss for Solana Trading Bot
Advanced liquidity-aware trailing stop implementation
"""

from dataclasses import dataclass
import math
from typing import Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class TrailingStopConfig:
    z: float = 1.65              # noise coverage multiplier
    alpha: float = 1.8           # scales impact term
    beta: float = 1.0            # scales spread buffer (keep 1.0; set buffer value directly)
    floor_pct: float = 0.06      # 6% minimum
    ceiling_pct: float = 0.40    # 40% maximum (safety)
    arm_factor: float = 0.7      # arm threshold as fraction of TS%
    tighten_on_vol_spike: bool = True
    vol_spike_mult: float = 1.5  # if vol > 1.5x entry vol, tighten
    min_tick: float = 0.000001   # for tiny price units

@dataclass
class MarketSnapshot:
    price: float                  # current price
    atr_pct: float                # ATR% (e.g., 0.12 for 12%) over last N mins
    spread_pct: float             # current effective spread%
    pool_liquidity_usd: float     # quote-side liquidity in USD (or notional)
    trade_size_usd: float         # your order notional in USD

class LiquidityTrailingStop:
    """
    Advanced trailing stop with liquidity awareness and volatility adaptation
    """
    
    def __init__(self, cfg: TrailingStopConfig):
        self.cfg = cfg
        self.entry_price: Optional[float] = None
        self.ts_pct_at_entry: Optional[float] = None
        self.armed: bool = False
        self.trailing_stop_price: Optional[float] = None
        self.highest_price: Optional[float] = None
        self.entry_vol_ref: Optional[float] = None

    def compute_ts_pct(self, m: MarketSnapshot) -> float:
        """
        Compute trailing stop percentage based on market conditions
        """
        try:
            impact = self.cfg.alpha * (m.trade_size_usd / max(m.pool_liquidity_usd, 1.0))
            noise = self.cfg.z * m.atr_pct
            buffer = self.cfg.beta * m.spread_pct
            ts = max(self.cfg.floor_pct, min(self.cfg.ceiling_pct, noise + impact + buffer))
            
            logger.debug(f"TS calculation: impact={impact:.4f}, noise={noise:.4f}, buffer={buffer:.4f}, final={ts:.4f}")
            return ts
        except Exception as e:
            logger.error(f"Error computing TS%: {e}")
            return self.cfg.floor_pct

    def on_entry(self, m: MarketSnapshot) -> dict:
        """
        Initialize trailing stop on position entry
        """
        try:
            self.entry_price = m.price
            self.ts_pct_at_entry = self.compute_ts_pct(m)
            self.entry_vol_ref = m.atr_pct
            self.highest_price = m.price
            self.trailing_stop_price = m.price * (1 - self.ts_pct_at_entry)
            self.armed = False  # arm after some profit
            
            result = {
                "ts_pct": self.ts_pct_at_entry,
                "arm_threshold": self.ts_pct_at_entry * self.cfg.arm_factor,
                "initial_stop": self.trailing_stop_price,
                "entry_price": self.entry_price
            }
            
            logger.info(f"Trailing stop initialized: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error on entry: {e}")
            return {"error": str(e)}

    def on_tick(self, m: MarketSnapshot) -> Optional[dict]:
        """
        Update trailing stop on each price tick
        """
        if self.entry_price is None:
            return None

        try:
            # Update highest
            if m.price > self.highest_price:
                self.highest_price = m.price
                logger.debug(f"New highest price: {self.highest_price}")

            # Arm once price moves up enough
            if not self.armed:
                gain_pct = (self.highest_price / self.entry_price) - 1
                arm_threshold = self.ts_pct_at_entry * self.cfg.arm_factor
                if gain_pct >= arm_threshold:
                    self.armed = True
                    logger.info(f"Trailing stop armed at gain {gain_pct:.2%} (threshold: {arm_threshold:.2%})")

            # Tighten on volatility spike
            ts_pct = self.ts_pct_at_entry
            if self.cfg.tighten_on_vol_spike and self.entry_vol_ref and m.atr_pct > (self.entry_vol_ref * self.cfg.vol_spike_mult):
                # tighten to cover elevated noise, but never loosen past original ts_pct
                elevated = self.compute_ts_pct(m)
                ts_pct = max(ts_pct, min(elevated, self.cfg.ceiling_pct))
                logger.info(f"Volatility spike detected, tightening TS to {ts_pct:.2%}")

            # Trail only when armed
            if self.armed:
                candidate = self.highest_price * (1 - ts_pct)
                if (self.trailing_stop_price is None) or (candidate > self.trailing_stop_price):
                    old_stop = self.trailing_stop_price
                    self.trailing_stop_price = candidate
                    logger.info(f"Trailing stop updated: {old_stop} -> {self.trailing_stop_price}")

            # Exit check
            exit_now = m.price <= (self.trailing_stop_price or -math.inf)
            if exit_now:
                logger.warning(f"TRAILING STOP TRIGGERED: price={m.price}, stop={self.trailing_stop_price}")

            return {
                "armed": self.armed,
                "ts_pct_active": ts_pct,
                "highest_price": self.highest_price,
                "trailing_stop_price": self.trailing_stop_price,
                "exit": exit_now,
                "gain_pct": (self.highest_price / self.entry_price) - 1 if self.entry_price else 0,
                "current_price": m.price
            }
            
        except Exception as e:
            logger.error(f"Error on tick: {e}")
            return {"error": str(e)}

    def reset(self):
        """Reset the trailing stop"""
        self.entry_price = None
        self.ts_pct_at_entry = None
        self.armed = False
        self.trailing_stop_price = None
        self.highest_price = None
        self.entry_vol_ref = None
        logger.info("Trailing stop reset")

    def get_status(self) -> dict:
        """Get current trailing stop status"""
        return {
            "active": self.entry_price is not None,
            "armed": self.armed,
            "entry_price": self.entry_price,
            "highest_price": self.highest_price,
            "trailing_stop_price": self.trailing_stop_price,
            "ts_pct_at_entry": self.ts_pct_at_entry
        }

# Global trailing stop manager for easy access
trailing_stop_manager = {}

def get_trailing_stop(user_id: str, token_address: str) -> LiquidityTrailingStop:
    """Get or create trailing stop for user and token"""
    key = f"{user_id}_{token_address}"
    if key not in trailing_stop_manager:
        trailing_stop_manager[key] = LiquidityTrailingStop(TrailingStopConfig())
    return trailing_stop_manager[key]

def remove_trailing_stop(user_id: str, token_address: str):
    """Remove trailing stop for user and token"""
    key = f"{user_id}_{token_address}"
    if key in trailing_stop_manager:
        del trailing_stop_manager[key]
        logger.info(f"Removed trailing stop for {key}")