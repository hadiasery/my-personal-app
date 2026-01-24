import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث تلقائي كل 10 ثوانٍ
st_autorefresh(interval=10000, key="mega_spx_radar_v20_final_fix")

st.set_page_config(page_title="رادار القناص الاحترافي", layout="wide")

# --- تنسيق الواجهة الشامل ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .legend-box { padding: 8px 15px; border-radius: 5px; margin: 5px; display: inline-block; font-weight: bold; color: white; font-size: 14px; }
    /* تنسيق الجدول لضمان الألوان */
    table { width: 100%; border-collapse: collapse; }
    th { background-color: #00416d !important; color: white !important; padding: 10px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# الترويسة
st.markdown(f"""
    <div style="background-color: #00416d; padding: 15px; border-radius: 10px; text-align: center; border-bottom: 5px solid #CCFF00; margin-bottom: 10px;">
        <h2 style="color: white; margin:0;">🚀 رادار القناص V20: النسخة الكاملة</h2>
    </div>
    """, unsafe_allow_html=True)

# --- دليل الألوان (الرموز) ---
st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <div class="legend-box" style="background-color: #0D47A1;">🔵 Call (شراء)</div>
        <div class="legend-box" style="background-color: #B71C1C;">🔴 Put (بيع)</div>
        <div class="legend-box" style="background-color: #CCFF00; color: black;">🔥🔥 سيولة عالية</div>
        <div class="legend-box" style="background-color: #FFA500; color: black;">⚠️ تحذير تشبع</div>
        <div class="legend-box" style="background-color: #f8f9fa; color: black; border: 1px solid #ccc;">⚪ هدوء</div>
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
            
            status, color, fire = "⚪ هدوء", "white", ""
            t_color = "black"
            
            # منطق الألوان (V20)
            if v_ratio > 1.2:
                fire = "🔥🔥🔥"
                status, color = "⚡ سيولة عالية", "#CCFF00"
                t_color = "black"
            
            if curr_p > p_high and macd_h > 0:
                if rsi > 75:
                    status, color, t_color = "⚠️ Call (خطر قمة!)", "#FFA500", "black"
                else:
                    status, color, t_color = "🔵 دخول Call مؤكد", "#0D47A1", "white"
            elif curr_p < p_low and macd_h < 0:
                if rsi < 25:
                    status, color, t_color = "⚠️ Put (خطر قاع!)", "#FFA500", "black"
                else:
                    status, color, t_color = "🔴 دخول Put مؤكد", "#B71C1C", "white"

            results.append({
                "الأداة": name, "انفجار": fire, "الحالة": status, 
                "السعر": f"{curr_p:.2f}", "قوة السيولة": f"{v_ratio:.2f}x", 
                "RSI": f"{rsi:.1f}", "الاتجاه": "📈 صاعد" if macd_h > 0 else "📉 هابط",
                "bg": color, "tc": t_color
            })
    except: continue

# عرض الجدول باستخدام HTML لضمان ثبات الألوان
if results:
    html_table = "<table style='width:100%; text-align:center; border: 1px solid #ddd;'><thead>"
    html_table += "<tr><th>الأداة</th><th>انفجار</th><th>الحالة</th><th>السعر</th><th>السيولة</th><th>RSI</th><th>الاتجاه</th></tr></thead><tbody>"
    
    for r in results:
        html_table += f"<tr style='background-color: {r['bg']}; color: {r['tc']}; font-weight: bold; border: 1px solid #ddd;'>"
        html_table += f"<td>{r['الأداة']}</td><td>{r['انفجار']}</td><td>{r['الحالة']}</td>"
        html_table += f"<td>{r['السعر']}</td><td>{r['قوة السيولة']}</td><td>{r['RSI']}</td><td>{r['الاتجاه']}</td></tr>"
    
    html_table += "</tbody></table>"
    st.markdown(html_table, unsafe_allow_html=True)

st.sidebar.write(f"آخر تحديث: {pd.Timestamp.now().strftime('%H:%M:%S')}")
