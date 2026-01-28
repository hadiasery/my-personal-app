import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
import time
from streamlit_autorefresh import st_autorefresh

# تحديث كل 15 ثانية لضمان الاستقرار
st_autorefresh(interval=15000, key="v40_1_calm_fix")

st.set_page_config(page_title="رادار القناص V40.1", layout="wide")

# --- تنسيق CSS لفرض اللون الأبيض في حالة الهدوء ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    table { width: 100%; border-collapse: collapse; }
    th { background-color: #00416d !important; color: white !important; text-align: center !important; }
    td { text-align: center !important; font-weight: bold !important; border: 1px solid #eeeeee !important; padding: 10px !important; }
    .target-cell { color: #007bff !important; }
    /* حالة الهدوء: خلفية بيضاء ونص رمادي */
    .calm-row { background-color: #ffffff !important; color: #6c757d !important; }
    /* حالة القوة: ألوان صريحة */
    .strong-call { background-color: #28a745 !important; color: white !important; }
    .strong-put { background-color: #dc3545 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']

if 'signal_start' not in st.session_state:
    st.session_state.signal_start = {}

results = []

for sym in STOCKS:
    try:
        ticker = yf.Ticker(sym)
        df = ticker.history(period='2d', interval='1m')
        
        if not df.empty and len(df) > 10:
            curr_p = float(df['Close'].iloc[-1])
            high_d, low_d = float(df['High'].max()), float(df['Low'].min())
            
            # اليونانيات والمؤشرات
            returns = np.log(df['Close'] / df['Close'].shift(1))
            iv_est = returns.std() * np.sqrt(252 * 390) * 100
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            m_val, s_val = float(macd.iloc[-1, 0]), float(macd.iloc[-1, 2])
            v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(5).mean().iloc[-1])
            
            # --- منطق الألوان الجديد (الهدوء باللون الأبيض) ---
            icon, status, row_class, target = "⚪", "هدوء / انتظار", "calm-row", "-"
            
            is_strong = v_ratio > 1.15 # شرط القوة (النار)

            if m_val > s_val:
                target = f"{curr_p + (high_d - low_d)*0.03:.2f}"
                if is_strong:
                    icon, status, row_class = "🔥", "كول قوي الآن", "strong-call"
                else:
                    icon, status, row_class = "🟢", "كول (هدوء)", "calm-row"
            
            elif m_val < s_val:
                target = f"{curr_p - (high_d - low_d)*0.03:.2f}"
                if is_strong:
                    icon, status, row_class = "🔥", "بوت قوي الآن", "strong-put"
                else:
                    icon, status, row_class = "🔴", "بوت (هدوء)", "calm-row"

            # حساب الوقت
            if "قوي" in status:
                if sym not in st.session_state.signal_start:
                    st.session_state.signal_start[sym] = time.time()
                time_str = f"{int(time.time() - st.session_state.signal_start[sym])}ث"
            else:
                st.session_state.signal_start.pop(sym, None)
                time_str = "-"

            results.append({
                "⚡": icon, "السهم": sym, "الحالة": status, "الوقت": time_str,
                "السعر": f"{curr_p:.2f}", "الهدف 🎯": target, "IV": f"{iv_est:.1f}%", "class": row_class
            })
    except: continue

st.markdown(f'<h1 style="text-align:center; color:#00416d;">💎 رادار V40.1: نسخة الهدوء 💎</h1>', unsafe_allow_html=True)

if results:
    html = "<table><thead><tr><th>🔥</th><th>السهم</th><th>الحالة</th><th>الوقت</th><th>السعر</th><th>الهدف 🎯</th><th>IV</th></tr></thead><tbody>"
    for r in results:
        html += f"<tr class='{r['class']}'>"
        html += f"<td style='font-size: 22px;'>{r['⚡']}</td><td>{r['السهم']}</td><td>{r['الحالة']}</td><td>{r['الوقت']}</td><td>{r['السعر']}</td><td class='target-cell'>{r['الهدف 🎯']}</td><td>{r['IV']}</td></tr>"
    st.markdown(html + "</tbody></table>", unsafe_allow_html=True)
