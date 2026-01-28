import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
import time
from streamlit_autorefresh import st_autorefresh

# تحديث كل 15 ثانية
st_autorefresh(interval=15000, key="v41_2_compact")

st.set_page_config(page_title="رادار القناص V41.2", layout="wide")

def play_beep():
    st.markdown("""<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

# --- تنسيق CSS لتقليل المسافات وتوسيط الجدول ---
st.markdown("""
    <style>
    .block-container { padding: 1rem; max-width: 95%; }
    .stApp { background-color: white; }
    
    .full-width-table { 
        width: 100% !important; 
        border-collapse: collapse; 
        background-color: white; 
        table-layout: auto; /* جعل الأعمدة تأخذ مساحة النص فقط */
    }
    
    th { 
        background-color: #1e293b !important; 
        color: white !important; 
        text-align: center !important; 
        padding: 8px !important; /* مسافة أصغر للعنوان */
        font-size: 14px;
    }
    
    td { 
        text-align: center !important; 
        font-weight: bold !important; 
        border: 1px solid #e2e8f0 !important; 
        padding: 6px 4px !important; /* تقليل المسافة بين الأعمدة والأسطر */
        font-size: 15px;
    }
    
    .row-calm { background-color: #ffffff !important; color: #64748b !important; }
    .row-call { background-color: #22c55e !important; color: white !important; }
    .row-put { background-color: #ef4444 !important; color: white !important; }
    .row-strong-call { background-color: #15803d !important; color: white !important; }
    .row-strong-put { background-color: #b91c1c !important; color: white !important; }
    
    .iv-blue { background-color: #0ea5e9 !important; color: white !important; }
    .target-cell { color: #2563eb !important; }
    </style>
    """, unsafe_allow_html=True)

STOCKS = {'SPY': 'SPX', 'AAPL': 'AAPL', 'NVDA': 'NVDA', 'TSLA': 'TSLA', 'MSFT': 'MSFT', 'AMZN': 'AMZN', 'META': 'META', 'GOOGL': 'GOOGL', 'AMD': 'AMD', 'NIO': 'NIO'}

if 'signal_start' not in st.session_state: st.session_state.signal_start = {}
results = []
sound_triggered = False

try:
    data = yf.download(list(STOCKS.keys()), period='2d', interval='1m', group_by='ticker', progress=False)
    
    for ticker_sym, display_name in STOCKS.items():
        df = data[ticker_sym].dropna()
        if not df.empty and len(df) > 10:
            curr_p = float(df['Close'].iloc[-1])
            multiplier = 10 if display_name == 'SPX' else 1
            display_price = curr_p * multiplier

            high_d, low_d = float(df['High'].max()), float(df['Low'].min())
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            m_val, s_val = float(macd.iloc[-1, 0]), float(macd.iloc[-1, 2])
            v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(5).mean().iloc[-1])
            returns = np.log(df['Close'] / df['Close'].shift(1))
            iv_val = returns.std() * np.sqrt(252 * 390) * 100
            
            icon, status, row_class, target = "⚪", "هدوء", "row-calm", "-"
            
            if m_val > s_val:
                target_val = curr_p + (high_d - low_d)*0.04
                target = f"{target_val * multiplier:.2f}"
                if v_ratio > 1.15: 
                    icon, status, row_class = "🔥", "قوي", "row-strong-call"
                    sound_triggered = True
                else: icon, status, row_class = "🟢", "كول", "row-call"
            elif m_val < s_val:
                target_val = curr_p - (high_d - low_d)*0.04
                target = f"{target_val * multiplier:.2f}"
                if v_ratio > 1.15: 
                    icon, status, row_class = "🔥", "قوي", "row-strong-put"
                    sound_triggered = True
                else: icon, status, row_class = "🔴", "بوت", "row-put"

            results.append({"⚡": icon, "S": display_name, "ST": status, "P": f"{display_price:.2f}", "TG": target, "IV": f"{iv_val:.1f}%", "class": row_class, "iv_val_num": iv_val})

    st.markdown("<h2 style='text-align:center; color:#1e293b;'>💎 رادار القناص V41.2 💎</h2>", unsafe_allow_html=True)

    if results:
        html = "<table class='full-width-table'><thead><tr><th>🔥</th><th>السهم</th><th>الحالة</th><th>السعر</th><th>الهدف 🎯</th><th>IV</th></tr></thead><tbody>"
        for r in results:
            iv_style = "class='iv-blue'" if r['iv_val_num'] < 10 else ""
            html += f"<tr class='{r['class']}'><td>{r['⚡']}</td><td>{r['S']}</td><td>{r['ST']}</td><td>{r['P']}</td><td class='target-cell'>{r['TG']}</td><td {iv_style}>{r['IV']}</td></tr>"
        st.markdown(html + "</tbody></table>", unsafe_allow_html=True)
        if sound_triggered: play_beep()
except:
    st.info("تحديث...")
