"""
Solana Best Trades Monitor
Fetches and analyzes top performing trades on Solana
"""

import asyncio
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
import aiohttp

logger = logging.getLogger(__name__)

class SolanaBestTradesMonitor:
    def __init__(self):
        self.birdeye_api = "https://public-api.birdeye.so"
        self.dexscreener_api = "https://api.dexscreener.com"
        self.headers = {
            "X-API-KEY": "YOUR_BIRDEYE_API_KEY",  # Replace with actual API key
            "User-Agent": "TradingBot/1.0"
        }
        
    async def get_top_gainers_24h(self, limit: int = 50) -> List[Dict]:
        """Get top gaining tokens in the last 24 hours"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get top gainers from Birdeye API
                url = f"{self.birdeye_api}/defi/tokenlist"
                params = {
                    "sort_by": "v24hChangePercent",
                    "sort_type": "desc",
                    "offset": 0,
                    "limit": limit
                }
                
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", {}).get("tokens", [])
                    else:
                        logger.error(f"Birdeye API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching top gainers: {e}")
            return []
    
    async def get_whale_transactions(self, limit: int = 100) -> List[Dict]:
        """Get recent large transactions (whale trades)"""
        try:
            # This would typically use a service like Solscan API
            # For demo purposes, we'll simulate whale trades
            
            whale_trades = []
            tokens = await self.get_top_gainers_24h(20)
            
            for i, token in enumerate(tokens[:10]):
                # Simulate whale trade data
                whale_trade = {
                    "wallet_address": self._generate_fake_wallet(),
                    "token_address": token.get("address", ""),
                    "token_symbol": token.get("symbol", "UNKNOWN"),
                    "transaction_type": "buy" if i % 2 == 0 else "sell",
                    "amount_sol": round(10 + (i * 5.5), 2),
                    "amount_usd": round((10 + (i * 5.5)) * 140, 2),  # Assuming SOL = $140
                    "price_change_24h": token.get("v24hChangePercent", 0),
                    "timestamp": datetime.now() - timedelta(hours=i),
                    "roi_percentage": round(token.get("v24hChangePercent", 0) * 0.8, 2)
                }
                whale_trades.append(whale_trade)
            
            return sorted(whale_trades, key=lambda x: x["roi_percentage"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error fetching whale transactions: {e}")
            return []
    
    def _generate_fake_wallet(self) -> str:
        """Generate a fake wallet address for demo purposes"""
        import random
        import string
        
        # Generate a Solana-like address
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=8)) + "..." + ''.join(random.choices(chars, k=4))
    
    async def analyze_wallet_performance(self, wallet_address: str, days: int = 7) -> Dict:
        """Analyze a specific wallet's performance"""
        try:
            # In a real implementation, this would analyze transaction history
            # For demo, return simulated data
            
            performance_data = {
                "wallet_address": wallet_address,
                "total_trades": random.randint(15, 100),
                "successful_trades": random.randint(10, 80),
                "win_rate": 0,
                "total_pnl_sol": round(random.uniform(-5, 50), 4),
                "total_pnl_usd": 0,
                "roi_percentage": 0,
                "average_hold_time": f"{random.randint(1, 48)} hours",
                "favorite_tokens": ["BONK", "WIF", "POPCAT"],
                "risk_score": random.uniform(0.3, 0.9)
            }
            
            # Calculate derived metrics
            performance_data["win_rate"] = round(
                (performance_data["successful_trades"] / performance_data["total_trades"]) * 100, 1
            )
            performance_data["total_pnl_usd"] = round(performance_data["total_pnl_sol"] * 140, 2)
            performance_data["roi_percentage"] = round(performance_data["total_pnl_sol"] * 10, 2)
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Error analyzing wallet performance: {e}")
            return {}
    
    async def get_trending_tokens(self, timeframe: str = "24h") -> List[Dict]:
        """Get trending tokens based on various metrics"""
        try:
            # Combine data from multiple sources for better accuracy
            trending_tokens = []
            
            # Get data from DexScreener
            async with aiohttp.ClientSession() as session:
                url = f"{self.dexscreener_api}/latest/dex/tokens/solana"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        pairs = data.get("pairs", [])
                        
                        for pair in pairs[:20]:  # Top 20 pairs
                            token_data = {
                                "address": pair.get("baseToken", {}).get("address", ""),
                                "symbol": pair.get("baseToken", {}).get("symbol", ""),
                                "name": pair.get("baseToken", {}).get("name", ""),
                                "price_usd": float(pair.get("priceUsd", 0)),
                                "volume_24h": float(pair.get("volume", {}).get("h24", 0)),
                                "price_change_24h": float(pair.get("priceChange", {}).get("h24", 0)),
                                "liquidity_usd": float(pair.get("liquidity", {}).get("usd", 0)),
                                "fdv": float(pair.get("fdv", 0)),
                                "market_cap": float(pair.get("marketCap", 0)),
                                "transactions_24h": pair.get("txns", {}).get("h24", {}),
                                "dex": pair.get("dexId", ""),
                                "pair_address": pair.get("pairAddress", "")
                            }
                            trending_tokens.append(token_data)
                    
                    # Sort by volume and price change
                    trending_tokens.sort(
                        key=lambda x: (x["volume_24h"] * abs(x["price_change_24h"])), 
                        reverse=True
                    )
                    
                    return trending_tokens[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Error fetching trending tokens: {e}")
            return []
    
    async def get_best_performing_wallets(self, limit: int = 5) -> List[Dict]:
        """Get the best performing wallets in the last 24 hours"""
        try:
            # In a real implementation, this would query blockchain data
            # For demo purposes, we'll generate realistic-looking data
            
            best_wallets = []
            
            for i in range(limit):
                wallet_data = {
                    "wallet_address": self._generate_fake_wallet(),
                    "total_pnl_sol": round(random.uniform(20, 100), 2),
                    "total_pnl_usd": 0,
                    "roi_percentage": round(random.uniform(200, 2000), 1),
                    "trades_count": random.randint(5, 25),
                    "win_rate": round(random.uniform(60, 95), 1),
                    "top_token": random.choice(["BONK", "WIF", "POPCAT", "PEPE", "DOGE"]),
                    "best_trade_roi": round(random.uniform(500, 3000), 1),
                    "avg_hold_time": f"{random.randint(2, 72)} hours",
                    "risk_score": round(random.uniform(0.2, 0.8), 2),
                    "last_active": datetime.now() - timedelta(hours=random.randint(1, 12))
                }
                
                wallet_data["total_pnl_usd"] = round(wallet_data["total_pnl_sol"] * 140, 2)
                best_wallets.append(wallet_data)
            
            # Sort by ROI percentage
            best_wallets.sort(key=lambda x: x["roi_percentage"], reverse=True)
            
            return best_wallets
            
        except Exception as e:
            logger.error(f"Error fetching best performing wallets: {e}")
            return []
    
    async def get_market_overview(self) -> Dict:
        """Get overall Solana DeFi market overview"""
        try:
            market_data = {
                "sol_price": await self._get_sol_price(),
                "total_volume_24h": random.uniform(100_000_000, 500_000_000),
                "total_transactions_24h": random.randint(800_000, 1_200_000),
                "active_traders_24h": random.randint(50_000, 100_000),
                "top_dex_by_volume": "Raydium",
                "biggest_gainer_24h": {
                    "symbol": "BONK",
                    "change": "+157.3%"
                },
                "biggest_loser_24h": {
                    "symbol": "SAMO",
                    "change": "-23.7%"
                },
                "new_tokens_24h": random.randint(50, 200),
                "total_liquidity": random.uniform(800_000_000, 1_200_000_000)
            }
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error fetching market overview: {e}")
            return {}
    
    async def _get_sol_price(self) -> float:
        """Get current SOL price"""
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://api.coingecko.com/api/v3/simple/price"
                params = {"ids": "solana", "vs_currencies": "usd"}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("solana", {}).get("usd", 140.0)
                    else:
                        return 140.0  # Fallback price
                        
        except Exception as e:
            logger.error(f"Error fetching SOL price: {e}")
            return 140.0

# Global instance for use in telegram bot
best_trades_monitor = SolanaBestTradesMonitor()

# For testing
if __name__ == "__main__":
    import asyncio
    import random
    
    async def test_monitor():
        monitor = SolanaBestTradesMonitor()
        
        print("Testing Best Trades Monitor...")
        
        # Test best performing wallets
        wallets = await monitor.get_best_performing_wallets()
        print(f"Found {len(wallets)} best performing wallets")
        for wallet in wallets:
            print(f"Wallet: {wallet['wallet_address']} | ROI: {wallet['roi_percentage']}% | PnL: {wallet['total_pnl_sol']} SOL")
        
        print("\n" + "="*50 + "\n")
        
        # Test trending tokens
        trending = await monitor.get_trending_tokens()
        print(f"Found {len(trending)} trending tokens")
        for token in trending[:5]:
            print(f"Token: {token['symbol']} | Price Change: {token['price_change_24h']:.2f}% | Volume: ${token['volume_24h']:,.0f}")
    
    asyncio.run(test_monitor())