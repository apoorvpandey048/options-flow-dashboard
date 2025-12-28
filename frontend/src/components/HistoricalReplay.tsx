import React, { useState, useEffect } from 'react';
import { Calendar, TrendingUp, BarChart3, Clock } from 'lucide-react';

interface DateSummary {
  date: string;
  spy_close: number;
  spy_volume: number;
  unusual_activity_count: number;
  top_contract: string;
  total_contracts: number;
}

interface UnusualActivity {
  ticker: string;
  strike: number;
  type: string;
  expiry: string;
  volume: number;
  avg_volume_20d: number;
  volume_ratio: number;
  rating: string;
  price: number;
  underlying: string;
}

interface Analysis {
  date: string;
  market_summary: {
    spy_open: number;
    spy_high: number;
    spy_low: number;
    spy_close: number;
    spy_volume: number;
    spy_change_pct: number;
  };
  options_summary: {
    total_unusual: number;
    extreme_flows: number;
    high_flows: number;
    elevated_flows: number;
  };
  unusual_activity: UnusualActivity[];
}

interface ChartData {
  ticker: string;
  date: string;
  times: string[];
  volumes: number[];
  prices: number[];
}

const HistoricalReplay: React.FC = () => {
  const [dates, setDates] = useState<DateSummary[]>([]);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAvailableDates();
  }, []);

  const loadAvailableDates = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/historical/dates', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setDates(data.dates || []);
    } catch (error) {
      console.error('Error loading dates:', error);
    }
  };

  const loadAnalysis = async (date: string) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/historical/analysis/${date}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setAnalysis(data);
      setSelectedDate(date);
      setSelectedTicker(null);
      setChartData(null);
      
      // Auto-load chart for first unusual activity
      if (data.unusual_activity && data.unusual_activity.length > 0) {
        loadChartData(date, data.unusual_activity[0].ticker);
      }
    } catch (error) {
      console.error('Error loading analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadChartData = async (date: string, ticker: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/historical/chart/${date}/${ticker}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setChartData(data);
      setSelectedTicker(ticker);
    } catch (error) {
      console.error('Error loading chart:', error);
    }
  };

  const getRatingColor = (rating: string) => {
    switch (rating) {
      case 'EXTREME': return 'text-red-500';
      case 'HIGH': return 'text-orange-500';
      case 'ELEVATED': return 'text-yellow-500';
      default: return 'text-gray-400';
    }
  };

  const getRatingEmoji = (rating: string) => {
    switch (rating) {
      case 'EXTREME': return '🔥';
      case 'HIGH': return '🚀';
      case 'ELEVATED': return '📈';
      default: return '➡️';
    }
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: '#000000' }}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Calendar className="w-8 h-8 text-blue-500" />
            Historical Replay
          </h1>
          <p className="text-gray-400 mt-2">
            Review past unusual options flow activity with detailed intraday charts
          </p>
        </div>

        {/* Date Browser */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {dates.map((date) => (
            <div
              key={date.date}
              onClick={() => loadAnalysis(date.date)}
              className={`p-4 rounded-lg border cursor-pointer transition-all ${
                selectedDate === date.date
                  ? 'border-blue-500 bg-blue-500/10'
                  : 'border-gray-700 bg-gray-900 hover:border-gray-600'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-white font-semibold">{date.date}</span>
                {date.unusual_activity_count > 0 && (
                  <span className="px-2 py-1 bg-red-500/20 text-red-400 text-xs rounded">
                    {date.unusual_activity_count} unusual
                  </span>
                )}
              </div>
              <div className="text-sm text-gray-400">
                SPY ${date.spy_close.toFixed(2)}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Vol: {formatNumber(date.spy_volume)}
              </div>
            </div>
          ))}
        </div>

        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            <p className="text-gray-400 mt-4">Loading analysis...</p>
          </div>
        )}

        {analysis && !loading && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Market Summary & Unusual Activity */}
            <div className="lg:col-span-1 space-y-6">
              {/* Market Summary */}
              <div className="bg-gray-900 rounded-lg border border-gray-800 p-6">
                <h2 className="text-xl font-bold text-white mb-4">Market Summary</h2>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-400">SPY Open</span>
                    <span className="text-white">${analysis.market_summary.spy_open.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">SPY High</span>
                    <span className="text-green-400">${analysis.market_summary.spy_high.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">SPY Low</span>
                    <span className="text-red-400">${analysis.market_summary.spy_low.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">SPY Close</span>
                    <span className="text-white font-semibold">${analysis.market_summary.spy_close.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Change</span>
                    <span className={analysis.market_summary.spy_change_pct >= 0 ? 'text-green-400' : 'text-red-400'}>
                      {analysis.market_summary.spy_change_pct >= 0 ? '+' : ''}{analysis.market_summary.spy_change_pct.toFixed(2)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Volume</span>
                    <span className="text-white">{formatNumber(analysis.market_summary.spy_volume)}</span>
                  </div>
                </div>
              </div>

              {/* Unusual Activity List */}
              <div className="bg-gray-900 rounded-lg border border-gray-800 p-6">
                <h2 className="text-xl font-bold text-white mb-4">Unusual Activity</h2>
                <div className="space-y-3">
                  {analysis.unusual_activity.map((activity, index) => (
                    <div
                      key={index}
                      onClick={() => loadChartData(selectedDate!, activity.ticker)}
                      className={`p-4 rounded-lg border cursor-pointer transition-all ${
                        selectedTicker === activity.ticker
                          ? 'border-blue-500 bg-blue-500/10'
                          : 'border-gray-700 hover:border-gray-600'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-white font-semibold">{activity.underlying}</span>
                        <span className={`text-2xl ${getRatingColor(activity.rating)}`}>
                          {getRatingEmoji(activity.rating)}
                        </span>
                      </div>
                      <div className="text-sm text-gray-400">
                        ${activity.strike} {activity.type}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        Vol: {formatNumber(activity.volume)} ({activity.volume_ratio.toFixed(1)}x avg)
                      </div>
                      <div className="text-xs text-gray-500">
                        Exp: {activity.expiry}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Column - Chart */}
            <div className="lg:col-span-2">
              {chartData && (
                <div className="bg-gray-900 rounded-lg border border-gray-800 p-6">
                  <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                    <BarChart3 className="w-6 h-6 text-blue-500" />
                    Intraday Volume - {chartData.ticker}
                  </h2>
                  
                  {/* Simple Bar Chart */}
                  <div className="relative h-80 border-l-2 border-b-2 border-gray-700 mt-8">
                    <div className="absolute inset-0 flex items-end justify-around px-4 pb-2">
                      {chartData.volumes.map((volume, index) => {
                        const maxVolume = Math.max(...chartData.volumes);
                        const height = (volume / maxVolume) * 100;
                        const isSpike = volume >= maxVolume * 0.7;
                        
                        return (
                          <div key={index} className="flex flex-col items-center flex-1 mx-1">
                            <div
                              className={`w-full rounded-t ${isSpike ? 'bg-red-500' : 'bg-blue-500'} transition-all hover:opacity-80`}
                              style={{ height: `${height}%` }}
                              title={`${chartData.times[index]}: ${volume} contracts`}
                            />
                            <span className="text-xs text-gray-400 mt-2 transform -rotate-45 origin-top-left">
                              {chartData.times[index]}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                    
                    {/* Y-axis labels */}
                    <div className="absolute -left-12 top-0 bottom-8 flex flex-col justify-between text-xs text-gray-400">
                      <span>{Math.max(...chartData.volumes)}</span>
                      <span>{Math.floor(Math.max(...chartData.volumes) / 2)}</span>
                      <span>0</span>
                    </div>
                  </div>

                  {/* Legend */}
                  <div className="mt-6 flex items-center gap-6 text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-blue-500 rounded"></div>
                      <span className="text-gray-400">Normal Volume</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-red-500 rounded"></div>
                      <span className="text-gray-400">Volume Spike</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {!selectedDate && !loading && (
          <div className="text-center py-12">
            <Clock className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-400 mb-2">Select a Date</h3>
            <p className="text-gray-500">Choose a trading day above to view historical options flow activity</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default HistoricalReplay;
