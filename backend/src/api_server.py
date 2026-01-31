"""
PyBot - API Server
Flask + WebSocket server that connects all components
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import time
from datetime import datetime

from price_monitor import PriceMonitor
from dex_handler import DEXHandler
from arbitrage_detector import ArbitrageDetector
from historical_data import HistoricalDataManager
from trade_simulator import TradeSimulator
from profit_calculator import ProfitCalculator

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize all components
print("Initializing PyBot API Server...")
price_monitor = PriceMonitor()
dex_handler = DEXHandler()
arbitrage_detector = ArbitrageDetector(min_profit_usd=5, min_profit_pct=0.1)
historical_manager = HistoricalDataManager()
trade_simulator = TradeSimulator()
profit_calculator = ProfitCalculator()

# Global state
is_monitoring = False
monitor_thread = None

print("All components initialized!")

# ==================== REST API ENDPOINTS ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'price_monitor': 'active',
            'dex_handler': 'active',
            'arbitrage_detector': 'active',
            'historical_manager': 'active',
            'trade_simulator': 'active'
        }
    })

@app.route('/api/prices/current', methods=['GET'])
def get_current_prices():
    """Get current prices from all DEXs"""
    prices = dex_handler.get_all_prices()
    return jsonify({
        'success': True,
        'data': prices,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/prices/comparison', methods=['GET'])
def get_price_comparison():
    """Get price comparison across DEXs"""
    comparison = dex_handler.compare_prices()
    return jsonify({
        'success': True,
        'data': comparison,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/arbitrage/detect', methods=['POST'])
def detect_arbitrage():
    """Detect arbitrage opportunities"""
    data = request.json or {}
    trade_amounts = data.get('trade_amounts', [0.5, 1.0, 5.0])
    
    opportunities = arbitrage_detector.detect_opportunities(trade_amounts)
    
    return jsonify({
        'success': True,
        'data': {
            'opportunities': opportunities,
            'count': len(opportunities)
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/historical/prices', methods=['GET'])
def get_historical_prices():
    """Get historical price data"""
    dex_name = request.args.get('dex_name')
    hours = int(request.args.get('hours', 24))
    
    prices = historical_manager.get_recent_prices(dex_name=dex_name, hours=hours)
    
    return jsonify({
        'success': True,
        'data': prices,
        'count': len(prices),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/historical/stats', methods=['GET'])
def get_price_stats():
    """Get price statistics"""
    dex_name = request.args.get('dex_name', 'Uniswap V2')
    hours = int(request.args.get('hours', 24))
    
    stats = historical_manager.get_price_stats(dex_name, hours)
    
    return jsonify({
        'success': True,
        'data': stats,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/trade/simulate', methods=['POST'])
def simulate_trade():
    """Simulate a trade"""
    data = request.json
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    # Simulate the trade
    result = trade_simulator.simulate_trade(data)
    
    return jsonify({
        'success': True,
        'data': result,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/trade/statistics', methods=['GET'])
def get_trade_statistics():
    """Get trading statistics"""
    stats = trade_simulator.get_statistics()
    
    return jsonify({
        'success': True,
        'data': stats,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/trade/history', methods=['GET'])
def get_trade_history():
    """Get recent trade history"""
    limit = int(request.args.get('limit', 10))
    trades = trade_simulator.get_recent_trades(limit)
    
    return jsonify({
        'success': True,
        'data': trades,
        'count': len(trades),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/profit/calculate', methods=['POST'])
def calculate_profit():
    """Calculate profit for given parameters"""
    data = request.json
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    result = profit_calculator.calculate_net_profit(
        buy_price=data['buy_price'],
        sell_price=data['sell_price'],
        trade_amount_eth=data['trade_amount_eth'],
        buy_dex=data['buy_dex'],
        sell_dex=data['sell_dex'],
        include_slippage=data.get('include_slippage', True)
    )
    
    return jsonify({
        'success': True,
        'data': result,
        'timestamp': datetime.now().isoformat()
    })

# ==================== WEBSOCKET EVENTS ====================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(' Client connected')
    emit('connection_response', {
        'status': 'connected',
        'message': 'Connected to PyBot API',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(' Client disconnected')

@socketio.on('start_monitoring')
def handle_start_monitoring(data):
    """Start real-time monitoring"""
    global is_monitoring, monitor_thread
    
    if is_monitoring:
        emit('monitoring_response', {
            'status': 'already_running',
            'message': 'Monitoring already active'
        })
        return
    
    interval = data.get('interval', 5)
    is_monitoring = True
    
    monitor_thread = threading.Thread(
        target=background_monitor,
        args=(interval,),
        daemon=True
    )
    monitor_thread.start()
    
    emit('monitoring_response', {
        'status': 'started',
        'message': f'Monitoring started (interval: {interval}s)',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('stop_monitoring')
def handle_stop_monitoring():
    """Stop real-time monitoring"""
    global is_monitoring
    
    is_monitoring = False
    
    emit('monitoring_response', {
        'status': 'stopped',
        'message': 'Monitoring stopped',
        'timestamp': datetime.now().isoformat()
    })

def background_monitor(interval):
    """Background thread for real-time monitoring"""
    global is_monitoring
    
    print(f" Background monitoring started (interval: {interval}s)")
    
    while is_monitoring:
        try:
            # Get current prices
            prices = dex_handler.get_all_prices()
            
            # Get comparison
            comparison = dex_handler.compare_prices()
            
            # Detect arbitrage
            opportunities = arbitrage_detector.detect_opportunities([0.5, 1.0, 5.0])
            
            # Log to database
            historical_manager.log_prices()
            
            # Emit updates via WebSocket
            socketio.emit('price_update', {
                'prices': prices,
                'comparison': comparison,
                'timestamp': datetime.now().isoformat()
            })
            
            if opportunities:
                socketio.emit('arbitrage_alert', {
                    'opportunities': opportunities,
                    'count': len(opportunities),
                    'timestamp': datetime.now().isoformat()
                })
            
            time.sleep(interval)
            
        except Exception as e:
            print(f"Error in background monitor: {e}")
            socketio.emit('error', {
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            })
            time.sleep(interval)
    
    print(" Background monitoring stopped")

# ==================== START SERVER ====================

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("PyBot API Server")
    print("=" * 70)
    print(" REST API: http://localhost:5000")
    print(" WebSocket: ws://localhost:5000")
    print("=" * 70)
    print("\nAvailable Endpoints:")
    print("  GET  /api/health")
    print("  GET  /api/prices/current")
    print("  GET  /api/prices/comparison")
    print("  POST /api/arbitrage/detect")
    print("  GET  /api/historical/prices")
    print("  GET  /api/historical/stats")
    print("  POST /api/trade/simulate")
    print("  GET  /api/trade/statistics")
    print("  GET  /api/trade/history")
    print("  POST /api/profit/calculate")
    print("\nWebSocket Events:")
    print("  → start_monitoring")
    print("  → stop_monitoring")
    print("  ← price_update")
    print("  ← arbitrage_alert")
    print("=" * 70)
    print("\n Starting server...\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)