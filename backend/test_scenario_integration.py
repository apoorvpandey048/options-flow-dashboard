"""Test historical scenario integration with backtester"""
from strategy_backtester import StrategyBacktester
from historical_scenario_generator import historical_generator

print("Testing historical scenario integration...\n")

# Test 1: Import check
print("✓ Imports successful")

# Test 2: Initialize backtester
bt = StrategyBacktester()
print("✓ Backtester initialized")

# Test 3: Run backtest without date (random fallback)
print("\n--- Test 1: Random Data (no date) ---")
result_random = bt.run_backtest()
print(f"Total trades: {result_random['total_trades']}")
print(f"Win rate: {result_random['win_rate']:.1f}%")
print(f"Total P&L: ${result_random['total_profit']:.2f}")

# Test 4: Run backtest with FOMC date (high volatility)
print("\n--- Test 2: FOMC Day (Dec 18, 2024) ---")
result_fomc = bt.run_backtest(date='2024-12-18')
print(f"Total trades: {result_fomc['total_trades']}")
print(f"Win rate: {result_fomc['win_rate']:.1f}%")
print(f"Total P&L: ${result_fomc['total_profit']:.2f}")

# Test 5: Run backtest with Christmas Eve (low volume)
print("\n--- Test 3: Christmas Eve (Dec 24, 2024) ---")
result_xmas = bt.run_backtest(date='2024-12-24')
print(f"Total trades: {result_xmas['total_trades']}")
print(f"Win rate: {result_xmas['win_rate']:.1f}%")
print(f"Total P&L: ${result_xmas['total_profit']:.2f}")

# Test 6: Compare strategies with scenario
print("\n--- Test 4: Compare Strategies (FOMC Day) ---")
result_compare = bt.compare_strategies(date='2024-12-18')
print(f"Advanced Puts Win Rate: {result_compare['advanced_puts']['win_rate']:.1f}%")
print(f"Basic Puts Win Rate: {result_compare['basic_puts']['win_rate']:.1f}%")
print(f"Advanced Calls Win Rate: {result_compare['advanced_calls']['win_rate']:.1f}%")

print("\n✓ All tests completed successfully!")
