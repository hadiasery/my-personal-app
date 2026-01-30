import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث كل 10 ثواني
st_autorefresh(interval=10000, key="v42_steel_version")

st.set_page_config(page_title="رادار القناص V42.2", layout="wide")

# تصميم الألوان والخطوط (أبيض بالكامل)
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    .big-font { font-size: 25px !important; font-weight: 900 !important; color: black !important; text-align: center; }
    .header-box { background-color: #1e293b; color: white; padding: 10px; text-align: center; font-size: 20px; font-weight: bold; border: 2px solid black; }
    .data-row-green { background-color: #22c55e; padding: 15px; border: 2px solid black; margin-bottom: -2px; }
    .data-row-red { background-color: #ef4444; padding: 15px; border: 2px solid black; margin-bottom: -2px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:black;'>💎 رادار القناص V42.2 💎</h1>", unsafe_allow_html=True)

STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']

# عناوين الجدول
h1, h2, h3, h4, h5, h6 = st.columns([1, 1, 1, 1, 2, 1])
h1.markdown('<div class="header-box">إشارة</div>', unsafe_allow_html=True)
h2.markdown('<div class="header-box">السهم</div>', unsafe_allow_html=True)
h3.markdown('<div class="header-box">يومي %</div>', unsafe_allow_html=True)
h4.markdown('<div class="header-box">السعر</div>', unsafe_allow_html=True)
h5.markdown('<div class="header-box">الفلتر (الاتجاه | RSI)</div>', unsafe_allow_html=True)
h6.markdown('<div class="header-box">الجودة</div>', unsafe_allow_html=True)

try:
    # جلب البيانات
    data = yf.download(STOCKS, period='2d', interval='5m', group_by='ticker', progress=False)

    for sym in STOCKS:
        df = data[sym].dropna()
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            p = float(df['Close'].iloc[-1])
            open_p = float(df['Open'].iloc[0])
            chg = ((p - open_p) / open_p) * 100
            rsi = int(ta.rsi(df['Close'], length=14).iloc[-1])
            ema = ta.ema(df['Close'], length=50).iloc[-1]
            
            # تحديد اللون بناءً على الاتجاه
            row_style = "data-row-green" if p > ema else "data-row-red"
            icon = "🟢" if p > ema else "🔴"
            trend = "صاعد ↑" if p > ema else "هابط ↓"
            
            # ميزة الاستباق ⚡ (فوليوم عالٍ)
            vol_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1])
            pre = "⚡" if vol_ratio > 1.3 else ""

            # عرض الصفوف باستخدام الأعمدة لضمان عدم الاختفاء
            c1, c2, c3, c4, c5, c6 = st.columns([1, 1, 1, 1, 2, 1])
            c1.markdown(f'<div class="{row_style} big-font">{pre}{icon}</div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="{row_style} big-font">{sym}</div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="{row_style} big-font">{chg:+.2f}%</div>', unsafe_allow_html=True)
            c4.markdown(f'<div class="{row_style} big-font">{p:.2f}</div>', unsafe_allow_html=True)
            c5.markdown(f'<div class="{row_style} big-font">{trend} | RSI:{rsi}</div>', unsafe_allow_html=True)
            c6.markdown(f'<div class="{row_style} big-font">ممتازة ✅</div>', unsafe_allow_html=True)

except Exception as e:
    st.error("انتظر.. يتم سحب البيانات الآن")
