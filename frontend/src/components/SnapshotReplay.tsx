import React, { useState, useEffect } from 'react';
import { Play, Pause, SkipBack, SkipForward, Calendar } from 'lucide-react';
import { apiService } from '../services/api';

const SnapshotReplay: React.FC = () => {
  const [availableDates, setAvailableDates] = useState<string[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [selectedSymbol, setSelectedSymbol] = useState('SPY');
  const [snapshots, setSnapshots] = useState<any[]>([]);
  const [currentSnapshotIndex, setCurrentSnapshotIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const SYMBOLS = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'TSLA'];

  // Fetch available dates on mount
  useEffect(() => {
    const fetchDates = async () => {
      try {
        const response = await apiService.getReplayAvailableDates();
        setAvailableDates(response.dates);
        if (response.dates.length > 0) {
          setSelectedDate(response.dates[0]);
        }
      } catch (err) {
        console.error('Error fetching dates:', err);
      }
    };
    fetchDates();
  }, []);

  // Fetch snapshots when date or symbol changes
  useEffect(() => {
    if (selectedDate) {
      fetchSnapshots();
    }
  }, [selectedDate, selectedSymbol]);

  // Auto-play functionality
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isPlaying && snapshots.length > 0) {
      interval = setInterval(() => {
        setCurrentSnapshotIndex((prev) => {
          if (prev >= snapshots.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 3000); // Change snapshot every 3 seconds
    }
    return () => clearInterval(interval);
  }, [isPlaying, snapshots.length]);

  const fetchSnapshots = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiService.getReplaySnapshots(selectedDate, selectedSymbol);
      setSnapshots(response.snapshots);
      setCurrentSnapshotIndex(0);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch snapshots');
    } finally {
      setLoading(false);
    }
  };

  const currentSnapshot = snapshots[currentSnapshotIndex];
  const maxVolume = currentSnapshot?.strikes 
    ? Math.max(...currentSnapshot.strikes.map((s: any) => Math.max(s.call_volume, s.put_volume)))
    : 1;

  const handlePrevious = () => {
    setCurrentSnapshotIndex((prev) => Math.max(0, prev - 1));
    setIsPlaying(false);
  };

  const handleNext = () => {
    setCurrentSnapshotIndex((prev) => Math.min(snapshots.length - 1, prev + 1));
    setIsPlaying(false);
  };

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-black">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="w-full min-h-screen p-4 bg-black">
      <div className="max-w-[1600px] mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-4xl font-bold text-white mb-2">📊 Historical Snapshot Replay</h1>
          <p className="text-gray-400">Step through 4 snapshots to see how options flow evolved throughout a trading day</p>
        </div>

        {/* Controls */}
        <div className="mb-6 p-6 bg-gray-900 rounded-xl border border-gray-700">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Date Selector */}
            <div>
              <label className="block text-sm font-semibold text-gray-400 mb-2">
                <Calendar className="inline w-4 h-4 mr-1" />
                Select Date
              </label>
              <select
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="w-full px-4 py-2 bg-gray-800 text-white border border-gray-600 rounded"
              >
                {availableDates.map((date) => (
                  <option key={date} value={date}>
                    {new Date(date).toLocaleDateString('en-US', { 
                      weekday: 'short', 
                      month: 'short', 
                      day: 'numeric', 
                      year: 'numeric' 
                    })}
                  </option>
                ))}
              </select>
            </div>

            {/* Symbol Selector */}
            <div>
              <label className="block text-sm font-semibold text-gray-400 mb-2">Symbol</label>
              <select
                value={selectedSymbol}
                onChange={(e) => setSelectedSymbol(e.target.value)}
                className="w-full px-4 py-2 bg-gray-800 text-white border border-gray-600 rounded"
              >
                {SYMBOLS.map((symbol) => (
                  <option key={symbol} value={symbol}>${symbol}</option>
                ))}
              </select>
            </div>

            {/* Snapshot Counter */}
            <div>
              <label className="block text-sm font-semibold text-gray-400 mb-2">Snapshot</label>
              <div className="px-4 py-2 bg-gray-800 text-white border border-gray-600 rounded flex items-center justify-center">
                <span className="text-2xl font-bold">
                  {currentSnapshotIndex + 1} / {snapshots.length}
                </span>
              </div>
            </div>
          </div>

          {/* Playback Controls */}
          <div className="mt-6 flex items-center justify-center gap-4">
            <button
              onClick={() => setCurrentSnapshotIndex(0)}
              disabled={currentSnapshotIndex === 0}
              className="p-3 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded-lg transition-colors"
            >
              <SkipBack className="w-6 h-6" />
            </button>
            
            <button
              onClick={handlePrevious}
              disabled={currentSnapshotIndex === 0}
              className="p-3 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded-lg transition-colors"
            >
              Previous
            </button>
            
            <button
              onClick={handlePlayPause}
              className="p-4 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
            >
              {isPlaying ? <Pause className="w-8 h-8" /> : <Play className="w-8 h-8" />}
            </button>
            
            <button
              onClick={handleNext}
              disabled={currentSnapshotIndex >= snapshots.length - 1}
              className="p-3 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded-lg transition-colors"
            >
              Next
            </button>
            
            <button
              onClick={() => setCurrentSnapshotIndex(snapshots.length - 1)}
              disabled={currentSnapshotIndex >= snapshots.length - 1}
              className="p-3 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded-lg transition-colors"
            >
              <SkipForward className="w-6 h-6" />
            </button>
          </div>

          {/* Progress Bar */}
          <div className="mt-4">
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${((currentSnapshotIndex + 1) / snapshots.length) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Snapshot Display */}
        {currentSnapshot && (
          <div className="p-6 bg-gray-900 rounded-xl border border-gray-700">
            {/* Snapshot Header */}
            <div className="flex justify-between items-start mb-6">
              <div>
                <div className="text-blue-400 text-lg mb-1">
                  {currentSnapshot.snapshot_label} at {currentSnapshot.snapshot_time}
                </div>
                <h2 className="text-white text-3xl font-bold">
                  ${selectedSymbol} Options Volume ({selectedDate})
                </h2>
              </div>
              <div className="text-right">
                <div className="text-gray-400 text-sm">Stock Price</div>
                <div className="text-white text-2xl font-bold">${currentSnapshot.price?.toFixed(2)}</div>
              </div>
            </div>

            {/* Volume Summary */}
            <div className="grid grid-cols-2 gap-6 mb-6">
              <div className="p-4 bg-gray-800 rounded-lg border-l-4 border-green-500">
                <div className="text-green-400 font-bold text-sm">CALLS</div>
                <div className="text-white text-3xl font-bold mt-1">
                  {currentSnapshot.calls?.total?.toLocaleString() || '0'}
                </div>
                <div className="text-gray-400 text-sm mt-2">
                  Buy: {currentSnapshot.calls?.buy?.toLocaleString() || '0'} | 
                  Sell: {currentSnapshot.calls?.sell?.toLocaleString() || '0'}
                </div>
                <div className="mt-2 text-sm">
                  <span className="text-gray-400">Ratio:</span>{' '}
                  <span className="text-green-400 font-bold">
                    {currentSnapshot.calls?.ratio?.toFixed(4) || '0'}
                  </span>
                </div>
              </div>

              <div className="p-4 bg-gray-800 rounded-lg border-l-4 border-red-500">
                <div className="text-red-400 font-bold text-sm">PUTS</div>
                <div className="text-white text-3xl font-bold mt-1">
                  {currentSnapshot.puts?.total?.toLocaleString() || '0'}
                </div>
                <div className="text-gray-400 text-sm mt-2">
                  Buy: {currentSnapshot.puts?.buy?.toLocaleString() || '0'} | 
                  Sell: {currentSnapshot.puts?.sell?.toLocaleString() || '0'}
                </div>
                <div className="mt-2 text-sm">
                  <span className="text-gray-400">Ratio:</span>{' '}
                  <span className="text-red-400 font-bold">
                    {currentSnapshot.puts?.ratio?.toFixed(4) || '0'}
                  </span>
                </div>
              </div>
            </div>

            {/* Options Chain Visualization */}
            <div className="relative">
              {currentSnapshot.strikes?.slice(0, 20).map((strike: any, idx: number) => {
                const isATM = Math.abs(strike.strike - currentSnapshot.price) < 5;
                const callWidthPercent = (strike.call_volume / maxVolume) * 45;
                const putWidthPercent = (strike.put_volume / maxVolume) * 45;

                return (
                  <div key={idx} className="relative h-6 mb-1">
                    {/* Call volume (left) */}
                    <div className="absolute left-[8%] top-0 h-full flex items-center justify-end" style={{ width: '42%' }}>
                      <div
                        className="h-5 bg-green-600 transition-all duration-500"
                        style={{ width: `${callWidthPercent}%` }}
                      />
                    </div>

                    {/* Strike price (center) */}
                    <div 
                      className="absolute top-0 h-full flex items-center justify-center text-sm font-bold z-10"
                      style={{ left: '50%', transform: 'translateX(-50%)', width: '80px' }}
                    >
                      <span className={isATM ? 'text-yellow-400' : 'text-gray-300'}>
                        {strike.strike?.toFixed(1)}
                      </span>
                      {isATM && (
                        <div className="absolute inset-0 border-t border-b border-yellow-500 opacity-30" />
                      )}
                    </div>

                    {/* Put volume (right) */}
                    <div className="absolute right-[8%] top-0 h-full flex items-center justify-start" style={{ width: '42%' }}>
                      <div
                        className="h-5 bg-red-600 transition-all duration-500"
                        style={{ width: `${putWidthPercent}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Legend */}
            <div className="mt-6 flex justify-center gap-8 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-600"></div>
                <span className="text-gray-400">Call Volume</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-red-600"></div>
                <span className="text-gray-400">Put Volume</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-yellow-400"></div>
                <span className="text-gray-400">At-The-Money</span>
              </div>
            </div>
          </div>
        )}

        {/* Comparison Panel */}
        {snapshots.length > 1 && currentSnapshotIndex > 0 && (
          <div className="mt-6 p-6 bg-gray-900 rounded-xl border border-blue-700">
            <h3 className="text-xl font-bold text-white mb-4">📈 Change from {snapshots[0].snapshot_label}</h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-gray-400 text-sm">Calls</div>
                <div className={`text-2xl font-bold ${
                  (currentSnapshot.calls?.total - snapshots[0].calls?.total) > 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {((currentSnapshot.calls?.total - snapshots[0].calls?.total) || 0) > 0 ? '+' : ''}
                  {((currentSnapshot.calls?.total - snapshots[0].calls?.total) || 0).toLocaleString()}
                </div>
              </div>
              <div className="text-center">
                <div className="text-gray-400 text-sm">Puts</div>
                <div className={`text-2xl font-bold ${
                  (currentSnapshot.puts?.total - snapshots[0].puts?.total) > 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {((currentSnapshot.puts?.total - snapshots[0].puts?.total) || 0) > 0 ? '+' : ''}
                  {((currentSnapshot.puts?.total - snapshots[0].puts?.total) || 0).toLocaleString()}
                </div>
              </div>
              <div className="text-center">
                <div className="text-gray-400 text-sm">Price</div>
                <div className={`text-2xl font-bold ${
                  (currentSnapshot.price - snapshots[0].price) > 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {((currentSnapshot.price - snapshots[0].price) || 0) > 0 ? '+' : ''}
                  ${((currentSnapshot.price - snapshots[0].price) || 0).toFixed(2)}
                </div>
              </div>
            </div>

            {/* Insight Box */}
            <div className="mt-4 p-4 bg-blue-900 bg-opacity-30 rounded-lg border border-blue-700">
              <h4 className="text-blue-400 font-bold mb-2">💡 Data Update Pattern</h4>
              <p className="text-gray-300 text-sm">
                {Math.abs((currentSnapshot.calls?.total - snapshots[0].calls?.total) || 0) > 20000 || 
                 Math.abs((currentSnapshot.puts?.total - snapshots[0].puts?.total) || 0) > 20000
                  ? "✅ Significant changes observed - Real-time monitoring (2s refresh) is valuable"
                  : "⚠️ Moderate changes - Consider 5-10s refresh for better efficiency"}
              </p>
            </div>
          </div>
        )}

        {error && (
          <div className="mt-6 p-4 bg-red-900 border border-red-700 rounded-lg text-red-100">
            {error}
          </div>
        )}

        {/* Info Box */}
        <div className="mt-6 p-4 bg-gray-900 rounded-lg border border-gray-700">
          <h4 className="text-white font-bold mb-2">ℹ️ About This Feature</h4>
          <p className="text-gray-400 text-sm">
            This replay uses simulated data showing realistic evolution patterns throughout a trading day. 
            With proper S3 credentials, it can load real historical minute-aggregate data from Massive's Flat Files.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SnapshotReplay;