import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

# تحديث كل 10 ثوانٍ لضمان استقرار الربط
st_autorefresh(interval=10000, key="v39_final_fixed")

st.set_page_config(page_title="رادار القناص V39", layout="wide")

st.markdown("""
    <style>
    th { background-color: #00416d !important; color: white !important; text-align: center !important; }
    td { text-align: center !important; font-weight: bold !important; border: 1px solid #eee !important; padding: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# قائمة الشركات
STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']

if 'signal_start' not in st.session_state:
    st.session_state.signal_start = {}

results = []

for sym in STOCKS:
    try:
        # جلب البيانات مع تفعيل prepost لإظهار البيانات حتى لو السوق مغلق
        df = yf.download(sym, period='2d', interval='1m', progress=False, prepost=True)
        
        if not df.empty and len(df) > 10:
            curr_p = float(df['Close'].iloc[-1])
            high_d = float(df['High'].max())
            low_d = float(df['Low'].min())
            
            # المؤشرات الفنية
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            m_val = float(macd.iloc[-1, 0])
            s_val = float(macd.iloc[-1, 2])
            
            # السيولة
            v_now = df['Volume'].iloc[-1]
            v_avg = df['Volume'].rolling(5).mean().iloc[-1]
            v_ratio = float(v_now / v_avg) if v_avg > 0 else 1.0
            
            icon, status, bg, tc, target = "⚪", "انتظار", "#FFFFFF", "black", "-"
            
            # منطق "قوي الآن" والأهداف
            if m_val > s_val:
                target = f"{curr_p + (high_d - low_d)*0.03:.2f}" # هدف قريب
                if v_ratio > 1.02: icon, status, bg = "🔥", "كول قوي الآن", "#00FF00"
                else: icon, status, bg = "🟢", "كول متابعة", "#90EE90"
            elif m_val < s_val:
                target = f"{curr_p - (high_d - low_d)*0.03:.2f}"
                if v_ratio > 1.02: icon, status, bg, tc = "🔥", "بوت قوي الآن", "#FF0000", "white"
                else: icon, status, bg = "🔴", "بوت متابعة", "#FFCCCB"

            # حساب عداد الثواني
            if "قوي" in status:
                if sym not in st.session_state.signal_start:
                    st.session_state.signal_start[sym] = time.time()
                elapsed = int(time.time() - st.session_state.signal_start[sym])
                time_str = f"{elapsed} ث"
            else:
                st.session_state.signal_start.pop(sym, None)
                time_str = "-"

            results.append({
                "⚡": icon, "السهم": sym, "الحالة": status, "منذ": time_str,
                "السعر": f"{curr_p:.2f}", "الهدف 🎯": target, "السيولة": f"{v_ratio:.2f}x",
                "_bg": bg, "_tc": tc
            })
    except: continue

st.markdown(f'<h2 style="text-align:center; color:#00416d;">🎯 رادار القناص V39: الأهداف والوقت والسيولة</h2>', unsafe_allow_html=True)

if results:
    html = "<table style='width:100%; border-collapse: collapse;'><thead><tr><th>🔥</th><th>السهم</th><th>الحالة</th><th>منذ</th><th>السعر</th><th>الهدف 🎯</th><th>السيولة</th></tr></thead><tbody>"
    for r in results:
        html += f"<tr style='background-color: {r['_bg']}; color: {r['_tc']}; font-weight: bold;'>"
        html += f"<td style='font-size: 22px;'>{r['⚡']}</td><td>{r['السهم']}</td><td>{r['الحالة']}</td><td>{r['منذ']}</td><td>{r['السعر']}</td><td style='color:blue;'>{r['الهدف 🎯']}</td><td>{r['السيولة']}</td></tr>"
    st.markdown(html + "</tbody></table>", unsafe_allow_html=True)
else:
    st.error("❌ فشل في جلب البيانات. يرجى إعادة تشغيل التطبيق (Reboot) من لوحة تحكم Streamlit.")
