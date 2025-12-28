import React, { useState, useEffect, useCallback } from 'react';
import { TrendingUp, TrendingDown, RefreshCw, AlertCircle } from 'lucide-react';
import { apiService } from '../services/api';
import { MonitorData } from '../types';

const SYMBOLS = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'TSLA', 'META', 'GOOGL', 'AMZN'];
const TIMEFRAMES = ['5min', '10min', '30min', '60min'];

const OptionsFlowMonitor: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('SPY');
  const [selectedTimeframe, setSelectedTimeframe] = useState('5min');
  const [monitorData, setMonitorData] = useState<MonitorData | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [currentTime, setCurrentTime] = useState(new Date());
  const [wsConnected, setWsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dataMode, setDataMode] = useState<'live' | 'historical'>('live');
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [replayTime, setReplayTime] = useState<string>('09:30');
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1000); // ms per minute

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const data = await apiService.getMonitorData(
        selectedSymbol, 
        selectedTimeframe,
        dataMode === 'historical' ? selectedDate || undefined : undefined,
        dataMode === 'historical' ? replayTime : undefined
      );
      setMonitorData(data);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Error fetching monitor data:', error);
      setError('Failed to fetch data. Retrying...');
    }
  }, [selectedSymbol, selectedTimeframe, dataMode, selectedDate, replayTime]);

  // Initial fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Live clock update every second
  useEffect(() => {
    const clockInterval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(clockInterval);
  }, []);

  // Auto-refresh with WebSocket
  useEffect(() => {
    if (dataMode === 'historical' || !autoRefresh) return;

    // Connect WebSocket
    apiService.connectWebSocket(
      () => setWsConnected(true),
      () => setWsConnected(false)
    );

    // Subscribe to symbol updates
    apiService.subscribeToSymbol(selectedSymbol, selectedTimeframe, (data) => {
      setMonitorData(data);
      setLastUpdate(new Date());
    });

    // Fallback polling every 2 seconds
    const interval = setInterval(fetchData, 2000);

    return () => {
      clearInterval(interval);
      apiService.unsubscribeFromSymbol(selectedSymbol);
      if (!autoRefresh) {
        apiService.disconnectWebSocket();
      }
    };
  }, [autoRefresh, selectedSymbol, selectedTimeframe, fetchData, dataMode]);

  // Historical replay playback
  useEffect(() => {
    if (dataMode !== 'historical' || !isPlaying) return;

    const playbackInterval = setInterval(() => {
      setReplayTime(prevTime => {
        const [hours, minutes] = prevTime.split(':').map(Number);
        let totalMinutes = hours * 60 + minutes + 1;
        
        // Stop at market close (16:00)
        if (totalMinutes >= 16 * 60) {
          setIsPlaying(false);
          return '16:00';
        }
        
        const newHours = Math.floor(totalMinutes / 60);
        const newMinutes = totalMinutes % 60;
        return `${String(newHours).padStart(2, '0')}:${String(newMinutes).padStart(2, '0')}`;
      });
      
      // Fetch new data to simulate progression
      fetchData();
    }, playbackSpeed);

    return () => clearInterval(playbackInterval);
  }, [dataMode, isPlaying, playbackSpeed, fetchData]);

  if (!monitorData) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const { calls, puts, sentiment, strikes, price, put_call_ratio } = monitorData;
  const maxVolume = Math.max(...strikes.map(s => Math.max(s.call_volume, s.put_volume)));

  const getColorClass = (ratio: number) => {
    if (ratio > 1.2) return 'text-green-400';
    if (ratio < 0.8) return 'text-red-400';
    return 'text-yellow-400';
  };

  return (
    <div className="w-full min-h-screen p-4" style={{ backgroundColor: '#000000' }}>
      <div className="max-w-[1600px] mx-auto">
        {/* Header Controls */}
        <div className="mb-4 space-y-3">
          {/* Data Mode Toggle */}
          <div className="flex gap-2 items-center flex-wrap">
            <span className="text-gray-400 text-sm">Data Mode:</span>
            <button
              onClick={() => {
                setDataMode('live');
                setSelectedDate(null);
                setIsPlaying(false);
              }}
              className={`px-4 py-1.5 text-sm font-bold transition-colors ${
                dataMode === 'live'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              🔴 Live Data
            </button>
            <button
              onClick={() => setDataMode('historical')}
              className={`px-4 py-1.5 text-sm font-bold transition-colors ${
                dataMode === 'historical'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              📅 Historical Replay
            </button>
            
            {dataMode === 'historical' && (
              <>
                <select
                  value={selectedDate || ''}
                  onChange={(e) => {
                    setSelectedDate(e.target.value);
                    setReplayTime('09:30');
                    setIsPlaying(false);
                  }}
                  className="px-3 py-1.5 bg-gray-800 text-white border border-gray-700 rounded text-sm"
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
                    <input
                      type="time"
                      value={replayTime}
                      onChange={(e) => setReplayTime(e.target.value)}
                      min="09:30"
                      max="16:00"
                      step="60"
                      className="px-3 py-1.5 bg-gray-800 text-white border border-gray-700 rounded text-sm"
                    />
                    
                    <button
                      onClick={() => setIsPlaying(!isPlaying)}
                      className={`px-4 py-1.5 text-sm font-bold transition-colors ${
                        isPlaying
                          ? 'bg-red-600 text-white hover:bg-red-700'
                          : 'bg-blue-600 text-white hover:bg-blue-700'
                      }`}
                    >
                      {isPlaying ? '⏸ Pause' : '▶ Play'}
                    </button>
                    
                    <select
                      value={playbackSpeed}
                      onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
                      className="px-3 py-1.5 bg-gray-800 text-white border border-gray-700 rounded text-sm"
                    >
                      <option value="500">2x Speed</option>
                      <option value="1000">1x Speed</option>
                      <option value="2000">0.5x Speed</option>
                    </select>
                  </>
                )}
              </>
            )}
          </div>
          
          {/* Symbol Buttons */}
          <div className="flex justify-between items-center">
            <div className="flex gap-2">
              {SYMBOLS.map(symbol => (
                <button
                  key={symbol}
                  onClick={() => setSelectedSymbol(symbol)}
                  className={`px-3 py-1.5 text-sm font-bold transition-colors ${
                    selectedSymbol === symbol
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  ${symbol}
                </button>
              ))}
            </div>
            
            {dataMode === 'live' && (
              <div className="flex gap-2 items-center">
                <div className="flex gap-1">
                  {TIMEFRAMES.map(tf => (
                    <button
                      key={tf}
                      onClick={() => setSelectedTimeframe(tf)}
                      className={`px-3 py-1.5 text-xs transition-colors ${
                        selectedTimeframe === tf
                          ? 'bg-green-700 text-white font-bold'
                          : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                      }`}
                    >
                      {tf}
                    </button>
                  ))}
                </div>
              </div>
            )}
            {dataMode === 'live' && wsConnected && (
              <span className="flex items-center gap-1 text-green-400 text-xs">
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                LIVE
              </span>
            )}
          </div>
        </div>

        {/* Main Options Flow Chart */}
        <div className="p-6" style={{ backgroundColor: '#000000', border: '2px solid #1f2937' }}>
          {/* Title Bar */}
          <div className="flex justify-between items-start mb-6">
            <div>
              <div className="text-blue-400 text-sm mb-1">
                {dataMode === 'live' ? (
                  <>🔴 LIVE: {selectedSymbol} last {selectedTimeframe} - refresh every 2s</>
                ) : (
                  <>📅 HISTORICAL REPLAY: {selectedDate || 'Select a date'} at {replayTime} - {selectedSymbol} {isPlaying && '(Playing...)'}</>
                )}
              </div>
              <h1 className="text-white text-2xl font-bold">
                ${selectedSymbol} Option Volume ({dataMode === 'historical' && selectedDate ? selectedDate : currentTime.toLocaleDateString('en-US', { 
                  month: '2-digit', 
                  day: '2-digit', 
                  year: 'numeric' 
                })} EXP) {dataMode === 'historical' ? replayTime : currentTime.toLocaleTimeString('en-US', { 
                  hour: '2-digit', 
                  minute: '2-digit', 
                  second: '2-digit',
                  hour12: false 
                })}
              </h1>
            </div>
          </div>

          {/* Buy/Sell Ratio Headers */}
          <div className="flex justify-between mb-4 text-sm">
            <div className="w-1/2 flex justify-between items-center px-4">
              <div>
                <span className="text-blue-400 font-bold">Calls</span>
                <div className="text-white text-2xl font-bold mt-1">{calls.total.toLocaleString()}</div>
              </div>
              <div className="text-right">
                <div className="flex gap-4 text-xs">
                  <span className="text-gray-400">Buy</span>
                  <span className="text-gray-400">Sell</span>
                </div>
                <div className="bg-gray-900 border border-green-700 px-3 py-1 mt-1">
                  <span className="text-green-400 font-bold">Ratio: {calls.ratio.toFixed(4)}</span>
                </div>
              </div>
            </div>
            
            <div className="w-1/2 flex justify-between items-center px-4">
              <div>
                <div className="flex gap-4 text-xs">
                  <span className="text-gray-400">Buy</span>
                  <span className="text-gray-400">Sell</span>
                </div>
                <div className="bg-gray-900 border border-red-700 px-3 py-1 mt-1">
                  <span className="text-red-400 font-bold">Ratio: {puts.ratio.toFixed(4)}</span>
                </div>
              </div>
              <div className="text-right">
                <span className="text-red-400 font-bold">Puts</span>
                <div className="text-white text-2xl font-bold mt-1">{puts.total.toLocaleString()}</div>
              </div>
            </div>
          </div>

          {/* Options Chain Bars */}
          <div className="relative">
            {strikes.map((strike, idx) => {
              const isATM = Math.abs(strike.strike - price) < 2.5;
              const callWidthPercent = (strike.call_volume / maxVolume) * 45;
              const putWidthPercent = (strike.put_volume / maxVolume) * 45;

              return (
                <div key={idx} className="relative h-5 mb-0.5">
                  {/* Call volume number (left) */}
                  <div className="absolute left-0 top-0 h-full flex items-center text-xs text-gray-400 pr-2" style={{ width: '8%' }}>
                    <span className="ml-auto">{strike.call_volume.toLocaleString()}</span>
                  </div>
                  
                  {/* Call bar (left side) */}
                  <div className="absolute left-[8%] top-0 h-full flex items-center justify-end" style={{ width: '42%' }}>
                    <div
                      className="h-4 bg-red-600 transition-all"
                      style={{ width: `${callWidthPercent}%` }}
                    />
                  </div>

                  {/* Strike price (center) */}
                  <div 
                    className="absolute top-0 h-full flex items-center justify-center text-sm font-bold z-10"
                    style={{ left: '50%', transform: 'translateX(-50%)', width: '80px' }}
                  >
                    <span className={isATM ? 'text-yellow-400' : 'text-gray-300'}>
                      {strike.strike.toFixed(1)}
                    </span>
                    {isATM && (
                      <div className="absolute inset-0 border-t border-b border-yellow-500 opacity-30" />
                    )}
                  </div>

                  {/* Stock price line */}
                  {isATM && (
                    <div className="absolute left-0 right-0 top-0 h-full border-t-2 border-white opacity-50" 
                         style={{ zIndex: 5 }}>
                      <span className="text-white text-xs absolute left-1/2 -top-5 transform -translate-x-1/2">
                        ${selectedSymbol} stock price: ${price.toFixed(2)}
                      </span>
                    </div>
                  )}

                  {/* Put bar (right side) */}
                  <div className="absolute right-[8%] top-0 h-full flex items-center justify-start" style={{ width: '42%' }}>
                    <div
                      className="h-4 bg-green-600 transition-all"
                      style={{ width: `${putWidthPercent}%` }}
                    />
                  </div>

                  {/* Put volume number (right) */}
                  <div className="absolute right-0 top-0 h-full flex items-center text-xs text-gray-400 pl-2" style={{ width: '8%' }}>
                    <span>{strike.put_volume.toLocaleString()}</span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* X-axis labels */}
          <div className="flex justify-between mt-4 text-xs text-gray-500">
            <div className="w-[50%] flex justify-around">
              <span>8000</span>
              <span>6000</span>
              <span>4000</span>
              <span>2000</span>
              <span>0</span>
            </div>
            <div className="w-[50%] flex justify-around">
              <span>0</span>
              <span>2000</span>
              <span>4000</span>
              <span>6000</span>
              <span>8000</span>
            </div>
          </div>

          <div className="flex justify-between mt-1 text-xs">
            <span className="text-gray-400 w-1/2 text-center">Call Volume</span>
            <span className="text-gray-400 w-1/2 text-center">Put Volume</span>
          </div>

          {/* Timespan indicator */}
          <div className="mt-4 text-right">
            <span className="bg-yellow-600 text-black px-3 py-1 text-xs font-bold">
              Timespan: {selectedTimeframe}
            </span>
          </div>
        </div>

        {/* Footer notice */}
        {error && (
          <div className="mt-2 bg-red-900 border border-red-700 px-4 py-2 text-sm text-red-100">
            {error}
          </div>
        )}
      </div>
    </div>
  );
};

export default OptionsFlowMonitor;
