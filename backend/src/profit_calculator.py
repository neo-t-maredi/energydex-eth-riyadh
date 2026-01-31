"""
PyBot - Profit Calculator
Advanced profit calculations including gas fees, slippage, and MEV considerations
"""

class ProfitCalculator:
    def __init__(self):
        # Gas cost estimates (in USD)
        self.gas_costs = {
            'swap': 15,           # Single swap
            'approve': 10,        # Token approval
            'flash_loan': 25,     # Flash loan execution
        }
        
        # Default slippage tolerance
        self.default_slippage = 0.005  # 0.5%
        
        # DEX fees
        self.dex_fees = {
            'Uniswap V2': 0.003,     # 0.3%
            'SushiSwap': 0.003,      # 0.3%
        }
        
        print("✅ ProfitCalculator initialized")
    
    def calculate_trade_cost(self, trade_type='standard'):
        """Calculate total gas cost for a trade"""
        if trade_type == 'standard':
            return self.gas_costs['swap'] * 2  # Buy + Sell
        elif trade_type == 'flash_loan':
            return self.gas_costs['flash_loan']
        else:
            return self.gas_costs['swap']
    
    def calculate_slippage_impact(self, amount, price, slippage=None):
        """Calculate potential slippage impact"""
        if slippage is None:
            slippage = self.default_slippage
        
        slippage_loss = amount * price * slippage
        return slippage_loss
    
    def calculate_dex_fee(self, trade_value, dex_name):
        """Calculate DEX trading fee"""
        fee_rate = self.dex_fees.get(dex_name, 0.003)
        return trade_value * fee_rate
    
    def calculate_net_profit(self, buy_price, sell_price, trade_amount_eth, 
                            buy_dex, sell_dex, include_slippage=True):
        """
        Calculate comprehensive net profit
        
        Returns:
            Dictionary with detailed breakdown
        """
        # Gross calculation
        buy_cost = trade_amount_eth * buy_price
        sell_revenue = trade_amount_eth * sell_price
        gross_profit = sell_revenue - buy_cost
        
        # Fee calculations
        buy_fee = self.calculate_dex_fee(buy_cost, buy_dex)
        sell_fee = self.calculate_dex_fee(sell_revenue, sell_dex)
        total_dex_fees = buy_fee + sell_fee
        
        # Gas costs
        gas_cost = self.calculate_trade_cost('standard')
        
        # Slippage
        slippage_cost = 0
        if include_slippage:
            buy_slippage = self.calculate_slippage_impact(trade_amount_eth, buy_price)
            sell_slippage = self.calculate_slippage_impact(trade_amount_eth, sell_price)
            slippage_cost = buy_slippage + sell_slippage
        
        # Net profit
        net_profit = gross_profit - total_dex_fees - gas_cost - slippage_cost
        
        # ROI calculations
        total_cost = buy_cost + total_dex_fees + gas_cost + slippage_cost
        roi_pct = (net_profit / total_cost) * 100 if total_cost > 0 else 0
        
        return {
            'trade_amount_eth': trade_amount_eth,
            'buy_price': buy_price,
            'sell_price': sell_price,
            'buy_cost': round(buy_cost, 2),
            'sell_revenue': round(sell_revenue, 2),
            'gross_profit': round(gross_profit, 2),
            'buy_dex_fee': round(buy_fee, 2),
            'sell_dex_fee': round(sell_fee, 2),
            'total_dex_fees': round(total_dex_fees, 2),
            'gas_cost': round(gas_cost, 2),
            'slippage_cost': round(slippage_cost, 2),
            'total_costs': round(total_dex_fees + gas_cost + slippage_cost, 2),
            'net_profit': round(net_profit, 2),
            'roi_pct': round(roi_pct, 3)
        }
    
    def find_optimal_trade_size(self, buy_price, sell_price, buy_dex, sell_dex,
                                max_eth=10, step=0.1):
        """Find the optimal trade size for maximum profit"""
        best_profit = -float('inf')
        best_size = 0
        
        trade_sizes = []
        current = step
        while current <= max_eth:
            trade_sizes.append(current)
            current += step
        
        for size in trade_sizes:
            calc = self.calculate_net_profit(
                buy_price, sell_price, size, buy_dex, sell_dex
            )
            
            if calc['net_profit'] > best_profit:
                best_profit = calc['net_profit']
                best_size = size
        
        return {
            'optimal_size': best_size,
            'max_profit': best_profit,
            'tested_sizes': len(trade_sizes)
        }

if __name__ == "__main__":
    calc = ProfitCalculator()
    
    # Example calculation
    result = calc.calculate_net_profit(
        buy_price=3285.12,
        sell_price=3287.45,
        trade_amount_eth=1.0,
        buy_dex='SushiSwap',
        sell_dex='Uniswap V2'
    )
    
    print("\n💰 Profit Breakdown:")
    print(f"Trade Size: {result['trade_amount_eth']} ETH")
    print(f"Gross Profit: ${result['gross_profit']}")
    print(f"DEX Fees: -${result['total_dex_fees']}")
    print(f"Gas Cost: -${result['gas_cost']}")
    print(f"Slippage: -${result['slippage_cost']}")
    print(f"NET PROFIT: ${result['net_profit']} ({result['roi_pct']}% ROI)")