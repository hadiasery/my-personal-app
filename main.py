import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث كل 5 ثوانٍ بدلاً من 10 لزيادة السرعة
st_autorefresh(interval=5000, key="turbo_radar_v22")

st.set_page_config(page_title="رادار القناص Turbo", layout="wide")

# --- دليل الألوان في اليسار ---
st.sidebar.markdown("""
    <div style="background-color: #00416d; padding: 15px; border-radius: 10px; color: white;">
        <h3 style="text-align: center; color: #CCFF00;">⚡ نظام Turbo السريع</h3>
        <hr>
        <p>🔵 <b>Call:</b> تقاطع سريع صاعد</p>
        <p>🔴 <b>Put:</b> تقاطع سريع هابط</p>
        <p>🟡 <b>سيولة:</b> دخول أموال (🔥)</p>
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
        # جلب بيانات أكثر تفصيلاً (آخر 100 دقيقة) للسرعة
        df = ticker.history(period='1d', interval='1m')
        
        if not df.empty and len(df) > 20:
            # استخدام إعدادات MACD سريعة جداً (Fast MACD)
            # 5, 13, 4 بدلاً من 12, 26, 9
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            macd_val = macd['MACD_5_13_4'].iloc[-1]
            signal_val = macd['MACDs_5_13_4'].iloc[-1]
            prev_macd = macd['MACD_5_13_4'].iloc[-2]
            prev_signal = macd['MACDs_5_13_4'].iloc[-2]
            
            rsi = float(ta.rsi(df['Close'], length=7).iloc[-1]) # RSI سريع أيضاً
            v_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(5).mean().iloc[-1]
            
            status_icon, bg_color, text_color = "⚪", "white", "black"
            status_text, fire = "هدوء", ""

            # شرط السيولة
            if v_ratio > 1.2:
                fire = "🔥🔥🔥"

            # --- محرك التقاطع اللحظي السريع ---
            # تقاطع صاعد (الماكد يخترق الإشارة للأعلى)
            if macd_val > signal_val and prev_macd <= prev_signal:
                status_icon, status_text, bg_color, text_color = "🔵", "تقاطع Call فوري", "#0D47A1", "white"
            # تقاطع هابط (الماكد يكسر الإشارة للأسفل)
            elif macd_val < signal_val and prev_macd >= prev_signal:
                status_icon, status_text, bg_color, text_color = "🔴", "تقاطع Put فوري", "#B71C1C", "white"
            # استمرار الاتجاه مع سيولة
            elif v_ratio > 1.2:
                status_icon, status_text, bg_color = "🟡", "انفجار سيولة", "#CCFF00"

            results.append({
                "⚡": status_icon,
                "الأداة": name,
                "انفجار": fire,
                "الحالة": status_text,
                "السعر": f"{curr_p:.2f}",
                "السيولة": f"{v_ratio:.2f}x",
                "RSI": f"{rsi:.1f}",
                "_bg": bg_color,
                "_tc": text_color
            })
    except: continue

# عرض الجدول
if results:
    table_html = """<table style="width:100%; text-align:center;">
    <thead><tr style="background-color:#00416d; color:white;">
        <th>⚡</th><th>الأداة</th><th>انفجار</th><th>الحالة</th><th>السعر</th><th>السيولة</th><th>RSI</th>
    </tr></thead><tbody>"""
    for r in results:
        table_html += f"""<tr style="background-color: {r['_bg']}; color: {r['_tc']}; font-weight: bold;">
            <td style="font-size: 20px;">{r['⚡']}</td><td>{r['الأداة']}</td><td>{r['انفجار']}</td>
            <td>{r['الحالة']}</td><td>{r['السعر']}</td><td>{r['السيولة']}</td><td>{r['RSI']}</td>
        </tr>"""
    st.markdown(table_html + "</tbody></table>", unsafe_allow_html=True)
