# Bugs and Potential Issues Report

## 🔴 CRITICAL ISSUES

### 1. **users.json File Location Inconsistency**
**Location:** `backend/auth.py` line 13  
**Severity:** HIGH  
**Issue:** The `users.json` file is created in the current working directory, not in a consistent location. When running from different directories, this creates multiple user databases.

**Current Code:**
```python
USERS_FILE = 'users.json'
```

**Problem:** If you run the backend from different directories, it will create `users.json` in each directory.

**Fix Required:**
```python
import os
USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')
```

---

### 2. **No Concurrent Access Protection for users.json**
**Location:** `backend/auth.py` lines 15-25  
**Severity:** HIGH  
**Issue:** Multiple simultaneous registrations could corrupt the users.json file due to race conditions.

**Problem:** 
- User A reads users.json
- User B reads users.json
- User A writes to users.json
- User B writes to users.json (overwriting User A's changes)

**Fix Required:** Add file locking or use a proper database.

---

### 3. **WebSocket Memory Leak in Frontend**
**Location:** `frontend/src/components/OptionsFlowMonitor.tsx` lines 39-58  
**Severity:** MEDIUM  
**Issue:** Multiple event listeners can be registered without cleanup when component re-renders.

**Current Code:**
```typescript
this.socket?.on('monitor_update', callback);
this.socket?.on('market_update', (data) => {
  if (data.symbol === symbol && data.timeframe === timeframe) {
    callback(data.data);
  }
});
```

**Problem:** Each time `subscribeToSymbol` is called, new listeners are added without removing old ones.

**Fix Required:** Remove old listeners before adding new ones:
```typescript
this.socket?.off('monitor_update');
this.socket?.off('market_update');
this.socket?.on('monitor_update', callback);
```

---

### 4. **Background Streaming Always Active**
**Location:** `backend/app.py` lines 211-225  
**Severity:** MEDIUM  
**Issue:** Background streaming broadcasts to ALL timeframes and symbols every 5 seconds, even when no clients need that data.

**Problem:**
- Wastes CPU/resources generating data for all 9 symbols × 4 timeframes = 36 data points every 5 seconds
- No client subscription tracking

**Fix Required:** Only stream data for symbols/timeframes that clients are subscribed to.

---

## 🟡 MODERATE ISSUES

### 5. **No Input Validation on Backtest Parameters**
**Location:** `backend/strategy_backtester.py`  
**Severity:** MEDIUM  
**Issue:** User can input invalid parameters (negative values, division by zero, etc.)

**Example Problems:**
- `position_size = -100` (negative money)
- `num_trades = 0` (division by zero)
- `profit_target = 10` (1000% return - unrealistic)

**Fix Required:** Add validation:
```python
def validate_params(params):
    assert params['num_trades'] > 0, "Must have at least 1 trade"
    assert params['position_size'] > 0, "Position size must be positive"
    assert -1 <= params['stop_loss'] < 0, "Stop loss must be between -100% and 0%"
    assert 0 < params['profit_target'] < 5, "Profit target must be between 0% and 500%"
```

---

### 6. **CORS Allows All Origins**
**Location:** `backend/app.py` line 18  
**Severity:** MEDIUM  
**Issue:** `CORS(app, resources={r"/*": {"origins": "*"}})` allows ANY website to make requests.

**Security Risk:** Any malicious website can:
- Register users
- Login and steal tokens
- Make API calls on behalf of users

**Fix Required:**
```python
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}})
```

---

### 7. **JWT Secret Key Is Hardcoded**
**Location:** `backend/auth.py` line 12  
**Severity:** HIGH  
**Issue:** `SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')`

**Problem:** Default secret is predictable. Anyone can forge tokens if the .env is not configured.

**Fix Required:** 
- Generate a strong random secret
- Fail if SECRET_KEY is not set in production
```python
SECRET_KEY = os.getenv('JWT_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY must be set in environment variables")
```

---

### 8. **No Rate Limiting**
**Location:** All API endpoints  
**Severity:** MEDIUM  
**Issue:** No rate limiting on authentication or API endpoints.

**Attack Vectors:**
- Brute force password attacks
- DoS by spamming backtest endpoint (CPU intensive)
- Register spam

**Fix Required:** Add Flask-Limiter:
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@limiter.limit("5 per minute")
@app.route('/api/auth/login', methods=['POST'])
def login():
    ...
```

---

### 9. **No Email Validation**
**Location:** `backend/auth.py` line 65  
**Severity:** LOW  
**Issue:** Email field is not validated. Users can register with invalid emails or no email.

**Fix Required:**
```python
import re
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

---

### 10. **Sensitive Data in Console Logs**
**Location:** Multiple files  
**Severity:** LOW  
**Issue:** Socket IDs and connection info printed to console could leak information.

**Examples:**
```python
print(f'Client connected: {request.sid}')
print(f'Client {request.sid} subscribed to {symbol}')
```

**Fix Required:** Use proper logging with levels:
```python
import logging
logging.info(f'Client connected: {request.sid}')
```

---

## 🟢 MINOR ISSUES & IMPROVEMENTS

### 11. **No Request Timeout on API Calls**
**Location:** `frontend/src/services/api.ts`  
**Severity:** LOW  
**Issue:** API calls have no timeout. Could hang forever if backend is unresponsive.

**Fix Required:**
```typescript
const response = await axios.get(`${API_BASE_URL}/api/health`, {
  timeout: 5000 // 5 second timeout
});
```

---

### 12. **WebSocket Not Properly Cleaned Up on Component Unmount**
**Location:** `frontend/src/components/OptionsFlowMonitor.tsx`  
**Severity:** LOW  
**Issue:** WebSocket connection might persist after component unmounts.

**Fix Required:** Add cleanup in useEffect return:
```typescript
return () => {
  clearInterval(interval);
  apiService.unsubscribeFromSymbol(selectedSymbol);
  if (!autoRefresh) {
    apiService.disconnectWebSocket(); // Add this
  }
};
```

---

### 13. **No Loading State for Authentication**
**Location:** `frontend/src/App.tsx` ProtectedRoute  
**Severity:** LOW  
**Issue:** Shows "Loading..." text without any styling or spinner.

**Improvement:**
```tsx
<div className="flex items-center justify-center min-h-screen bg-gray-900">
  <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
</div>
```

---

### 14. **Cache Can Grow Unbounded**
**Location:** `backend/data_fetcher.py` line 61  
**Severity:** LOW  
**Issue:** While `_clear_old_cache_entries()` exists, there's no maximum cache size limit.

**Problem:** If someone queries all 9 symbols × 4 timeframes continuously, cache could grow large.

**Fix Required:** Add max cache size:
```python
if len(self.cache) > 100:
    self._clear_old_cache_entries()
```

---

### 15. **TypeScript Type Assertion Overuse**
**Location:** `frontend/src/components/Login.tsx` line 33  
**Severity:** LOW  
**Issue:** `err: any` - loses type safety

**Improvement:**
```typescript
catch (err) {
  if (axios.isAxiosError(err)) {
    setError(err.response?.data?.error || 'Authentication failed');
  } else {
    setError('An unexpected error occurred');
  }
}
```

---

### 16. **No Password Strength Requirements**
**Location:** `backend/auth.py`, `frontend/src/components/Login.tsx`  
**Severity:** LOW  
**Issue:** Users can register with weak passwords like "1" or "a".

**Fix Required:** Add validation:
```python
def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    # Add more checks as needed
    return True, None
```

---

### 17. **Debug Mode in Production**
**Location:** `backend/app.py` line 245  
**Severity:** MEDIUM  
**Issue:** `debug=Config.DEBUG` could be True in production if .env is misconfigured.

**Security Risk:** Debug mode exposes:
- Stack traces with code
- Interactive debugger in browser
- Internal paths

**Fix Required:**
```python
socketio.run(app, debug=False, host='0.0.0.0', port=5000)
```

---

### 18. **No .gitignore for users.json**
**Location:** Repository root  
**Severity:** LOW  
**Issue:** `users.json` with user credentials could be committed to git.

**Fix Required:** Add to `.gitignore`:
```
backend/users.json
backend/*.json
```

---

### 19. **Division by Zero Risk in Options Monitor**
**Location:** `backend/options_monitor.py` line 116  
**Severity:** LOW  
**Issue:** If `total_call_vol` or `total_put_vol` is 0, division by zero occurs.

**Current Protection:** None in this specific method.

**Fix Required:**
```python
'percentage': round(max_call_strike['call_volume'] / max(total_call_vol, 1) * 100, 2)
```

---

### 20. **No Database Indexes**
**Location:** User storage  
**Severity:** LOW  
**Issue:** Using JSON file instead of database means no indexes, slow lookups.

**Recommendation:** Migrate to SQLite or PostgreSQL for better:
- Performance
- Concurrency
- Data integrity
- Query capabilities

---

## 📊 SUMMARY

| Severity | Count | Category |
|----------|-------|----------|
| Critical | 4 | Security, Data Loss |
| High | 3 | Security, Corruption |
| Medium | 6 | Performance, UX |
| Low | 7 | Quality, Minor bugs |

**Total Issues Found:** 20

## 🛠️ PRIORITY FIXES (Immediate Action Required)

1. ✅ Fix `users.json` path to use absolute path
2. ✅ Add file locking or migrate to SQLite
3. ✅ Fix CORS to whitelist only localhost:3000
4. ✅ Enforce strong JWT secret key
5. ✅ Add rate limiting to prevent abuse
6. ✅ Optimize background streaming to only active subscriptions
7. ✅ Fix WebSocket memory leak

## 🔍 TESTING RECOMMENDATIONS

1. **Load Testing:** Test with 100+ concurrent users
2. **Security Testing:** Try brute force attacks, XSS, SQL injection
3. **Memory Testing:** Monitor memory usage over 24 hours
4. **Concurrency Testing:** Register 10 users simultaneously
5. **WebSocket Testing:** Connect/disconnect rapidly

---

*Generated: December 22, 2025*
