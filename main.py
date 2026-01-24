import pandas as pd
import yfinance as yf
import time
import streamlit as st

# قائمة الشركات بعد الحذف
tickers = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'AMD']

st.set_page_config(page_title="رادار القناص", layout="wide")
placeholder = st.empty()

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
            color = "black"
            vol_color = "white"
            
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
                'Ticker': ticker, 'Price': round(current_price, 2),
                'Change': round(current_price - prev_price, 2),
                'Volume Ratio': round(vol_ratio, 2),
                'Signal': status, 'color': color, 'vol_color': vol_color
            })
        except: continue
    return data_list

# حلقة العرض الخاصة بـ Streamlit لتعمل بدون أخطاء
while True:
    data = get_live_data(tickers)
    with placeholder.container():
        html = """
        <style>
            .radar-table { width: 100%; border-collapse: collapse; font-family: Arial; background-color: white; color: black; }
            .radar-table th { background-color: #f2f2f2; padding: 10px; border: 1px solid #ddd; }
            .radar-table td { padding: 10px; border: 1px solid #ddd; text-align: center; font-weight: bold; }
        </style>
        <table class="radar-table">
            <tr><th>Ticker</th><th>Price</th><th>Change</th><th>Vol Ratio</th><th>Action</th></tr>
        """
        for row in data:
            html += f"""
            <tr style="color: {row['color']};">
                <td>{row['Ticker']}</td><td>{row['Price']}</td><td>{row['Change']}</td>
                <td style="background-color: {row['vol_color']};">{row['Volume Ratio']}x</td>
                <td style="border: 2px solid {row['color']};">{row['Signal']}</td>
            </tr>
            """
        html += "</table>"
        st.markdown(html, unsafe_allow_html=True)
        st.write(f"آخر تحديث: {time.strftime('%H:%M:%S')}")
    time.sleep(10)
