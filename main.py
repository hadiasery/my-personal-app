import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث فائق السرعة
st_autorefresh(interval=5000, key="v27_final_green_now")

st.set_page_config(page_title="رادار القناص - نسخة الآن", layout="wide")

# --- تنسيق إجباري (CSS) لفرض اللون الأخضر ومنع الأزرق تماماً ---
st.markdown("""
    <style>
    th { background-color: #00416d !important; color: white !important; }
    td { text-align: center !important; font-weight: bold !important; border: 1px solid #ddd !important; }
    /* منع أي تداخل للألوان القديمة */
    .call-bg { background-color: #00FF00 !important; color: black !important; }
    .put-bg { background-color: #FF0000 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

STOCKS = {
    '📊 مؤشر سباكس (SPY)': 'SPY', 'أبل (Apple)': 'AAPL', 'نيفيديا (Nvidia)': 'NVDA', 
    'تسلا (Tesla)': 'TSLA', 'مايكروسوفت (MSFT)': 'MSFT', 'أمازون (AMZN)': 'AMZN', 
    'ميتا (Meta)': 'META', 'غوغل (Google)': 'GOOGL', 'نيو (NIO)': 'NIO', 'AMD (AMD)': 'AMD'
}

results = []

for name, sym in STOCKS.items():
    try:
        df = yf.download(sym, period='1d', interval='1m', progress=False)
        
        if not df.empty and len(df) > 10:
            curr_p = df['Close'].iloc[-1]
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            m_val = macd['MACD_5_13_4'].iloc[-1]
            s_val = macd['MACDs_5_13_4'].iloc[-1]
            v_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(5).mean().iloc[-1]
            
            # القيم الافتراضية
            icon, status, bg, tc = "⚪", "انتظار", "white", "black"

            # --- منطق "الآن" وقوة الإشارة ---
            if m_val > s_val:
                if v_ratio > 1.2: 
                    icon, status, bg, tc = "🟢🔥", "كول قوي الآن", "#00FF00", "black" # اللون الأخضر
                else:
                    icon, status, bg, tc = "🟢", "كول (متابعة)", "#90EE90", "black"
            
            elif m_val < s_val:
                if v_ratio > 1.2:
                    icon, status, bg, tc = "🔴🔥", "بوت قوي الآن", "#FF0000", "white" # اللون الأحمر
                else:
                    icon, status, bg, tc = "🔴", "بوت (متابعة)", "#FFCCCB", "black"

            results.append({
                "⚡": icon, "الأداة": name, "الحالة": status,
                "السعر": f"{curr_p:.2f}", "السيولة": f"{v_ratio:.2f}x",
                "_bg": bg, "_tc": tc
            })
    except: continue

if results:
    table = "<table style='width:100%; border-collapse: collapse;'><thead><tr>"
    table += "<th>⚡</th><th>الأداة</th><th>الحالة</th><th>السعر</th><th>السيولة</th></tr></thead><tbody>"
    for r in results:
        # هنا يتم فرض اللون أخضر (#00FF00) أو أحمر رغماً عن أي إعدادات أخرى
        table += f"<tr style='background-color: {r['_bg']}; color: {r['_tc']};'>"
        table += f"<td>{r['⚡']}</td><td>{r['الأداة']}</td><td>{r['الحالة']}</td><td>{r['السعر']}</td><td>{r['السيولة']}</td></tr>"
    st.markdown(table + "</tbody></table>", unsafe_allow_html=True)
