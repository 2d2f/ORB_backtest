# NQ Opening Range Breakout - Quantitative Analysis

## Overview

This repository contains a quantitative trading framework designed for the Nasdaq-100 (NQ) index. The project demonstrates the evolution of a trading strategy from a basic price-action model to an optimized, volatility-adjusted system.

The strategy focuses on the 15-minute Opening Range (09:30 - 09:45 ET) and uses a combination of directional bias and volatility filters to identify high-probability breakouts.

## Methodology

The final model utilizes three distinct layers of filtering to ensure statistical robustness:

### 1. Pre-Market Directional Bias
The strategy analyzes price action during the 60-minute window prior to the New York open (08:30 - 09:30 ET). This specific lookback period was identified through brute-force testing as the most effective for capturing institutional reactions to high-impact economic news releases.

### 2. Volatility Normalization (ATR Filter)
To adapt to changing market regimes, the Opening Range is compared to the 14-day Average True Range (ATR).
* Minimum Threshold (0.20): Trades are ignored if the range is too narrow, filtering out low-momentum market noise.
* Maximum Threshold (0.50): Trades are ignored if the range is too wide, preventing entries into potentially exhausted trends.

### 3. Trade Management
* Entry: Stop order on a 5-minute candle close outside the Opening Range.
* Stop Loss: Fixed at 100% of the Opening Range to account for Nasdaq volatility.
* Take Profit: Set at a 1.5 Risk/Reward ratio.
* Time Exit: Any open positions are liquidated at 16:00 ET (Market Close).

## Performance Results

The following metrics were achieved over a 12-month backtesting period on 5-minute NQ data.

| Metric | Result |
| :--- | :--- |
| Total Trades | 82 |
| Win Rate | 56.10% |
| Expectancy | 0.30 R / trade |
| Total Return | 24.85 R |
| Risk/Reward Ratio | 1.5 |

These results represent a "Champion" configuration identified through a sensitivity analysis of 300+ parameter combinations.

## Installation and Usage

### Prerequisites
* Python 3.x
* Pandas
* NumPy

### Execution
1. Clone the repository to your local machine.
2. Ensure your data file is named NQ_M5_Last_12_Months.csv and placed in the root directory.
3. Run the analysis script:
   python3 orb_strategy.py

## Disclaimer
Trading involves significant risk. This project is for educational and research purposes only. Past performance is not indicative of future results.
