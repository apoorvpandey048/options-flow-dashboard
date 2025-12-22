/**
 * TypeScript type definitions for the Options Flow Monitor application
 */

export interface Strike {
  strike: number;
  call_volume: number;
  put_volume: number;
  call_oi?: number;
  put_oi?: number;
  call_iv?: number;
  put_iv?: number;
}

export interface OptionsSummary {
  buy: number;
  sell: number;
  total: number;
  ratio: number;
}

export interface Sentiment {
  direction: 'Bullish' | 'Bearish' | 'Neutral';
  strength: 'Strong' | 'Moderate' | 'Weak';
  score: number;
}

export interface MonitorData {
  symbol: string;
  timeframe: string;
  timestamp: string;
  price: number;
  calls: OptionsSummary;
  puts: OptionsSummary;
  put_call_ratio: number;
  sentiment: Sentiment;
  strikes: Strike[];
}

export interface SymbolSummary {
  symbol: string;
  price: number;
  put_call_ratio: number;
  sentiment: Sentiment;
  call_ratio: number;
  put_ratio: number;
}

export interface BacktestParams {
  put_call_threshold: number;
  num_trades: number;
  initial_capital: number;
  position_size: number;
  profit_target: number;
  stop_loss: number;
  volume_spike_threshold: number;
  iv_threshold: number;
  use_volume_spike: boolean;
  use_iv_filter: boolean;
  use_multi_timeframe: boolean;
}

export interface Trade {
  trade_num: number;
  direction: string;
  put_call_ratio: number;
  volume_spike: number;
  iv_percentile: number;
  timeframe_align: string;
  volume_conc: number;
  result: 'Win' | 'Loss';
  percent_return: number;
  profit: number;
  capital: number;
  drawdown: number;
  win_prob?: number;
}

export interface BacktestResult {
  direction: string;
  params: BacktestParams;
  trades: Trade[];
  all_trades_count: number;
  total_trades: number;
  trades_attempted: number;
  trades_filtered: number;
  filter_rate: number;
  wins: number;
  losses: number;
  win_rate: number;
  total_profit: number;
  final_capital: number;
  return_percent: number;
  avg_win: number;
  avg_loss: number;
  profit_factor: number;
  max_drawdown: number;
  sharpe_ratio: number;
  max_consecutive_wins: number;
  max_consecutive_losses: number;
  expectancy: number;
  timestamp: string;
}

export interface ComparisonResult {
  advanced_puts: BacktestResult;
  basic_puts: BacktestResult;
  advanced_calls: BacktestResult;
  comparison: {
    win_rate_improvement: number;
    profit_factor_improvement: number;
    puts_vs_calls_win_rate: number;
    best_strategy: string;
    best_profit_factor: number;
    filter_efficiency: {
      advanced_puts_filter_rate: number;
      trades_quality_improvement: number;
    };
  };
}
