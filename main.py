import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

# تحديث كل 10 ثوانٍ
st_autorefresh(interval=10000, key="v42_9_final_fix")

st.set_page_config(page_title="رادار القناص V42.9", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    .header-box { background-color: #1e293b; color: white; padding: 10px; text-align: center; font-size: 18px; font-weight: bold; border: 1px solid #475569; }
    .white-col-empty { background-color: white !important; border: 1px solid #cbd5e1; display: flex; justify-content: center; align-items: center; height: 70px; }
    .fire-box-blue { background-color: #0000FF !important; color: white !important; font-size: 25px !important; padding: 5px 20px; border-radius: 5px; font-weight: bold; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .row-g { background-color: #dcfce7; padding: 10px; border: 1px solid #22c55e; text-align: center; font-size: 20px; font-weight: bold; color: #166534; height: 70px; display: flex; align-items: center; justify-content: center; }
    .row-r { background-color: #fee2e2; padding: 10px; border: 1px solid #ef4444; text-align: center; font-size: 20px; font-weight: bold; color: #991b1b; height: 70px; display: flex; align-items: center; justify-content: center; }
    .num-box { background-color: #f8fafc; color: #1e293b; padding: 10px; border: 1px solid #cbd5e1; text-align: center; font-size: 22px; font-weight: bold; height: 70px; display: flex; align-items: center; justify-content: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"<h2 style='text-align:center; color:black;'>💎 رادار القناص V42.9 - دقة الأرقام 💎</h2>", unsafe_allow_html=True)

STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']

# تقسيم الأعمدة بوضوح
cols = st.columns([0.8, 1, 1, 1, 1, 1.5, 1.5])
titles = ["إشارة", "السهم", "السعر", "النسبة %", "الاتجاه", "الحالة", "تنبيه"]

for col, title in zip(cols, titles):
    col.markdown(f'<div class="header-box">{title}</div>', unsafe_allow_html=True)

try:
    data = yf.download(STOCKS, period='2d', interval='1m', group_by='ticker', progress=False)

    for sym in STOCKS:
        try:
            df = data[sym].dropna()
            if not df.empty:
                p = float(df['Close'].iloc[-1])
                rsi = ta.rsi(df['Close'], length=14).iloc[-1]
                ema = ta.ema(df['Close'], length=50).iloc[-1]
                v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1])
                
                # تحديد الحالة
                if rsi > 70: status = "تشبع شرائي ⚠️"
                elif rsi < 30: status = "تشبع بيعي ⚠️"
                elif 45 < rsi < 55: status = "تذبذب ممل ⚖️"
                else: status = "تحرك نشط ✅"

                # شرط الدخول
                is_entry = (v_ratio > 1.2 and ((p > ema and rsi > 52) or (p < ema and rsi < 48)))
                
                # اللون بناءً على RSI (أكبر من 50 أخضر، أصغر أحمر)
                style = "row-g" if rsi > 50 else "row-r"
                trend_text = "صاعد ↑" if rsi > 50 else "هابط ↓"

                r1, r2, r3, r4, r5, r6, r7 = st.columns([0.8, 1, 1, 1, 1, 1.5, 1.5])
                
                r1.markdown(f'<div class="white-col-empty">{"<div class=\'fire-box-blue\'>🔥</div>" if is_entry else ""}</div>', unsafe_allow_html=True)
                r2.markdown(f'<div class="{style}">{sym}</div>', unsafe_allow_html=True)
                r3.markdown(f'<div class="num-box">{p:.2f}</div>', unsafe_allow_html=True)
                r4.markdown(f'<div class="{style}">{int(rsi)}%</div>', unsafe_allow_html=True)
                r5.markdown(f'<div class="{style}">{trend_text}</div>', unsafe_allow_html=True)
                r6.markdown(f'<div class="num-box" style="font-size:16px;">{status}</div>', unsafe_allow_html=True)
                r7.markdown(f'<div class="num-box" style="font-size:16px;">{"دخول الآن 🔥" if is_entry else "إشارة غير مؤكدة"}</div>', unsafe_allow_html=True)
        except: continue
except:
    st.write("🔄 جاري تحديث البيانات...")
