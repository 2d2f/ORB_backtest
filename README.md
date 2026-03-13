# NQ Opening Range Breakout (ORB) Quantitative Analysis

This repository contains a professional-grade **Python** backtesting engine designed to analyze and optimize the **Opening Range Breakout (ORB)** strategy on the **Nasdaq-100 (NQ)** index.

The project features a **12-hour momentum filter** and a **Sensitivity Analysis** module to determine the optimal Stop Loss placement relative to market volatility.

---

## Strategy Logic

The algorithm processes M5 historical data using a multi-step verification process:

### 1. Contextual Trend Filter
* **Lookback:** 4 to 12 hours (Optimized at **4h** for intraday momentum).
* **Bias:** The price at 09:30 ET must be outside the structure's midpoint to confirm a `BULL` or `BEAR` bias. Neutral days are discarded to avoid "choppy" price action.

### 2. Execution & Trigger
* **Opening Range:** 09:30 - 09:45 ET.
* **Double Confirmation:** Requires two consecutive M5 closes outside the range to filter out liquidity sweeps (fakeouts).
* **Target:** Fixed Risk/Reward ratio of **1.5**.

---

## Parameter Optimization (Sensitivity Analysis)

We conducted a comparative study on **Stop Loss (SL) placement** to balance Win Rate and capital protection. The results clearly identify the **100% Range SL** as the most robust configuration.

| SL Percentage | Win Rate | Expectancy (R) | Expectancy (Pts) | Max Drawdown |
| :--- | :--- | :--- | :--- | :--- |
| 25% of Range | 41.67% | 0.04 R | 1.98 pts | -13.00 R |
| 50% of Range | 44.17% | 0.11 R | 5.20 pts | -9.85 R |
| 75% of Range | 49.17% | 0.17 R | 10.52 pts | -9.29 R |
| **100% (Optimal)** | **50.00%** | **0.17 R** | **13.98 pts** | **-7.47 R** |

### Key Findings:
* **Volatility Buffer:** Tightening the SL (25-50%) significantly increases the Max Drawdown due to "market noise" on NQ.
* **Robustness:** The 100% SL setup offers the lowest Drawdown and the highest expectancy in points, providing a safer cushion against slippage.

---

## Final Performance Summary (100% SL Setup)

| Metric | Result |
| :--- | :--- |
| **Total Trades** | 120 |
| **Win Rate** | **50.00%** |
| **Profit Factor** | **1.44** |
| **Expectancy** | **+0.17 R / trade** |
| **Max Drawdown** | **-7.47 R** |
