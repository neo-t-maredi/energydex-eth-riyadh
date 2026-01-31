"""
PyBot - Historical Data Manager
Stores and retrieves price history from SQLite database
"""

import sqlite3
import os
from datetime import datetime, timedelta
from dex_handler import DEXHandler
import time

class HistoricalDataManager:
    def __init__(self, db_path='../data/pybot.db'):
        """Initialize database connection"""
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        self.db_path = db_path
        self.dex_handler = DEXHandler()
        self._init_database()
        print(f"✅ HistoricalDataManager initialized")
    
    def _init_database(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                dex_name TEXT NOT NULL,
                eth_price REAL NOT NULL,
                reserve_usdc REAL,
                reserve_weth REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arbitrage_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                buy_dex TEXT NOT NULL,
                sell_dex TEXT NOT NULL,
                buy_price REAL NOT NULL,
                sell_price REAL NOT NULL,
                trade_amount_eth REAL NOT NULL,
                gross_profit REAL NOT NULL,
                net_profit REAL NOT NULL,
                profit_pct REAL NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_prices(self):
        """Fetch and log current prices from all DEXs"""
        prices = self.dex_handler.get_all_prices()
        if not prices:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for dex_name, data in prices.items():
            cursor.execute('''
                INSERT INTO price_history (dex_name, eth_price, reserve_usdc, reserve_weth)
                VALUES (?, ?, ?, ?)
            ''', (dex_name, data['price'], data['reserve_usdc'], data['reserve_weth']))
        
        conn.commit()
        conn.close()
        return True
    
    def log_arbitrage(self, arb_data):
        """Log an arbitrage opportunity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO arbitrage_history 
            (buy_dex, sell_dex, buy_price, sell_price, trade_amount_eth, 
             gross_profit, net_profit, profit_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            arb_data['buy_dex'], arb_data['sell_dex'],
            arb_data['buy_price'], arb_data['sell_price'],
            arb_data['trade_amount_eth'],
            arb_data['gross_profit'], arb_data['net_profit'],
            arb_data['profit_pct']
        ))
        
        conn.commit()
        conn.close()
    
    def get_recent_prices(self, dex_name=None, hours=24, limit=1000):
        """Get recent price history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        time_threshold = datetime.now() - timedelta(hours=hours)
        
        if dex_name:
            cursor.execute('''
                SELECT timestamp, dex_name, eth_price, reserve_usdc, reserve_weth
                FROM price_history
                WHERE dex_name = ? AND timestamp >= ?
                ORDER BY timestamp DESC LIMIT ?
            ''', (dex_name, time_threshold, limit))
        else:
            cursor.execute('''
                SELECT timestamp, dex_name, eth_price, reserve_usdc, reserve_weth
                FROM price_history
                WHERE timestamp >= ?
                ORDER BY timestamp DESC LIMIT ?
            ''', (time_threshold, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'timestamp': row[0],
                'dex_name': row[1],
                'eth_price': row[2],
                'reserve_usdc': row[3],
                'reserve_weth': row[4]
            }
            for row in rows
        ]
    
    def get_price_stats(self, dex_name, hours=24):
        """Get price statistics for a DEX"""
        prices = self.get_recent_prices(dex_name=dex_name, hours=hours)
        if not prices:
            return None
        
        price_values = [p['eth_price'] for p in prices]
        
        return {
            'dex_name': dex_name,
            'current': price_values[0],
            'high': max(price_values),
            'low': min(price_values),
            'avg': sum(price_values) / len(price_values),
            'data_points': len(price_values)
        }

if __name__ == "__main__":
    manager = HistoricalDataManager()
    print("Database ready!")