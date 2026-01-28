import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
import time
import base64
from streamlit_autorefresh import st_autorefresh

# تحديث كل 12 ثانية
st_autorefresh(interval=12000, key="v40_5_final_audio")

st.set_page_config(page_title="رادار القناص V40.5", layout="wide")

# --- دالة التنبيه الصوتي ---
def play_sound():
    sound_html = """
    <audio autoplay>
    <source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg">
    </audio>
    """
    st.markdown(sound_html, unsafe_allow_html=True)

# --- تنسيق CSS المتكامل ---
st.markdown("""
    <style>
    table { width: 100%; border-collapse: collapse; font-family: sans-serif; }
    th { background-color: #0f172a !important; color: white !important; padding: 12px; }
    td { text-align: center !important; font-weight: bold !important; border: 1px solid #e2e8f0 !important; padding: 10px !important; }
    
    .calm-row { background-color: #ffffff !important; color: #94a3b8 !important; }
    .call-row { background-color: #dcfce7 !important; color: #166534 !important; }
    .put-row { background-color: #fee2e2 !important; color: #991b1b !important; }
    .strong-call { background-color: #22c55e !important; color: white !important; animation: pulse 1s infinite; }
    .strong-put { background-color: #ef4444 !important; color: white !important; animation: pulse 1s infinite; }
    
    .iv-cheap { background-color: #bae6fd !important; color: #0369a1 !important; } /* أزرق سماوي */
    .target-hit { background-color: #facc15 !important; color: black !important; border: 2px solid orange !important; }
    
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.8; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']
if 'signal_start' not in st.session_state: st.session_state.signal_start = {}

results = []
trigger_audio = False

for sym in STOCKS:
    try:
        ticker = yf.Ticker(sym)
        df = ticker.history(period='2d', interval='1m')
        if not df.empty and len(df) > 10:
            curr_p = float(df['Close'].iloc[-1])
            high_d, low_d = float(df['High'].max()), float(df['Low'].min())
            
            # المؤشرات
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            m_val, s_val = float(macd.iloc[-1, 0]), float(macd.iloc[-1, 2])
            v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(5).mean().iloc[-1])
            returns = np.log(df['Close'] / df['Close'].shift(1))
            iv_val = returns.std() * np.sqrt(252 * 390) * 100
            
            # المنطق وتحديد الألوان
            icon, status, row_class, target = "⚪", "هدوء", "calm-row", 0.0
            is_strong = v_ratio > 1.15

            if m_val > s_val:
                target = round(curr_p + (high_d - low_d)*0.02, 2)
                row_class = "strong-call" if is_strong else "call-row"
                icon, status = ("🔥", "كول قوي") if is_strong else ("🟢", "كول")
                if is_strong: trigger_audio = True
            elif m_val < s_val:
                target = round(curr_p - (high_d - low_d)*0.02, 2)
                row_class = "strong-put" if is_strong else "put-row"
                icon, status = ("🔥", "بوت قوي") if is_strong else ("🔴", "بوت")
                if is_strong: trigger_audio = True

            # فحص لمس الهدف
            target_hit_class = ""
            if status != "هدوء":
                is_hit = (status.startswith("كول") and curr_p >= target) or (status.startswith("بوت") and curr_p <= target)
                if is_hit:
                    target_hit_class = "target-hit"
                    trigger_audio = True

            # الوقت
            if "قوي" in status:
                if sym not in st.session_state.signal_start: st.session_state.signal_start[sym] = time.time()
                time_str = f"{int(time.time() - st.session_state.signal_start[sym])}ث"
            else:
                st.session_state.signal_start.pop(sym, None)
                time_str = "-"

            results.append({
                "⚡": icon, "sym": sym, "status": status, "time": time_str,
                "price": f"{curr_p:.2f}", "target": f"{target:.2f}", "iv": f"{iv_val:.1f}%",
                "row_class": row_class, "iv_class": "iv-cheap" if iv_val < 10 else "",
                "hit_class": target_hit_class
            })
    except: continue

# تشغيل الصوت إذا وجدت إشارة قوية أو هدف
if trigger_audio: play_sound()

st.markdown("<h1 style='text-align:center;'>🚀 رادار القناص V40.5 (المنبه الصوتي)</h1>", unsafe_allow_html=True)

if results:
    html = "<table><thead><tr><th>إشارة</th><th>السهم</th><th>الحالة</th><th>الوقت</th><th>السعر</th><th>الهدف 🎯</th><th>IV (تقلب)</th></tr></thead><tbody>"
    for r in results:
        html += f"<tr class='{r['row_class']}'>"
        html += f"<td style='font-size:22px;'>{r['⚡']}</td><td>{r['sym']}</td><td>{r['status']}</td><td>{r['time']}</td><td>{r['price']}</td>"
        html += f"<td class='{r['hit_class']}'>{r['target']}</td><td class='{r['iv_class']}'>{r['iv']}</td></tr>"
    st.markdown(html + "</tbody></table>", unsafe_allow_html=True)
