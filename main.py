import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

# التحديث كل 10 ثوانٍ
st_autorefresh(interval=10000, key="v42_final_stable")

st.set_page_config(page_title="رادار القناص V42.2", layout="wide")

# تصميم الألوان والخطوط (أبيض بالكامل - خط 30)
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    .big-font { font-size: 30px !important; font-weight: 900 !important; color: black !important; text-align: center; }
    .header-box { background-color: #1e293b; color: white; padding: 10px; text-align: center; font-size: 25px; font-weight: bold; border: 3px solid black; }
    .row-g { background-color: #22c55e; padding: 20px; border: 3px solid black; margin-bottom: -3px; }
    .row-r { background-color: #ef4444; padding: 20px; border: 3px solid black; margin-bottom: -3px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"<h1 style='text-align:center; color:black;'>💎 رادار القناص V42.2 💎 <br> <span style='font-size:22px;'>توقيت الرصد: {time.strftime('%H:%M:%S')}</span></h1>", unsafe_allow_html=True)

STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']

# العناوين
cols = st.columns([1, 1, 1, 1, 2, 1])
titles = ["إشارة", "السهم", "يومي %", "السعر", "الفلتر", "الجودة"]
for col, title in zip(cols, titles):
    col.markdown(f'<div class="header-box">{title}</div>', unsafe_allow_html=True)

try:
    # جلب البيانات
    data = yf.download(STOCKS, period='2d', interval='1m', group_by='ticker', progress=False, threads=True)

    for sym in STOCKS:
        try:
            df = data[sym].dropna()
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                
                p = float(df['Close'].iloc[-1])
                # حساب التغير من إغلاق أمس الفعلي
                prev_c = df['Close'].iloc[0]
                chg = ((p - prev_c) / prev_c) * 100
                
                rsi = int(ta.rsi(df['Close'], length=14).iloc[-1])
                ema = ta.ema(df['Close'], length=50).iloc[-1]
                
                # منطق الاستباق ⚡ (فوليوم عالٍ جداً)
                v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1])
                pre = "⚡" if v_ratio > 1.3 else ""
                
                # التنسيق والألوان
                style = "row-g" if p > ema else "row-r"
                icon = "🟢" if p > ema else "🔴"
                trend = "صاعد ↑" if p > ema else "هابط ↓"

                # العرض المباشر
                r1, r2, r3, r4, r5, r6 = st.columns([1, 1, 1, 1, 2, 1])
                r1.markdown(f'<div class="{style} big-font">{pre}{icon}</div>', unsafe_allow_html=True)
                r2.markdown(f'<div class="{style} big-font">{sym}</div>', unsafe_allow_html=True)
                r3.markdown(f'<div class="{style} big-font">{chg:+.2f}%</div>', unsafe_allow_html=True)
                r4.markdown(f'<div class="{style} big-font">{p:.2f}</div>', unsafe_allow_html=True)
                r5.markdown(f'<div class="{style} big-font">{trend} | RSI:{rsi}</div>', unsafe_allow_html=True)
                r6.markdown(f'<div class="{style} big-font">{"ممتازة ✅" if (p > ema and rsi > 50) or (p < ema and rsi < 50) else "مراقبة"}</div>', unsafe_allow_html=True)
        except: continue

except Exception as e:
    st.write("🔄 جاري تحديث السيولة...")
