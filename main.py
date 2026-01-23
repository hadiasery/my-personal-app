import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

# --- 1. إعدادات التنبيه ---
TOKEN = "7566263341:AAHadbOMY8BLpQgTj9eujY52mnKQxuawZjY"
CHAT_ID = "692583333"

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID, "text": text}, timeout=5)
    except: pass

st_autorefresh(interval=120000, key="mega_radar_v5")

st.set_page_config(page_title="رادار هادي العملاق", layout="wide")
st.markdown("<h1 style='text-align: center; color: #D32F2F;'>🚀 رادار القناص: Call & Put (القائمة الموسعة)</h1>", unsafe_allow_html=True)

# --- 2. القائمة الموسعة (18 شركة + المؤشر) ---
STOCKS = {
    '📈 مؤشر S&P 500': '^GSPC',
    'أبل': 'AAPL', 'نيفيديا': 'NVDA', 'تسلا': 'TSLA', 'مايكروسوفت': 'MSFT', 
    'أمازون': 'AMZN', 'ميتا (Facebook)': 'META', 'غوغل': 'GOOGL', 'نتفليكس': 'NFLX',
    'AMD': 'AMD', 'إنتل': 'INTC', 'لوسيد': 'LCID', 'نيو': 'NIO', 'بالانتير': 'PLTR',
    'كوين بيز': 'COIN', 'شوبيفاي': 'SHOP', 'مودرنا': 'MRNA', 'ديزني': 'DIS'
}

results = []
my_bar = st.progress(0)

# --- 3. التحليل الفني ---
for i, (name, sym) in enumerate(STOCKS.items()):
    try:
        data = yf.download(sym, period='7d', interval='5m', progress=False)
        if not data.empty and len(data) > 30:
            data = data.ffill().bfill()
            close_prices = data['Close'].squeeze()
            volumes = data['Volume'].squeeze()
            curr_p = float(close_prices.iloc[-1])
            
            # المؤشرات
            rsi_val = float(ta.rsi(close_prices, length=14).iloc[-1])
            sma_5 = float(ta.sma(close_prices, length=5).iloc[-1])
            sma_13 = float(ta.sma(close_prices, length=13).iloc[-1])
            macd_h = float(ta.macd(close_prices)['MACDh_12_26_9'].iloc[-1])
            
            # حماية (قمة وقاع سابقة)
            prev_high = float(data['High'].squeeze().iloc[-2])
            prev_low = float(data['Low'].squeeze().iloc[-2])
            
            # قوة الانفجار
            vol_ratio = volumes.iloc[-1] / volumes.rolling(window=10).mean().iloc[-1]
            explosion = "🔥 عالية" if vol_ratio > 1.5 else "⚠️ عادية" if vol_ratio > 1.0 else "❄️ ضعيفة"

            status, color = "⚪ انتظار", "transparent"
            
            # منطق الـ Call
            if rsi_val < 35:
                if (curr_p > prev_high) and (sma_5 > sma_13) and (macd_h > 0):
                    status, color = "🔵 دخول Call مؤكد", "#0D47A1"
                    send_msg(f"🚀 Call Signal: {name} at {curr_p:.2f}")
                else: status, color = "🟢 مراقبة Call", "#2E7D32"

            # منطق الـ Put
            elif rsi_val > 65:
                if (curr_p < prev_low) and (sma_5 < sma_13) and (macd_h < 0):
                    status, color = "🔴 دخول Put مؤكد", "#B71C1C"
                    send_msg(f"📉 Put Signal: {name} at {curr_p:.2f}")
                else: status, color = "🟠 مراقبة Put", "#E65100"
                
            results.append({"الأداة": name, "الحالة": status, "السعر": f"{curr_p:.2f}", "الانفجار": explosion, "RSI": round(rsi_val, 1), "الاتجاه": "📈 صاعد" if macd_h > 0 else "📉 هابط", "_color": color})
    except: continue
    my_bar.progress((i + 1) / len(STOCKS))

# --- 4. العرض ---
if results:
    df = pd.DataFrame(results)
    def apply_style(row):
        return [f'background-color: {row["_color"]}; color: white; font-weight: bold' if row['_color'] != "transparent" else '' for _ in row]
    
    st.dataframe(df.style.apply(apply_style, axis=1), column_order=("الأداة", "الحالة", "السعر", "الانفجار", "RSI", "الاتجاه"), use_container_width=True, hide_index=True, height=600)

st.caption("نظام القناص المطور V5 - يعمل الآن على 18 شركة ومؤشر رئيسي.")
