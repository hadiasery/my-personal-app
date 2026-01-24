import pandas as pd
import yfinance as yf
import time
from IPython.display import clear_output, display

# --- قائمة الأسهم المحدثة حسب طلبك ---
tickers = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'AMD']

def get_live_data(ticker_list):
    data_list = []
    for ticker in ticker_list:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period='2d', interval='1m')
            
            if df.empty: continue
            
            current_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2]
            high_price = df['High'].iloc[-2]
            low_price = df['Low'].iloc[-2]
            volume = df['Volume'].iloc[-1]
            avg_volume = df['Volume'].mean()
            
            exp1 = df['Close'].ewm(span=12, adjust=False).mean()
            exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            
            status = "WAIT"
            color = "white"
            vol_color = "black"
            
            if current_price > high_price and macd.iloc[-1] > signal.iloc[-1]:
                status = "CALL (Buy)"
                color = "blue"
            elif current_price < low_price and macd.iloc[-1] < signal.iloc[-1]:
                status = "PUT (Sell)"
                color = "red"
            
            vol_ratio = volume / avg_volume
            if vol_ratio > 1.5:
                vol_color = "#CCFF00" 
                
            data_list.append({
                'Ticker': ticker,
                'Price': round(current_price, 2),
                'Change': round(current_price - prev_price, 2),
                'Volume Ratio': round(vol_ratio, 2),
                'Signal': status,
                'color': color,
                'vol_color': vol_color
            })
        except:
            continue
    return data_list

def display_radar(data):
    html = """
    <style>
        .radar-table { width: 100%; border-collapse: collapse; font-family: Arial; background-color: white; }
        .radar-table th { background-color: #f2f2f2; padding: 10px; border: 1px solid #ddd; }
        .radar-table td { padding: 10px; border: 1px solid #ddd; text-align: center; font-weight: bold; }
    </style>
    <table class="radar-table">
        <tr>
            <th>Ticker</th><th>Price</th><th>Change</th><th>Vol Ratio</th><th>Action</th>
        </tr>
    """
    for row in data:
        html += f"""
        <tr style="color: {row['color']};">
            <td>{row['Ticker']}</td>
            <td>{row['Price']}</td>
            <td>{row['Change']}</td>
            <td style="background-color: {row['vol_color']}; color: black;">{row['Volume Ratio']}x</td>
            <td style="border: 2px solid {row['color']};">{row['Signal']}</td>
        </tr>
        """
    html += "</table>"
    display({'text/html': html}, raw=True)

print("🚀 رادار القناص يعمل الآن بنفس النظام الأصلي...")
try:
    while True:
        live_data = get_live_data(tickers)
        clear_output(wait=True)
        display_radar(live_data)
        print(f"\nآخر تحديث: {time.strftime('%H:%M:%S')}")
        time.sleep(10)
except KeyboardInterrupt:
    print("\nتم إيقاف الرادار.")
