import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث تلقائي كل 10 ثوانٍ
st_autorefresh(interval=10000, key="mega_spx_radar_v20_pro")

st.set_page_config(page_title="رادار القناص الاحترافي", layout="wide")

# --- تنسيق الواجهة ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    th { background-color: #00416d !important; color: white !important; text-align: center !important; }
    td { text-align: center !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"""
    <div style="background-color: #00416d; padding: 15px; border-radius: 10px; text-align: center; border-bottom: 5px solid #CCFF00; margin-bottom: 20px;">
        <h2 style="color: white; margin:0;">🚀 رادار القناص V20: نظام التحذير الذكي</h2>
        <p style="color: #CCFF00; margin:0;">🔥 مراقبة السيولة + ⚠️ تنبيهات التشبع</p>
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
            
            status, color, fire = "⚪ هدوء", "transparent", ""
            
            # 1. فحص السيولة (النار)
            if v_ratio > 1.2:
                fire = "🔥🔥🔥"
                status, color = "⚡ سيولة عالية", "#CCFF00"
            
            # 2. فحص الدخول مع التحذير (RSI)
            if curr_p > p_high and macd_h > 0:
                if rsi > 75:
                    status, color = "⚠️ Call (خطر قمة!)", "#FFA500" # برتقالي للتحذير
                else:
                    status, color = "🔵 دخول Call مؤكد", "#0D47A1"
            elif curr_p < p_low and macd_h < 0:
                if rsi < 25:
                    status, color = "⚠️ Put (خطر قاع!)", "#FFA500" # برتقالي للتحذير
                else:
                    status, color = "🔴 دخول Put مؤكد", "#B71C1C"

            results.append({
                "الأداة": name, "انفجار": fire, "الحالة": status, 
                "السعر": f"{curr_p:.2f}", "قوة السيولة": f"{v_ratio:.2f}x", 
                "RSI": f"{rsi:.1f}", "الاتجاه": "📈 صاعد" if macd_h > 0 else "📉 هابط",
                "_color": color 
            })
    except: continue

if results:
    df_res = pd.DataFrame(results)
    def apply_row_style(row):
        color = row['_color']
        text_color = "black" if color in ["#CCFF00", "#FFA500"] else "white"
        if color == "transparent": return ['color: #333333'] * len(row)
        return [f'background-color: {color}; color: {text_color}; border: 1px solid #ccc'] * len(row)

    st.table(df_res.style.apply(apply_row_style, axis=1).hide(axis='columns', subset=['_color']))

st.sidebar.info("اللون البرتقالي ⚠️ يعني تشبع السعر، انتظر قليلاً ولا تندفع.")
