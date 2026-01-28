import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث فائق السرعة كل 5 ثوانٍ
st_autorefresh(interval=5000, key="turbo_radar_v22_final")

st.set_page_config(page_title="رادار القناص Turbo", layout="wide")

# --- التنسيق البصري ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    th { background-color: #00416d !important; color: white !important; text-align: center !important; padding: 12px; }
    td { text-align: center !important; font-weight: bold !important; border: 1px solid #eee !important; padding: 10px; }
    .sidebar-content { background-color: #00416d; padding: 15px; border-radius: 10px; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- القائمة الجانبية (دليل الألوان) ---
with st.sidebar:
    st.markdown("""
        <div class="sidebar-content">
            <h3 style="text-align: center; color: #CCFF00;">⚡ دليل نظام Turbo</h3>
            <hr>
            <p>🔵 <b>دخول Call:</b> تقاطع ماكد صاعد لحظي</p>
            <p>🔴 <b>دخول Put:</b> تقاطع ماكد هابط لحظي</p>
            <p>🟡 <b>سيولة عالية:</b> تدفق أموال (🔥)</p>
            <p>🟠 <b>تحذير:</b> تشبع RSI (خطر انعكاس)</p>
            <p style="font-size: 12px; color: #aaa;">* ملاحظة: تم تسريع التقاطعات لصيد البدايات.</p>
        </div>
        """, unsafe_allow_html=True)

# الترويسة
st.markdown(f"""
    <div style="background-color: #00416d; padding: 15px; border-radius: 10px; text-align: center; border-bottom: 5px solid #CCFF00; margin-bottom: 20px;">
        <h2 style="color: white; margin:0;">🚀 رادار القناص V22 (Turbo Mode)</h2>
        <p style="color: #CCFF00; margin:0; font-weight: bold;">صيد التقاطعات اللحظية بفارق زمني صفر ⚡</p>
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
            # محرك MACD السريع جداً (Fast Settings: 5, 13, 4)
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            macd_val = macd['MACD_5_13_4'].iloc[-1]
            sig_val = macd['MACDs_5_13_4'].iloc[-1]
            p_macd = macd['MACD_5_13_4'].iloc[-2]
            p_sig = macd['MACDs_5_13_4'].iloc[-2]
            
            rsi = float(ta.rsi(df['Close'], length=7).iloc[-1]) # RSI قصير المدى
            v_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(5).mean().iloc[-1]
            
            icon, status, bg, tc, fire = "⚪", "هدوء", "white", "black", ""

            if v_ratio > 1.2: 
                fire = "🔥🔥🔥"
                icon, status, bg = "🟡", "سيولة عالية", "#CCFF00"

            # كشف التقاطع الفوري (قبل أن يبتعد السعر)
            if macd_val > sig_val and p_macd <= p_sig:
                if rsi > 80: icon, status, bg, tc = "🟠", "تحذير قمة", "#FFA500", "black"
                else: icon, status, bg, tc = "🔵", "تقاطع Call", "#0D47A1", "white"
            elif macd_val < sig_val and p_macd >= p_sig:
                if rsi < 20: icon, status, bg, tc = "🟠", "تحذير قاع", "#FFA500", "black"
                else: icon, status, bg, tc = "🔴", "تقاطع Put", "#B71C1C", "white"

            results.append({
                "⚡": icon, "الأداة": name, "انفجار": fire, "الحالة": status,
                "السعر": f"{curr_p:.2f}", "السيولة": f"{v_ratio:.2f}x", "RSI": f"{rsi:.1f}",
                "_bg": bg, "_tc": tc
            })
    except: continue

# عرض الجدول
if results:
    table = "<table style='width:100%; text-align:center;'><thead><tr>"
    for col in ["⚡", "الأداة", "انفجار", "الحالة", "السعر", "السيولة", "RSI"]:
        table += f"<th>{col}</th>"
    table += "</tr></thead><tbody>"
    for r in results:
        table += f"<tr style='background-color: {r['_bg']}; color: {r['_tc']}; font-weight: bold;'>"
        table += f"<td>{r['⚡']}</td><td>{r['الأداة']}</td><td>{r['انفجار']}</td><td>{r['الحالة']}</td><td>{r['السعر']}</td><td>{r['السيولة']}</td><td>{r['RSI']}</td></tr>"
    st.markdown(table + "</tbody></table>", unsafe_allow_html=True)

st.sidebar.info(f"آخر تحديث: {pd.Timestamp.now().strftime('%H:%M:%S')}")
