"""
Comprehensive API Configuration for Solana Trading Bot
All RPC endpoints, APIs, and services organized in one file
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class ServiceType(Enum):
    RPC = "rpc"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    REST_API = "rest_api"
    SWAP_API = "swap_api"
    ANALYTICS = "analytics"

@dataclass
class APIEndpoint:
    name: str
    url: str
    api_key: Optional[str] = None
    service_type: ServiceType = ServiceType.REST_API
    description: str = ""
    headers: Optional[Dict[str, str]] = None
    active: bool = True

class TradingBotAPIManager:
    """Centralized API management for the trading bot"""
    
    def __init__(self):
        self.endpoints = self._initialize_endpoints()
        self.current_rpc = None
        self.current_swap_api = None
        
    def _initialize_endpoints(self) -> Dict[str, APIEndpoint]:
        """Initialize all API endpoints"""
        
        endpoints = {}
        
        # ==============================================
        # SOLANA RPC ENDPOINTS
        # ==============================================
        
        # Primary Shyft RPC (Active)
        endpoints['shyft_rpc_primary'] = APIEndpoint(
            name="Shyft RPC Primary",
            url="https://rpc.shyft.to",
            api_key="7Rt0hE2MGrr0R668",
            service_type=ServiceType.RPC,
            description="Primary Shyft RPC endpoint - fast and reliable"
        )
        
        # Backup Shyft RPC
        endpoints['shyft_rpc_backup'] = APIEndpoint(
            name="Shyft RPC Backup", 
            url="https://rpc.shyft.to",
            api_key="t3zFJjMFGdo1eCZc",
            service_type=ServiceType.RPC,
            description="Backup Shyft RPC endpoint",
            active=False
        )
        
        # Helius RPC
        endpoints['helius_rpc'] = APIEndpoint(
            name="Helius RPC",
            url="https://mainnet.helius-rpc.com/",
            api_key="cd716db1-6133-46b4-9f2f-59f5b72c329b",
            service_type=ServiceType.RPC,
            description="Helius high-performance RPC",
            active=False
        )
        
        # InstantNodes RPC
        endpoints['instantnodes_rpc'] = APIEndpoint(
            name="InstantNodes RPC",
            url="https://solana-api.instantnodes.io/token-dMuwjOK7nHyM8HdJvpbiHfKlpMLhfLoi",
            service_type=ServiceType.RPC,
            description="InstantNodes RPC service",
            active=False
        )
        
        # Public Node RPC
        endpoints['publicnode_rpc'] = APIEndpoint(
            name="PublicNode RPC",
            url="https://solana-rpc.publicnode.com",
            service_type=ServiceType.RPC,
            description="Free public RPC endpoint"
        )
        
        # Solana Vibe Station RPC
        endpoints['vibestation_rpc'] = APIEndpoint(
            name="Solana Vibe Station RPC",
            url="https://ultra.swqos.solanavibestation.com/",
            api_key="4c23252afdacb7860ad5de1d3d3daea2",
            service_type=ServiceType.RPC,
            description="Vibe Station Ultra RPC",
            active=False
        )
        
        # Custom RPC Endpoints
        endpoints['custom_rpc_1'] = APIEndpoint(
            name="Custom RPC 1",
            url="http://92.204.192.50:54331",
            service_type=ServiceType.RPC,
            description="Custom RPC endpoint",
            active=False
        )
        
        endpoints['custom_rpc_2'] = APIEndpoint(
            name="Custom RPC 2", 
            url="http://67.213.120.33:8899",
            service_type=ServiceType.RPC,
            description="Custom RPC endpoint 2",
            active=False
        )
        
        # ==============================================
        # GRPC ENDPOINTS
        # ==============================================
        
        # Shyft gRPC
        endpoints['shyft_grpc'] = APIEndpoint(
            name="Shyft gRPC",
            url="https://grpc.ny.shyft.to/",
            api_key="935103d8-187a-4e97-8d82-5fd1f68cef22",
            service_type=ServiceType.GRPC,
            description="Shyft gRPC streaming endpoint"
        )
        
        # Solana Vibe Station gRPC
        endpoints['vibestation_grpc'] = APIEndpoint(
            name="Vibe Station gRPC",
            url="https://ultra.grpc.solanavibestation.com",
            api_key="45051a801143c59510aef2b375b0f8f1",
            service_type=ServiceType.GRPC,
            description="Vibe Station gRPC endpoint"
        )
        
        # PublicNode gRPC
        endpoints['publicnode_grpc'] = APIEndpoint(
            name="PublicNode gRPC",
            url="solana-yellowstone-grpc.publicnode.com:443",
            service_type=ServiceType.GRPC,
            description="Public gRPC endpoint for Yellowstone"
        )
        
        # ==============================================
        # WEBSOCKET ENDPOINTS
        # ==============================================
        
        endpoints['publicnode_ws'] = APIEndpoint(
            name="PublicNode WebSocket",
            url="wss://solana-rpc.publicnode.com",
            service_type=ServiceType.WEBSOCKET,
            description="WebSocket for real-time data"
        )
        
        # ==============================================
        # JUPITER AGGREGATOR APIs
        # ==============================================
        
        # Jupiter Swap API (Primary)
        endpoints['jupiter_swap'] = APIEndpoint(
            name="Jupiter Swap API",
            url="https://quote-api.jup.ag/v6",
            service_type=ServiceType.SWAP_API,
            description="Jupiter aggregator for optimal swaps"
        )
        
        # Jupiter Ultra API
        endpoints['jupiter_ultra'] = APIEndpoint(
            name="Jupiter Ultra API",
            url="https://dev.jup.ag/api/ultra",
            service_type=ServiceType.SWAP_API,
            description="Jupiter Ultra API for advanced features"
        )
        
        # Jupiter Token API
        endpoints['jupiter_token'] = APIEndpoint(
            name="Jupiter Token API",
            url="https://dev.jup.ag/api/token/v2",
            service_type=ServiceType.ANALYTICS,
            description="Token information and search"
        )
        
        # Jupiter Price API
        endpoints['jupiter_price'] = APIEndpoint(
            name="Jupiter Price API",
            url="https://dev.jup.ag/api/price/v3",
            service_type=ServiceType.ANALYTICS,
            description="Real-time token prices"
        )
        
        # ==============================================
        # MEV & TRANSACTION SUBMISSION
        # ==============================================
        
        # ZeroSlot (Primary MEV)
        endpoints['zeroslot_primary'] = APIEndpoint(
            name="ZeroSlot Primary",
            url="http://ny1.0slot.trade/",
            api_key="ca6fc089f334462e90d47012d2a17b9c",
            service_type=ServiceType.RPC,
            description="ZeroSlot MEV protection - Primary"
        )
        
        endpoints['zeroslot_backup'] = APIEndpoint(
            name="ZeroSlot Backup",
            url="http://ams1.0slot.trade/",
            api_key="a1edaae64b574b4e906304f2b331b474",
            service_type=ServiceType.RPC,
            description="ZeroSlot MEV protection - Backup",
            active=False
        )
        
        endpoints['zeroslot_alt'] = APIEndpoint(
            name="ZeroSlot Alternative",
            url="http://ny1.0slot.trade/",
            api_key="f5815cad762f468882f1b66cf0d905ff",
            service_type=ServiceType.RPC,
            description="Alternative ZeroSlot endpoint"
        )
        
        endpoints['zeroslot_health'] = APIEndpoint(
            name="ZeroSlot Health Check",
            url="https://ny1.0slot.trade/health",
            service_type=ServiceType.REST_API,
            description="Health check for ZeroSlot"
        )
        
        # Nozomi
        endpoints['nozomi_primary'] = APIEndpoint(
            name="Nozomi Primary",
            url="http://ams1.nozomi.temporal.xyz/",
            api_key="4516a74a-ad06-4faf-9de4-10cce6e37f6b",
            service_type=ServiceType.RPC,
            description="Nozomi MEV protection"
        )
        
        endpoints['nozomi_alt'] = APIEndpoint(
            name="Nozomi Alternative", 
            url="http://ewr1.nozomi.temporal.xyz/",
            api_key="4516a74a-ad06-4faf-9de4-10cce6e37f6b",
            service_type=ServiceType.RPC,
            description="Alternative Nozomi endpoint"
        )
        
        # NextBlock
        endpoints['nextblock'] = APIEndpoint(
            name="NextBlock API",
            url="https://ny.nextblock.io/api/v2/submit",
            api_key="trial1752153681-UTJSpE5Nz%2BMy0lWqP8eW63o9OEVd9xOMZQrzf3gHJt8%3D",
            service_type=ServiceType.REST_API,
            description="NextBlock transaction submission"
        )
        
        return endpoints
    
    def get_active_rpc(self) -> APIEndpoint:
        """Get the currently active RPC endpoint"""
        if self.current_rpc:
            return self.current_rpc
        
        # Default to Shyft primary
        rpc = self.endpoints.get('shyft_rpc_primary')
        if rpc and rpc.active:
            self.current_rpc = rpc
            return rpc
        
        # Fallback to public node
        return self.endpoints['publicnode_rpc']
    
    def get_rpc_url(self) -> str:
        """Get formatted RPC URL with API key"""
        rpc = self.get_active_rpc()
        if rpc.api_key:
            return f"{rpc.url}?api_key={rpc.api_key}"
        return rpc.url
    
    def get_swap_api(self) -> APIEndpoint:
        """Get the swap API endpoint"""
        return self.endpoints['jupiter_swap']
    
    def get_mev_endpoints(self) -> List[APIEndpoint]:
        """Get all MEV protection endpoints"""
        mev_endpoints = []
        for key in ['zeroslot_primary', 'nozomi_primary', 'nextblock']:
            endpoint = self.endpoints.get(key)
            if endpoint and endpoint.active:
                mev_endpoints.append(endpoint)
        return mev_endpoints
    
    def get_analytics_apis(self) -> List[APIEndpoint]:
        """Get analytics and data APIs"""
        return [
            self.endpoints['jupiter_token'],
            self.endpoints['jupiter_price'],
            self.endpoints['jupiter_ultra']
        ]
    
    def switch_rpc(self, endpoint_key: str) -> bool:
        """Switch to a different RPC endpoint"""
        endpoint = self.endpoints.get(endpoint_key)
        if endpoint and endpoint.service_type == ServiceType.RPC:
            self.current_rpc = endpoint
            return True
        return False
    
    def get_endpoint_status(self) -> Dict[str, Dict]:
        """Get status of all endpoints"""
        status = {}
        for key, endpoint in self.endpoints.items():
            status[key] = {
                'name': endpoint.name,
                'url': endpoint.url,
                'type': endpoint.service_type.value,
                'active': endpoint.active,
                'has_key': bool(endpoint.api_key),
                'description': endpoint.description
            }
        return status
    
    def get_jupiter_endpoints(self) -> Dict[str, str]:
        """Get all Jupiter API endpoints for trading"""
        return {
            # Swap API
            'quote': f"{self.endpoints['jupiter_swap'].url}/quote",
            'swap': f"{self.endpoints['jupiter_swap'].url}/swap", 
            'swap_instructions': f"{self.endpoints['jupiter_swap'].url}/swap-instructions",
            'program_labels': f"{self.endpoints['jupiter_swap'].url}/program-id-to-label",
            
            # Ultra API
            'ultra_order': f"{self.endpoints['jupiter_ultra'].url}/order",
            'ultra_execute': f"{self.endpoints['jupiter_ultra'].url}/execute",
            'ultra_holdings': f"{self.endpoints['jupiter_ultra'].url}/holdings",
            'ultra_shield': f"{self.endpoints['jupiter_ultra'].url}/shield",
            'ultra_search': f"{self.endpoints['jupiter_ultra'].url}/search",
            
            # Token API
            'token_search': f"{self.endpoints['jupiter_token'].url}/search",
            'token_recent': f"{self.endpoints['jupiter_token'].url}/recent",
            
            # Price API
            'prices': f"{self.endpoints['jupiter_price'].url}/price"
        }
    
    def get_tip_accounts(self) -> Dict[str, str]:
        """Get tip accounts for MEV protection"""
        return {
            'zeroslot': '6rYLG55Q9RpsPGvqdPNJs4z5WTxJVatMB8zV3WJhs5EK',
            'nozomi': 'nozWNju6dY353eMkMqURqwQEoM3SFgEKC6psLCSfUne',
            'zeroslot_tip_value': '0.0015'
        }
    
    def get_headers_for_endpoint(self, endpoint_key: str) -> Dict[str, str]:
        """Get appropriate headers for an endpoint"""
        endpoint = self.endpoints.get(endpoint_key)
        if not endpoint:
            return {}
        
        headers = {
            'User-Agent': 'SolanaTraderBot/1.0',
            'Content-Type': 'application/json'
        }
        
        if endpoint.api_key:
            if 'shyft' in endpoint_key:
                headers['x-api-key'] = endpoint.api_key
            elif 'nextblock' in endpoint_key:
                headers['Authorization'] = f'Bearer {endpoint.api_key}'
            else:
                headers['X-API-KEY'] = endpoint.api_key
        
        if endpoint.headers:
            headers.update(endpoint.headers)
        
        return headers

# Global API manager instance
api_manager = TradingBotAPIManager()

# Configuration constants
class APIConfig:
    """API Configuration Constants"""
    
    # Timeouts
    RPC_TIMEOUT = 30
    API_TIMEOUT = 15
    WEBSOCKET_TIMEOUT = 60
    
    # Retry settings
    MAX_RETRIES = 3
    RETRY_DELAY = 1
    
    # Rate limiting
    RPC_RATE_LIMIT = 100  # requests per second
    API_RATE_LIMIT = 50
    
    # Default values
    DEFAULT_SLIPPAGE_BPS = 100  # 1%
    DEFAULT_COMPUTE_UNIT_LIMIT = 200000
    DEFAULT_COMPUTE_UNIT_PRICE = 1000
    
    # MEV Protection
    ENABLE_MEV_PROTECTION = True
    MEV_TIP_LAMPORTS = 1500  # 0.0015 SOL
    
    @classmethod
    def get_active_config(cls) -> Dict:
        """Get current active configuration"""
        return {
            'rpc_url': api_manager.get_rpc_url(),
            'jupiter_endpoints': api_manager.get_jupiter_endpoints(),
            'mev_endpoints': [ep.url for ep in api_manager.get_mev_endpoints()],
            'tip_accounts': api_manager.get_tip_accounts(),
            'timeouts': {
                'rpc': cls.RPC_TIMEOUT,
                'api': cls.API_TIMEOUT,
                'websocket': cls.WEBSOCKET_TIMEOUT
            },
            'trading': {
                'default_slippage_bps': cls.DEFAULT_SLIPPAGE_BPS,
                'compute_unit_limit': cls.DEFAULT_COMPUTE_UNIT_LIMIT,
                'compute_unit_price': cls.DEFAULT_COMPUTE_UNIT_PRICE,
                'mev_protection': cls.ENABLE_MEV_PROTECTION,
                'mev_tip_lamports': cls.MEV_TIP_LAMPORTS
            }
        }

if __name__ == "__main__":
    # Test the API manager
    print("🔧 Solana Trading Bot API Manager")
    print("=" * 50)
    
    print(f"📡 Active RPC: {api_manager.get_active_rpc().name}")
    print(f"🔗 RPC URL: {api_manager.get_rpc_url()}")
    print()
    
    print("🚀 Jupiter Endpoints:")
    for name, url in api_manager.get_jupiter_endpoints().items():
        print(f"  • {name}: {url}")
    print()
    
    print("⚡ MEV Protection:")
    for endpoint in api_manager.get_mev_endpoints():
        print(f"  • {endpoint.name}: {endpoint.url}")
    print()
    
    print("💡 Tip Accounts:")
    for name, account in api_manager.get_tip_accounts().items():
        print(f"  • {name}: {account}")
    print()
    
    print("📊 Endpoint Status:")
    status = api_manager.get_endpoint_status()
    for key, info in status.items():
        status_icon = "🟢" if info['active'] else "🔴"
        key_icon = "🔑" if info['has_key'] else "🆓"
        print(f"  {status_icon} {key_icon} {info['name']} ({info['type']})")