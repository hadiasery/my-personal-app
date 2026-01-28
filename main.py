import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث كل 5 ثوانٍ
st_autorefresh(interval=5000, key="v36_fix_visibility")

st.set_page_config(page_title="رادار القناص V36", layout="wide")

st.markdown("""
    <style>
    th { background-color: #00416d !important; color: white !important; text-align: center !important; }
    td { text-align: center !important; font-weight: bold !important; border: 1px solid #eee !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <div style="background-color: #00416d; padding: 15px; border-radius: 10px; text-align: center; border-bottom: 5px solid #00FF00; margin-bottom: 20px;">
        <h2 style="color: white; margin:0;">🚀 رادار القناص V36: إصلاح ظهور البيانات</h2>
    </div>
    """, unsafe_allow_html=True)

# قائمة الشركات
STOCKS = {
    'SPY': 'SPY', 'AAPL': 'AAPL', 'NVDA': 'NVDA', 
    'TSLA': 'TSLA', 'MSFT': 'MSFT', 'AMZN': 'AMZN', 
    'META': 'META', 'GOOGL': 'GOOGL'
}

results = []

for name, sym in STOCKS.items():
    try:
        # استخدام yf.download بدلاً من Ticker.history لثبات أكثر
        df = yf.download(sym, period='1d', interval='1m', progress=False)
        
        if df.empty:
            st.warning(f"⚠️ لا توجد بيانات حالياً لسهم {sym}")
            continue
            
        if len(df) > 10:
            curr_p = float(df['Close'].iloc[-1])
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            m_val = float(macd.iloc[-1, 0])
            s_val = float(macd.iloc[-1, 2])
            v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(5).mean().iloc[-1])
            
            icon, status, bg, tc = "⚪", "انتظار", "white", "black"
            
            if m_val > s_val:
                icon, status, bg = ("🔥", "كول قوي الآن", "#00FF00") if v_ratio > 1.05 else ("🟢", "كول ضعيف", "#90EE90")
            elif m_val < s_val:
                icon, status, bg, tc = ("🔥", "بوت قوي الآن", "#FF0000", "white") if v_ratio > 1.05 else ("🔴", "بوت ضعيف", "#FFCCCB", "black")

            results.append({
                "⚡": icon, "الأداة": name, "الحالة": status,
                "السعر": f"{curr_p:.2f}", "السيولة": f"{v_ratio:.2f}x",
                "_bg": bg, "_tc": tc
            })
    except Exception as e:
        st.error(f"❌ خطأ في {sym}: {e}")

# إذا كانت النتائج فارغة، نظهر رسالة تنبيه
if not results:
    st.info("🔄 جاري الاتصال بسيرفرات الأسعار... تأكد من أن السوق مفتوح حالياً.")
else:
    html = "<table style='width:100%; border-collapse: collapse;'><thead><tr>"
    html += "<th>🔥</th><th>الأداة</th><th>الحالة</th><th>السعر</th><th>السيولة</th></tr></thead><tbody>"
    for r in results:
        html += f"<tr style='background-color: {r['_bg']}; color: {r['_tc']}; font-weight: bold;'>"
        html += f"<td style='font-size: 22px;'>{r['⚡']}</td><td>{r['الأداة']}</td><td>{r['الحالة']}</td><td>{r['السعر']}</td><td>{r['السيولة']}</td></tr>"
    st.markdown(html + "</tbody></table>", unsafe_allow_html=True)
