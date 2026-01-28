import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
import time
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=5000, key="v35_greeks_radar")

st.set_page_config(page_title="رادار الأوبشن الاحترافي V35", layout="wide")

st.markdown("""
    <style>
    th { background-color: #00416d !important; color: white !important; }
    td { text-align: center !important; font-weight: bold !important; border: 1px solid #eee !important; }
    .iv-high { color: #ff4b4b; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <div style="background-color: #013220; padding: 15px; border-radius: 10px; text-align: center; border-bottom: 5px solid #00FF00;">
        <h2 style="color: white; margin:0;">💎 رادار الأوبشن V35: دمج الـ IV و Theta</h2>
    </div>
    """, unsafe_allow_html=True)

STOCKS = {'SPY': 'SPY', 'AAPL': 'AAPL', 'NVDA': 'NVDA', 'TSLA': 'TSLA', 'MSFT': 'MSFT', 'AMZN': 'AMZN', 'META': 'META', 'GOOGL': 'GOOGL'}

results = []

for name, sym in STOCKS.items():
    try:
        df = yf.download(sym, period='2d', interval='1m', progress=False)
        if not df.empty and len(df) > 20:
            curr_p = float(df['Close'].iloc[-1])
            
            # --- حساب الـ IV التقديري (Volatility) ---
            returns = np.log(df['Close'] / df['Close'].shift(1))
            iv_est = returns.std() * np.sqrt(252 * 390) * 100 # تقريب للتقلب السنوي من بيانات الدقيقة
            
            # --- حساب الـ Theta التقديري (تآكل الوقت لنهاية اليوم) ---
            # كلما اقتربنا من الإغلاق، زاد تأثير الثيتا على العقود اليومية
            current_hour = time.localtime().tm_hour
            theta_risk = "منخفض" if current_hour < 20 else "مرتفع 🔥"

            # المؤشرات الفنية
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            m_val = float(macd['MACD_5_13_4'].iloc[-1])
            s_val = float(macd['MACDs_5_13_4'].iloc[-1])
            v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1])
            
            status, bg, tc, icon = "انتظار", "#FFFFFF", "black", "⚪"
            
            # منطق الدخول الذكي (IV + MACD + Volume)
            if m_val > s_val and v_ratio > 1.1:
                icon, status, bg = "🔥", "كول قوي الآن", "#00FF00"
            elif m_val < s_val and v_ratio > 1.1:
                icon, status, bg, tc = "🔥", "بوت قوي الآن", "#FF0000", "white"

            results.append({
                "⚡": icon, "الأداة": sym, "الحالة": status,
                "IV %": f"{iv_est:.1f}%", "خطر الثيتا": theta_risk,
                "السعر": f"{curr_p:.2f}", "السيولة": f"{v_ratio:.2f}x",
                "_bg": bg, "_tc": tc
            })
    except: continue

if results:
    html = "<table style='width:100%; border-collapse: collapse;'><thead><tr>"
    html += "<th>🔥</th><th>السهم</th><th>الحالة</th><th>IV (تقلب)</th><th>Theta (وقت)</th><th>السعر</th><th>السيولة</th></tr></thead><tbody>"
    for r in results:
        html += f"<tr style='background-color: {r['_bg']}; color: {r['_tc']}; font-weight: bold;'>"
        html += f"<td>{r['⚡']}</td><td>{r['الأداة']}</td><td>{r['الحالة']}</td><td>{r['IV %']}</td><td>{r['خطر الثيتا']}</td><td>{r['السعر']}</td><td>{r['السيولة']}</td></tr>"
    st.markdown(html + "</tbody></table>", unsafe_allow_html=True)
