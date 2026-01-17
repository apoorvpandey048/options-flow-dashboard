# Debug Instructions - Strike Ladder Issues

## Current Status

✅ **Backend**: Running on http://localhost:10000  
✅ **Frontend**: Running on http://localhost:3000  
✅ **Compilation**: Successful (only unused variable warnings)

## Issues to Investigate

1. **White horizontal line not visible**
2. **Current price not showing**
3. **Only ~10 strikes total visible instead of 21 (10 above + median + 10 below)**

## How to Debug

### Step 1: Open Browser DevTools

1. Open http://localhost:3000 in your browser
2. Press **F12** to open DevTools
3. Click on the **Console** tab

### Step 2: Check Debug Output

You should see console output like this:

```javascript
Debug: {
  currentPrice: 456.78,
  closestStrikeIndex: 15,
  totalStrikes: 41,
  visibleCount: 21,
  medianIndexInVisible: 10,
  medianStrike: 456.5
}
```

**Check these values:**

- `totalStrikes`: Should be ≥21 (at least 21 strikes from backend)
- `visibleCount`: Should be 21 (10 above + median + 10 below)
- `medianIndexInVisible`: Should be around 10 (middle of 21 strikes)
- `currentPrice` vs `medianStrike`: Should be very close

### Step 3: Inspect SVG Elements

1. In DevTools, click the **Elements** tab
2. Press **Ctrl+F** and search for: `<line`
3. Look for a line with `stroke="#ffffff"` (white color)
4. Check if:
   - The line element exists
   - The `y1` and `y2` values are reasonable (not 0 or negative)
   - The `opacity` is set to 0.9

### Step 4: Check Visible Strikes

Count the visible strike prices in the center column. Should be **21 total**.

## Expected Behavior

### ✅ Correct State:
- 21 strike prices visible (10 above current, current price, 10 below)
- White horizontal line crossing the entire width at the current price
- P/C Ratio pill above the white line showing:
  - Symbol price: $XXX.XX
  - P/C: X.XX
  - Sentiment (🐂 Bullish / 🐻 Bearish / ⚖️ Neutral)

### ❌ Current Issues:
- White line not rendering or not visible
- P/C ratio pill not visible
- Only ~10 strikes instead of 21

## Possible Root Causes

1. **Backend Data Insufficient**: Backend returns < 21 strikes total
   - Check `totalStrikes` in console
   - If < 21, backend needs to fetch more strike prices

2. **Median Detection Failing**: `medianIndexInVisible === -1`
   - Check console output
   - Fallback rendering should show line at center even if -1

3. **SVG Rendering Issue**: Element exists but not visible
   - Z-index problem (covered by other elements)
   - Y-position calculated incorrectly
   - Opacity too low
   - Line outside visible SVG area

4. **Window Size Calculation**: `visibleStrikes.length !== 21`
   - Check if `startIdx` and `endIdx` are correct
   - Verify `closestStrikeIndex` is finding the right strike

## Next Steps

**Please share:**
1. The console debug output showing the values
2. Screenshot showing only ~10 strikes visible
3. Whether the white line appears (even partially)
4. Browser DevTools Elements tab showing the `<line>` element (if it exists)

This will help identify whether the issue is:
- **Backend** (not enough data)
- **Calculation** (wrong window selection)
- **Rendering** (SVG element not displaying)
