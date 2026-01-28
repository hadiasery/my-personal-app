import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث كل 5 ثوانٍ لضمان السرعة
st_autorefresh(interval=5000, key="fixed_green_turbo_v24")

st.set_page_config(page_title="رادار القناص الأخضر", layout="wide")

# --- تنسيق الألوان الإجباري ---
st.markdown("""
    <style>
    th { background-color: #00416d !important; color: white !important; }
    td { text-align: center !important; font-weight: bold !important; border: 1px solid #eee !important; }
    </style>
    """, unsafe_allow_html=True)

# ترويسة الرادار
st.markdown(f"""
    <div style="background-color: #00416d; padding: 15px; border-radius: 10px; text-align: center; border-bottom: 5px solid #00FF00; margin-bottom: 20px;">
        <h2 style="color: white; margin:0;">🚀 رادار القناص: نظام التقاطع الأخضر (V24)</h2>
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
        ticker = yf.Ticker(sym)
        curr_p = ticker.fast_info['last_price']
        df = ticker.history(period='1d', interval='1m')
        
        if not df.empty and len(df) > 15:
            # محرك MACD فائق السرعة
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            m_val = macd['MACD_5_13_4'].iloc[-1]
            s_val = macd['MACDs_5_13_4'].iloc[-1]
            pm_val = macd['MACD_5_13_4'].iloc[-2]
            ps_val = macd['MACDs_5_13_4'].iloc[-2]
            
            v_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(5).mean().iloc[-1]
            
            # القيم الافتراضية (هدوء)
            icon, status, bg, tc, fire = "⚪", "هدوء", "white", "black", ""

            # شرط السيولة (فسفوري)
            if v_ratio > 1.2:
                fire = "🔥🔥🔥"
                icon, status, bg = "🟡", "سيولة عالية", "#CCFF00"

            # --- فرض اللون الأخضر للتقاطع الصاعد ---
            if m_val > s_val and pm_val <= ps_val:
                icon, status, bg, tc = "🟢", "دخول Call (أخضر)", "#00FF00", "black"
            
            # --- فرض اللون الأحمر للتقاطع الهابط ---
            elif m_val < s_val and pm_val >= ps_val:
                icon, status, bg, tc = "🔴", "دخول Put (أحمر)", "#FF0000", "white"

            results.append({
                "⚡": icon, "الأداة": name, "انفجار": fire, "الحالة": status,
                "السعر": f"{curr_p:.2f}", "السيولة": f"{v_ratio:.2f}x",
                "_bg": bg, "_tc": tc
            })
    except: continue

if results:
    # بناء الجدول يدوياً لضمان عدم تدخل نظام ستريم ليت في الألوان
    table = "<table style='width:100%; border-collapse: collapse;'><thead><tr>"
    table += "<th style='padding:10px;'>⚡</th><th>الأداة</th><th>انفجار</th><th>الحالة</th><th>السعر</th><th>السيولة</th></tr></thead><tbody>"
    for r in results:
        table += f"<tr style='background-color: {r['_bg']}; color: {r['_tc']};'>"
        table += f"<td>{r['⚡']}</td><td>{r['الأداة']}</td><td>{r['انفجار']}</td><td>{r['الحالة']}</td><td>{r['السعر']}</td><td>{r['السيولة']}</td></tr>"
    st.markdown(table + "</tbody></table>", unsafe_allow_html=True)
    
