"""
Advanced Strategy Backtester Module
Implements put/call ratio strategies with multiple filters and comparisons
"""
import numpy as np
import pandas as pd
from datetime import datetime
from config import Config


class StrategyBacktester:
    """Backtest options trading strategies with advanced filters"""
    
    def __init__(self):
        self.default_params = {
            'put_call_threshold': Config.DEFAULT_PUT_CALL_THRESHOLD,
            'num_trades': Config.DEFAULT_NUM_TRADES,
            'initial_capital': Config.DEFAULT_INITIAL_CAPITAL,
            'position_size': Config.DEFAULT_POSITION_SIZE,
            'profit_target': Config.DEFAULT_PROFIT_TARGET,
            'stop_loss': Config.DEFAULT_STOP_LOSS,
            'volume_spike_threshold': Config.DEFAULT_VOLUME_SPIKE_THRESHOLD,
            'iv_threshold': Config.DEFAULT_IV_THRESHOLD,
            'use_volume_spike': True,
            'use_iv_filter': True,
            'use_multi_timeframe': True
        }
    
    def run_backtest(self, params=None):
        """Run a single backtest with given parameters"""
        if params is None:
            params = self.default_params.copy()
        else:
            # Merge with defaults
            p = self.default_params.copy()
            p.update(params)
            params = p
        
        # Validate parameters
        self._validate_params(params)
        
        result = self._execute_backtest(params, 'puts')
        return result
    
    def _validate_params(self, params):
        """Validate backtest parameters"""
        errors = []
        
        if params['num_trades'] <= 0:
            errors.append("Number of trades must be greater than 0")
        if params['num_trades'] > 100000:
            errors.append("Number of trades cannot exceed 100,000")
        if params['initial_capital'] <= 0:
            errors.append("Initial capital must be greater than 0")
        if params['position_size'] <= 0:
            errors.append("Position size must be greater than 0")
        if params['position_size'] > params['initial_capital']:
            errors.append("Position size cannot exceed initial capital")
        if params['profit_target'] <= 0 or params['profit_target'] > 10:
            errors.append("Profit target must be between 0% and 1000%")
        if params['stop_loss'] >= 0 or params['stop_loss'] < -1:
            errors.append("Stop loss must be between -100% and 0%")
        if params['put_call_threshold'] <= 0:
            errors.append("Put/Call threshold must be greater than 0")
        if params['volume_spike_threshold'] <= 0:
            errors.append("Volume spike threshold must be greater than 0")
        if params['iv_threshold'] < 0 or params['iv_threshold'] > 100:
            errors.append("IV threshold must be between 0 and 100")
        
        if errors:
            raise ValueError("Invalid parameters: " + "; ".join(errors))
    
    def compare_strategies(self, params=None):
        """Compare multiple strategies: advanced puts, basic puts, advanced calls"""
        if params is None:
            params = self.default_params.copy()
        else:
            p = self.default_params.copy()
            p.update(params)
            params = p
        
        # Validate parameters
        self._validate_params(params)
        
        # Run advanced puts strategy
        advanced_puts = self._execute_backtest(params, 'puts')
        
        # Run basic puts (no filters)
        basic_params = params.copy()
        basic_params.update({
            'use_volume_spike': False,
            'use_iv_filter': False,
            'use_multi_timeframe': False
        })
        basic_puts = self._execute_backtest(basic_params, 'puts')
        
        # Run advanced calls (inverse signals)
        advanced_calls = self._execute_backtest(params, 'calls')
        
        return {
            'advanced_puts': advanced_puts,
            'basic_puts': basic_puts,
            'advanced_calls': advanced_calls,
            'comparison': self._calculate_comparison(advanced_puts, basic_puts, advanced_calls)
        }
    
    def _execute_backtest(self, params, direction):
        """Execute backtest for a specific direction (puts or calls)"""
        trades = []
        capital = params['initial_capital']
        wins = 0
        losses = 0
        total_profit = 0
        max_drawdown = 0
        peak_capital = params['initial_capital']
        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        
        trades_attempted = 0
        trades_filtered = 0
        
        for i in range(params['num_trades'] * 3):  # Attempt 3x trades to account for filters
            if len(trades) >= params['num_trades']:
                break
            
            trades_attempted += 1
            
            # Simulate market conditions
            put_call_ratio = 0.8 + np.random.random() * 1.5
            volume_concentration = np.random.random()
            current_volume = 50000 + np.random.random() * 150000
            avg_volume = 100000
            volume_spike = current_volume / avg_volume
            iv_percentile = np.random.random() * 100
            
            # Multi-timeframe alignment
            tf5min = put_call_ratio + (np.random.random() - 0.5) * 0.1
            tf10min = put_call_ratio + (np.random.random() - 0.5) * 0.15
            tf30min = put_call_ratio + (np.random.random() - 0.5) * 0.2
            timeframe_alignment = (
                abs(tf5min - put_call_ratio) < 0.1 and 
                abs(tf10min - put_call_ratio) < 0.15 and
                abs(tf30min - put_call_ratio) < 0.2
            )
            
            # Entry logic with filters
            should_trade = False
            edge_bonus = 0
            
            if direction == 'puts':
                should_trade = put_call_ratio > params['put_call_threshold']
            else:
                should_trade = put_call_ratio < (2 - params['put_call_threshold'])
            
            if not should_trade:
                trades_filtered += 1
                continue
            
            # Apply filters
            if params['use_volume_spike']:
                if volume_spike > params['volume_spike_threshold']:
                    edge_bonus += 0.05  # 5% win probability boost
                else:
                    trades_filtered += 1
                    continue
            
            if params['use_iv_filter']:
                if params['iv_threshold'] < iv_percentile < 70:
                    edge_bonus += 0.04  # 4% win probability boost
                else:
                    trades_filtered += 1
                    continue
            
            if params['use_multi_timeframe']:
                if timeframe_alignment:
                    edge_bonus += 0.06  # 6% win probability boost
                else:
                    trades_filtered += 1
                    continue
            
            # Calculate win probability
            win_probability = 0.45 if direction == 'puts' else 0.43
            
            # Adjust for extreme readings
            if direction == 'puts':
                if put_call_ratio > 1.5:
                    win_probability = 0.52  # Oversold
                elif put_call_ratio > 1.3:
                    win_probability = 0.48
            else:
                if put_call_ratio < 0.9:
                    win_probability = 0.50  # Overbought
            
            # Volume concentration bonus
            if volume_concentration > 0.7:
                edge_bonus += 0.03
            
            # Apply edge bonus
            win_probability += edge_bonus
            
            # Execute trade
            is_win = np.random.random() < win_probability
            
            if is_win:
                # Winner - hit profit target or partial profit
                percent_return = params['profit_target'] if np.random.random() < 0.35 else (0.05 + np.random.random() * 0.15)
                wins += 1
                consecutive_wins += 1
                consecutive_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
            else:
                # Loser - hit stop loss or partial loss
                percent_return = params['stop_loss'] if np.random.random() < 0.4 else (-0.10 - np.random.random() * 0.40)
                losses += 1
                consecutive_losses += 1
                consecutive_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
            
            trade_profit = params['position_size'] * percent_return
            capital += trade_profit
            total_profit += trade_profit
            
            # Track drawdown
            if capital > peak_capital:
                peak_capital = capital
            current_drawdown = ((peak_capital - capital) / peak_capital) * 100 if peak_capital > 0 else 0
            max_drawdown = max(max_drawdown, current_drawdown)
            
            # Record trade
            trades.append({
                'trade_num': len(trades) + 1,
                'direction': direction,
                'put_call_ratio': round(put_call_ratio, 4),
                'volume_spike': round(volume_spike, 2),
                'iv_percentile': round(iv_percentile, 1),
                'timeframe_align': 'Yes' if timeframe_alignment else 'No',
                'volume_conc': round(volume_concentration * 100, 1),
                'result': 'Win' if is_win else 'Loss',
                'percent_return': round(percent_return * 100, 2),
                'profit': round(trade_profit, 2),
                'capital': round(capital, 2),
                'drawdown': round(current_drawdown, 2),
                'win_prob': round(win_probability * 100, 1)
            })
        
        # Calculate metrics
        total_trades = wins + losses
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        winning_trades = [t for t in trades if t['result'] == 'Win']
        losing_trades = [t for t in trades if t['result'] == 'Loss']
        
        avg_win = np.mean([t['profit'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['profit'] for t in losing_trades]) if losing_trades else 0
        
        profit_factor = abs(avg_win * wins / (avg_loss * losses)) if losses > 0 and avg_loss != 0 else 0
        sharpe_ratio = self._calculate_sharpe([t['percent_return'] for t in trades])
        expectancy = total_profit / total_trades if total_trades > 0 else 0
        return_percent = ((capital - params['initial_capital']) / params['initial_capital']) * 100
        
        return {
            'direction': direction,
            'params': params,
            'trades': trades[-50:],  # Last 50 trades
            'all_trades_count': len(trades),
            'total_trades': total_trades,
            'trades_attempted': trades_attempted,
            'trades_filtered': trades_filtered,
            'filter_rate': round(trades_filtered / trades_attempted * 100, 1) if trades_attempted > 0 else 0,
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate, 2),
            'total_profit': round(total_profit, 2),
            'final_capital': round(capital, 2),
            'return_percent': round(return_percent, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'max_drawdown': round(max_drawdown, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'expectancy': round(expectancy, 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_sharpe(self, returns):
        """Calculate Sharpe ratio"""
        if not returns:
            return 0
        
        returns_array = np.array(returns)
        avg_return = np.mean(returns_array)
        std_dev = np.std(returns_array)
        
        if std_dev == 0:
            return 0
        
        # Annualized Sharpe (assuming 252 trading days)
        sharpe = (avg_return / std_dev) * np.sqrt(252)
        return sharpe
    
    def _calculate_comparison(self, advanced_puts, basic_puts, advanced_calls):
        """Calculate comparison metrics between strategies"""
        return {
            'win_rate_improvement': round(advanced_puts['win_rate'] - basic_puts['win_rate'], 2),
            'profit_factor_improvement': round(advanced_puts['profit_factor'] - basic_puts['profit_factor'], 2),
            'puts_vs_calls_win_rate': round(advanced_puts['win_rate'] - advanced_calls['win_rate'], 2),
            'best_strategy': max(
                [('Advanced Puts', advanced_puts['profit_factor']),
                 ('Basic Puts', basic_puts['profit_factor']),
                 ('Advanced Calls', advanced_calls['profit_factor'])],
                key=lambda x: x[1]
            )[0],
            'best_profit_factor': max(
                advanced_puts['profit_factor'],
                basic_puts['profit_factor'],
                advanced_calls['profit_factor']
            ),
            'filter_efficiency': {
                'advanced_puts_filter_rate': advanced_puts['filter_rate'],
                'trades_quality_improvement': round(
                    advanced_puts['expectancy'] - basic_puts['expectancy'], 2
                )
            }
        }


# Singleton instance
strategy_backtester = StrategyBacktester()
