import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, RefreshCw, AlertCircle } from 'lucide-react';

const OptionsFlowMonitor = () => {
  const [selectedTimeframe, setSelectedTimeframe] = useState('5min');
  const [selectedSymbol, setSelectedSymbol] = useState('SPY');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  // Sample data structure - in production, this would come from a real-time API
  const [optionsData, setOptionsData] = useState({
    'SPY': generateMockData('SPY', 662.17),
    'QQQ': generateMockData('QQQ', 485.32),
    'AAPL': generateMockData('AAPL', 245.18),
    'MSFT': generateMockData('MSFT', 425.67),
    'NVDA': generateMockData('NVDA', 138.42),
    'TSLA': generateMockData('TSLA', 387.91),
    'META': generateMockData('META', 612.83),
    'GOOGL': generateMockData('GOOGL', 178.24),
    'AMZN': generateMockData('AMZN', 218.56),
  });

  function generateMockData(symbol, price) {
    const strikes = [];
    const baseStrike = Math.floor(price / 5) * 5;
    
    for (let i = -10; i <= 10; i++) {
      const strike = baseStrike + (i * 5);
      const distance = Math.abs(price - strike);
      const atmFactor = Math.max(0, 1 - (distance / 50));
      
      strikes.push({
        strike,
        callVolume: Math.floor(Math.random() * 50000 * (atmFactor + 0.2)),
        putVolume: Math.floor(Math.random() * 50000 * (atmFactor + 0.2)),
        callBuy: Math.floor(Math.random() * 30000 * (atmFactor + 0.2)),
        callSell: Math.floor(Math.random() * 30000 * (atmFactor + 0.2)),
        putBuy: Math.floor(Math.random() * 30000 * (atmFactor + 0.2)),
        putSell: Math.floor(Math.random() * 30000 * (atmFactor + 0.2)),
      });
    }
    
    return {
      price,
      strikes,
      timeframes: {
        '5min': { callBuy: 13932, callSell: 24898, putBuy: 33732, putSell: 21729 },
        '10min': { callBuy: 26458, callSell: 42823, putBuy: 54209, putSell: 37105 },
        '30min': { callBuy: 74948, callSell: 121331, putBuy: 134389, putSell: 97445 },
        '60min': { callBuy: 165279, callSell: 231838, putBuy: 262927, putSell: 183417 },
      }
    };
  }

  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      setOptionsData(prev => {
        const updated = {};
        Object.keys(prev).forEach(symbol => {
          updated[symbol] = generateMockData(symbol, prev[symbol].price);
        });
        return updated;
      });
      setLastUpdate(new Date());
    }, 5000);

    return () => clearInterval(interval);
  }, [autoRefresh]);

  const calculateRatio = (buyVol, sellVol) => {
    if (sellVol === 0) return buyVol > 0 ? 9.99 : 0;
    return (buyVol / sellVol).toFixed(4);
  };

  const currentData = optionsData[selectedSymbol];
  const tfData = currentData.timeframes[selectedTimeframe];
  const callRatio = calculateRatio(tfData.callBuy, tfData.callSell);
  const putRatio = calculateRatio(tfData.putBuy, tfData.putSell);

  const getColorClass = (ratio) => {
    if (ratio > 1.2) return 'text-green-400';
    if (ratio < 0.8) return 'text-red-400';
    return 'text-yellow-400';
  };

  const maxVolume = Math.max(
    ...currentData.strikes.map(s => Math.max(s.callVolume, s.putVolume))
  );

  return (
    <div className="w-full h-screen bg-black text-white p-4 overflow-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-3xl font-bold mb-2">Real-Time Options Flow</h1>
            <p className="text-gray-400 text-sm">
              Last Update: {lastUpdate.toLocaleTimeString()}
            </p>
          </div>
          
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center gap-2 px-4 py-2 rounded ${
              autoRefresh ? 'bg-green-600' : 'bg-gray-600'
            }`}
          >
            <RefreshCw className={`w-4 h-4 ${autoRefresh ? 'animate-spin' : ''}`} />
            {autoRefresh ? 'Auto-Refresh ON' : 'Auto-Refresh OFF'}
          </button>
        </div>

        {/* Symbol Selection */}
        <div className="flex gap-2 mb-4 flex-wrap">
          {Object.keys(optionsData).map(symbol => (
            <button
              key={symbol}
              onClick={() => setSelectedSymbol(symbol)}
              className={`px-4 py-2 rounded font-semibold ${
                selectedSymbol === symbol
                  ? 'bg-blue-600'
                  : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              {symbol}
            </button>
          ))}
        </div>

        {/* Timeframe Selection */}
        <div className="flex gap-2 mb-4">
          {['5min', '10min', '30min', '60min'].map(tf => (
            <button
              key={tf}
              onClick={() => setSelectedTimeframe(tf)}
              className={`px-4 py-2 rounded ${
                selectedTimeframe === tf
                  ? 'bg-purple-600'
                  : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              {tf.replace('min', ' min')}
            </button>
          ))}
        </div>
      </div>

      {/* Main Display */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Calls Summary */}
        <div className="bg-gray-900 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-bold mb-4 text-blue-400">Calls</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Total Volume:</span>
              <span className="font-bold">{(tfData.callBuy + tfData.callSell).toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-400">Buy:</span>
              <span className="font-bold text-green-400">{tfData.callBuy.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-red-400">Sell:</span>
              <span className="font-bold text-red-400">{tfData.callSell.toLocaleString()}</span>
            </div>
            <div className="pt-3 border-t border-gray-700">
              <div className="flex justify-between items-center">
                <span className="font-semibold">Buy/Sell Ratio:</span>
                <span className={`text-2xl font-bold ${getColorClass(callRatio)}`}>
                  {callRatio}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Current Price */}
        <div className="bg-gray-900 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-bold mb-4 text-center">{selectedSymbol}</h2>
          <div className="text-center">
            <div className="text-5xl font-bold mb-2">${currentData.price}</div>
            <div className="text-gray-400 text-sm mb-6">Stock Price</div>
            
            <div className="bg-gray-800 rounded p-4">
              <div className="text-sm text-gray-400 mb-2">Market Sentiment</div>
              <div className="flex items-center justify-center gap-2">
                {putRatio > callRatio ? (
                  <>
                    <TrendingDown className="text-red-400" />
                    <span className="text-red-400 font-bold">Bearish</span>
                  </>
                ) : (
                  <>
                    <TrendingUp className="text-green-400" />
                    <span className="text-green-400 font-bold">Bullish</span>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Puts Summary */}
        <div className="bg-gray-900 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-bold mb-4 text-purple-400">Puts</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Total Volume:</span>
              <span className="font-bold">{(tfData.putBuy + tfData.putSell).toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-400">Buy:</span>
              <span className="font-bold text-green-400">{tfData.putBuy.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-red-400">Sell:</span>
              <span className="font-bold text-red-400">{tfData.putSell.toLocaleString()}</span>
            </div>
            <div className="pt-3 border-t border-gray-700">
              <div className="flex justify-between items-center">
                <span className="font-semibold">Buy/Sell Ratio:</span>
                <span className={`text-2xl font-bold ${getColorClass(putRatio)}`}>
                  {putRatio}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Options Chain Volume */}
      <div className="bg-gray-900 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-bold mb-4">
          Options Chain Volume - {selectedTimeframe.replace('min', ' minutes')}
        </h2>
        
        <div className="space-y-1">
          {currentData.strikes.map((strike, idx) => {
            const isATM = Math.abs(strike.strike - currentData.price) < 2.5;
            const callWidth = (strike.callVolume / maxVolume) * 100;
            const putWidth = (strike.putVolume / maxVolume) * 100;
            
            return (
              <div
                key={idx}
                className={`flex items-center py-1 ${
                  isATM ? 'bg-gray-800 border-l-4 border-yellow-500' : ''
                }`}
              >
                <div className="w-1/4 text-right pr-4">
                  <div
                    className="h-6 bg-red-600 ml-auto"
                    style={{ width: `${callWidth}%` }}
                  />
                </div>
                
                <div className={`w-20 text-center font-bold ${
                  isATM ? 'text-yellow-400 text-lg' : 'text-gray-300'
                }`}>
                  {strike.strike}
                </div>
                
                <div className="w-1/4 pl-4">
                  <div
                    className="h-6 bg-green-600"
                    style={{ width: `${putWidth}%` }}
                  />
                </div>

                <div className="w-1/4 text-right text-xs text-gray-400">
                  <div>C: {strike.callVolume.toLocaleString()}</div>
                  <div>P: {strike.putVolume.toLocaleString()}</div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="flex justify-around mt-4 text-sm text-gray-400">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-red-600" />
            <span>Call Volume</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-green-600" />
            <span>Put Volume</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 border-l-4 border-yellow-500 bg-gray-800" />
            <span>At The Money</span>
          </div>
        </div>
      </div>

      {/* Info Notice */}
      <div className="mt-6 bg-blue-900 border border-blue-700 rounded-lg p-4 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-blue-100">
          <strong>Note:</strong> This demo uses simulated data. To connect to real-time options data, 
          you'll need to integrate with a provider like Tradier, CBOE DataShop, Polygon.io, or TD Ameritrade API. 
          These services require API keys and may have subscription costs.
        </div>
      </div>
    </div>
  );
};

export default OptionsFlowMonitor;