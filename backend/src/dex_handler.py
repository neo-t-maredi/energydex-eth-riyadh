"""
PyBot - Multi-DEX Handler
Fetches prices from multiple DEXs (Uniswap V2 & SushiSwap)
"""

import os
from web3 import Web3
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class DEXHandler:
    def __init__(self):
        # Connect to Ethereum
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('ALCHEMY_URL')))
        
        if not self.w3.is_connected():
            raise Exception("Failed to connect to Ethereum")
        
        # DEX Pool Addresses - ETH/USDC pairs
        self.pools = {
            'Uniswap V2': '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc',
            'SushiSwap': '0x397FF1542f962076d0BFE58eA045FfA2d347ACa0'
        }
        
        # Minimal ABI for getReserves
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
            },
            {
                "constant": True,
                "inputs": [],
                "name": "token0",
                "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                "payable": False,
                "stateMutability": "view",
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "token1",
                "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                "payable": False,
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        print(" DEXHandler initialized - Tracking Uniswap V2 & SushiSwap")
    
    def get_price_from_dex(self, dex_name):
        """Fetch price from a specific DEX"""
        try:
            pool_address = self.pools[dex_name]
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(pool_address),
                abi=self.pool_abi
            )
            
            # Get reserves
            reserves = contract.functions.getReserves().call()
            
            # USDC = 6 decimals, WETH = 18 decimals
            reserve_usdc = reserves[0] / 10**6
            reserve_weth = reserves[1] / 10**18
            
            # Calculate price
            eth_price = reserve_usdc / reserve_weth
            
            return {
                'dex': dex_name,
                'price': round(eth_price, 2),
                'reserve_usdc': round(reserve_usdc, 2),
                'reserve_weth': round(reserve_weth, 4),
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            
        except Exception as e:
            print(f" Error fetching from {dex_name}: {e}")
            return None
    
    def get_all_prices(self):
        """Fetch prices from all DEXs"""
        prices = {}
        
        for dex_name in self.pools.keys():
            price_data = self.get_price_from_dex(dex_name)
            if price_data:
                prices[dex_name] = price_data
        
        return prices
    
    def compare_prices(self):
        """Compare prices across DEXs and find differences"""
        prices = self.get_all_prices()
        
        if len(prices) < 2:
            return None
        
        # Extract just the price values
        dex_prices = {dex: data['price'] for dex, data in prices.items()}
        
        # Find highest and lowest
        highest_dex = max(dex_prices, key=dex_prices.get)
        lowest_dex = min(dex_prices, key=dex_prices.get)
        
        highest_price = dex_prices[highest_dex]
        lowest_price = dex_prices[lowest_dex]
        
        # Calculate difference
        price_diff = highest_price - lowest_price
        price_diff_pct = (price_diff / lowest_price) * 100
        
        return {
            'prices': prices,
            'highest': {'dex': highest_dex, 'price': highest_price},
            'lowest': {'dex': lowest_dex, 'price': lowest_price},
            'difference': round(price_diff, 2),
            'difference_pct': round(price_diff_pct, 3),
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
    
    def monitor_comparison(self, interval=5):
        """Monitor price differences in real-time"""
        import time
        
        print("\n PyBot - Multi-DEX Price Comparison")
        print("=" * 70)
        print(f"Comparing: {', '.join(self.pools.keys())}")
        print(f"Update interval: {interval} seconds")
        print("=" * 70)
        print("\nPress Ctrl+C to stop\n")
        
        try:
            while True:
                comparison = self.compare_prices()
                
                if comparison:
                    print(f"\n[{comparison['timestamp']}]")
                    print("-" * 70)
                    
                    for dex, data in comparison['prices'].items():
                        print(f"{dex:12} | ${data['price']:,.2f}")
                    
                    print("-" * 70)
                    print(f"Price Spread: ${comparison['difference']} "
                          f"({comparison['difference_pct']}%)")
                    print(f"   Buy on {comparison['lowest']['dex']} @ ${comparison['lowest']['price']}")
                    print(f"   Sell on {comparison['highest']['dex']} @ ${comparison['highest']['price']}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n Monitoring stopped")

# Test the handler
if __name__ == "__main__":
    handler = DEXHandler()
    handler.monitor_comparison()

