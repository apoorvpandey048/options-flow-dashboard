# Quick Start Guide - Testing the New UI

## Prerequisites
- Virtual environment set up (`.venv` folder exists)
- Node modules installed (`frontend/node_modules` exists)
- Insight Sentry API key configured (already in `start-backend.ps1`)

---

## Step 1: Start Backend Server

Open **PowerShell Terminal #1** and run:

```powershell
cd C:\Users\Apoor\options-flow-dashboard
.\start-backend.ps1
```

**Expected Output:**
```
================================
Starting Backend Server
================================

Activating virtual environment...
Starting Flask server...
Backend will be available at: http://localhost:10000
API Health Check: http://localhost:10000/api/health

Press Ctrl+C to stop the server

 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:10000
```

**Verify Backend:**
- Open browser: http://localhost:10000/api/health
- Should see: `{"status":"healthy","timestamp":"...","version":"1.0.0"}`

**DO NOT CLOSE THIS TERMINAL** - Keep it running in background.

---

## Step 2: Start Frontend Server

Open **PowerShell Terminal #2** and run:

```powershell
cd C:\Users\Apoor\options-flow-dashboard
.\start-frontend.ps1
```

**Expected Output:**
```
================================
Starting Frontend Server
================================

Starting React development server...
Frontend will be available at: http://localhost:3000

Make sure backend is running on port 5000
Press Ctrl+C to stop the server

Compiled successfully!

You can now view options-flow-dashboard in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

**Browser Should Auto-Open:** http://localhost:3000

**DO NOT CLOSE THIS TERMINAL** - Keep it running in background.

---

## Step 3: Login (If Required)

If you see a login page:
1. Use existing credentials OR
2. Register new account
3. Click "Login"

---

## Step 4: Navigate to Options Flow Monitor

1. Click **"Options Flow Monitor"** button/link
2. Dashboard should load with default symbol: **SPY**
3. Wait 2-5 seconds for data to load

---

## Step 5: Visual Verification Checklist

### ✅ Overall Layout:
- [ ] Black background (`#000000`)
- [ ] Title at top: "SPY Options Volume [date] [time]"
- [ ] Calls summary top-left (green text, white numbers)
- [ ] Puts summary top-right (red text, white numbers)
- [ ] Strike ladder in center
- [ ] X-axis at bottom with symmetric numbers

### ✅ Strike Ladder:
- [ ] Strike prices in CENTER column (light gray text)
- [ ] GREEN bars extending LEFT from center (Calls)
- [ ] RED bars extending RIGHT from center (Puts)
- [ ] Bars are rounded rectangles (not sharp corners)
- [ ] One row highlighted (strike closest to current price)
- [ ] WHITE horizontal line across at current price

### ✅ Color Verification:
- [ ] Calls = GREEN (left side)
- [ ] Puts = RED (right side)
- [ ] NOT red on left or green on right (old bug)

### ✅ Bottom Axis:
- [ ] Symmetric numbers on both sides
- [ ] Left side: descending (8000, 6000, 4000, 2000, 0)
- [ ] Right side: ascending (0, 2000, 4000, 6000, 8000)
- [ ] Labels: "Call Volume" (left) and "Put Volume" (right)

---

## Step 6: Test Symbol Switching

Click each symbol button at the top:
- [ ] **SPY** - S&P 500 ETF
- [ ] **QQQ** - Nasdaq ETF
- [ ] **AAPL** - Apple stock
- [ ] **TSLA** - Tesla stock

**For each symbol, verify:**
- Data loads within 2-3 seconds
- Strike ladder updates
- Current price line moves
- Totals in header change
- Bars resize appropriately

---

## Step 7: Test Timeframe Selection

Click each timeframe button:
- [ ] **5min** - 5 minute window
- [ ] **10min** - 10 minute window
- [ ] **30min** - 30 minute window
- [ ] **60min** - 60 minute window

**Verify:**
- Data updates when switching
- Volume totals may change
- "Timespan: Xmin" indicator updates (bottom-right)

---

## Step 8: Test Live Data Mode

In Live Data mode (default):
- [ ] Green dot with "LIVE" text in top-right corner
- [ ] Data refreshes automatically every ~2 seconds
- [ ] Bars animate/update smoothly
- [ ] No lag or freezing

**Watch for 30 seconds:**
- Numbers should occasionally change
- Bars may grow/shrink slightly
- Current price may update

---

## Step 9: Test Historical Replay Mode

1. Click **"📅 Historical Replay"** button
2. Select a date from dropdown (e.g., Dec 27, 2025)
3. Set time to **09:30** (market open)
4. Click **▶ Play** button

**Verify:**
- Time advances automatically
- Strike ladder updates every second
- Can pause with **⏸ Pause** button
- Can change speed (0.5x, 1x, 2x)
- Stops automatically at 16:00 (market close)

---

## Step 10: Test P/C Ratio Indicator

In the footer (bottom-right area):
- [ ] P/C Ratio displayed (e.g., "1.25")
- [ ] Color changes based on value:
  - **Green** if P/C < 0.8 (Bullish - more calls)
  - **Red** if P/C > 1.2 (Bearish - more puts)
  - **Yellow** if 0.8 ≤ P/C ≤ 1.2 (Neutral)
- [ ] Emoji indicator: 🐂 Bullish / 🐻 Bearish / ⚖️ Neutral

---

## Step 11: Check Responsiveness (Optional)

1. Resize browser window:
   - [ ] **Wide (>1400px):** Full width ladder
   - [ ] **Medium (1000px):** Narrower bars, still readable
   - [ ] **Narrow (<800px):** Consider scrolling or stacked view

2. Zoom in/out (Ctrl + / Ctrl -):
   - [ ] SVG scales cleanly (no pixelation)
   - [ ] Text remains readable

---

## Step 12: Performance Check

Open browser **DevTools** (F12):

### Console Tab:
- [ ] No red errors
- [ ] Only info/debug messages (expected)

### Network Tab:
- [ ] Requests to `/api/monitor/SPY` every 2s (live mode)
- [ ] WebSocket connection established (ws://localhost:10000)
- [ ] Response times < 500ms

### Performance Tab (Optional):
- [ ] Record 10 seconds of live updates
- [ ] FPS stays above 30
- [ ] No memory leaks

---

## Step 13: Compare to Reference Image

Open the reference image (Mark Moses tool) side-by-side:

**Side-by-Side Comparison:**
- [ ] Layout matches (mirrored bars, center strikes)
- [ ] Colors match (green left, red right, black background)
- [ ] Proportions similar (bar widths, spacing)
- [ ] Information density comparable
- [ ] Professional appearance

**Notable Improvements in Our Version:**
- ✅ Web-based (no desktop install)
- ✅ Multi-symbol support (not just SPY)
- ✅ Historical replay feature
- ✅ Real-time WebSocket updates
- ✅ Authentication system
- ✅ Responsive design

---

## Troubleshooting

### Issue: Backend won't start
**Solution:**
```powershell
# Ensure virtual environment exists
python -m venv .venv
.\.venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
```

### Issue: Frontend shows errors
**Solution:**
```powershell
cd frontend
npm install
npm start
```

### Issue: No data loading
**Check:**
1. Backend running? (http://localhost:10000/api/health)
2. CORS errors in browser console?
3. API key valid? (check `start-backend.ps1`)
4. Symbol supported? (only SPY, QQQ, AAPL, TSLA)

### Issue: Colors wrong (red on left, green on right)
**Solution:**
- Hard refresh browser (Ctrl + Shift + R)
- Clear browser cache
- Restart frontend server

### Issue: White line not visible
**Possible causes:**
- Current price not within displayed strike range
- Strike data incomplete
- Check console for errors

---

## Success Criteria

✅ **Visual Match:** UI looks like Mark Moses' tool  
✅ **Functional:** All features work (live, historical, switching)  
✅ **Performance:** No lag, smooth updates  
✅ **Data Accuracy:** Numbers match backend API  
✅ **Colors Correct:** Calls=green, Puts=red  

If all checkboxes are ✅, the upgrade is successful!

---

## Next Steps (After Testing)

1. **Report any issues** found during testing
2. **Request additional features** if desired:
   - Tooltips on hover
   - Click to expand contract details
   - Export to image/PDF
   - Sound alerts for extreme P/C ratios
   - TradingView chart integration
3. **Deploy to production** (if testing passes)

---

## Quick Reference

| Component | URL | Port |
|-----------|-----|------|
| Backend API | http://localhost:10000 | 10000 |
| Frontend UI | http://localhost:3000 | 3000 |
| Health Check | http://localhost:10000/api/health | 10000 |

| Keyboard Shortcuts | Action |
|--------------------|--------|
| Ctrl + R | Refresh data |
| 1-4 | Switch symbols (SPY/QQQ/AAPL/TSLA) |
| Tab | Cycle through timeframes |
| F12 | Open DevTools |

| Data Provider | Status |
|---------------|--------|
| Insight Sentry | ✅ Configured |
| API Key | ✅ In start-backend.ps1 |
| Symbols Limit | 4 (SPY, QQQ, AAPL, TSLA) |
| Rate Limits | 5 symbols, 1 WebSocket |

---

**Testing Date:** January 14, 2026  
**Version:** 2.0 (Mirrored Strike Ladder UI)  
**Status:** Ready for testing
