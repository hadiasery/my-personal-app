import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
import time
import datetime
from streamlit_autorefresh import st_autorefresh

# تحديث كل 10 ثوانٍ (توازن بين السرعة والاستقرار)
st_autorefresh(interval=10000, key="v41_royal_radar")

st.set_page_config(page_title="رادار القناص الملكي V41", layout="wide")

# --- التنسيق الجمالي الجديد ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; }
    .main { background-color: #f8f9fa; }
    th { background-color: #1e293b !important; color: #f8fafc !important; text-align: center !important; padding: 15px !important; border-radius: 5px 5px 0 0; }
    td { text-align: center !important; font-weight: 600 !important; border-bottom: 1px solid #e2e8f0 !important; padding: 12px !important; }
    .target-val { color: #2563eb !important; font-size: 1.1em; text-decoration: underline; }
    .fire-row { animation: pulse 2s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.8; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

# العنوان
now_time = datetime.datetime.now().strftime("%H:%M:%S")
st.markdown(f"""
    <div style="background: linear-gradient(90deg, #1e293b, #334155); padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 20px;">
        <h1 style="color: #f1f5f9; margin:0;">💎 رادار القناص الملكي V41 💎</h1>
        <p style="color: #94a3b8; margin:5px 0 0 0;">وقت التحديث الحالي: {now_time} (بيانات لحظية)</p>
    </div>
    """, unsafe_allow_html=True)

STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']

if 'signal_start' not in st.session_state: st.session_state.signal_start = {}

results = []

for sym in STOCKS:
    try:
        # جلب البيانات
        df = yf.download(sym, period='2d', interval='1m', progress=False)
        
        if not df.empty and len(df) > 15:
            curr_p = float(df['Close'].iloc[-1])
            high_d, low_d = float(df['High'].max()), float(df['Low'].min())
            
            # اليونانيات والمؤشرات
            returns = np.log(df['Close'] / df['Close'].shift(1))
            iv_est = returns.std() * np.sqrt(252 * 390) * 100
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            m_val, s_val = float(macd.iloc[-1, 0]), float(macd.iloc[-1, 2])
            v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1])
            
            # --- منطق الألوان الجديد (لإعادة الهدوء) ---
            icon, status, bg, tc, target = "⚪", "هدوء / انتظار", "#ffffff", "#64748b", "-"
            
            is_strong = v_ratio > 1.15  # شرط القوة (النار)
            
            if m_val > s_val:
                target = f"{curr_p + (high_d - low_d)*0.02:.2f}"
                if is_strong: icon, status, bg, tc = "🔥", "كول قوي الآن", "#dcfce7", "#166534"
                else: icon, status, bg, tc = "🟢", "كول هادئ", "#f8fafc", "#22c55e"
            elif m_val < s_val:
                target = f"{curr_p - (high_d - low_d)*0.02:.2f}"
                if is_strong: icon, status, bg, tc = "🔥", "بوت قوي الآن", "#fee2e2", "#991b1b"
                else: icon, status, bg, tc = "🔴", "بوت هادئ", "#f8fafc", "#ef4444"

            # العداد
            if "قوي" in status:
                if sym not in st.session_state.signal_start: st.session_state.signal_start[sym] = time.time()
                time_str = f"{int(time.time() - st.session_state.signal_start[sym])}ث"
            else:
                st.session_state.signal_start.pop(sym, None)
                time_str = "-"

            results.append({"⚡": icon, "السهم": sym, "الحالة": status, "منذ": time_str, "السعر": f"{curr_p:.2f}", "الهدف 🎯": target, "IV": f"{iv_est:.1f}%", "_bg": bg, "_tc": tc})
    except: continue

if results:
    html = "<table style='width:100%; border-collapse: separate; border-spacing: 0 8px;'><thead><tr>"
    html += "<th>إشارة</th><th>السهم</th><th>الحالة</th><th>الوقت</th><th>السعر</th><th>الهدف 🎯</th><th>IV (تقلب)</th></tr></thead><tbody>"
    for r in results:
        row_class = "fire-row" if "🔥" in r['⚡'] else ""
        html += f"<tr class='{row_class}' style='background-color: {r['_bg']}; color: {r['_tc']}; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>"
        html += f"<td style='font-size: 22px;'>{r['⚡']}</td><td>{r['السهم']}</td><td>{r['الحالة']}</td><td>{r['منذ']}</td><td>{r['السعر']}</td><td class='target-val'>{r['الهدف 🎯']}</td><td>{r['IV']}</td></tr>"
    st.markdown(html + "</tbody></table>", unsafe_allow_html=True)
