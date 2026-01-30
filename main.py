import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

# تحديث كل 10 ثوانٍ
st_autorefresh(interval=10000, key="v42_precise_entry_fix")

st.set_page_config(page_title="رادار القناص V42.2", layout="wide")

# تصميم الألوان والخطوط (خلفية بيضاء - خط 30)
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    .big-font { font-size: 30px !important; font-weight: 900 !important; color: black !important; text-align: center; }
    .header-box { background-color: #1e293b; color: white; padding: 10px; text-align: center; font-size: 25px; font-weight: bold; border: 3px solid black; }
    
    .row-g { background-color: #22c55e; padding: 20px; border: 3px solid black; margin-bottom: -3px; }
    .row-r { background-color: #ef4444; padding: 20px; border: 3px solid black; margin-bottom: -3px; }
    
    .entry-box-white { 
        background-color: white !important; 
        color: black !important; 
        font-size: 32px !important; 
        font-weight: 900; 
        padding: 20px; 
        border: 4px solid black; 
        text-align: center; 
    }
    .wait-box-white { 
        background-color: white !important; 
        color: #aaaaaa !important; 
        font-size: 25px; 
        padding: 20px; 
        border: 3px solid black; 
        text-align: center; 
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"<h1 style='text-align:center; color:black;'>💎 رادار القناص V42.2 💎 <br> <span style='font-size:20px;'>نبض السوق اللحظي: {time.strftime('%H:%M:%S')}</span></h1>", unsafe_allow_html=True)

STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']

cols = st.columns([1, 1, 1, 1, 2, 1, 2])
titles = ["إشارة", "السهم", "يومي %", "السعر", "الفلتر", "الجودة", "⚡ تنبيه استباقي"]
for col, title in zip(cols, titles):
    col.markdown(f'<div class="header-box">{title}</div>', unsafe_allow_html=True)

try:
    data = yf.download(STOCKS, period='2d', interval='1m', group_by='ticker', progress=False, threads=True)

    for sym in STOCKS:
        try:
            df = data[sym].dropna()
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                
                p = float(df['Close'].iloc[-1])
                prev_c = df['Close'].iloc[0]
                chg = ((p - prev_c) / prev_c) * 100
                rsi = int(ta.rsi(df['Close'], length=14).iloc[-1])
                ema = ta.ema(df['Close'], length=50).iloc[-1]
                
                # --- المنطق المصلح للدخول (عودة شرط السيولة الذكي) ---
                # حساب حجم التداول اللحظي مقارنة بآخر 10 دقائق
                current_vol = df['Volume'].iloc[-1]
                avg_vol = df['Volume'].rolling(10).mean().iloc[-1]
                v_ratio = current_vol / avg_vol if avg_vol > 0 else 0
                
                # شرط الدخول: (اتجاه صحيح + RSI قوي) "و" (سيولة أعلى من المعدل بـ 25%)
                # v_ratio > 1.25 تعني أن هناك انفجار سيولة الآن
                is_entry = (v_ratio > 1.25) and ((p > ema and rsi > 52) or (p < ema and rsi < 48))
                
                if is_entry:
                    pre_msg = "⚡ الدخول الآن ⚡"
                    msg_style = "entry-box-white"
                else:
                    pre_msg = "مراقبة.."
                    msg_style = "wait-box-white"
                
                style = "row-g" if p > ema else "row-r"
                icon = "🟢" if p > ema else "🔴"
                trend = "صاعد ↑" if p > ema else "هابط ↓"

                r1, r2, r3, r4, r5, r6, r7 = st.columns([1, 1, 1, 1, 2, 1, 2])
                r1.markdown(f'<div class="{style} big-font">{icon}</div>', unsafe_allow_html=True)
                r2.markdown(f'<div class="{style} big-font">{sym}</div>', unsafe_allow_html=True)
                r3.markdown(f'<div class="{style} big-font">{chg:+.2f}%</div>', unsafe_allow_html=True)
                r4.markdown(f'<div class="{style} big-font">{p:.2f}</div>', unsafe_allow_html=True)
                r5.markdown(f'<div class="{style} big-font">{trend} | {rsi}</div>', unsafe_allow_html=True)
                r6.markdown(f'<div class="{style} big-font">ممتازة ✅</div>', unsafe_allow_html=True)
                r7.markdown(f'<div class="{msg_style}">{pre_msg}</div>', unsafe_allow_html=True)
        except: continue
except:
    st.write("🔄 تحديث..")
