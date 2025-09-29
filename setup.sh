#!/bin/bash

# =================================================================
# Telegram Trading Bot - Setup Script
# Maestro-style Trading Bot for Solana with TradingView Integration
# =================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_banner() {
    echo -e "${BLUE}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════════╗
║                   🤖 TELEGRAM TRADING BOT 🤖                    ║
║                                                                  ║
║                     Setup & Installation                        ║
║                   Maestro Style Dashboard                       ║
║                  TradingView Integration                        ║
║                   Solana Auto Trading                          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python() {
    if command_exists python3; then
        python_version=$(python3 --version 2>&1 | awk '{print $2}')
        print_status "Python version: $python_version"
        
        # Check if version is 3.8 or higher
        if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python version is compatible (3.8+)"
            return 0
        else
            print_error "Python 3.8+ is required. Current version: $python_version"
            return 1
        fi
    else
        print_error "Python 3 is not installed"
        return 1
    fi
}

# Function to check if we're in a virtual environment
check_venv() {
    if [[ -n "$VIRTUAL_ENV" ]]; then
        print_success "Virtual environment detected: $VIRTUAL_ENV"
        return 0
    else
        print_warning "No virtual environment detected"
        return 1
    fi
}

# Function to create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
        else
            print_status "Using existing virtual environment"
            return 0
        fi
    fi
    
    python3 -m venv venv
    print_success "Virtual environment created"
}

# Function to activate virtual environment
activate_venv() {
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_success "Virtual environment activated"
    else
        print_error "Virtual environment not found"
        return 1
    fi
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Install main dependencies
    if [ -f "requirements_full.txt" ]; then
        print_status "Installing from requirements_full.txt..."
        pip install -r requirements_full.txt
    else
        print_status "Installing essential dependencies..."
        pip install \
            python-telegram-bot==20.6 \
            flask==2.3.3 \
            fastapi==0.104.1 \
            uvicorn==0.24.0 \
            solana==0.30.2 \
            aiohttp==3.9.1 \
            requests==2.31.0 \
            python-dotenv==1.0.0 \
            pydantic==2.5.2 \
            base58==2.1.1
    fi
    
    print_success "Dependencies installed successfully"
}

# Function to setup configuration
setup_config() {
    print_status "Setting up configuration..."
    
    # Copy example env file if .env doesn't exist
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Created .env file from template"
        else
            print_warning ".env.example not found, creating basic .env file..."
            cat > .env << EOF
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
WEBHOOK_SECRET_KEY=your-secret-webhook-key-123
WEBHOOK_PORT=8080
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
DEFAULT_TRADE_AMOUNT_SOL=0.01
DEFAULT_SLIPPAGE_BPS=100
LOG_LEVEL=INFO
EOF
            print_success "Created basic .env file"
        fi
    else
        print_success ".env file already exists"
    fi
    
    print_warning "⚠️  Please edit .env file and add your Telegram Bot Token!"
    print_status "Get your bot token from @BotFather on Telegram"
}

# Function to test configuration
test_config() {
    print_status "Testing configuration..."
    
    if command_exists python3; then
        if python3 -c "from config_manager import validate_config; errors = validate_config(); exit(0 if not errors else 1)" 2>/dev/null; then
            print_success "Configuration is valid"
        else
            print_warning "Configuration has some issues. Please check .env file"
        fi
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p wallets
    
    print_success "Directories created"
}

# Function to setup systemd service (Linux only)
setup_service() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_status "Setting up systemd service..."
        
        read -p "Do you want to create a systemd service? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            SERVICE_FILE="/etc/systemd/system/trading-bot.service"
            CURRENT_DIR=$(pwd)
            USER=$(whoami)
            
            cat > trading-bot.service << EOF
[Unit]
Description=Telegram Trading Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment=PATH=$CURRENT_DIR/venv/bin
ExecStart=$CURRENT_DIR/venv/bin/python main_app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
            
            print_status "Systemd service file created: trading-bot.service"
            print_status "To install: sudo cp trading-bot.service /etc/systemd/system/"
            print_status "To enable: sudo systemctl enable trading-bot"
            print_status "To start: sudo systemctl start trading-bot"
        fi
    fi
}

# Function to show next steps
show_next_steps() {
    print_success "🎉 Setup completed successfully!"
    echo
    print_status "📋 Next Steps:"
    echo "1. Edit .env file with your Telegram Bot Token"
    echo "2. Get your bot token from @BotFather on Telegram"
    echo "3. Set your webhook secret key in .env"
    echo "4. Configure your trading preferences in .env"
    echo
    print_status "🚀 To start the bot:"
    echo "  source venv/bin/activate  # Activate virtual environment"
    echo "  python main_app.py        # Start the trading bot"
    echo
    print_status "📱 To use the bot:"
    echo "  Send /start to your bot on Telegram"
    echo
    print_status "🔧 Configuration files:"
    echo "  .env                 - Main configuration"
    echo "  config_manager.py    - Configuration management"
    echo "  main_app.py         - Main application"
    echo "  telegram_bot.py     - Telegram bot interface"
    echo
    print_status "📚 Documentation:"
    echo "  README.md                    - General information"
    echo "  SOLANA_AUTO_TRADER_GUIDE.md - Solana trading guide"
    echo
    print_warning "⚠️  Important Security Notes:"
    echo "  • Never share your .env file or private keys"
    echo "  • Use a strong webhook secret key"
    echo "  • Test with small amounts first"
    echo "  • Monitor your bot regularly"
}

# Main installation function
main() {
    print_banner
    
    print_status "Starting Telegram Trading Bot setup..."
    
    # Check Python
    if ! check_python; then
        print_error "Please install Python 3.8+ and try again"
        exit 1
    fi
    
    # Check if in virtual environment, create one if not
    if ! check_venv; then
        create_venv
        activate_venv
    fi
    
    # Install dependencies
    install_dependencies
    
    # Setup configuration
    setup_config
    
    # Create directories
    create_directories
    
    # Test configuration
    test_config
    
    # Setup service (optional)
    setup_service
    
    # Show next steps
    show_next_steps
}

# Handle script arguments
case "${1:-}" in
    "install")
        main
        ;;
    "update")
        print_status "Updating dependencies..."
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        fi
        install_dependencies
        print_success "Update completed"
        ;;
    "test")
        print_status "Testing configuration..."
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        fi
        python3 -c "from config_manager import validate_config, print_config_summary; print_config_summary(); errors = validate_config(); print('Errors:' if errors else 'No errors'); [print(f'  {e}') for e in errors]"
        ;;
    "clean")
        print_status "Cleaning up..."
        rm -rf venv __pycache__ *.pyc logs/*.log
        print_success "Cleanup completed"
        ;;
    *)
        echo "Usage: $0 {install|update|test|clean}"
        echo
        echo "Commands:"
        echo "  install  - Full setup and installation"
        echo "  update   - Update dependencies only"
        echo "  test     - Test current configuration"
        echo "  clean    - Clean up generated files"
        echo
        echo "For first-time setup, run: $0 install"
        exit 1
        ;;
esac