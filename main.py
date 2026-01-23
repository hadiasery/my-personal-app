import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import time

# تحديث تلقائي كل 10 ثوانٍ لمواكبة عقود الأوبشن السريعة
st_autorefresh(interval=10000, key="mega_spx_radar_v9_counter")

st.set_page_config(page_title="رادار هادي V9 - نسخة العداد", layout="wide")

# --- إضافة عداد الثواني البصري في الأعلى ---
placeholder = st.empty()
with placeholder.container():
    st.markdown(f"""
        <div style="background-color: #1e1e1e; padding: 10px; border-radius: 10px; border: 1px solid #333; text-align: center; margin-bottom: 20px;">
            <span style="color: white; font-size: 18px;">🔄 تحديث البيانات القادم خلال: </span>
            <span style="color: #CCFF00; font-size: 24px; font-weight: bold;">10 ثوانٍ</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: white; background: linear-gradient(to right, #1e3c72, #2a5298); padding: 15px; border-radius: 10px;'>🚀 رادار القناص: SPX والأسهم (V9 + عداد)</h1>", unsafe_allow_html=True)

# --- قائمة الأسهم المختارة ---
STOCKS = {
    '📊 مؤشر سباكس (SPY/SPX)': 'SPY', 
    'أبل (Apple)': 'AAPL', 
    'نيفيديا (Nvidia)': 'NVDA', 
    'تسلا (Tesla)': 'TSLA', 
    'مايكروسوفت (Microsoft)': 'MSFT', 
    'أمازون (Amazon)': 'AMZN', 
    'ميتا (Meta)': 'META', 
    'غوغل (Google)': 'GOOGL', 
    'AMD (AMD)': 'AMD', 
    'بالانتير (Palantir)': 'PLTR'
}

results = []
my_bar = st.progress(0)

# --- محرك التحليل الفني ---
for i, (name, sym) in enumerate(STOCKS.items()):
    try:
        data = yf.download(sym, period='2d', interval='1m', progress=False)
        if not data.empty and len(data) > 20:
            data = data.ffill().bfill()
            close_p = data['Close'].squeeze()
            volumes = data['Volume'].squeeze()
            curr_p = float(close_p.iloc[-1])
            
            # المؤشرات الفنية
            rsi_val = float(ta.rsi(close_p, length=14).iloc[-1])
            sma_5 = float(ta.sma(close_p, length=5).iloc[-1])
            sma_13 = float(ta.sma(close_p, length=13).iloc[-1])
            macd = ta.macd(close_p)
            macd_h = float(macd['MACDh_12_26_9'].iloc[-1])
            
            # حماية الاختراق
            prev_high = float(data['High'].squeeze().iloc[-2])
            prev_low = float(data['Low'].squeeze().iloc[-2])
            
            # قوة السيولة
            avg_vol = volumes.rolling(window=10).mean().iloc[-1]
            vol_ratio = volumes.iloc[-1] / avg_vol
            is_explosion = vol_ratio > 1.2

            status, color = "⚪ هدوء", "transparent"
            
            # منطق الألوان (V9)
            if rsi_val < 35: status, color = "🟢 مراقبة Call", "#2E7D32"
            elif rsi_val > 65: status, color = "🟠 مراقبة Put", "#E65100"

            if is_explosion: status, color = "⚡ انفجار سيولة", "#CCFF00"
            
            if (curr_p > prev_high) and (sma_5 > sma_13) and (macd_h > 0):
                status, color = "🔵 دخول Call مؤكد", "#0D47A1"
            elif (curr_p < prev_low) and (sma_5 < sma_13) and (macd_h < 0):
                status, color = "🔴 دخول Put مؤكد", "#B71C1C"

            results.append({
                "الأداة": name, "الحالة": status, "السعر": f"{curr_p:.2f}",
                "قوة السيولة": f"{vol_ratio:.2f}x", "RSI": int(rsi_val),
                "الاتجاه": "📈 صاعد" if macd_h > 0 else "📉 هابط", "_color": color
            })
    except: continue
    my_bar.progress((i + 1) / len(STOCKS))

# --- العرض ---
if results:
    df = pd.DataFrame(results)
    def apply_style(row):
        txt_color = "black" if row['_color'] == "#CCFF00" else "white"
        if row['_color'] != "transparent":
            return [f'background-color: {row["_color"]}; color: {txt_color}; font-weight: bold'] * len(row)
        return [''] * len(row)
    
    st.table(df.drop(columns=['_color'])) # استخدام table لضمان الاستقرار في التحديث السريع

st.sidebar.info("العداد في الأعلى يخبرك متى سيتم تحديث الأسعار والسيولة تلقائياً.")
