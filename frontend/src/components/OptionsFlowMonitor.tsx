import React, { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';
import { MonitorData } from '../types';
import MirroredStrikeLadder from './MirroredStrikeLadder';

const SYMBOLS = ['SPY', 'QQQ', 'AAPL', 'TSLA'];  // Core 4 symbols using Insight Sentry
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

        {/* Main Options Flow Chart - New Mirrored Strike Ladder */}
        <div className="flex justify-center" style={{ backgroundColor: '#000000' }}>
          <MirroredStrikeLadder
            symbol={selectedSymbol}
            strikes={strikes}
            currentPrice={price}
            callsTotal={calls.total}
            putsTotal={puts.total}
            callRatio={calls.ratio}
            putRatio={puts.ratio}
            callsBuy={calls.buy}
            callsSell={calls.sell}
            putsBuy={puts.buy}
            putsSell={puts.sell}
            putCallRatio={put_call_ratio}
            timestamp={dataMode === 'historical' && selectedDate 
              ? `${selectedDate} ${replayTime}:00` 
              : new Date().toISOString()}
            width={1400}
            heightPerRow={20}
            windowSize={10}
          />
        </div>

        {/* Status Footer - Simplified (P/C moved to chart) */}
        <div className="mt-4 flex justify-between items-center px-4">
          <div className="text-xs text-gray-400">
            {dataMode === 'live' ? (
              <>🔴 LIVE: {selectedSymbol} last {selectedTimeframe} - refresh every 2s</>
            ) : (
              <>📅 HISTORICAL REPLAY: {selectedDate || 'Select a date'} at {replayTime} - {selectedSymbol} {isPlaying && '(Playing...)'}</>
            )}
          </div>
          
          <div className="flex items-center gap-4">
            {/* Timespan */}
            <div className="bg-yellow-600 text-black px-3 py-1 text-xs font-bold rounded">
              Timespan: {selectedTimeframe}
            </div>
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
