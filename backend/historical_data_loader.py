"""
Historical Data Loader - Provides 4 sample dates of options flow data
Mimics Massive Flat Files format (day_aggs_v1 and minute_aggs_v1)
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any

# 4 Sample dates with realistic options flow data
HISTORICAL_SAMPLES = {
    "2025-12-27": {
        "market_summary": {
            "spy_open": 689.82,
            "spy_high": 691.15,
            "spy_low": 689.12,
            "spy_close": 690.31,
            "spy_volume": 41669457,
            "spy_change_pct": 0.08
        },
        "unusual_activity": [
            {
                "ticker": "O:SPY260102C00690000",
                "strike": 690,
                "type": "CALL",
                "expiry": "2026-01-02",
                "volume": 102,
                "avg_volume_20d": 29,
                "volume_ratio": 3.5,
                "rating": "EXTREME",
                "price": 12.45,
                "underlying": "SPY"
            },
            {
                "ticker": "O:NVDA260109P00190000",
                "strike": 190,
                "type": "PUT",
                "expiry": "2026-01-09",
                "volume": 178,
                "avg_volume_20d": 82,
                "volume_ratio": 2.2,
                "rating": "HIGH",
                "price": 8.92,
                "underlying": "NVDA"
            }
        ],
        "intraday_data": {
            "O:SPY260102C00690000": [
                {"time": "09:30", "volume": 5, "open": 12.20, "high": 12.30, "low": 12.18, "close": 12.25},
                {"time": "09:45", "volume": 8, "open": 12.25, "high": 12.40, "low": 12.22, "close": 12.35},
                {"time": "10:00", "volume": 12, "open": 12.35, "high": 12.50, "low": 12.30, "close": 12.45},
                {"time": "10:15", "volume": 22, "open": 12.45, "high": 12.65, "low": 12.42, "close": 12.58},
                {"time": "10:30", "volume": 18, "open": 12.58, "high": 12.70, "low": 12.52, "close": 12.60},
            ]
        }
    },
    "2025-12-26": {
        "market_summary": {
            "spy_open": 689.25,
            "spy_high": 690.45,
            "spy_low": 688.95,
            "spy_close": 689.75,
            "spy_volume": 35240180,
            "spy_change_pct": -0.05
        },
        "unusual_activity": [
            {
                "ticker": "O:AAPL260102C00270000",
                "strike": 270,
                "type": "CALL",
                "expiry": "2026-01-02",
                "volume": 68,
                "avg_volume_20d": 19,
                "volume_ratio": 3.6,
                "rating": "EXTREME",
                "price": 15.80,
                "underlying": "AAPL"
            }
        ],
        "intraday_data": {
            "O:AAPL260102C00270000": [
                {"time": "09:30", "volume": 4, "open": 15.50, "high": 15.60, "low": 15.45, "close": 15.55},
                {"time": "10:00", "volume": 9, "open": 15.55, "high": 15.75, "low": 15.52, "close": 15.70},
                {"time": "10:30", "volume": 18, "open": 15.70, "high": 15.92, "low": 15.68, "close": 15.85},
                {"time": "11:00", "volume": 15, "open": 15.85, "high": 15.90, "low": 15.75, "close": 15.80},
                {"time": "11:30", "volume": 12, "open": 15.80, "high": 15.88, "low": 15.78, "close": 15.82},
            ]
        }
    },
    "2025-12-24": {
        "market_summary": {
            "spy_open": 689.10,
            "spy_high": 689.80,
            "spy_low": 688.45,
            "spy_close": 688.95,
            "spy_volume": 18560230,
            "spy_change_pct": -0.12
        },
        "unusual_activity": [
            {
                "ticker": "O:QQQ260102P00620000",
                "strike": 620,
                "type": "PUT",
                "expiry": "2026-01-02",
                "volume": 145,
                "avg_volume_20d": 52,
                "volume_ratio": 2.8,
                "rating": "HIGH",
                "price": 18.25,
                "underlying": "QQQ"
            }
        ],
        "intraday_data": {
            "O:QQQ260102P00620000": [
                {"time": "09:30", "volume": 8, "open": 17.90, "high": 18.00, "low": 17.85, "close": 17.95},
                {"time": "10:00", "volume": 22, "open": 17.95, "high": 18.15, "low": 17.92, "close": 18.10},
                {"time": "10:30", "volume": 38, "open": 18.10, "high": 18.35, "low": 18.08, "close": 18.28},
                {"time": "11:00", "volume": 31, "open": 18.28, "high": 18.40, "low": 18.20, "close": 18.30},
                {"time": "11:30", "volume": 25, "open": 18.30, "high": 18.35, "low": 18.22, "close": 18.25},
            ]
        }
    },
    "2025-12-23": {
        "market_summary": {
            "spy_open": 688.15,
            "spy_high": 688.95,
            "spy_low": 687.50,
            "spy_close": 687.85,
            "spy_volume": 42350680,
            "spy_change_pct": -0.18
        },
        "unusual_activity": [
            {
                "ticker": "O:TSLA251227C00420000",
                "strike": 420,
                "type": "CALL",
                "expiry": "2025-12-27",
                "volume": 2450,
                "avg_volume_20d": 850,
                "volume_ratio": 2.9,
                "rating": "HIGH",
                "price": 28.50,
                "underlying": "TSLA"
            },
            {
                "ticker": "O:AAPL260103P00265000",
                "strike": 265,
                "type": "PUT",
                "expiry": "2026-01-03",
                "volume": 92,
                "avg_volume_20d": 55,
                "volume_ratio": 1.7,
                "rating": "ELEVATED",
                "price": 9.15,
                "underlying": "AAPL"
            }
        ],
        "intraday_data": {
            "O:TSLA251227C00420000": [
                {"time": "09:30", "volume": 150, "open": 27.80, "high": 28.00, "low": 27.75, "close": 27.90},
                {"time": "10:00", "volume": 380, "open": 27.90, "high": 28.20, "low": 27.85, "close": 28.10},
                {"time": "10:30", "volume": 520, "open": 28.10, "high": 28.55, "low": 28.05, "close": 28.45},
                {"time": "11:00", "volume": 450, "open": 28.45, "high": 28.65, "low": 28.35, "close": 28.50},
                {"time": "11:30", "volume": 380, "open": 28.50, "high": 28.60, "low": 28.42, "close": 28.52},
            ]
        }
    }
}


class HistoricalDataLoader:
    """Loads pre-defined historical options flow data for demo/testing"""
    
    def __init__(self):
        self.data = HISTORICAL_SAMPLES
    
    def get_available_dates(self) -> List[str]:
        """Get list of available historical dates"""
        return sorted(self.data.keys(), reverse=True)
    
    def get_date_summary(self, date: str) -> Dict[str, Any]:
        """Get summary for a specific date"""
        if date not in self.data:
            return None
        
        data = self.data[date]
        return {
            "date": date,
            "spy_close": data["market_summary"]["spy_close"],
            "spy_volume": data["market_summary"]["spy_volume"],
            "unusual_activity_count": len(data["unusual_activity"]),
            "top_contract": data["unusual_activity"][0]["ticker"] if data["unusual_activity"] else None,
            "total_contracts": len(data["unusual_activity"])
        }
    
    def get_full_day_analysis(self, date: str) -> Dict[str, Any]:
        """Get complete analysis for a trading day"""
        if date not in self.data:
            return None
        
        data = self.data[date]
        return {
            "date": date,
            "market_summary": data["market_summary"],
            "options_summary": {
                "total_unusual": len(data["unusual_activity"]),
                "extreme_flows": sum(1 for x in data["unusual_activity"] if x["rating"] == "EXTREME"),
                "high_flows": sum(1 for x in data["unusual_activity"] if x["rating"] == "HIGH"),
                "elevated_flows": sum(1 for x in data["unusual_activity"] if x["rating"] == "ELEVATED")
            },
            "unusual_activity": data["unusual_activity"]
        }
    
    def get_unusual_activity(self, date: str, min_ratio: float = 1.5) -> List[Dict[str, Any]]:
        """Get unusual options activity for a date filtered by volume ratio"""
        if date not in self.data:
            return []
        
        activities = self.data[date]["unusual_activity"]
        return [a for a in activities if a["volume_ratio"] >= min_ratio]
    
    def get_intraday_chart_data(self, date: str, ticker: str) -> Dict[str, Any]:
        """Get minute-by-minute data for charting"""
        if date not in self.data:
            return None
        
        intraday = self.data[date].get("intraday_data", {}).get(ticker)
        if not intraday:
            return None
        
        return {
            "ticker": ticker,
            "date": date,
            "data_points": intraday,
            "times": [d["time"] for d in intraday],
            "volumes": [d["volume"] for d in intraday],
            "prices": [d["close"] for d in intraday],
            "ohlc": [{
                "open": d["open"],
                "high": d["high"],
                "low": d["low"],
                "close": d["close"]
            } for d in intraday]
        }
    
    def calculate_flow_score(self, date: str, ticker: str) -> Dict[str, Any]:
        """Calculate flow metrics for a specific contract"""
        if date not in self.data:
            return None
        
        activities = self.data[date]["unusual_activity"]
        contract = next((a for a in activities if a["ticker"] == ticker), None)
        
        if not contract:
            return None
        
        return {
            "ticker": contract["ticker"],
            "volume": contract["volume"],
            "avg_volume": contract["avg_volume_20d"],
            "ratio": contract["volume_ratio"],
            "rating": contract["rating"],
            "score": round(contract["volume_ratio"] * 100)
        }


# Singleton instance
historical_loader = HistoricalDataLoader()
