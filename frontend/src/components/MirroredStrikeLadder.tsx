import React from 'react';
import { Strike } from '../types';

interface MirroredStrikeLadderProps {
  symbol: string;
  strikes: Strike[];
  currentPrice: number;
  callsTotal: number;
  putsTotal: number;
  callRatio: number;
  putRatio: number;
  timestamp: string;
  width?: number;
  heightPerRow?: number;
  windowSize?: number; // Number of strikes above and below median (default: 10)
}

/**
 * Mirrored Strike Ladder Component
 * Displays options flow exactly like Mark Moses' tool:
 * - Center column: Strike prices
 * - Left side (GREEN): Call volume bars extending left
 * - Right side (RED): Put volume bars extending right
 * - White horizontal line at current stock price
 * - Symmetric X-axis with matching scale on both sides
 * - Dark theme with minimal labels
 */
const MirroredStrikeLadder: React.FC<MirroredStrikeLadderProps> = ({
  symbol,
  strikes,
  currentPrice,
  callsTotal,
  putsTotal,
  callRatio,
  putRatio,
  timestamp,
  width = 1200,
  heightPerRow = 18,
  windowSize = 10, // Show 10 strikes above and 10 below median
}) => {
  // Sort strikes by strike price (ascending)
  const sortedStrikes = [...strikes].sort((a, b) => a.strike - b.strike);
  
  // Find the index of the strike closest to current price (median)
  const closestStrikeIndex = sortedStrikes.reduce((closest, strike, idx) => {
    const currentDiff = Math.abs(strike.strike - currentPrice);
    const closestDiff = Math.abs(sortedStrikes[closest].strike - currentPrice);
    return currentDiff < closestDiff ? idx : closest;
  }, 0);

  // Select strikes: windowSize above and windowSize below the median
  // Ensure we always show windowSize * 2 + 1 strikes (median + above + below)
  const startIdx = Math.max(0, closestStrikeIndex - windowSize);
  const endIdx = Math.min(sortedStrikes.length, closestStrikeIndex + windowSize + 1);
  const visibleStrikes = sortedStrikes.slice(startIdx, endIdx).reverse(); // Reverse to show high strikes at top
  
  // Find median index in visible strikes
  const medianIndexInVisible = visibleStrikes.findIndex(s => {
    const idx = sortedStrikes.indexOf(s);
    return idx === closestStrikeIndex;
  });
  
  console.log('Debug:', {
    currentPrice,
    closestStrikeIndex,
    totalStrikes: sortedStrikes.length,
    visibleCount: visibleStrikes.length,
    medianIndexInVisible,
    medianStrike: visibleStrikes[medianIndexInVisible]?.strike,
    visibleRange: `${visibleStrikes[0]?.strike} - ${visibleStrikes[visibleStrikes.length - 1]?.strike}`
  });
  
  const rowsCount = visibleStrikes.length;
  const headerHeight = 100; // Increased for larger summary boxes
  const footerHeight = 80; // Increased for P/C ratio pill
  const height = headerHeight + (rowsCount * heightPerRow) + footerHeight;
  const centerX = width / 2;
  
  // Calculate max volume for symmetric scaling
  const maxCallVolume = Math.max(...visibleStrikes.map(s => s.call_volume), 1);
  const maxPutVolume = Math.max(...visibleStrikes.map(s => s.put_volume), 1);
  const maxVolume = Math.max(maxCallVolume, maxPutVolume);
  
  // Available width for bars (excluding center strike column and padding)
  const barAreaWidth = (width / 2) - 100; // 100px for labels and padding
  const scale = (volume: number) => (volume / maxVolume) * barAreaWidth;

  // Calculate Buy/Sell for calls and puts (simplified - using ratio as proxy)
  const callsBuy = Math.round(callsTotal * callRatio / (1 + callRatio));
  const callsSell = callsTotal - callsBuy;
  const putsBuy = Math.round(putsTotal * putRatio / (1 + putRatio));
  const putsSell = putsTotal - putsBuy;

  // Determine overall sentiment from put/call ratio
  const putCallRatio = putsTotal / (callsTotal || 1);
  const sentiment = putCallRatio > 1.2 ? 'Bearish' : putCallRatio < 0.8 ? 'Bullish' : 'Neutral';
  const sentimentColor = putCallRatio > 1.2 ? '#ef4444' : putCallRatio < 0.8 ? '#16a34a' : '#fbbf24';

  // Calculate buy/sell split for each strike
  const getStrikeBuySell = (volume: number, ratio: number) => {
    const buy = Math.round(volume * ratio / (1 + ratio));
    const sell = volume - buy;
    return { buy, sell };
  };
  
  // Format timestamp
  const formatTimestamp = (ts: string) => {
    try {
      const date = new Date(ts);
      const dateStr = date.toLocaleDateString('en-US', { 
        month: '2-digit', 
        day: '2-digit', 
        year: 'numeric' 
      });
      const timeStr = date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      });
      return `${dateStr.replace(/\//g, '/')} ${timeStr}`;
    } catch {
      return ts;
    }
  };

  // Calculate tick values for X-axis
  const getTickValues = () => {
    const roundTo = (num: number) => {
      if (num >= 5000) return Math.ceil(num / 1000) * 1000;
      if (num >= 1000) return Math.ceil(num / 500) * 500;
      if (num >= 100) return Math.ceil(num / 100) * 100;
      return Math.ceil(num / 10) * 10;
    };
    
    const roundedMax = roundTo(maxVolume);
    const ticks = [];
    const numTicks = 5;
    for (let i = 0; i <= numTicks; i++) {
      ticks.push(Math.round((roundedMax / numTicks) * i));
    }
    return ticks.reverse();
  };

  const tickValues = getTickValues();

  return (
    <svg 
      width={width} 
      height={height} 
      style={{ backgroundColor: '#000000', fontFamily: 'monospace' }}
    >
      {/* Title */}
      <text 
        x={centerX} 
        y={25} 
        fill="#ffffff" 
        fontSize="16" 
        fontWeight="bold"
        textAnchor="middle"
      >
        {symbol} Options Volume {formatTimestamp(timestamp)}
      </text>

      {/* P/C Ratio + Sentiment - TOP CENTER below title */}
      <g>
        <rect 
          x={centerX - 140} 
          y={35} 
          width={280} 
          height={28} 
          fill="#1f2937" 
          stroke={sentimentColor}
          strokeWidth="2" 
          rx="14"
          opacity="0.95"
        />
        
        <text
          x={centerX - 95}
          y={54}
          fill={sentimentColor}
          fontSize="12"
          fontWeight="bold"
        >
          P/C: {putCallRatio.toFixed(2)}
        </text>
        
        <text
          x={centerX - 25}
          y={54}
          fill="#6b7280"
          fontSize="12"
        >
          |
        </text>
        
        <text
          x={centerX}
          y={54}
          fill={sentimentColor}
          fontSize="11"
          fontWeight="bold"
        >
          {sentiment === 'Bullish' ? '🐂' : sentiment === 'Bearish' ? '🐻' : '⚖️'} {sentiment}
        </text>
      </g>

      {/* Top Left - Calls Summary (ENLARGED) */}
      <g>
        <text x={40} y={35} fill="#16a34a" fontSize="16" fontWeight="bold">
          Calls
        </text>
        <text x={40} y={58} fill="#ffffff" fontSize="22" fontWeight="bold">
          {callsTotal.toLocaleString()}
        </text>
        
        {/* Buy/Sell Labels and Values */}
        <text x={200} y={35} fill="#9ca3af" fontSize="12">
          Buy
        </text>
        <text x={200} y={52} fill="#16a34a" fontSize="14" fontWeight="bold">
          {callsBuy.toLocaleString()}
        </text>
        
        <text x={280} y={35} fill="#9ca3af" fontSize="12">
          Sell
        </text>
        <text x={280} y={52} fill="#ef4444" fontSize="14" fontWeight="bold">
          {callsSell.toLocaleString()}
        </text>
        
        {/* Ratio Box */}
        <rect x={200} y={60} width={120} height={26} fill="#1f2937" stroke="#16a34a" strokeWidth="1.5" rx="4" />
        <text x={260} y={77} fill="#16a34a" fontSize="13" fontWeight="bold" textAnchor="middle">
          Ratio: {callRatio.toFixed(4)}
        </text>
      </g>

      {/* Top Right - Puts Summary (ENLARGED) */}
      <g>
        <text x={width - 40} y={35} fill="#ef4444" fontSize="16" fontWeight="bold" textAnchor="end">
          Puts
        </text>
        <text x={width - 40} y={58} fill="#ffffff" fontSize="22" fontWeight="bold" textAnchor="end">
          {putsTotal.toLocaleString()}
        </text>
        
        {/* Buy/Sell Labels and Values */}
        <text x={width - 280} y={35} fill="#9ca3af" fontSize="12" textAnchor="end">
          Buy
        </text>
        <text x={width - 280} y={52} fill="#16a34a" fontSize="14" fontWeight="bold" textAnchor="end">
          {putsBuy.toLocaleString()}
        </text>
        
        <text x={width - 200} y={35} fill="#9ca3af" fontSize="12" textAnchor="end">
          Sell
        </text>
        <text x={width - 200} y={52} fill="#ef4444" fontSize="14" fontWeight="bold" textAnchor="end">
          {putsSell.toLocaleString()}
        </text>
        
        {/* Ratio Box */}
        <rect x={width - 320} y={60} width={120} height={26} fill="#1f2937" stroke="#ef4444" strokeWidth="1.5" rx="4" />
        <text x={width - 260} y={77} fill="#ef4444" fontSize="13" fontWeight="bold" textAnchor="middle">
          Ratio: {putRatio.toFixed(4)}
        </text>
      </g>

      {/* Strike Rows */}
      {visibleStrikes.map((strike, idx) => {
        const y = headerHeight + (idx * heightPerRow);
        const callWidth = scale(strike.call_volume);
        const putWidth = scale(strike.put_volume);
        const isMedian = idx === medianIndexInVisible;
        const isNearPrice = Math.abs(strike.strike - currentPrice) < 2.5;

        // Calculate buy/sell portions for this strike
        const callSplit = getStrikeBuySell(strike.call_volume, callRatio);
        const putSplit = getStrikeBuySell(strike.put_volume, putRatio);
        const callBuyWidth = callWidth * (callSplit.buy / (strike.call_volume || 1));
        const callSellWidth = callWidth * (callSplit.sell / (strike.call_volume || 1));
        const putBuyWidth = putWidth * (putSplit.buy / (strike.put_volume || 1));
        const putSellWidth = putWidth * (putSplit.sell / (strike.put_volume || 1));

        return (
          <g key={`${strike.strike}-${idx}`}>
            {/* Highlight median row with stronger background */}
            {isMedian && (
              <rect 
                x={0} 
                y={y - 2} 
                width={width} 
                height={heightPerRow + 4} 
                fill="rgba(255, 255, 255, 0.12)" 
              />
            )}

            {/* Call bar (LEFT side) - Buy portion (GREEN) */}
            <rect
              x={centerX - callWidth - 60}
              y={y + 2}
              width={callBuyWidth}
              height={heightPerRow - 4}
              fill="#16a34a"
              rx="4"
            />

            {/* Call bar (LEFT side) - Sell portion (RED) */}
            <rect
              x={centerX - callWidth - 60 + callBuyWidth}
              y={y + 2}
              width={callSellWidth}
              height={heightPerRow - 4}
              fill="#ef4444"
              rx="4"
            />

            {/* Put bar (RIGHT side) - Buy portion (GREEN) */}
            <rect
              x={centerX + 60}
              y={y + 2}
              width={putBuyWidth}
              height={heightPerRow - 4}
              fill="#16a34a"
              rx="4"
            />

            {/* Put bar (RIGHT side) - Sell portion (RED) */}
            <rect
              x={centerX + 60 + putBuyWidth}
              y={y + 2}
              width={putSellWidth}
              height={heightPerRow - 4}
              fill="#ef4444"
              rx="4"
            />

            {/* Strike price label (CENTER) */}
            <text
              x={centerX}
              y={y + (heightPerRow / 2) + 5}
              fill={isNearPrice ? "#fbbf24" : "#cbd5e1"}
              fontSize="12"
              fontWeight={isNearPrice ? "bold" : "normal"}
              textAnchor="middle"
            >
              {strike.strike.toFixed(1)}
            </text>

            {/* Optional: Volume numbers at the ends (very small) */}
            {strike.call_volume > 0 && (
              <text
                x={centerX - callWidth - 70}
                y={y + (heightPerRow / 2) + 4}
                fill="#6b7280"
                fontSize="9"
                textAnchor="end"
              >
                {strike.call_volume.toLocaleString()}
              </text>
            )}
            
            {strike.put_volume > 0 && (
              <text
                x={centerX + putWidth + 70}
                y={y + (heightPerRow / 2) + 4}
                fill="#6b7280"
                fontSize="9"
                textAnchor="start"
              >
                {strike.put_volume.toLocaleString()}
              </text>
            )}
          </g>
        );
      })}

      {/* Current Price Label + White horizontal line with gap */}
      {(() => {
        const lineIdx = medianIndexInVisible >= 0 ? medianIndexInVisible : Math.floor(visibleStrikes.length / 2);
        const lineY = headerHeight + (lineIdx * heightPerRow) + (heightPerRow / 2);
        const gapWidth = 100; // Gap in the center for strike price
        
        return (
          <g>
            {/* Current price label on the left side of the line */}
            <text
              x={70}
              y={lineY - 8}
              fill="#fbbf24"
              fontSize="12"
              fontWeight="bold"
              textAnchor="start"
            >
              {`${symbol} stock price: $${currentPrice.toFixed(2)}`}
            </text>
            
            {/* Left segment of white line */}
            <line
              x1={60}
              x2={centerX - gapWidth / 2}
              y1={lineY}
              y2={lineY}
              stroke="#ffffff"
              strokeWidth="3"
              opacity="0.95"
            />
            
            {/* Right segment of white line */}
            <line
              x1={centerX + gapWidth / 2}
              x2={width - 60}
              y1={lineY}
              y2={lineY}
              stroke="#ffffff"
              strokeWidth="3"
              opacity="0.95"
            />
          </g>
        );
      })()}

      {/* Bottom X-axis - Symmetric scale */}
      <g>
        {/* Left side (Calls) - descending ticks */}
        {tickValues.map((tick, idx) => {
          const x = centerX - 60 - (scale(tick));
          return (
            <text
              key={`left-tick-${idx}`}
              x={x}
              y={height - 45}
              fill="#6b7280"
              fontSize="10"
              textAnchor="middle"
            >
              {tick.toLocaleString()}
            </text>
          );
        })}

        {/* Right side (Puts) - ascending ticks */}
        {tickValues.slice().reverse().map((tick, idx) => {
          const x = centerX + 60 + (scale(tick));
          return (
            <text
              key={`right-tick-${idx}`}
              x={x}
              y={height - 45}
              fill="#6b7280"
              fontSize="10"
              textAnchor="middle"
            >
              {tick.toLocaleString()}
            </text>
          );
        })}

        {/* Axis labels */}
        <text
          x={centerX - 150}
          y={height - 25}
          fill="#9ca3af"
          fontSize="11"
          textAnchor="middle"
        >
          Call Volume
        </text>
        <text
          x={centerX + 150}
          y={height - 25}
          fill="#9ca3af"
          fontSize="11"
          textAnchor="middle"
        >
          Put Volume
        </text>
      </g>
    </svg>
  );
};

export default MirroredStrikeLadder;
