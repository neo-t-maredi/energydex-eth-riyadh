"""
PyBot - Live Price Monitor
Connects to Uniswap V2 and fetches real-time ETH/USDC prices
"""

import os
from web3 import Web3
from dotenv import load_dotenv
import time
from datetime import datetime

# Load environment variables
load_dotenv()

class PriceMonitor:
    def __init__(self):
        # Connect to Ethereum via Alchemy
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('ALCHEMY_URL')))
        
        # Verify connection
        if not self.w3.is_connected():
            raise Exception("Failed to connect to Ethereum network")
        
        print("✅ Connected to Ethereum Mainnet")
        
        # Uniswap V2 ETH/USDC Pool address
        self.pool_address = '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc'
        
        # Minimal ABI - just the getReserves function we need
        self.pool_abi = [
            {
                "constant": True,
                "inputs": [],
                "name": "getReserves",
                "outputs": [
                    {"internalType": "uint112", "name": "_reserve0", "type": "uint112"},
                    {"internalType": "uint112", "name": "_reserve1", "type": "uint112"},
                    {"internalType": "uint32", "name": "_blockTimestampLast", "type": "uint32"}
                ],
                "payable": False,
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        # Create contract instance
        self.pool_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.pool_address),
            abi=self.pool_abi
        )
        
    def get_eth_price(self):
        """Fetch current ETH/USDC price from Uniswap V2"""
        try:
            # Get reserves from the pool
            reserves = self.pool_contract.functions.getReserves().call()
            
            # reserve0 = USDC (6 decimals)
            # reserve1 = WETH (18 decimals)
            reserve_usdc = reserves[0] / 10**6
            reserve_weth = reserves[1] / 10**18
            
            # Calculate price: USDC / WETH
            eth_price = reserve_usdc / reserve_weth
            
            return {
                'price': round(eth_price, 2),
                'reserve_usdc': round(reserve_usdc, 2),
                'reserve_weth': round(reserve_weth, 4),
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'dex': 'Uniswap V2'
            }
            
        except Exception as e:
            print(f" Error fetching price: {e}")
            return None
    
    def monitor_live(self, interval=5):
        """Monitor price in real-time"""
        print("\n PyBot - Live ETH Price Monitor")
        print("=" * 50)
        print(f"Monitoring Uniswap V2 ETH/USDC Pool")
        print(f"Update interval: {interval} seconds")
        print("=" * 50)
        print("\nPress Ctrl+C to stop\n")
        
        try:
            while True:
                price_data = self.get_eth_price()
                
                if price_data:
                    print(f"[{price_data['timestamp']}] "
                          f"ETH/USDC: ${price_data['price']:,.2f} "
                          f"| Pool: {price_data['reserve_usdc']:,.0f} USDC / "
                          f"{price_data['reserve_weth']:,.2f} WETH")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n Monitoring stopped")

# Test the monitor
if __name__ == "__main__":
    monitor = PriceMonitor()
    monitor.monitor_live()