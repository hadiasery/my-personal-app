import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
import time
from streamlit_autorefresh import st_autorefresh

# التحديث التلقائي
st_autorefresh(interval=12000, key="v40_fixed_hadi")

st.set_page_config(page_title="رادار القناص V40 - المطور", layout="wide")

# دالة الصوت
def play_beep():
    audio_html = """
    <audio autoplay>
    <source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# التنسيق الأصلي لكود 40 مع تعديلاتك
st.markdown("""
    <style>
    th { background-color: #00416d !important; color: white !important; text-align: center !important; }
    td { text-align: center !important; font-weight: bold !important; border: 1px solid #222 !important; padding: 12px !important; }
    .target-cell { color: #00d4ff !important; font-size: 18px; }
    /* إضافة لون الـ IV الأزرق */
    .iv-blue { background-color: #00d4ff !important; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']
if 'signal_start' not in st.session_state: st.session_state.signal_start = {}

results = []
sound_triggered = False

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
            
            # الحالة الافتراضية (هدوء باللون الأبيض)
            icon, status, bg, tc, target = "⚪", "هدوء", "#FFFFFF", "black", "-"
            
            # منطق الألوان الأصلي لكود 40
            if m_val > s_val:
                target = f"{curr_p + (high_d - low_d)*0.04:.2f}"
                if v_ratio > 1.05: 
                    icon, status, bg, tc = "🔥", "كول قوي الآن", "#00FF00", "black"
                    sound_triggered = True
                else: 
                    icon, status, bg, tc = "🟢", "كول", "#006400", "white"
            elif m_val < s_val:
                target = f"{curr_p - (high_d - low_d)*0.04:.2f}"
                if v_ratio > 1.05: 
                    icon, status, bg, tc = "🔥", "بوت قوي الآن", "#FF0000", "white"
                    sound_triggered = True
                else: 
                    icon, status, bg, tc = "🔴", "بوت", "#8B0000", "white"

            # وقت الإشارة
            if "قوي" in status:
                if sym not in st.session_state.signal_start: st.session_state.signal_start[sym] = time.time()
                time_str = f"{int(time.time() - st.session_state.signal_start[sym])}ث"
            else:
                st.session_state.signal_start.pop(sym, None)
                time_str = "-"

            # لون الـ IV
            iv_bg = "#00d4ff" if iv_val < 10 else bg
            iv_tc = "black" if iv_val < 10 else tc

            results.append({
                "⚡": icon, "S": sym, "ST": status, "T": time_str, "P": f"{curr_p:.2f}", 
                "TG": target, "IV": f"{iv_val:.1f}%", "bg": bg, "tc": tc, "iv_bg": iv_bg, "iv_tc": iv_tc
            })
    except: continue

if sound_triggered: play_beep()

st.markdown("<h2 style='text-align:center;'>💎 رادار القناص V40 المعدل 💎</h2>", unsafe_allow_html=True)

if results:
    html = "<table><thead><tr><th>🔥</th><th>السهم</th><th>الحالة</th><th>الوقت</th><th>السعر</th><th>الهدف 🎯</th><th>IV</th></tr></thead><tbody>"
    for r in results:
        html += f"<tr style='background-color: {r['bg']}; color: {r['tc']};'>"
        html += f"<td>{r['⚡']}</td><td>{r['S']}</td><td>{r['ST']}</td><td>{r['T']}</td><td>{r['P']}</td><td class='target-cell'>{r['TG']}</td>"
        html += f"<td style='background-color: {r['iv_bg']}; color: {r['iv_tc']};'>{r['IV']}</td></tr>"
    st.markdown(html + "</tbody></table>", unsafe_allow_html=True)
