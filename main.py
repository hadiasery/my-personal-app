import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث فائق السرعة كل 5 ثوانٍ
st_autorefresh(interval=5000, key="fixed_v28_final")

st.set_page_config(page_title="رادار القناص V28", layout="wide")

# --- تنسيق CSS لضمان عدم ظهور اللون الأزرق نهائياً ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    th { background-color: #00416d !important; color: white !important; text-align: center !important; }
    td { text-align: center !important; font-weight: bold !important; border: 1px solid #ddd !important; }
    </style>
    """, unsafe_allow_html=True)

# ترويسة الرادار
st.markdown("""
    <div style="background-color: #00416d; padding: 15px; border-radius: 10px; text-align: center; border-bottom: 5px solid #00FF00; margin-bottom: 20px;">
        <h2 style="color: white; margin:0;">🚀 رادار القناص: نظام التنبيه الفوري (V28)</h2>
    </div>
    """, unsafe_allow_html=True)

STOCKS = {
    '📊 مؤشر سباكس (SPY)': 'SPY', 'أبل (Apple)': 'AAPL', 'نيفيديا (Nvidia)': 'NVDA', 
    'تسلا (Tesla)': 'TSLA', 'مايكروسوفت (MSFT)': 'MSFT', 'أمازون (AMZN)': 'AMZN', 
    'ميتا (Meta)': 'META', 'غوغل (Google)': 'GOOGL', 'نيو (NIO)': 'NIO', 'AMD (AMD)': 'AMD'
}

results = []

for name, sym in STOCKS.items():
    try:
        # جلب البيانات
        df = yf.download(sym, period='1d', interval='1m', progress=False)
        
        if not df.empty and len(df) > 10:
            curr_p = float(df['Close'].iloc[-1])
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            m_val = float(macd['MACD_5_13_4'].iloc[-1])
            s_val = float(macd['MACDs_5_13_4'].iloc[-1])
            v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(5).mean().iloc[-1])
            
            # القيم الافتراضية (هدوء)
            icon, status, bg, tc = "⚪", "انتظار (هدوء)", "#FFFFFF", "black"

            # --- منطق الألوان وكلمة "الآن" ---
            # حالة الـ Call
            if m_val > s_val:
                if v_ratio > 1.2:
                    icon, status, bg, tc = "🟢🔥", "كول قوي الآن", "#00FF00", "black" # أخضر فاقع
                else:
                    icon, status, bg, tc = "🟢", "كول (متابعة)", "#90EE90", "black" # أخضر فاتح
            
            # حالة الـ Put
            elif m_val < s_val:
                if v_ratio > 1.2:
                    icon, status, bg, tc = "🔴🔥", "بوت قوي الآن", "#FF0000", "white" # أحمر فاقع
                else:
                    icon, status, bg, tc = "🔴", "بوت (متابعة)", "#FFCCCB", "black" # أحمر فاتح

            results.append({
                "⚡": icon, "الأداة": name, "الحالة والوقت": status,
                "السعر": f"{curr_p:.2f}", "السيولة": f"{v_ratio:.2f}x",
                "_bg": bg, "_tc": tc
            })
    except Exception as e:
        continue

# عرض الجدول بنظام HTML لضمان ثبات التنسيق
if results:
    html_code = "<table style='width:100%; border-collapse: collapse;'><thead><tr>"
    html_code += "<th>⚡</th><th>الأداة</th><th>الحالة والوقت</th><th>السعر</th><th>السيولة</th></tr></thead><tbody>"
    
    for r in results:
        html_code += f"<tr style='background-color: {r['_bg']}; color: {r['_tc']}; font-weight: bold;'>"
        html_code += f"<td>{r['⚡']}</td><td>{r['الأداة']}</td><td>{r['الحالة والوقت']}</td><td>{r['السعر']}</td><td>{r['السيولة']}</td></tr>"
    
    html_code += "</tbody></table>"
    st.markdown(html_code, unsafe_allow_html=True)
