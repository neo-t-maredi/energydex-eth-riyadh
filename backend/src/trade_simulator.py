"""
PyBot - Trade Simulator
Simulates trade execution and tracks performance
"""

from datetime import datetime
from profit_calculator import ProfitCalculator
import json

class TradeSimulator:
    def __init__(self):
        self.profit_calc = ProfitCalculator()
        self.trade_history = []
        self.total_profit = 0
        self.total_trades = 0
        self.successful_trades = 0
        
        print("TradeSimulator initialized")
    
    def simulate_trade(self, arbitrage_opportunity):
        """
        Simulate executing an arbitrage trade
        
        Args:
            arbitrage_opportunity: Dict from ArbitrageDetector
        
        Returns:
            Trade execution result
        """
        # Extract data
        buy_dex = arbitrage_opportunity['buy_dex']
        sell_dex = arbitrage_opportunity['sell_dex']
        buy_price = arbitrage_opportunity['buy_price']
        sell_price = arbitrage_opportunity['sell_price']
        trade_amount = arbitrage_opportunity['trade_amount_eth']
        
        # Calculate detailed profit
        profit_breakdown = self.profit_calc.calculate_net_profit(
            buy_price=buy_price,
            sell_price=sell_price,
            trade_amount_eth=trade_amount,
            buy_dex=buy_dex,
            sell_dex=sell_dex,
            include_slippage=True
        )
        
        # Determine if trade would be successful
        is_successful = profit_breakdown['net_profit'] > 0
        
        # Create trade record
        trade_record = {
            'timestamp': datetime.now().isoformat(),
            'trade_id': f"TRADE_{self.total_trades + 1}",
            'buy_dex': buy_dex,
            'sell_dex': sell_dex,
            'buy_price': buy_price,
            'sell_price': sell_price,
            'trade_amount_eth': trade_amount,
            'profit_breakdown': profit_breakdown,
            'is_successful': is_successful,
            'status': 'SUCCESS' if is_successful else 'FAILED'
        }
        
        # Update statistics
        self.trade_history.append(trade_record)
        self.total_trades += 1
        
        if is_successful:
            self.successful_trades += 1
            self.total_profit += profit_breakdown['net_profit']
        
        return trade_record
    
    def get_statistics(self):
        """Get trading statistics"""
        if self.total_trades == 0:
            return {
                'total_trades': 0,
                'successful_trades': 0,
                'failed_trades': 0,
                'success_rate': 0,
                'total_profit': 0,
                'avg_profit_per_trade': 0
            }
        
        return {
            'total_trades': self.total_trades,
            'successful_trades': self.successful_trades,
            'failed_trades': self.total_trades - self.successful_trades,
            'success_rate': round((self.successful_trades / self.total_trades) * 100, 2),
            'total_profit': round(self.total_profit, 2),
            'avg_profit_per_trade': round(self.total_profit / self.successful_trades if self.successful_trades > 0 else 0, 2),
            'best_trade': self._get_best_trade(),
            'worst_trade': self._get_worst_trade()
        }
    
    def _get_best_trade(self):
        """Find the most profitable trade"""
        if not self.trade_history:
            return None
        
        best = max(self.trade_history, 
                   key=lambda x: x['profit_breakdown']['net_profit'])
        return {
            'trade_id': best['trade_id'],
            'timestamp': best['timestamp'],
            'net_profit': best['profit_breakdown']['net_profit'],
            'trade_amount': best['trade_amount_eth']
        }
    
    def _get_worst_trade(self):
        """Find the least profitable trade"""
        if not self.trade_history:
            return None
        
        worst = min(self.trade_history,
                    key=lambda x: x['profit_breakdown']['net_profit'])
        return {
            'trade_id': worst['trade_id'],
            'timestamp': worst['timestamp'],
            'net_profit': worst['profit_breakdown']['net_profit'],
            'trade_amount': worst['trade_amount_eth']
        }
    
    def get_recent_trades(self, limit=10):
        """Get most recent trades"""
        return self.trade_history[-limit:] if self.trade_history else []
    
    def print_trade_result(self, trade_record):
        """Pretty print a trade result"""
        print("\n" + "=" * 70)
        print(f"TRADE SIMULATION: {trade_record['trade_id']}")
        print("=" * 70)
        print(f"Status: {trade_record['status']}")
        print(f"Time: {trade_record['timestamp']}")
        print()
        print(f"Buy from {trade_record['buy_dex']:12} @ ${trade_record['buy_price']:,.2f}")
        print(f"Sell on {trade_record['sell_dex']:12} @ ${trade_record['sell_price']:,.2f}")
        print(f"Trade Size: {trade_record['trade_amount_eth']} ETH")
        print()
        
        breakdown = trade_record['profit_breakdown']
        print("Profit Breakdown:")
        print(f"  Gross Profit:    ${breakdown['gross_profit']:>10}")
        print(f"  DEX Fees:       -${breakdown['total_dex_fees']:>10}")
        print(f"  Gas Cost:       -${breakdown['gas_cost']:>10}")
        print(f"  Slippage:       -${breakdown['slippage_cost']:>10}")
        print(f"  {'─' * 30}")
        print(f"  NET PROFIT:      ${breakdown['net_profit']:>10} ({breakdown['roi_pct']}% ROI)")
        print("=" * 70)
    
    def print_statistics(self):
        """Pretty print trading statistics"""
        stats = self.get_statistics()
        
        print("\n" + "=" * 70)
        print("TRADING STATISTICS")
        print("=" * 70)
        print(f"Total Trades:      {stats['total_trades']}")
        print(f"Successful:        {stats['successful_trades']} ({stats['success_rate']}%)")
        print(f"Failed:            {stats['failed_trades']}")
        print(f"Total Profit:      ${stats['total_profit']}")
        print(f"Avg Profit/Trade:  ${stats['avg_profit_per_trade']}")
        
        if stats['best_trade']:
            print(f"\nBest Trade:        {stats['best_trade']['trade_id']}")
            print(f"  Profit: ${stats['best_trade']['net_profit']}")
        
        if stats['worst_trade']:
            print(f"\nWorst Trade:       {stats['worst_trade']['trade_id']}")
            print(f"  Profit: ${stats['worst_trade']['net_profit']}")
        
        print("=" * 70)
    
    def export_history(self, filepath='../data/trade_history.json'):
        """Export trade history to JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.trade_history, f, indent=2)
        print(f"Trade history exported to {filepath}")

if __name__ == "__main__":
    # Example usage
    simulator = TradeSimulator()
    
    # Simulate an example trade
    example_opportunity = {
        'buy_dex': 'SushiSwap',
        'sell_dex': 'Uniswap V2',
        'buy_price': 3285.12,
        'sell_price': 3287.45,
        'trade_amount_eth': 1.0
    }
    
    result = simulator.simulate_trade(example_opportunity)
    simulator.print_trade_result(result)
    simulator.print_statistics()

    