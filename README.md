# NQ Opening Range Breakout (ORB) Quantitative Analysis

This repository contains a robust **Python** backtesting script designed to analyze the **Opening Range Breakout (ORB)** strategy on the **Nasdaq-100 (NQ)** index. 

The script implements a specific **Global Trend Filter** and a **Double Candle Confirmation** mechanism to mitigate false signals common during New York market open volatility.

---

## 🛠 Strategy Overview

The script automates the analysis of M5 historical data based on the following rules:

### 1. Trend Bias (Contextual Filter)
* **Lookback:** Analyzes the 12 hours preceding the New York open (09:30 ET).
* **Logic:** The price at 09:30 must be situated outside the 12-hour structure midpoint (Mid) to validate a `BULL` or `BEAR` bias. If the price remains within the previous range's equilibrium, the day is categorized as `NEUTRAL` and no trades are initiated.

### 2. Opening Range (Trigger)
* **Reference Window:** 09:30 - 09:45 ET.
* **Confirmation:** The price must break out of the initial 15-minute range.
* **Double Close Rule:** To filter out high-volatility wicks and "fakeouts," this setup requires two consecutive M5 candles to close outside the range boundaries.

### 3. Risk Management
* **Risk/Reward (R:R):** Fixed at **1.5**.
* **Stop Loss (SL):** Placed at the opposite side of the Opening Range (09:30-09:45).
* **Time Exit:** A hard exit is enforced at 16:00 ET if neither the target nor the stop loss has been reached.

---

## 📈 Performance Metrics (NQ - Last 12 Months)

Based on historical M5 data, the strategy yields the following performance metrics:

| Metric | Result |
| :--- | :--- |
| **Win Rate** | **48.00%** |
| **Risk/Reward** | **1.5** |
| **Expectancy** | **+0.20 R / trade** |
| **Profit Factor** | **1.38** |
| **Trade Frequency** | ~10 trades / month |

---

## 🚀 Getting Started

### Prerequisites
* Python 3.x
* Pandas library

### Installation
1. Clone the repository to your local machine.
2. Ensure your data file (`NQ_M5_Last_12_Months.csv`) is in the root directory.
3. Install the required dependencies:
   ```bash
   pip install pandas
