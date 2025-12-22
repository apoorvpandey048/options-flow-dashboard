"""
Main Flask application with WebSocket support for real-time options flow
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import time
import os
from datetime import datetime

from config import Config
from options_monitor import options_monitor
from strategy_backtester import strategy_backtester
from data_fetcher import data_fetcher
from auth import register_user, login_user, token_required

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
# CORS - only allow frontend origin for security
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, resources={r"/*": {"origins": allowed_origins}})
socketio = SocketIO(app, cors_allowed_origins=allowed_origins, async_mode='threading')

# Global state
active_connections = set()
active_subscriptions = {}  # {sid: {symbol: timeframe}}
streaming_active = False


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    token, error = register_user(username, password, email or '')
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'token': token,
        'username': username
    })


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    token, error = login_user(username, password)
    
    if error:
        return jsonify({'error': error}), 401
    
    return jsonify({
        'token': token,
        'username': username
    })


@app.route('/api/auth/verify', methods=['GET'])
@token_required
def verify(username):
    """Verify token"""
    return jsonify({
        'valid': True,
        'username': username
    })


@app.route('/api/symbols', methods=['GET'])
def get_symbols():
    """Get list of available symbols"""
    return jsonify({
        'symbols': Config.SYMBOLS,
        'timeframes': Config.TIMEFRAMES
    })


@app.route('/api/monitor/<symbol>', methods=['GET'])
def get_monitor_data(symbol):
    """Get options flow data for a specific symbol"""
    timeframe = request.args.get('timeframe', '5min')
    
    if symbol not in Config.SYMBOLS:
        return jsonify({'error': 'Invalid symbol'}), 400
    
    if timeframe not in Config.TIMEFRAMES:
        return jsonify({'error': 'Invalid timeframe'}), 400
    
    data = options_monitor.get_monitor_data(symbol, timeframe)
    return jsonify(data)


@app.route('/api/monitor/<symbol>/all-timeframes', methods=['GET'])
def get_all_timeframes(symbol):
    """Get data for all timeframes for a symbol"""
    if symbol not in Config.SYMBOLS:
        return jsonify({'error': 'Invalid symbol'}), 400
    
    data = options_monitor.get_all_timeframes(symbol)
    return jsonify(data)


@app.route('/api/monitor/summary', methods=['GET'])
def get_summary():
    """Get summary for all symbols"""
    timeframe = request.args.get('timeframe', '5min')
    data = options_monitor.get_all_symbols_summary(timeframe)
    return jsonify(data)


@app.route('/api/monitor/<symbol>/strikes', methods=['GET'])
def get_strike_analysis(symbol):
    """Get detailed strike-level analysis"""
    if symbol not in Config.SYMBOLS:
        return jsonify({'error': 'Invalid symbol'}), 400
    
    data = options_monitor.get_strike_analysis(symbol)
    return jsonify(data)


@app.route('/api/backtest/run', methods=['POST'])
def run_backtest():
    """Run strategy backtest with specified parameters"""
    params = request.json
    
    try:
        result = strategy_backtester.run_backtest(params)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/backtest/compare', methods=['POST'])
def compare_strategies():
    """Run and compare multiple strategies"""
    params = request.json
    
    try:
        result = strategy_backtester.compare_strategies(params)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    # Reduced logging of connection IDs for security
    active_connections.add(request.sid)
    emit('connection_response', {'status': 'connected', 'timestamp': datetime.now().isoformat()})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    active_connections.discard(request.sid)
    # Clean up subscriptions
    if request.sid in active_subscriptions:
        del active_subscriptions[request.sid]


@socketio.on('subscribe')
def handle_subscribe(data):
    """Subscribe to real-time updates for a symbol"""
    symbol = data.get('symbol', 'SPY')
    timeframe = data.get('timeframe', '5min')
    
    # Track subscription
    if request.sid not in active_subscriptions:
        active_subscriptions[request.sid] = {}
    active_subscriptions[request.sid][symbol] = timeframe
    
    emit('subscribed', {'symbol': symbol, 'timeframe': timeframe})


@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    """Unsubscribe from updates"""
    symbol = data.get('symbol')
    if request.sid in active_subscriptions and symbol in active_subscriptions[request.sid]:
        del active_subscriptions[request.sid][symbol]
    emit('unsubscribed', {'symbol': symbol})


@socketio.on('request_update')
def handle_request_update(data):
    """Handle manual update request"""
    symbol = data.get('symbol', 'SPY')
    timeframe = data.get('timeframe', '5min')
    
    monitor_data = options_monitor.get_monitor_data(symbol, timeframe)
    emit('monitor_update', monitor_data)


def background_streaming():
    """Background thread for streaming real-time data"""
    global streaming_active
    
    while streaming_active:
        if active_subscriptions:
            # Only stream data for active subscriptions (more efficient)
            symbols_to_update = set()
            timeframes_to_update = set()
            
            for sid, subs in active_subscriptions.items():
                for symbol, timeframe in subs.items():
                    symbols_to_update.add(symbol)
                    timeframes_to_update.add(timeframe)
            
            # Stream only subscribed data
            for symbol in symbols_to_update:
                for timeframe in timeframes_to_update:
                    data = options_monitor.get_monitor_data(symbol, timeframe)
                    socketio.emit('market_update', {
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'data': data
                    })
        
        time.sleep(Config.REFRESH_RATE)


def start_background_streaming():
    """Start the background streaming thread"""
    global streaming_active
    streaming_active = True
    thread = threading.Thread(target=background_streaming, daemon=True)
    thread.start()
    print('Background streaming started')


if __name__ == '__main__':
    print('='*60)
    print('Options Flow Monitor & Strategy Backtester')
    print('='*60)
    print(f'Starting server on http://localhost:5000')
    print(f'API Documentation: http://localhost:5000/api/health')
    print(f'WebSocket endpoint: ws://localhost:5000')
    print('='*60)
    
    # Start background streaming
    start_background_streaming()
    
    # Run the Flask app with SocketIO
    # Force debug=False in production for security
    debug_mode = Config.DEBUG if Config.FLASK_ENV != 'production' else False
    # Use PORT environment variable for deployment platforms (Render, Heroku, etc.)
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, debug=debug_mode, host='0.0.0.0', port=port)
