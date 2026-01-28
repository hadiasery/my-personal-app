import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
import time
from streamlit_autorefresh import st_autorefresh

# تحديث كل 15 ثانية لتقليل الضغط على السيرفر وضمان عدم الحظر
st_autorefresh(interval=15000, key="v40_pro_radar")

st.set_page_config(page_title="رادار القناص V40", layout="wide")

# --- تنسيق CSS احترافي ---
st.markdown("""
    <style>
    .main { background-color: #050505; }
    th { background-color: #00416d !important; color: white !important; text-align: center !important; font-size: 16px; }
    td { text-align: center !important; font-weight: bold !important; border: 1px solid #222 !important; padding: 12px !important; }
    .target-cell { color: #00d4ff !important; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# قائمة الشركات
STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']

if 'signal_start' not in st.session_state:
    st.session_state.signal_start = {}

results = []

for sym in STOCKS:
    try:
        # استخدام Ticker لجلب البيانات بشكل أكثر استقراراً
        ticker = yf.Ticker(sym)
        df = ticker.history(period='2d', interval='1m')
        
        if not df.empty and len(df) > 10:
            curr_p = float(df['Close'].iloc[-1])
            high_d = float(df['High'].max())
            low_d = float(df['Low'].min())
            
            # --- دمج IV (التقلب الضمني التقديري) ---
            returns = np.log(df['Close'] / df['Close'].shift(1))
            iv_est = returns.std() * np.sqrt(252 * 390) * 100
            
            # --- دمج Theta (تآكل الوقت) ---
            # حساب الوقت المتبقي لإغلاق السوق الأمريكي (21:00 بتوقيت GMT)
            theta_risk = "عالي ⚠️" if time.localtime().tm_hour >= 19 else "طبيعي"

            # المؤشرات الفنية
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            m_val = float(macd.iloc[-1, 0])
            s_val = float(macd.iloc[-1, 2])
            
            # السيولة
            v_now = df['Volume'].iloc[-1]
            v_avg = df['Volume'].rolling(5).mean().iloc[-1]
            v_ratio = float(v_now / v_avg) if v_avg > 0 else 1.0
            
            icon, status, bg, tc, target = "⚪", "انتظار", "#1a1a1a", "white", "-"
            
            # منطق "قوي الآن" والأهداف
            if m_val > s_val:
                target = f"{curr_p + (high_d - low_d)*0.04:.2f}"
                if v_ratio > 1.05: icon, status, bg, tc = "🔥", "كول قوي الآن", "#00FF00", "black"
                else: icon, status, bg, tc = "🟢", "كول متابعة", "#006400", "white"
            elif m_val < s_val:
                target = f"{curr_p - (high_d - low_d)*0.04:.2f}"
                if v_ratio > 1.05: icon, status, bg, tc = "🔥", "بوت قوي الآن", "#FF0000", "white"
                else: icon, status, bg, tc = "🔴", "بوت متابعة", "#8B0000", "white"

            # عداد الوقت
            if "قوي" in status:
                if sym not in st.session_state.signal_start:
                    st.session_state.signal_start[sym] = time.time()
                elapsed = int(time.time() - st.session_state.signal_start[sym])
                time_str = f"{elapsed}ث"
            else:
                st.session_state.signal_start.pop(sym, None)
                time_str = "-"

            results.append({
                "⚡": icon, "السهم": sym, "الحالة": status, "منذ": time_str,
                "السعر": f"{curr_p:.2f}", "الهدف 🎯": target, "IV": f"{iv_est:.1f}%", "Theta": theta_risk, "_bg": bg, "_tc": tc
            })
    except: continue

st.markdown(f'<h1 style="text-align:center; color:#CCFF00;">💎 رادار المحترفين V40 💎</h1>', unsafe_allow_html=True)

if results:
    html = "<table style='width:100%; border-collapse: collapse;'><thead><tr>"
    html += "<th>🔥</th><th>السهم</th><th>الحالة</th><th>الوقت</th><th>السعر</th><th>الهدف 🎯</th><th>IV</th><th>Theta</th></tr></thead><tbody>"
    for r in results:
        html += f"<tr style='background-color: {r['_bg']}; color: {r['_tc']};'>"
        html += f"<td style='font-size: 24px;'>{r['⚡']}</td><td>{r['السهم']}</td><td>{r['الحالة']}</td><td>{r['منذ']}</td><td>{r['السعر']}</td><td class='target-cell'>{r['الهدف 🎯']}</td><td>{r['IV']}</td><td>{r['Theta']}</td></tr>"
    st.markdown(html + "</tbody></table>", unsafe_allow_html=True)
else:
    st.warning("⚠️ ياهو فاينانس يرفض الطلب حالياً. سيقوم الرادار بإعادة المحاولة تلقائياً خلال ثوانٍ...")
