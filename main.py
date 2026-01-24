import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث تلقائي كل 10 ثوانٍ
st_autorefresh(interval=10000, key="mega_spx_radar_final_v21")

st.set_page_config(page_title="رادار القناص V20", layout="wide")

# --- دليل الألوان في الجهة اليسرى (Sidebar) ---
st.sidebar.markdown("""
    <div style="background-color: #00416d; padding: 15px; border-radius: 10px; color: white;">
        <h3 style="text-align: center; color: #CCFF00;">🎨 دليل الألوان</h3>
        <hr>
        <p>🔵 <b>دخول Call:</b> سعر مخترق + ماكد صاعد</p>
        <p>🔴 <b>دخول Put:</b> سعر مكسور + ماكد هابط</p>
        <p>🟡 <b>سيولة عالية:</b> انفجار فوليوم (🔥)</p>
        <p>🟠 <b>تحذير:</b> تشبع RSI (قمة/قاع)</p>
        <p>⚪ <b>هدوء:</b> انتظار الإشارة</p>
    </div>
    """, unsafe_allow_html=True)

# --- تنسيق واجهة الجدول ---
st.markdown("""
    <style>
    th { background-color: #00416d !important; color: white !important; text-align: center !important; }
    td { text-align: center !important; font-weight: bold !important; border: 1px solid #ddd !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"""
    <div style="background-color: #00416d; padding: 15px; border-radius: 10px; text-align: center; border-bottom: 5px solid #CCFF00; margin-bottom: 20px;">
        <h2 style="color: white; margin:0;">🚀 رادار القناص SPX والأسهم (V20)</h2>
        <p style="color: #CCFF00; margin:0; font-weight: bold;">تحديث البيانات اللحظي: كل 10 ثوانٍ 🔍</p>
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
        df = ticker.history(period='2d', interval='1m')
        
        if not df.empty and len(df) > 1:
            close_s = df['Close'].squeeze()
            rsi = float(ta.rsi(close_s, length=14).iloc[-1])
            macd = ta.macd(close_s)
            macd_h = float(macd['MACDh_12_26_9'].iloc[-1])
            p_high = float(df['High'].iloc[-2])
            p_low = float(df['Low'].iloc[-2])
            v_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
            
            # تحديد الأيقونة واللون
            status_icon, bg_color, text_color = "⚪", "white", "black"
            status_text = "هدوء"
            fire = ""

            if v_ratio > 1.2:
                fire = "🔥🔥🔥"
                status_icon, status_text, bg_color = "🟡", "انفجار سيولة", "#CCFF00"

            if curr_p > p_high and macd_h > 0:
                if rsi > 75:
                    status_icon, status_text, bg_color = "🟠", "تحذير قمة", "#FFA500"
                else:
                    status_icon, status_text, bg_color, text_color = "🔵", "دخول Call", "#0D47A1", "white"
            elif curr_p < p_low and macd_h < 0:
                if rsi < 25:
                    status_icon, status_text, bg_color = "🟠", "تحذير قاع", "#FFA500"
                else:
                    status_icon, status_text, bg_color, text_color = "🔴", "دخول Put", "#B71C1C", "white"

            results.append({
                "الإشارة": status_icon, # هذا هو عمود الأيقونة الملونة
                "الأداة": name,
                "انفجار": fire,
                "الحالة": status_text,
                "السعر": f"{curr_p:.2f}",
                "السيولة": f"{v_ratio:.2f}x",
                "RSI": f"{rsi:.1f}",
                "الاتجاه": "📈 صاعد" if macd_h > 0 else "📉 هابط",
                "_bg": bg_color,
                "_tc": text_color
            })
    except: continue

# عرض الجدول بنظام HTML لضمان ثبات الألوان والأيقونات
if results:
    table_html = """<table style="width:100%;">
    <thead><tr>
        <th>الإشارة</th><th>الأداة</th><th>انفجار</th><th>الحالة</th><th>السعر</th><th>السيولة</th><th>RSI</th><th>الاتجاه</th>
    </tr></thead><tbody>"""
    
    for r in results:
        table_html += f"""
        <tr style="background-color: {r['_bg']}; color: {r['_tc']};">
            <td style="font-size: 24px;">{r['الإشارة']}</td>
            <td>{r['الأداة']}</td>
            <td>{r['انفجار']}</td>
            <td>{r['الحالة']}</td>
            <td>{r['السعر']}</td>
            <td>{r['السيولة']}</td>
            <td>{r['RSI']}</td>
            <td>{r['الاتجاه']}</td>
        </tr>"""
    
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)

st.sidebar.success("الرادار يعمل الآن.. راقب الإشارات 🎯")
