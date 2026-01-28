import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث كل 5 ثوانٍ
st_autorefresh(interval=5000, key="v37_force_data")

st.set_page_config(page_title="رادار القناص V37", layout="wide")

st.markdown("""
    <style>
    th { background-color: #00416d !important; color: white !important; text-align: center !important; }
    td { text-align: center !important; font-weight: bold !important; border: 1px solid #eee !important; padding: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <div style="background-color: #00416d; padding: 15px; border-radius: 10px; text-align: center; border-bottom: 5px solid #00FF00; margin-bottom: 20px;">
        <h2 style="color: white; margin:0;">🚀 رادار القناص V37: الربط المباشر بالسيرفرات</h2>
    </div>
    """, unsafe_allow_html=True)

# قائمة الشركات المختصرة للتأكد من السرعة
STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']

results = []

for sym in STOCKS:
    try:
        # محاولة جلب البيانات بأسلوب فائق السرعة
        df = yf.download(sym, period='1d', interval='1m', progress=False, ignore_tz=True)
        
        if df is not None and not df.empty:
            # التأكد من أن البيانات تحتوي على أرقام
            curr_p = float(df['Close'].iloc[-1])
            
            # حساب المؤشرات
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            # التعامل مع أسماء الأعمدة الديناميكية في MACD
            m_val = float(macd.iloc[-1, 0])
            s_val = float(macd.iloc[-1, 2])
            
            # السيولة
            v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(5).mean().iloc[-1])
            
            icon, status, bg, tc = "⚪", "انتظار", "#FFFFFF", "black"
            is_strong = v_ratio > 1.05

            if m_val > s_val:
                if is_strong: icon, status, bg = "🔥", "كول قوي الآن", "#00FF00"
                else: icon, status, bg = "🟢", "كول ضعيف", "#90EE90"
            elif m_val < s_val:
                if is_strong: icon, status, bg, tc = "🔥", "بوت قوي الآن", "#FF0000", "white"
                else: icon, status, bg, tc = "🔴", "بوت ضعيف", "#FFCCCB", "black"

            results.append({
                "🔥": icon, "السهم": sym, "الحالة": status,
                "السعر": f"{curr_p:.2f}", "السيولة": f"{v_ratio:.2f}x",
                "_bg": bg, "_tc": tc
            })
    except Exception as e:
        continue

if results:
    html = "<table style='width:100%; border-collapse: collapse;'><thead><tr>"
    html += "<th>إشارة</th><th>السهم</th><th>الحالة والوقت</th><th>السعر</th><th>السيولة</th></tr></thead><tbody>"
    for r in results:
        html += f"<tr style='background-color: {r['_bg']}; color: {r['_tc']}; font-weight: bold;'>"
        html += f"<td style='font-size: 22px;'>{r['🔥']}</td><td>{r['السهم']}</td><td>{r['الحالة']}</td><td>{r['السعر']}</td><td>{r['السيولة']}</td></tr>"
    st.markdown(html + "</tbody></table>", unsafe_allow_html=True)
else:
    # رسالة مساعدة إذا استمرت المشكلة
    st.warning("⚠️ السيرفرات لا تستجيب حالياً. جارِ محاولة الاتصال التلقائي...")
    st.info("نصيحة: تأكد من أن ملف requirements.txt يحتوي على yfinance و pandas-ta")
