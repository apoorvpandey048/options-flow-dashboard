import React from 'react';
import { Link } from 'react-router-dom';
import { Activity, TrendingUp, Zap, Shield, BarChart3, Eye, Calendar } from 'lucide-react';

const Home: React.FC = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold mb-6 bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 text-transparent bg-clip-text">
            Options Flow Monitor & Strategy Backtester
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            Professional-grade options flow analysis with real-time data visualization and
            advanced strategy backtesting for SPY, QQQ, and major tech stocks.
          </p>
          <div className="flex gap-4 justify-center mt-8">
            <Link
              to="/monitor"
              className="px-8 py-4 bg-blue-600 hover:bg-blue-700 rounded-lg font-bold text-lg transition-colors flex items-center gap-2"
            >
              <Activity className="w-5 h-5" />
              Start Monitoring
            </Link>
            <Link
              to="/historical"
              className="px-8 py-4 bg-green-600 hover:bg-green-700 rounded-lg font-bold text-lg transition-colors flex items-center gap-2"
            >
              <Calendar className="w-5 h-5" />
              View Historical
            </Link>
            <Link
              to="/backtest"
              className="px-8 py-4 bg-purple-600 hover:bg-purple-700 rounded-lg font-bold text-lg transition-colors flex items-center gap-2"
            >
              <TrendingUp className="w-5 h-5" />
              Run Backtest
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-20">
          <FeatureCard
            icon={<Eye className="w-8 h-8 text-blue-400" />}
            title="Real-Time Monitoring"
            description="Track options flow across multiple timeframes (5min, 10min, 30min, 60min) with live updates"
          />
          <FeatureCard
            icon={<BarChart3 className="w-8 h-8 text-purple-400" />}
            title="Options Chain Visualization"
            description="Visual representation of volume distribution by strike price with ATM highlighting"
          />
          <FeatureCard
            icon={<TrendingUp className="w-8 h-8 text-green-400" />}
            title="Put/Call Ratio Analysis"
            description="Real-time buy/sell ratios for puts and calls with market sentiment indicators"
          />
          <FeatureCard
            icon={<Zap className="w-8 h-8 text-yellow-400" />}
            title="Multi-Signal Backtester"
            description="Test strategies with volume spikes, IV filters, and multi-timeframe confirmation"
          />
          <FeatureCard
            icon={<Shield className="w-8 h-8 text-red-400" />}
            title="Strategy Comparison"
            description="Compare advanced puts, basic puts, and calls strategies side-by-side"
          />
          <FeatureCard
            icon={<Activity className="w-8 h-8 text-indigo-400" />}
            title="Performance Metrics"
            description="Win rate, profit factor, Sharpe ratio, max drawdown, and detailed trade logs"
          />
        </div>

        {/* Tech Stack */}
        <div className="mt-20 p-8 bg-gray-800 bg-opacity-50 rounded-xl border border-gray-700">
          <h2 className="text-3xl font-bold mb-6 text-center">Professional Tech Stack</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <TechItem name="React + TypeScript" />
            <TechItem name="Python Flask" />
            <TechItem name="WebSocket Real-Time" />
            <TechItem name="Recharts Visualization" />
          </div>
        </div>

        {/* Supported Symbols */}
        <div className="mt-12 p-8 bg-gradient-to-r from-blue-900 to-purple-900 rounded-xl border border-blue-700">
          <h3 className="text-2xl font-bold mb-4 text-center">Supported Symbols</h3>
          <div className="flex flex-wrap justify-center gap-4">
            {['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'TSLA', 'META', 'GOOGL', 'AMZN'].map(symbol => (
              <span
                key={symbol}
                className="px-4 py-2 bg-white bg-opacity-10 rounded-lg font-bold text-lg"
              >
                {symbol}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const FeatureCard: React.FC<{ icon: React.ReactNode; title: string; description: string }> = ({
  icon,
  title,
  description
}) => (
  <div className="p-6 bg-gray-800 bg-opacity-50 rounded-xl border border-gray-700 hover:border-gray-600 transition-colors">
    <div className="mb-4">{icon}</div>
    <h3 className="text-xl font-bold mb-2">{title}</h3>
    <p className="text-gray-400">{description}</p>
  </div>
);

const TechItem: React.FC<{ name: string }> = ({ name }) => (
  <div className="py-3 px-4 bg-gray-700 rounded-lg font-semibold">{name}</div>
);

export default Home;
