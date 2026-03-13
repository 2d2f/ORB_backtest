import pandas as pd
import numpy as np

# =============================================================================
# 1. OPTIMIZED CONFIGURATION (CHAMPION PARAMETERS)
# =============================================================================
FILE_PATH = 'NQ_M5_Last_12_Months.csv'
RISK_REWARD = 1.5

# After Brute Force testing, LB 1.0h (Pre-Market News window) 
# and AL 0.20 (Quality Filter) provided the highest stability.
TREND_LOOKBACK_HOURS = 1.0 
SL_RANGE_PERCENT = 1.0 

# VOLATILITY FILTERS (ATR-BASED)
ATR_PERIOD = 14
ATR_MULTIPLIER_LOW = 0.20   # High-quality signal threshold
ATR_MULTIPLIER_HIGH = 0.50  # Avoids exhausted market conditions

def run_final_strategy():
    """
    Final optimized NQ ORB Strategy.
    Expectancy: 0.30 R | Win Rate: 56.10%
    """
    print("--- Running Champion ORB Strategy (NQ) ---")
    
    try:
        df = pd.read_csv(FILE_PATH)
    except FileNotFoundError:
        print(f"Error: {FILE_PATH} not found.")
        return

    df['Time'] = pd.to_datetime(df['Time'])
    df.sort_values('Time', inplace=True)
    df['Date'] = df['Time'].dt.date
    
    # 0. Daily ATR Calculation
    daily_df = df.groupby('Date').agg({'High': 'max', 'Low': 'min', 'Close': 'last'})
    daily_df['Prev_Close'] = daily_df['Close'].shift(1)
    daily_df['TR'] = np.maximum(daily_df['High'] - daily_df['Low'], 
                     np.maximum(abs(daily_df['High'] - daily_df['Prev_Close']), 
                                abs(daily_df['Low'] - daily_df['Prev_Close'])))
    daily_df['ATR'] = daily_df['TR'].rolling(window=ATR_PERIOD).mean()
    
    dates = df['Date'].unique()
    results = []
    
    for d in dates:
        if d not in daily_df.index or pd.isna(daily_df.loc[d, 'ATR']): continue
        current_atr = daily_df.loc[d, 'ATR']

        # 1. Trend Filter (1.0h Lookback)
        t_0930 = pd.to_datetime(f"{d} 09:30:00")
        t_start = t_0930 - pd.Timedelta(hours=TREND_LOOKBACK_HOURS)
        bias_window = df[(df['Time'] >= t_start) & (df['Time'] < t_0930)]
        if len(bias_window) < 3: continue
            
        mid_point = (bias_window['High'].max() + bias_window['Low'].min()) / 2
        price_start = bias_window.iloc[0]['Open']
        price_0930 = df.loc[df['Time'] == t_0930, 'Open'].values[0]
        
        trend = 'BULL' if price_0930 > price_start and price_0930 > mid_point else \
                'BEAR' if price_0930 < price_start and price_0930 < mid_point else 'NEUTRAL'
        if trend == 'NEUTRAL': continue
            
        # 2. Opening Range & Volatility Filter
        orb_data = df[(df['Time'] >= t_0930) & (df['Time'] < pd.to_datetime(f"{d} 09:45:00"))]
        if len(orb_data) < 3: continue 
        o_h, o_l = orb_data['High'].max(), orb_data['Low'].min()
        range_size = o_h - o_l
        
        if range_size < (current_atr * ATR_MULTIPLIER_LOW) or range_size > (current_atr * ATR_MULTIPLIER_HIGH):
            continue

        # 3. Entry Trigger
        t_1100 = pd.to_datetime(f"{d} 11:00:00")
        trigger_window = df[(df['Time'] >= pd.to_datetime(f"{d} 09:45:00")) & (df['Time'] <= t_1100)]
        entry_p, entry_t = None, None
        
        for _, c in trigger_window.iterrows():
            if (trend == 'BULL' and c['Close'] > o_h) or (trend == 'BEAR' and c['Close'] < o_l):
                idx = df[df['Time'] == c['Time']].index[0]
                if idx + 1 < len(df):
                    entry_p, entry_t = df.loc[idx+1, 'Open'], df.loc[idx+1, 'Time']
                break
        if not entry_t: continue
            
        # 4. Management & Time Exit (16:00)
        risk = (entry_p - o_l) if trend == 'BULL' else (o_h - entry_p)
        sl = o_l if trend == 'BULL' else o_h
        tp = (entry_p + RISK_REWARD * risk) if trend == 'BULL' else (entry_p - RISK_REWARD * risk)
        
        trade_data = df[(df['Time'] >= entry_t) & (df['Time'] <= pd.to_datetime(f"{d} 16:00:00"))]
        outcome, pnl_r = 'TIME', 0
        
        for _, c in trade_data.iterrows():
            if (trend == 'BULL' and c['Low'] <= sl) or (trend == 'BEAR' and c['High'] >= sl):
                outcome, pnl_r = 'LOSS', -1; break
            if (trend == 'BULL' and c['High'] >= tp) or (trend == 'BEAR' and c['Low'] <= tp):
                outcome, pnl_r = 'WIN', RISK_REWARD; break
        
        if outcome == 'TIME' and not trade_data.empty:
            exit_p = trade_data.iloc[-1]['Close']
            pts = (exit_p - entry_p) if trend == 'BULL' else (entry_p - exit_p)
            pnl_r = pts / risk
                    
        results.append({'Date': d, 'PnL_R': pnl_r})

    res_df = pd.DataFrame(results)
    print(f"\nTotal Trades: {len(res_df)}")
    print(f"Win Rate:     {(len(res_df[res_df['PnL_R'] > 0])/len(res_df))*100:.2f}%")
    print(f"Expectancy:   {res_df['PnL_R'].mean():.3f} R")
    print(f"Total Profit: {res_df['PnL_R'].sum():.2f} R")

if __name__ == "__main__":
    run_final_strategy()
