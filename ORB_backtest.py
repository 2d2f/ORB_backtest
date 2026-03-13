import pandas as pd

# ==========================================
# 1. CONFIGURATION
# ==========================================
FILE_PATH = 'NQ_M5_Last_12_Months.csv'
RISK_REWARD = 1.5
TREND_LOOKBACK_HOURS = 4

# ---> MODIFY THE STOP LOSS VALUE HERE <---
# Replace the value with the desired percentage of the range:
# 1.0  = 100% (Classic SL, placed on the opposite side of the range)
# 0.75 = 75%  (SL is at 3/4 of the range)
# 0.50 = 50%  (SL is placed exactly in the middle of the range)
# 0.25 = 25%  (Very tight SL, close to the breakout point)
SL_RANGE_PERCENT = 0.25

def run_orb_backtest():
    print(f"Loading data for ORB analysis ({TREND_LOOKBACK_HOURS}h Trend, SL at {SL_RANGE_PERCENT*100}% of Range)...")
    df = pd.read_csv(FILE_PATH)
    df['Time'] = pd.to_datetime(df['Time'])
    df.sort_values('Time', inplace=True)
    df['Date'] = df['Time'].dt.date
    
    dates = df['Date'].unique()
    results = []
    
    print("Analyzing trend, breakouts, and dynamic Stop Loss...\n")
    
    for d in dates:
        # ---------------------------------------------
        # STEP 1: TREND FILTER (Previous 12h)
        # ---------------------------------------------
        t_0930 = pd.to_datetime(f"{d} 09:30:00")
        t_minus_12 = t_0930 - pd.Timedelta(hours=TREND_LOOKBACK_HOURS)
        
        past_12h = df[(df['Time'] >= t_minus_12) & (df['Time'] < t_0930)]
        if len(past_12h) < 20: 
            continue
            
        high_12 = past_12h['High'].max()
        low_12 = past_12h['Low'].min()
        mid_12 = (high_12 + low_12) / 2
        
        price_t12 = past_12h.iloc[0]['Open']
        
        c_0930 = df.loc[df['Time'] == t_0930]
        if c_0930.empty: continue
        price_0930 = c_0930.iloc[0]['Open']
        
        trend = 'NEUTRAL'
        if price_0930 > price_t12 and price_0930 > mid_12:
            trend = 'BULL'
        elif price_0930 < price_t12 and price_0930 < mid_12:
            trend = 'BEAR'
            
        if trend == 'NEUTRAL': 
            continue
            
        # ---------------------------------------------
        # STEP 2: OPENING RANGE (09:30 - 09:45)
        # ---------------------------------------------
        t_0945 = pd.to_datetime(f"{d} 09:45:00")
        orb_data = df[(df['Time'] >= t_0930) & (df['Time'] < t_0945)]
        
        if len(orb_data) < 3: continue 
            
        orb_high = orb_data['High'].max()
        orb_low = orb_data['Low'].min()
        range_size = orb_high - orb_low # Calculate the total size of the range
        
        # ---------------------------------------------
        # STEP 3: TRIGGER (Breakout between 09:45 and 11:00)
        # ---------------------------------------------
        t_1100 = pd.to_datetime(f"{d} 11:00:00")
        trigger_window = df[(df['Time'] >= t_0945) & (df['Time'] <= t_1100)]
        
        trigger = None
        entry_price = 0
        entry_time = None
        
        for _, candle in trigger_window.iterrows():
            if trend == 'BULL' and candle['Close'] > orb_high:
                trigger = 'LONG'
                idx = df[df['Time'] == candle['Time']].index[0]
                if idx + 1 < len(df):
                    entry_price = df.loc[idx + 1, 'Open']
                    entry_time = df.loc[idx + 1, 'Time']
                break
                
            elif trend == 'BEAR' and candle['Close'] < orb_low:
                trigger = 'SHORT'
                idx = df[df['Time'] == candle['Time']].index[0]
                if idx + 1 < len(df):
                    entry_price = df.loc[idx + 1, 'Open']
                    entry_time = df.loc[idx + 1, 'Time']
                break
                
        if not trigger or entry_time is None: 
            continue
            
        # ---------------------------------------------
        # STEP 4: DYNAMIC TRADE MANAGEMENT
        # ---------------------------------------------
        # Calculate Stop Loss based on the defined percentage of the range
        if trigger == 'LONG':
            sl = orb_high - (range_size * SL_RANGE_PERCENT)
            risk = entry_price - sl
            if risk <= 0: continue
            tp = entry_price + (RISK_REWARD * risk)
        else:
            sl = orb_low + (range_size * SL_RANGE_PERCENT)
            risk = sl - entry_price
            if risk <= 0: continue
            tp = entry_price - (RISK_REWARD * risk)
            
        t_1600 = pd.to_datetime(f"{d} 16:00:00")
        trade_data = df[(df['Time'] >= entry_time) & (df['Time'] <= t_1600)]
        
        outcome = 'TIME'
        pnl_r = 0
        pnl_pts = 0
        
        for _, candle in trade_data.iterrows():
            if trigger == 'LONG':
                if candle['Low'] <= sl: 
                    outcome = 'LOSS'
                    pnl_r = -1
                    pnl_pts = -risk
                    break
                elif candle['High'] >= tp:
                    outcome = 'WIN'
                    pnl_r = RISK_REWARD
                    pnl_pts = RISK_REWARD * risk
                    break
            else:
                if candle['High'] >= sl:
                    outcome = 'LOSS'
                    pnl_r = -1
                    pnl_pts = -risk
                    break
                elif candle['Low'] <= tp:
                    outcome = 'WIN'
                    pnl_r = RISK_REWARD
                    pnl_pts = RISK_REWARD * risk
                    break
        
        if outcome == 'TIME' and not trade_data.empty:
            exit_price = trade_data.iloc[-1]['Close']
            if trigger == 'LONG':
                pnl_pts = exit_price - entry_price
            else:
                pnl_pts = entry_price - exit_price
            pnl_r = pnl_pts / risk
            outcome = 'WIN' if pnl_pts > 0 else 'LOSS'
                    
        results.append({
            'Date': d,
            'Trend': trend,
            'Trigger': trigger,
            'Outcome': outcome,
            'PnL_R': pnl_r,
            'PnL_Pts': pnl_pts
        })

    # ==========================================
    # 5. METRICS CALCULATION
    # ==========================================
    res_df = pd.DataFrame(results)
    
    if res_df.empty:
        print("No trades met all the criteria.")
        return
        
    total_trades = len(res_df)
    wins = len(res_df[res_df['PnL_R'] > 0])
    losses = total_trades - wins
    win_rate = (wins / total_trades) * 100
    
    expectancy_pts = res_df['PnL_Pts'].mean()
    expectancy_r = res_df['PnL_R'].mean()
    
    res_df['Cum_R'] = res_df['PnL_R'].cumsum()
    res_df['High_Water_Mark'] = res_df['Cum_R'].cummax()
    res_df['Drawdown'] = res_df['Cum_R'] - res_df['High_Water_Mark']
    max_dd_r = res_df['Drawdown'].min()

    print(f"=== ORB PERFORMANCE REPORT (SL: {SL_RANGE_PERCENT*100}% of Range) ===")
    print(f"Total Trades : {total_trades}")
    print(f"Wins : {wins} | Losses : {losses}")
    print(f"Win Rate : {win_rate:.2f}%")
    print(f"Expectancy (Points) : {expectancy_pts:.2f} Pts / Trade")
    print(f"Expectancy (R) : {expectancy_r:.2f} R / Trade")
    print(f"Max Drawdown : {max_dd_r:.2f} R")
    
    res_df.to_csv('ORB_Dynamic_SL_Results.csv', index=False)
    print("\nAll trades have been saved to 'ORB_Dynamic_SL_Results.csv'.")

if __name__ == "__main__":
    run_orb_backtest()
