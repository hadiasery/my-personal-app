import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
import time
from streamlit_autorefresh import st_autorefresh

# تحديث تلقائي كل 12 ثانية
st_autorefresh(interval=12000, key="v40_8_final_white")

# إعداد الصفحة لتكون بعرض الشاشة الكامل
st.set_page_config(page_title="رادار القناص V40", layout="wide")

# دالة التنبيه الصوتي
def play_beep():
    audio_html = """
    <audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg"></audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# --- تنسيق CSS المطور للهدوء والاتساع ---
st.markdown("""
    <style>
    /* جعل الصفحة تمتد بالكامل */
    .block-container { padding: 1rem 1rem; max-width: 100%; }
    
    /* تنسيق الجدول */
    .full-width-table { width: 100% !important; border-collapse: collapse; background-color: white; }
    th { background-color: #0f172a !important; color: white !important; text-align: center !important; padding: 15px; }
    td { text-align: center !important; font-weight: bold !important; border: 1px solid #f1f5f9 !important; padding: 12px !important; }
    
    /* حالة الهدوء: خلفية بيضاء صريحة */
    .row-calm { background-color: #ffffff !important; color: #94a3b8 !important; }
    
    /* حالة كول وبوت: ألوان كود 40 الأصلية */
    .row-call { background-color: #006400 !important; color: white !important; }
    .row-put { background-color: #8B0000 !important; color: white !important; }
    
    /* حالة القوة: ألوان فاقعة ونبض */
    .row-strong-call { background-color: #00FF00 !important; color: black !important; }
    .row-strong-put { background-color: #FF0000 !important; color: white !important; }

    .target-cell { color: #0ea5e9 !important; }
    .iv-blue { background-color: #bae6fd !important; color: #0369a1 !important; }
    </style>
    """, unsafe_allow_html=True)

# قائمة الأسهم
STOCKS = {'SPY': 'SPX', 'AAPL': 'AAPL', 'NVDA': 'NVDA', 'TSLA': 'TSLA', 'MSFT': 'MSFT', 'AMZN': 'AMZN', 'META': 'META', 'GOOGL': 'GOOGL', 'AMD': 'AMD', 'NIO': 'NIO'}

if 'signal_start' not in st.session_state: st.session_state.signal_start = {}
results = []
sound_triggered = False

for ticker_sym, display_name in STOCKS.items():
    try:
        df = yf.download(ticker_sym, period='2d', interval='1m', progress=False)
        if not df.empty and len(df) > 10:
            curr_p = float(df['Close'].iloc[-1])
            high_d, low_d = float(df['High'].max()), float(df['Low'].min())
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            m_val, s_val = float(macd.iloc[-1, 0]), float(macd.iloc[-1, 2])
            v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(5).mean().iloc[-1])
            returns = np.log(df['Close'] / df['Close'].shift(1))
            iv_val = returns.std() * np.sqrt(252 * 390) * 100
            
            # منطق الحالة: هدوء أبيض كقاعدة أساسية
            icon, status, row_class, target = "⚪", "هدوء", "row-calm", "-"
            
            if m_val > s_val:
                target = f"{curr_p + (high_d - low_d)*0.04:.2f}"
                if v_ratio > 1.10: 
                    icon, status, row_class = "🔥", "كول قوي", "row-strong-call"
                    sound_triggered = True
                else: icon, status, row_class = "🟢", "كول متابعة", "row-call"
            elif m_val < s_val:
                target = f"{curr_p - (high_d - low_d)*0.04:.2f}"
                if v_ratio > 1.10: 
                    icon, status, row_class = "🔥", "بوت قوي", "row-strong-put"
                    sound_triggered = True
                else: icon, status, row_class = "🔴", "بوت متابعة", "row-put"

            # حساب الوقت
            if "قوي" in status:
                if ticker_sym not in st.session_state.signal_start: st.session_state.signal_start[ticker_sym] = time.time()
                time_str = f"{int(time.time() - st.session_state.signal_start[ticker_sym])}ث"
            else:
                st.session_state.signal_start.pop(ticker_sym, None)
                time_str = "-"

            results.append({"⚡": icon, "S": display_name, "ST": status, "T": time_str, "P": f"{curr_p:.2f}", "TG": target, "IV": f"{iv_val:.1f}%", "class": row_class, "iv_val_num": iv_val})
    except: continue

if sound_triggered: play_beep()
st.markdown("<h1 style='text-align:center;'>💎 رادار القناص V40.8 (النسخة البيضاء) 💎</h1>", unsafe_allow_html=True)

if results:
    html = "<table class='full-width-table'><thead><tr><th>🔥</th><th>السهم</th><th>الحالة</th><th>الوقت</th><th>السعر</th><th>الهدف 🎯</th><th>IV</th></tr></thead><tbody>"
    for r in results:
        iv_cell_class = "class='iv-blue'" if r['iv_val_num'] < 10 else ""
        html += f"<tr class='{r['class']}'><td>{r['⚡']}</td><td>{r['S']}</td><td>{r['ST']}</td><td>{r['T']}</td><td>{r['P']}</td><td class='target-cell'>{r['TG']}</td><td {iv_cell_class}>{r['IV']}</td></tr>"
    st.markdown(html + "</tbody></table>", unsafe_allow_html=True)
