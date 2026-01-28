import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
import time
from streamlit_autorefresh import st_autorefresh

# تحديث كل 15 ثانية
st_autorefresh(interval=15000, key="v41_light_colors")

st.set_page_config(page_title="رادار القناص V41", layout="wide")

def play_beep():
    st.markdown("""<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

# --- تنسيق الألوان الفاتحة ---
st.markdown("""
    <style>
    .block-container { padding: 1rem; max-width: 100%; }
    .stApp { background-color: white; }
    .full-width-table { width: 100% !important; border-collapse: collapse; background-color: white; }
    th { background-color: #f8fafc !important; color: #1e293b !important; text-align: center !important; border-bottom: 2px solid #e2e8f0 !important; padding: 12px; }
    td { text-align: center !important; font-weight: bold !important; border: 1px solid #f1f5f9 !important; padding: 10px; }
    
    /* ألوان فاتحة (Pastel) */
    .row-calm { background-color: #ffffff !important; color: #94a3b8 !important; }
    .row-call { background-color: #dcfce7 !important; color: #166534 !important; } /* أخضر فاتح */
    .row-put { background-color: #fee2e2 !important; color: #991b1b !important; }  /* أحمر فاتح */
    .row-strong-call { background-color: #4ade80 !important; color: white !important; } /* أخضر زاهي */
    .row-strong-put { background-color: #f87171 !important; color: white !important; }  /* أحمر زاهي */
    
    .iv-blue { background-color: #e0f2fe !important; color: #0369a1 !important; }
    .target-cell { color: #3b82f6 !important; }
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
            
            # تعديل سعر SPX ليظهر بشكل صحيح (ضرب في 10)
            if display_name == 'SPX':
                display_price = curr_p * 10
                multiplier = 10
            else:
                display_price = curr_p
                multiplier = 1

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
                    icon, status, row_class = "🔥", "كول قوي", "row-strong-call"
                    sound_triggered = True
                else: icon, status, row_class = "🟢", "كول", "row-call"
            elif m_val < s_val:
                target_val = curr_p - (high_d - low_d)*0.04
                target = f"{target_val * multiplier:.2f}"
                if v_ratio > 1.15: 
                    icon, status, row_class = "🔥", "بوت قوي", "row-strong-put"
                    sound_triggered = True
                else: icon, status, row_class = "🔴", "بوت", "row-put"

            results.append({"⚡": icon, "S": display_name, "ST": status, "P": f"{display_price:.2f}", "TG": target, "IV": f"{iv_val:.1f}%", "class": row_class, "iv_val_num": iv_val})

    st.markdown("<h1 style='text-align:center; color:#1e293b;'>💎 رادار القناص V41.0 💎</h1>", unsafe_allow_html=True)

    if results:
        html = "<table class='full-width-table'><thead><tr><th>إشارة</th><th>السهم</th><th>الحالة</th><th>السعر</th><th>الهدف 🎯</th><th>IV</th></tr></thead><tbody>"
        for r in results:
            iv_style = "class='iv-blue'" if r['iv_val_num'] < 10 else ""
            html += f"<tr class='{r['class']}'><td>{r['⚡']}</td><td>{r['S']}</td><td>{r['ST']}</td><td>{r['P']}</td><td class='target-cell'>{r['TG']}</td><td {iv_style}>{r['IV']}</td></tr>"
        st.markdown(html + "</tbody></table>", unsafe_allow_html=True)
        if sound_triggered: play_beep()
except Exception as e:
    st.error("جاري تحديث البيانات... انتظر ثواني")
