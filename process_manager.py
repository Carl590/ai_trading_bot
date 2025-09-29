#!/usr/bin/env python3
"""
Process Management Script for Trading Bot
Helps manage bot instances and conflicts
"""

import os
import sys
import psutil
import signal
import time
from typing import List, Dict

def find_bot_processes() -> List[Dict]:
    """Find all running bot processes"""
    bot_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            
            # Look for bot-related processes
            if any(keyword in cmdline.lower() for keyword in [
                'telegram_bot.py',
                'start_bot.py', 
                'start_group_bot.py',
                'deploy.py',
                'main_app.py',
                'group_bot.py'
            ]):
                bot_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': cmdline
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return bot_processes

def stop_process(pid: int, name: str) -> bool:
    """Stop a process by PID"""
    try:
        proc = psutil.Process(pid)
        
        print(f"🛑 Stopping process {pid} ({name})...")
        
        # Try graceful termination first
        proc.terminate()
        
        # Wait up to 5 seconds for graceful shutdown
        try:
            proc.wait(timeout=5)
            print(f"✅ Process {pid} stopped gracefully")
            return True
        except psutil.TimeoutExpired:
            # Force kill if needed
            print(f"⚠️  Force killing process {pid}...")
            proc.kill()
            proc.wait(timeout=3)
            print(f"✅ Process {pid} force killed")
            return True
            
    except psutil.NoSuchProcess:
        print(f"✅ Process {pid} already stopped")
        return True
    except Exception as e:
        print(f"❌ Failed to stop process {pid}: {e}")
        return False

def stop_all_bots():
    """Stop all bot processes"""
    print("🔍 Scanning for bot processes...")
    processes = find_bot_processes()
    
    if not processes:
        print("✅ No bot processes found running")
        return True
    
    print(f"📋 Found {len(processes)} bot process(es):")
    for proc in processes:
        print(f"  • PID {proc['pid']}: {proc['name']}")
        print(f"    Command: {proc['cmdline']}")
    
    print("\n🛑 Stopping all bot processes...")
    all_stopped = True
    
    for proc in processes:
        if not stop_process(proc['pid'], proc['name']):
            all_stopped = False
    
    # Wait a moment and check again
    time.sleep(2)
    remaining = find_bot_processes()
    
    if remaining:
        print(f"⚠️  {len(remaining)} process(es) still running")
        all_stopped = False
    else:
        print("✅ All bot processes stopped")
    
    return all_stopped

def show_status():
    """Show current bot process status"""
    processes = find_bot_processes()
    
    print("📊 Bot Process Status")
    print("=" * 40)
    
    if not processes:
        print("✅ No bot processes running")
    else:
        print(f"🏃 {len(processes)} process(es) running:")
        for proc in processes:
            print(f"  • PID {proc['pid']}: {proc['name']}")
            print(f"    Command: {proc['cmdline'][:80]}...")

def clear_telegram_webhook():
    """Clear Telegram webhook to prevent conflicts"""
    try:
        import requests
        from config_manager import config_manager
        
        config = config_manager.get_config()
        if not config.telegram_bot_token:
            print("❌ No Telegram bot token found")
            return False
        
        # Clear webhook
        url = f"https://api.telegram.org/bot{config.telegram_bot_token}/deleteWebhook"
        response = requests.post(url)
        
        if response.status_code == 200:
            print("✅ Telegram webhook cleared")
            return True
        else:
            print(f"⚠️  Failed to clear webhook: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error clearing webhook: {e}")
        return False

def main():
    """Main process management function"""
    if len(sys.argv) < 2:
        print("🤖 Trading Bot Process Manager")
        print("=" * 40)
        print("Usage: python process_manager.py <command>")
        print("\nCommands:")
        print("  status    - Show current bot processes")
        print("  stop      - Stop all bot processes")
        print("  clean     - Stop processes and clear webhook")
        print("  clear     - Clear Telegram webhook only")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    print("🤖 Trading Bot Process Manager")
    print("=" * 40)
    
    if command == "status":
        show_status()
    
    elif command == "stop":
        stop_all_bots()
    
    elif command == "clean":
        print("🧹 Cleaning up bot processes and webhooks...")
        stop_all_bots()
        time.sleep(1)
        clear_telegram_webhook()
        print("✅ Cleanup complete")
    
    elif command == "clear":
        clear_telegram_webhook()
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: status, stop, clean, clear")
        sys.exit(1)

if __name__ == "__main__":
    main()