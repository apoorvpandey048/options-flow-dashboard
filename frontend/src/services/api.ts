/**
 * API Service for communicating with Flask backend
 */
import axios from 'axios';
import { io, Socket } from 'socket.io-client';
import { MonitorData, BacktestParams, BacktestResult, ComparisonResult } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const WS_URL = process.env.REACT_APP_WS_URL || 'http://localhost:5000';

class ApiService {
  private socket: Socket | null = null;

  private getAuthHeader() {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async register(username: string, password: string, email: string) {
    const response = await axios.post(`${API_BASE_URL}/api/auth/register`, {
      username,
      password,
      email,
    });
    return response.data;
  }

  async login(username: string, password: string) {
    const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
      username,
      password,
    });
    return response.data;
  }

  async verifyToken() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/auth/verify`, {
        headers: this.getAuthHeader(),
      });
      return response.data;
    } catch {
      return null;
    }
  }

  // REST API calls
  async healthCheck() {
    const response = await axios.get(`${API_BASE_URL}/api/health`, {
      timeout: 5000 // 5 second timeout
    });
    return response.data;
  }

  async getSymbols() {
    const response = await axios.get(`${API_BASE_URL}/api/symbols`);
    return response.data;
  }

  async getMonitorData(symbol: string, timeframe: string = '5min'): Promise<MonitorData> {
    const response = await axios.get(`${API_BASE_URL}/api/monitor/${symbol}`, {
      params: { timeframe },
      headers: this.getAuthHeader(),
      timeout: 5000
    });
    return response.data;
  }

  async getAllTimeframes(symbol: string) {
    const response = await axios.get(`${API_BASE_URL}/api/monitor/${symbol}/all-timeframes`, {
      headers: this.getAuthHeader(),
      timeout: 5000
    });
    return response.data;
  }

  async getSummary(timeframe: string = '5min') {
    const response = await axios.get(`${API_BASE_URL}/api/monitor/summary`, {
      params: { timeframe },
      headers: this.getAuthHeader(),
      timeout: 5000
    });
    return response.data;
  }

  async getStrikeAnalysis(symbol: string) {
    const response = await axios.get(`${API_BASE_URL}/api/monitor/${symbol}/strikes`, {
      headers: this.getAuthHeader(),
      timeout: 5000
    });
    return response.data;
  }

  async runBacktest(params: Partial<BacktestParams>): Promise<BacktestResult> {
    const response = await axios.post(`${API_BASE_URL}/api/backtest/run`, params, {
      headers: this.getAuthHeader(),
      timeout: 30000
    });
    return response.data;
  }

  async compareStrategies(params: Partial<BacktestParams>): Promise<ComparisonResult> {
    const response = await axios.post(`${API_BASE_URL}/api/backtest/compare`, params, {
      headers: this.getAuthHeader(),
      timeout: 30000
    });
    return response.data;
  }

  // WebSocket methods
  connectWebSocket(onConnect?: () => void, onDisconnect?: () => void) {
    if (this.socket) {
      return this.socket;
    }

    this.socket = io(WS_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      onConnect?.();
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      onDisconnect?.();
    });

    this.socket.on('connection_response', (data) => {
      console.log('Connection response:', data);
    });

    return this.socket;
  }

  disconnectWebSocket() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  subscribeToSymbol(symbol: string, timeframe: string, callback: (data: MonitorData) => void) {
    if (!this.socket) {
      this.connectWebSocket();
    }

    // Remove old listeners to prevent memory leak
    this.socket?.off('monitor_update');
    this.socket?.off('market_update');
    
    this.socket?.emit('subscribe', { symbol, timeframe });
    this.socket?.on('monitor_update', callback);
    this.socket?.on('market_update', (data) => {
      if (data.symbol === symbol && data.timeframe === timeframe) {
        callback(data.data);
      }
    });
  }

  unsubscribeFromSymbol(symbol: string) {
    this.socket?.emit('unsubscribe', { symbol });
    this.socket?.off('monitor_update');
    this.socket?.off('market_update');
  }

  requestUpdate(symbol: string, timeframe: string) {
    this.socket?.emit('request_update', { symbol, timeframe });
  }
}

export const apiService = new ApiService();
