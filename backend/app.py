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
from historical_data_loader import historical_loader
from historical_replay import get_replay_loader

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
    replay_date = request.args.get('date')  # Format: YYYY-MM-DD
    replay_time = request.args.get('time')  # Format: HH:MM
    
    if symbol not in Config.SYMBOLS:
        return jsonify({'error': 'Invalid symbol'}), 400
    
    if timeframe not in Config.TIMEFRAMES:
        return jsonify({'error': 'Invalid timeframe'}), 400
    
    data = options_monitor.get_monitor_data(symbol, timeframe, replay_date, replay_time)
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


@app.route('/api/debug/clear-cache', methods=['POST'])
def clear_cache():
    """Debug endpoint to clear data fetcher cache"""
    try:
        data_fetcher.cache.clear()
        return jsonify({'cleared': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/debug/provider', methods=['GET'])
def debug_provider():
    """Return the active data provider name for debugging"""
    try:
        provider = data_fetcher.provider
        return jsonify({
            'provider_name': provider.get_provider_name(),
            'provider_class': provider.__class__.__name__
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitor/<symbol>/strikes', methods=['GET'])
def get_strike_analysis(symbol):
    """Get detailed strike-level analysis"""
    if symbol not in Config.SYMBOLS:
        return jsonify({'error': 'Invalid symbol'}), 400
    
    data = options_monitor.get_strike_analysis(symbol)
    return jsonify(data)


@app.route('/api/monitor/<symbol>/ratio', methods=['GET'])
def get_ratio_only(symbol):
    """Return minimal data: timestamp and put/call ratio, with a simple recommendation."""
    if symbol not in Config.SYMBOLS:
        return jsonify({'error': 'Invalid symbol'}), 400

    timeframe = request.args.get('timeframe', '5min')
    data = options_monitor.get_monitor_data(symbol, timeframe)
    ratio = data.get('put_call_ratio', None)

    if ratio is None:
        return jsonify({'error': 'Ratio not available'}), 500

    # Simple recommendation: buy PUT if ratio>1, buy CALL if ratio<1
    if ratio > 1.0:
        recommended = 'PUT'
    elif ratio < 1.0:
        recommended = 'CALL'
    else:
        recommended = 'NEUTRAL'

    return jsonify({
        'symbol': symbol,
        'timeframe': timeframe,
        'timestamp': data.get('timestamp'),
        'put_call_ratio': ratio,
        'recommended_side': recommended
    })


@app.route('/api/backtest/run', methods=['POST'])
def run_backtest():
    """Run strategy backtest with specified parameters"""
    params = request.json
    date = params.pop('date', None) if params else None
    
    try:
        result = strategy_backtester.run_backtest(params, date=date)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/backtest/compare', methods=['POST'])
def compare_strategies():
    """Run and compare multiple strategies"""
    params = request.json
    date = params.pop('date', None) if params else None
    
    try:
        result = strategy_backtester.compare_strategies(params, date=date)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Historical Data Replay endpoints
@app.route('/api/historical/dates', methods=['GET'])
@token_required
def get_historical_dates():
    """Get available historical dates with summaries"""
    try:
        dates = historical_loader.get_available_dates()
        summaries = [historical_loader.get_date_summary(date) for date in dates]
        return jsonify({
            'count': len(dates),
            'dates': summaries
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/historical/analysis/<date>', methods=['GET'])
@token_required
def get_historical_analysis(date):
    """Get full day analysis for a specific date"""
    try:
        analysis = historical_loader.get_full_day_analysis(date)
        if not analysis:
            return jsonify({'error': 'Date not found'}), 404
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/historical/unusual/<date>', methods=['GET'])
@token_required
def get_historical_unusual(date):
    """Get unusual activity for a date"""
    try:
        min_ratio = float(request.args.get('min_ratio', 1.5))
        activity = historical_loader.get_unusual_activity(date, min_ratio)
        return jsonify({
            'date': date,
            'count': len(activity),
            'activity': activity
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/historical/chart/<date>/<ticker>', methods=['GET'])
@token_required
def get_historical_chart(date, ticker):
    """Get intraday chart data for a specific contract"""
    try:
        chart_data = historical_loader.get_intraday_chart_data(date, ticker)
        if not chart_data:
            return jsonify({'error': 'Data not found'}), 404
        return jsonify(chart_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/historical/flow-score/<date>/<ticker>', methods=['GET'])
@token_required
def get_historical_flow_score(date, ticker):
    """Get flow score calculation for a specific contract"""
    try:
        score = historical_loader.calculate_flow_score(date, ticker)
        if not score:
            return jsonify({'error': 'Contract not found'}), 404
        return jsonify(score)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/historical/replay/snapshots/<date>', methods=['GET'])
@token_required
def get_replay_snapshots(date):
    """Get 4 time-based snapshots for a specific historical date"""
    try:
        symbol = request.args.get('symbol', 'SPY')
        replay_loader = get_replay_loader()
        snapshots = replay_loader.create_snapshots(date, symbol)
        
        return jsonify({
            'date': date,
            'symbol': symbol,
            'snapshots': snapshots,
            'count': len(snapshots)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/historical/replay/available-dates', methods=['GET'])
@token_required
def get_replay_available_dates():
    """Get list of available dates for replay"""
    # Return recent trading days (last 5 trading days)
    from datetime import datetime, timedelta
    dates = []
    current = datetime.now()
    
    # Go back up to 10 days to find 5 trading days (weekdays)
    for i in range(1, 11):
        date = current - timedelta(days=i)
        # Skip weekends
        if date.weekday() < 5:
            dates.append(date.strftime('%Y-%m-%d'))
            if len(dates) >= 5:
                break
    
    return jsonify({'dates': dates})


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
    # Allow Werkzeug in production (for deployment platforms like Render)
    # Note: In real production, use gunicorn or another WSGI server
    socketio.run(app, debug=debug_mode, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
