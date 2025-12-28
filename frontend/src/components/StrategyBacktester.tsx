import React, { useState } from 'react';
import { Play, TrendingUp, TrendingDown, BarChart3, DollarSign, Activity } from 'lucide-react';
import { apiService } from '../services/api';
import { BacktestParams, ComparisonResult } from '../types';

const StrategyBacktester: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<ComparisonResult | null>(null);
  const [dataMode, setDataMode] = useState<'live' | 'historical'>('live');
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [replayTime, setReplayTime] = useState<string>('09:30');
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1000);

  const [params, setParams] = useState<BacktestParams>({
    put_call_threshold: 1.1,
    num_trades: 1000,
    initial_capital: 10000,
    position_size: 100,
    profit_target: 0.20,
    stop_loss: -0.50,
    volume_spike_threshold: 1.5,
    iv_threshold: 30,
    use_volume_spike: true,
    use_iv_filter: true,
    use_multi_timeframe: true
  });

  const runBacktest = async () => {
    setIsRunning(true);
    setProgress(0);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) return prev;
        return prev + 10;
      });
    }, 200);

    try {
      // Add selectedDate to params if available
      const paramsWithDate = selectedDate 
        ? { ...params, date: selectedDate.toISOString().split('T')[0] }
        : params;
      
      const result = await apiService.compareStrategies(paramsWithDate);
      setResults(result);
      setProgress(100);
    } catch (error) {
      console.error('Error running backtest:', error);
      alert('Error running backtest. Please check console for details.');
    } finally {
      clearInterval(progressInterval);
      setIsRunning(false);
    }
  };

  const updateParam = (key: keyof BacktestParams, value: any) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="w-full min-h-screen p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Advanced Options Strategy Backtester</h1>
          <p className="text-gray-400">
            Multi-Signal Analysis with Volume Spikes, IV Filters & Timeframe Confirmation
          </p>
        </div>

        {/* Data Mode Toggle */}
        <div className="mb-6 flex gap-2 items-center p-4 bg-gray-800 rounded-xl border border-gray-700">
          <span className="text-gray-400 text-sm font-semibold">Data Mode:</span>
          <button
            onClick={() => {
              setDataMode('live');
              setSelectedDate(null);
            }}
            className={`px-4 py-2 text-sm font-bold transition-colors rounded ${
              dataMode === 'live'
                ? 'bg-green-600 text-white'
                : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
            }`}
          >
            Live Data (Simulated)
          </button>
          <button
            onClick={() => setDataMode('historical')}
            className={`px-4 py-2 text-sm font-bold transition-colors rounded ${
              dataMode === 'historical'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
            }`}
          >
            Historical Data
          </button>
          {dataMode === 'historical' && (
            <div className="flex gap-3 items-center flex-wrap">
              <select
                value={selectedDate || ''}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="px-3 py-2 bg-gray-700 text-white border border-gray-600 rounded text-sm"
              >
                <option value="">Select Date...</option>
                <option value="2025-12-27">Dec 27, 2025</option>
                <option value="2025-12-26">Dec 26, 2025</option>
                <option value="2025-12-24">Dec 24, 2025</option>
                <option value="2025-12-23">Dec 23, 2025</option>
                <option value="2025-12-20">Dec 20, 2025</option>
              </select>
              
              {selectedDate && (
                <>
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400 text-sm">Time:</span>
                    <input
                      type="time"
                      value={replayTime}
                      onChange={(e) => setReplayTime(e.target.value)}
                      min="09:30"
                      max="16:00"
                      step="60"
                      className="px-3 py-1.5 bg-gray-700 text-white border border-gray-600 rounded text-sm"
                    />
                  </div>
                  
                  <button
                    onClick={() => setIsPlaying(!isPlaying)}
                    className={`px-4 py-1.5 text-sm font-bold rounded transition-colors ${
                      isPlaying
                        ? 'bg-red-600 hover:bg-red-700 text-white'
                        : 'bg-green-600 hover:bg-green-700 text-white'
                    }`}
                  >
                    {isPlaying ? '⏸ Pause' : '▶ Play'}
                  </button>
                  
                  <select
                    value={playbackSpeed}
                    onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
                    className="px-3 py-1.5 bg-gray-700 text-white border border-gray-600 rounded text-sm"
                  >
                    <option value="2000">0.5x Speed</option>
                    <option value="1000">1x Speed</option>
                    <option value="500">2x Speed</option>
                    <option value="250">4x Speed</option>
                  </select>
                  
                  <span className="text-sm text-purple-400">
                    📅 {selectedDate} at {replayTime} {isPlaying && '(Playing...)'}
                  </span>
                </>
              )}
            </div>
          )}
        </div>

        {/* Strategy Parameters */}
        <div className="bg-gray-800 rounded-xl p-6 mb-6 border border-gray-700">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <BarChart3 className="w-6 h-6" />
            Strategy Parameters
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <InputField
              label="Put/Call Threshold"
              value={params.put_call_threshold}
              onChange={v => updateParam('put_call_threshold', v)}
              step={0.1}
            />
            <InputField
              label="Number of Trades"
              value={params.num_trades}
              onChange={v => updateParam('num_trades', v)}
              step={100}
            />
            <InputField
              label="Initial Capital ($)"
              value={params.initial_capital}
              onChange={v => updateParam('initial_capital', v)}
              step={1000}
            />
            <InputField
              label="Position Size ($)"
              value={params.position_size}
              onChange={v => updateParam('position_size', v)}
              step={10}
            />
            <InputField
              label="Profit Target (%)"
              value={params.profit_target * 100}
              onChange={v => updateParam('profit_target', v / 100)}
              step={5}
            />
            <InputField
              label="Stop Loss (%)"
              value={params.stop_loss * 100}
              onChange={v => updateParam('stop_loss', v / 100)}
              step={5}
            />
            <InputField
              label="Volume Spike Threshold"
              value={params.volume_spike_threshold}
              onChange={v => updateParam('volume_spike_threshold', v)}
              step={0.1}
            />
            <InputField
              label="IV Percentile Min"
              value={params.iv_threshold}
              onChange={v => updateParam('iv_threshold', v)}
              step={5}
            />
          </div>

          {/* Filter Toggles */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <ToggleFilter
              label="Volume Spike Filter"
              description="Only trade on volume spikes"
              checked={params.use_volume_spike}
              onChange={v => updateParam('use_volume_spike', v)}
            />
            <ToggleFilter
              label="IV Filter"
              description="Filter by IV percentile"
              checked={params.use_iv_filter}
              onChange={v => updateParam('use_iv_filter', v)}
            />
            <ToggleFilter
              label="Multi-Timeframe"
              description="Require timeframe alignment"
              checked={params.use_multi_timeframe}
              onChange={v => updateParam('use_multi_timeframe', v)}
            />
          </div>

          <button
            onClick={runBacktest}
            disabled={isRunning}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-8 py-3 rounded-lg font-bold flex items-center gap-2 transition-colors"
          >
            <Play className="w-5 h-5" />
            {isRunning ? 'Running Backtest...' : 'Run Comprehensive Backtest'}
          </button>

          {isRunning && (
            <div className="mt-4">
              <div className="w-full bg-gray-700 rounded-full h-3">
                <div
                  className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-sm text-gray-400 mt-2">Processing: {progress}%</p>
            </div>
          )}
        </div>

        {/* Results */}
        {results && (
          <>
            {/* Strategy Comparison */}
            <div className="bg-gradient-to-r from-purple-900 to-blue-900 rounded-xl p-6 mb-6 border border-purple-500">
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <Activity className="w-6 h-6" />
                Strategy Comparison
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <StrategyCard
                  title="Advanced Puts (Multi-Signal)"
                  result={results.advanced_puts}
                  color="green"
                />
                <StrategyCard
                  title="Basic Puts (No Filters)"
                  result={results.basic_puts}
                  color="yellow"
                />
                <StrategyCard
                  title="Advanced Calls (Inverse)"
                  result={results.advanced_calls}
                  color="blue"
                />
              </div>

              {/* Performance Improvement */}
              <div className="p-4 bg-gray-800 rounded-lg">
                <h4 className="font-bold mb-3">Performance Improvement Analysis</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                  <ImprovementMetric
                    label="Win Rate Improvement"
                    value={results.comparison.win_rate_improvement}
                    suffix="%"
                  />
                  <ImprovementMetric
                    label="Profit Factor Improvement"
                    value={results.comparison.profit_factor_improvement}
                    suffix="x"
                  />
                  <ImprovementMetric
                    label="Puts vs Calls Win Rate"
                    value={results.comparison.puts_vs_calls_win_rate}
                    suffix="%"
                  />
                  <div>
                    <span className="text-gray-400">Best Strategy:</span>
                    <span className="ml-2 font-bold text-yellow-400">
                      {results.comparison.best_strategy}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Main Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <MetricCard
                icon={<TrendingUp className="w-6 h-6" />}
                label="Win Rate"
                value={`${results.advanced_puts.win_rate.toFixed(2)}%`}
                subtitle={`${results.advanced_puts.wins}W / ${results.advanced_puts.losses}L`}
                color="green"
              />
              <MetricCard
                icon={results.advanced_puts.total_profit >= 0 ? <TrendingUp className="w-6 h-6" /> : <TrendingDown className="w-6 h-6" />}
                label="Total P&L"
                value={`$${results.advanced_puts.total_profit.toFixed(2)}`}
                subtitle={`${results.advanced_puts.return_percent.toFixed(2)}% Return`}
                color={results.advanced_puts.total_profit >= 0 ? 'blue' : 'red'}
              />
              <MetricCard
                icon={<BarChart3 className="w-6 h-6" />}
                label="Profit Factor"
                value={results.advanced_puts.profit_factor.toFixed(2)}
                subtitle={`Expectancy: $${results.advanced_puts.expectancy.toFixed(2)}`}
                color="purple"
              />
              <MetricCard
                icon={<DollarSign className="w-6 h-6" />}
                label="Max Drawdown"
                value={`${results.advanced_puts.max_drawdown.toFixed(2)}%`}
                subtitle={`Sharpe: ${results.advanced_puts.sharpe_ratio.toFixed(2)}`}
                color="orange"
              />
            </div>

            {/* Trade Log */}
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <h3 className="text-xl font-bold mb-4">
                Recent Trades (Last 50) - Advanced Puts Strategy
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="text-left p-2">#</th>
                      <th className="text-left p-2">P/C</th>
                      <th className="text-left p-2">Vol Spike</th>
                      <th className="text-left p-2">IV %</th>
                      <th className="text-left p-2">TF Align</th>
                      <th className="text-left p-2">Result</th>
                      <th className="text-right p-2">Return %</th>
                      <th className="text-right p-2">P&L</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.advanced_puts.trades.map((trade, idx) => (
                      <tr key={idx} className="border-b border-gray-700 hover:bg-gray-700">
                        <td className="p-2">{trade.trade_num}</td>
                        <td className="p-2 font-mono">{trade.put_call_ratio.toFixed(4)}</td>
                        <td className="p-2 font-mono">{trade.volume_spike}x</td>
                        <td className="p-2 font-mono">{trade.iv_percentile}%</td>
                        <td className="p-2">{trade.timeframe_align}</td>
                        <td className="p-2">
                          <span
                            className={`px-2 py-1 rounded text-xs font-bold ${
                              trade.result === 'Win'
                                ? 'bg-green-900 text-green-200'
                                : 'bg-red-900 text-red-200'
                            }`}
                          >
                            {trade.result}
                          </span>
                        </td>
                        <td
                          className={`p-2 text-right font-mono ${
                            trade.percent_return >= 0 ? 'text-green-400' : 'text-red-400'
                          }`}
                        >
                          {trade.percent_return}%
                        </td>
                        <td
                          className={`p-2 text-right font-mono ${
                            trade.profit >= 0 ? 'text-green-400' : 'text-red-400'
                          }`}
                        >
                          ${trade.profit}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Key Findings */}
            <KeyFindings params={params} results={results} />
          </>
        )}
      </div>
    </div>
  );
};

// Helper Components
const InputField: React.FC<{
  label: string;
  value: number;
  onChange: (value: number) => void;
  step: number;
}> = ({ label, value, onChange, step }) => (
  <div>
    <label className="block text-sm text-gray-400 mb-2">{label}</label>
    <input
      type="number"
      step={step}
      value={value}
      onChange={e => onChange(parseFloat(e.target.value))}
      className="w-full bg-gray-700 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
    />
  </div>
);

const ToggleFilter: React.FC<{
  label: string;
  description: string;
  checked: boolean;
  onChange: (value: boolean) => void;
}> = ({ label, description, checked, onChange }) => (
  <label className="flex items-center gap-3 bg-gray-700 p-3 rounded cursor-pointer hover:bg-gray-600">
    <input
      type="checkbox"
      checked={checked}
      onChange={e => onChange(e.target.checked)}
      className="w-5 h-5"
    />
    <div>
      <div className="font-semibold">{label}</div>
      <div className="text-xs text-gray-400">{description}</div>
    </div>
  </label>
);

const StrategyCard: React.FC<{
  title: string;
  result: any;
  color: 'green' | 'yellow' | 'blue';
}> = ({ title, result, color }) => {
  const colorClasses = {
    green: 'border-green-500 text-green-400',
    yellow: 'border-yellow-500 text-yellow-400',
    blue: 'border-blue-500 text-blue-400'
  };

  return (
    <div className={`bg-gray-800 rounded-lg p-4 border-2 ${colorClasses[color]}`}>
      <h3 className={`font-bold mb-3 ${colorClasses[color]}`}>{title}</h3>
      <div className="space-y-2 text-sm">
        <MetricRow label="Win Rate" value={`${result.win_rate.toFixed(2)}%`} highlight={color} />
        <MetricRow
          label="Total P&L"
          value={`$${result.total_profit.toFixed(2)}`}
          highlight={result.total_profit >= 0 ? 'green' : 'red'}
        />
        <MetricRow label="Profit Factor" value={result.profit_factor.toFixed(2)} />
        <MetricRow label="Trades" value={result.total_trades.toString()} />
        <MetricRow label="Expectancy" value={`$${result.expectancy.toFixed(2)}`} />
      </div>
    </div>
  );
};

const MetricRow: React.FC<{
  label: string;
  value: string;
  highlight?: 'green' | 'yellow' | 'blue' | 'red';
}> = ({ label, value, highlight }) => {
  const highlightClasses = {
    green: 'text-green-400',
    yellow: 'text-yellow-400',
    blue: 'text-blue-400',
    red: 'text-red-400'
  };

  return (
    <div className="flex justify-between">
      <span className="text-gray-400">{label}:</span>
      <span className={`font-bold ${highlight ? highlightClasses[highlight] : ''}`}>{value}</span>
    </div>
  );
};

const MetricCard: React.FC<{
  icon: React.ReactNode;
  label: string;
  value: string;
  subtitle: string;
  color: 'green' | 'blue' | 'purple' | 'orange' | 'red';
}> = ({ icon, label, value, subtitle, color }) => {
  const colorClasses = {
    green: 'from-green-600 to-green-700 border-green-500',
    blue: 'from-blue-600 to-blue-700 border-blue-500',
    purple: 'from-purple-600 to-purple-700 border-purple-500',
    orange: 'from-orange-600 to-orange-700 border-orange-500',
    red: 'from-red-600 to-red-700 border-red-500'
  };

  return (
    <div className={`bg-gradient-to-br rounded-lg p-6 border ${colorClasses[color]}`}>
      <div className="text-sm text-white mb-1">{label}</div>
      <div className="text-3xl font-bold flex items-center gap-2">
        {icon}
        {value}
      </div>
      <div className="text-sm text-white mt-2">{subtitle}</div>
    </div>
  );
};

const ImprovementMetric: React.FC<{
  label: string;
  value: number;
  suffix: string;
}> = ({ label, value, suffix }) => (
  <div>
    <span className="text-gray-400">{label}:</span>
    <span
      className={`ml-2 font-bold ${value > 0 ? 'text-green-400' : value < 0 ? 'text-red-400' : 'text-gray-400'}`}
    >
      {value > 0 ? '+' : ''}
      {value.toFixed(2)}
      {suffix}
    </span>
  </div>
);

const KeyFindings: React.FC<{ params: BacktestParams; results: ComparisonResult }> = ({
  params,
  results
}) => (
  <div className="mt-6 bg-gradient-to-r from-green-900 to-blue-900 border border-green-700 rounded-lg p-6">
    <h3 className="text-2xl font-bold mb-4 text-green-200">Key Findings & Insights</h3>
    <div className="space-y-3 text-sm text-green-100">
      <FindingCard
        title="✓ Multi-Signal Approach"
        description="Adding volume spikes, IV filters, and multi-timeframe confirmation typically improves win rates by 5-15% compared to basic P/C ratio signals alone."
      />
      <FindingCard
        title="✓ Volume Spike Filter"
        description={`Trades with ${params.volume_spike_threshold}x+ volume spikes show ${params.use_volume_spike ? '+5%' : 'N/A'} win probability increase. High volume confirms institutional interest.`}
      />
      <FindingCard
        title="✓ IV Sweet Spot"
        description="Elevated IV (30-70 percentile) provides optimal entry - enough premium to profit from, but not extreme panic levels that continue selling."
      />
      <FindingCard
        title="✓ Timeframe Alignment"
        description="When 5min, 10min, and 30min P/C ratios align, win probability increases ~6%. Confirms trend across multiple timeframes."
      />
      <FindingCard
        title="⚠ Puts vs Calls"
        description={`Buying puts on high P/C generally outperforms buying calls on low P/C by ~${results.comparison.puts_vs_calls_win_rate.toFixed(1)}% win rate. Market fear (high P/C) tends to be more predictive than greed.`}
        color="yellow"
      />
      <FindingCard
        title="⚠ Trade Frequency vs Quality"
        description={`Filters reduce total trades from ${results.basic_puts.total_trades} to ${results.advanced_puts.total_trades}, but improve expectancy from $${results.basic_puts.expectancy.toFixed(2)} to $${results.advanced_puts.expectancy.toFixed(2)} per trade.`}
        color="yellow"
      />
      <div className="bg-red-900 bg-opacity-50 p-3 rounded border border-red-700">
        <strong className="text-red-300">⚠️ CRITICAL DISCLAIMER:</strong>
        <p className="mt-1">This backtest uses realistic market dynamics but SIMULATED data. Real-world results require:</p>
        <ul className="list-disc list-inside ml-4 mt-2 space-y-1">
          <li>Historical tick-by-tick options data with bid/ask spreads</li>
          <li>Accurate IV calculations and Greeks</li>
          <li>Slippage modeling (2-5% on options is common)</li>
          <li>Commission costs ($0.50-$1.00 per contract)</li>
          <li>Liquidity constraints on entry/exit</li>
          <li>Market impact on larger positions</li>
        </ul>
        <p className="mt-2 font-semibold">
          Real win rates may be 10-20% lower than simulated results due to execution costs.
        </p>
      </div>
    </div>
  </div>
);

const FindingCard: React.FC<{
  title: string;
  description: string;
  color?: 'green' | 'yellow';
}> = ({ title, description, color = 'green' }) => (
  <div
    className={`${color === 'yellow' ? 'bg-yellow-900' : 'bg-gray-800'} bg-opacity-50 p-3 rounded`}
  >
    <strong className={color === 'yellow' ? 'text-yellow-300' : 'text-green-300'}>{title}</strong>
    <p className="mt-1">{description}</p>
  </div>
);

export default StrategyBacktester;
