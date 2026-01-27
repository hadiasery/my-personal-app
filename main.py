import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث كل 5 ثوانٍ
st_autorefresh(interval=5000, key="smart_power_radar_v25")

st.set_page_config(page_title="رادار القناص - فلتر القوة", layout="wide")

# --- التنسيق ---
st.markdown("""
    <style>
    th { background-color: #00416d !important; color: white !important; }
    td { text-align: center !important; font-weight: bold !important; border: 1px solid #eee !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"""
    <div style="background-color: #00416d; padding: 15px; border-radius: 10px; text-align: center; border-bottom: 5px solid #00FF00; margin-bottom: 20px;">
        <h2 style="color: white; margin:0;">🚀 رادار القناص: نظام تقييم قوة الصفقات (V25)</h2>
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
            # محرك MACD السريع
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            m_val = macd['MACD_5_13_4'].iloc[-1]
            s_val = macd['MACDs_5_13_4'].iloc[-1]
            pm_val = macd['MACD_5_13_4'].iloc[-2]
            ps_val = macd['MACDs_5_13_4'].iloc[-2]
            
            v_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(5).mean().iloc[-1]
            
            # القيم الافتراضية
            icon, status, bg, tc = "⚪", "انتظار (هدوء)", "white", "black"

            # --- منطق تقييم القوة ---
            
            # 1. حالة الـ Call
            if m_val > s_val and pm_val <= ps_val:
                if v_ratio > 1.3: # تقاطع + سيولة عالية
                    icon, status, bg, tc = "🟢🔥", "Call قوي جداً", "#00FF00", "black"
                else: # تقاطع + سيولة عادية
                    icon, status, bg, tc = "🟢", "Call ضعيف (حذر)", "#90EE90", "black" # أخضر فاتح للضعيف
            
            # 2. حالة الـ Put
            elif m_val < s_val and pm_val >= ps_val:
                if v_ratio > 1.3: # كسر + سيولة عالية
                    icon, status, bg, tc = "🔴🔥", "Put قوي جداً", "#FF0000", "white"
                else: # كسر + سيولة عادية
                    icon, status, bg, tc = "🔴", "Put ضعيف (حذر)", "#FFCCCB", "black" # أحمر فاتح للضعيف

            # 3. حالة انفجار سيولة بدون تقاطع
            elif v_ratio > 1.5:
                icon, status, bg, tc = "🟡", "سيولة ضخمة (ترقب)", "#CCFF00", "black"

            results.append({
                "⚡": icon, "الأداة": name, "القوة والحالة": status,
                "السعر": f"{curr_p:.2f}", "السيولة": f"{v_ratio:.2f}x",
                "_bg": bg, "_tc": tc
            })
    except: continue

if results:
    table = "<table style='width:100%; border-collapse: collapse;'><thead><tr>"
    table += "<th>⚡</th><th>الأداة</th><th>القوة والحالة</th><th>السعر</th><th>السيولة</th></tr></thead><tbody>"
    for r in results:
        table += f"<tr style='background-color: {r['_bg']}; color: {r['_tc']};'>"
        table += f"<td>{r['⚡']}</td><td>{r['الأداة']}</td><td>{r['القوة والحالة']}</td><td>{r['السعر']}</td><td>{r['السيولة']}</td></tr>"
    st.markdown(table + "</tbody></table>", unsafe_allow_html=True)

st.sidebar.info("الفرق بين القوي والضعيف هو حجم السيولة لحظة التقاطع.")
