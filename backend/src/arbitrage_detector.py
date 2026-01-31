"""
PyBot - Arbitrage Detector
Identifies profitable arbitrage opportunities between DEXs
"""

import os
from web3 import Web3
from dotenv import load_dotenv
from datetime import datetime
from dex_handler import DEXHandler

load_dotenv()

class ArbitrageDetector:
    def __init__(self, min_profit_usd=5, min_profit_pct=0.1):
        """
        Initialize arbitrage detector
        
        Args:
            min_profit_usd: Minimum profit in USD to consider (after gas)
            min_profit_pct: Minimum profit percentage to consider
        """
        self.dex_handler = DEXHandler()
        self.min_profit_usd = min_profit_usd
        self.min_profit_pct = min_profit_pct
        
        # Estimated gas costs (in USD) - rough estimates
        self.gas_cost_swap = 15  # ~$15 per swap on mainnet
        self.gas_cost_total = self.gas_cost_swap * 2  # Buy + Sell
        
        print(f"   ArbitrageDetector initialized")
        print(f"   Min Profit: ${min_profit_usd} ({min_profit_pct}%)")
        print(f"   Est. Gas Cost: ${self.gas_cost_total}")
    
    def calculate_arbitrage(self, trade_amount_eth=1.0):
        """
        Calculate arbitrage opportunity
        
        Args:
            trade_amount_eth: Amount of ETH to trade (default 1.0)
        
        Returns:
            Dictionary with arbitrage details or None
        """
        comparison = self.dex_handler.compare_prices()
        
        if not comparison:
            return None
        
        buy_dex = comparison['lowest']['dex']
        sell_dex = comparison['highest']['dex']
        buy_price = comparison['lowest']['price']
        sell_price = comparison['highest']['price']
        
        # Calculate costs and profits
        buy_cost = trade_amount_eth * buy_price
        sell_revenue = trade_amount_eth * sell_price
        
        gross_profit = sell_revenue - buy_cost
        net_profit = gross_profit - self.gas_cost_total
        
        profit_pct = (gross_profit / buy_cost) * 100
        net_profit_pct = (net_profit / buy_cost) * 100
        
        # Determine if profitable
        is_profitable = (net_profit >= self.min_profit_usd and 
                        profit_pct >= self.min_profit_pct)
        
        return {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'trade_amount_eth': trade_amount_eth,
            'buy_dex': buy_dex,
            'sell_dex': sell_dex,
            'buy_price': buy_price,
            'sell_price': sell_price,
            'buy_cost': round(buy_cost, 2),
            'sell_revenue': round(sell_revenue, 2),
            'gross_profit': round(gross_profit, 2),
            'gas_cost': self.gas_cost_total,
            'net_profit': round(net_profit, 2),
            'profit_pct': round(profit_pct, 3),
            'net_profit_pct': round(net_profit_pct, 3),
            'is_profitable': is_profitable,
            'price_spread': comparison['difference'],
            'price_spread_pct': comparison['difference_pct']
        }
    
    def detect_opportunities(self, trade_amounts=[0.1, 0.5, 1.0, 5.0]):
        """
        Detect arbitrage opportunities for multiple trade amounts
        
        Args:
            trade_amounts: List of ETH amounts to test
        
        Returns:
            List of profitable opportunities
        """
        opportunities = []
        
        for amount in trade_amounts:
            arb = self.calculate_arbitrage(trade_amount_eth=amount)
            
            if arb and arb['is_profitable']:
                opportunities.append(arb)
        
        return opportunities
    
    def monitor_arbitrage(self, interval=10, trade_amounts=[0.5, 1.0, 5.0]):
        """Monitor for arbitrage opportunities in real-time"""
        import time
        
        print("\n PyBot - Arbitrage Opportunity Monitor")
        print("=" * 80)
        print(f"Testing trade amounts: {trade_amounts} ETH")
        print(f"Update interval: {interval} seconds")
        print("=" * 80)
        print("\nPress Ctrl+C to stop\n")
        
        opportunities_found = 0
        
        try:
            while True:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scanning...")
                print("-" * 80)
                
                opportunities = self.detect_opportunities(trade_amounts)
                
                if opportunities:
                    opportunities_found += len(opportunities)
                    print(f" ARBITRAGE OPPORTUNITY DETECTED! \n")
                    
                    for opp in opportunities:
                        print(f"Trade Size: {opp['trade_amount_eth']} ETH")
                        print(f"  Buy  {opp['buy_dex']:12} @ ${opp['buy_price']:,.2f} = ${opp['buy_cost']:,.2f}")
                        print(f"  Sell {opp['sell_dex']:12} @ ${opp['sell_price']:,.2f} = ${opp['sell_revenue']:,.2f}")
                        print(f"  Gross Profit: ${opp['gross_profit']} ({opp['profit_pct']}%)")
                        print(f"  Gas Cost: -${opp['gas_cost']}")
                        print(f"  NET PROFIT: ${opp['net_profit']} ({opp['net_profit_pct']}%)")
                        print()
                else:
                    # Still show current prices even without opportunity
                    arb = self.calculate_arbitrage(trade_amount_eth=1.0)
                    if arb:
                        print(f"Current Spread: ${arb['price_spread']} ({arb['price_spread_pct']}%)")
                        print(f"  {arb['buy_dex']}: ${arb['buy_price']:,.2f}")
                        print(f"  {arb['sell_dex']}: ${arb['sell_price']:,.2f}")
                        print(f"  Net Profit (1 ETH): ${arb['net_profit']} - NOT PROFITABLE")
                
                print(f"\nTotal Opportunities Found: {opportunities_found}")
                print("-" * 80)
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n\n Monitoring stopped")
            print(f" Total opportunities detected: {opportunities_found}")

# Test the detector
if __name__ == "__main__":
    # Initialize with reasonable thresholds
    detector = ArbitrageDetector(
        min_profit_usd=5,      # Need at least $5 profit
        min_profit_pct=0.1     # Need at least 0.1% profit
    )
    
    detector.monitor_arbitrage(interval=10)

