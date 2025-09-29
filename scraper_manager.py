#!/usr/bin/env python3
"""
Scraper Management Script
Control and manage the Telegram scraper
"""

import asyncio
import argparse
import json
import os
from datetime import datetime
from telegram_scraper import SolanaTelegramScraper, GroupConfig

class ScraperManager:
    """Manager for the Telegram scraper"""
    
    def __init__(self):
        self.scraper = SolanaTelegramScraper()
    
    async def add_group(self, group_link: str, group_name: str = None, auto_trade: bool = False, min_confidence: float = 0.8):
        """Add a group to monitor"""
        print(f"Adding group: {group_link}")
        
        try:
            # Connect to Telegram
            await self.scraper.client.start()
            
            success = await self.scraper.add_group(group_link, group_name, auto_trade, min_confidence)
            
            if success:
                auto_msg = " (auto-trade enabled)" if auto_trade else ""
                print(f"✅ Successfully added group: {group_name or group_link}{auto_msg}")
            else:
                print(f"❌ Failed to add group: {group_link}")
            
            await self.scraper.client.disconnect()
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def list_groups(self):
        """List all monitored groups"""
        print("📋 Monitored Groups:")
        print("-" * 50)
        
        try:
            groups = await self.scraper.list_groups()
            
            if not groups:
                print("No groups configured")
                return
            
            for group in groups:
                status = "🟢 Enabled" if group['enabled'] else "🔴 Disabled"
                auto_trade = "🤖 Auto-trade ON" if group['auto_trade'] else "👤 Manual only"
                
                print(f"📱 {group['name']}")
                print(f"   ID: {group['id']}")
                print(f"   Status: {status}")
                print(f"   Trading: {auto_trade}")
                print(f"   Min Confidence: {group['min_confidence']:.0%}")
                print()
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def view_found_contracts(self, limit: int = 20):
        """View recently found contracts"""
        print(f"📊 Last {limit} Found Solana Contracts:")
        print("-" * 50)
        
        contracts_file = 'found_solana_contracts.json'
        if not os.path.exists(contracts_file):
            print("No contracts found yet")
            return
        
        try:
            with open(contracts_file, 'r') as f:
                contracts = json.load(f)
            
            # Show most recent contracts
            recent_contracts = contracts[-limit:][::-1]  # Reverse to show newest first
            
            for i, contract in enumerate(recent_contracts, 1):
                timestamp = contract.get('timestamp', '')
                if timestamp:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    time_str = 'Unknown'
                
                symbol = contract.get('symbol', 'Unknown')
                confidence = contract.get('confidence_score', 0) * 100
                
                decimals = contract.get('decimals', 9)
                
                print(f"{i:2d}. 💎 ${symbol} (SOL)")
                print(f"    📍 {contract['address']}")
                print(f"    🔢 Decimals: {decimals}")
                print(f"    📊 Confidence: {confidence:.0f}%")
                print(f"    📱 Source: {contract.get('source_group', 'Unknown')}")
                print(f"    🕒 Found: {time_str}")
                print()
        
        except Exception as e:
            print(f"❌ Error reading contracts: {e}")
    
    def show_stats(self):
        """Show scraper statistics"""
        print("📈 Solana Scraper Statistics:")
        print("-" * 30)
        
        # Count contracts
        contracts_file = 'found_solana_contracts.json'
        total_contracts = 0
        if os.path.exists(contracts_file):
            try:
                with open(contracts_file, 'r') as f:
                    contracts = json.load(f)
                total_contracts = len(contracts)
                
                # Count high confidence
                high_confidence = sum(1 for c in contracts if c.get('confidence_score', 0) >= 0.8)
                
                # Count by decimals (common Solana token info)
                standard_decimals = sum(1 for c in contracts if c.get('decimals') == 9)
                custom_decimals = sum(1 for c in contracts if c.get('decimals') != 9 and c.get('decimals') is not None)
                
                print(f"📊 Total Solana Contracts Found: {total_contracts}")
                print(f"⭐ High Confidence (>80%): {high_confidence}")
                print(f"� Standard Decimals (9): {standard_decimals}")
                print(f"🔣 Custom Decimals: {custom_decimals}")
                
            except Exception as e:
                print(f"❌ Error reading stats: {e}")
        else:
            print("📊 Total Contracts Found: 0")
        
        # Count groups
        groups_file = 'scraper_groups.json'
        if os.path.exists(groups_file):
            try:
                with open(groups_file, 'r') as f:
                    data = json.load(f)
                groups = data.get('groups', [])
                enabled_groups = sum(1 for g in groups if g.get('enabled', False))
                
                print(f"📱 Monitored Groups: {len(groups)}")
                print(f"🟢 Active Groups: {enabled_groups}")
                
            except Exception as e:
                print(f"❌ Error reading groups: {e}")
    
    async def start_scraper(self):
        """Start the scraper"""
        print("🚀 Starting Telegram scraper...")
        await self.scraper.start()

async def main():
    """Main function with CLI interface"""
    parser = argparse.ArgumentParser(description='Solana Telegram Contract Scraper Manager')
    parser.add_argument('action', choices=['start', 'add-group', 'list-groups', 'contracts', 'stats'],
                      help='Action to perform')
    parser.add_argument('--group-link', help='Telegram group link or username')
    parser.add_argument('--group-name', help='Custom name for the group')
    parser.add_argument('--auto-trade', action='store_true', help='Enable auto-trading for this group')
    parser.add_argument('--min-confidence', type=float, default=0.8, help='Minimum confidence for auto-trade')
    parser.add_argument('--limit', type=int, default=20, help='Limit for contracts display')
    
    args = parser.parse_args()
    
    manager = ScraperManager()
    
    try:
        if args.action == 'start':
            await manager.start_scraper()
        
        elif args.action == 'add-group':
            if not args.group_link:
                print("❌ Group link is required")
                return
            
            # Add auto-trade configuration
            auto_trade_msg = ""
            if args.auto_trade:
                auto_trade_msg = f" with auto-trading (min confidence: {args.min_confidence})"
            
            print(f"Adding group{auto_trade_msg}...")
            await manager.add_group(args.group_link, args.group_name, args.auto_trade, args.min_confidence)
        
        elif args.action == 'list-groups':
            await manager.list_groups()
        
        elif args.action == 'contracts':
            manager.view_found_contracts(args.limit)
        
        elif args.action == 'stats':
            manager.show_stats()
    
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())