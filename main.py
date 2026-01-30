import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=10000, key="v42_5_spy_sniper")

st.set_page_config(page_title="رادار القناص V42.5", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    .big-font { font-size: 30px !important; font-weight: 900 !important; color: black !important; text-align: center; }
    .header-box { background-color: #1e293b; color: white; padding: 10px; text-align: center; font-size: 25px; font-weight: bold; border: 3px solid black; }
    .white-col-empty { background-color: white !important; border: 3px solid black; display: flex; justify-content: center; align-items: center; height: 85px; }
    .fire-box-blue { background-color: #0000FF !important; color: white !important; font-size: 38px !important; padding: 5px 30px; border-radius: 8px; font-weight: bold; }
    .row-g { background-color: #22c55e; padding: 20px; border: 3px solid black; margin-bottom: -3px; }
    .row-r { background-color: #ef4444; padding: 20px; border: 3px solid black; margin-bottom: -3px; }
    .entry-blue-text { color: #0000FF !important; font-size: 30px !important; font-weight: 900; text-align: center; background-color: white; padding: 20px; border: 4px solid #0000FF; }
    .wait-box { background-color: white; color: #cccccc; font-size: 25px; padding: 20px; border: 3px solid black; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"<h1 style='text-align:center; color:black;'>💎 رادار القناص V42.5 💎<br><span style='font-size:18px;'>فلتر السنتات الذكي | {time.strftime('%H:%M:%S')}</span></h1>", unsafe_allow_html=True)

STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']

cols = st.columns([1, 1, 1, 1, 2, 1, 2.2])
for col, title in zip(cols, ["إشارة", "السهم", "يومي %", "السعر", "الفلتر", "الجودة", "⚡ تنبيه استباقي"]):
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
                rsi = ta.rsi(df['Close'], length=14).iloc[-1]
                ema = ta.ema(df['Close'], length=50).iloc[-1]
                
                # --- تعديل الحساسية للسنتات (خاصة في SPY) ---
                v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1])
                # حساب التسارع في آخر دقيقة واحدة فقط لرصد القفزات اللحظية
                velocity = (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100
                
                # شرط الدخول المطور: سيولة هادئة مع حركة سعرية (0.05%) أو سيولة قوية
                is_entry = (v_ratio > 1.12 and abs(velocity) > 0.05) or (v_ratio > 1.40)
                is_entry = is_entry and ((p > ema and rsi > 51) or (p < ema and rsi < 49))
                
                style = "row-g" if p > ema else "row-r"

                if is_entry:
                    icon_html = f'<div class="white-col-empty"><div class="fire-box-blue">🔥</div></div>'
                    entry_html = f'<div class="entry-blue-text">الدخول الآن 🔥</div>'
                else:
                    icon_html = f'<div class="white-col-empty"></div>'
                    entry_html = f'<div class="wait-box">مراقبة..</div>'

                r1, r2, r3, r4, r5, r6, r7 = st.columns([1, 1, 1, 1, 2, 1, 2.2])
                r1.markdown(icon_html, unsafe_allow_html=True)
                r2.markdown(f'<div class="{style} big-font">{sym}</div>', unsafe_allow_html=True)
                r3.markdown(f'<div class="{style} big-font">{chg:+.2f}%</div>', unsafe_allow_html=True)
                r4.markdown(f'<div class="{style} big-font">{p:.2f}</div>', unsafe_allow_html=True)
                r5.markdown(f'<div class="{style} big-font">{"صاعد ↑" if p > ema else "هابط ↓"} | {int(rsi)}</div>', unsafe_allow_html=True)
                r6.markdown(f'<div class="{style} big-font">ممتازة ✅</div>', unsafe_allow_html=True)
                r7.markdown(entry_html, unsafe_allow_html=True)
        except: continue
except:
    st.write("🔄 جاري التحديث...")
