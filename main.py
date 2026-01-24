import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث تلقائي كل 10 ثوانٍ
st_autorefresh(interval=10000, key="mega_spx_radar_v19")

st.set_page_config(page_title="رادار القناص V19 - White", layout="wide")

# --- تنسيق الواجهة (White Mode) ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; color: #000000; }
    div[data-testid="stTable"] { background-color: #f8f9fa; border-radius: 10px; border: 1px solid #dee2e6; }
    th { background-color: #e9ecef !important; color: #00416d !important; text-align: center !important; border: 1px solid #dee2e6 !important; }
    td { text-align: center !important; border: 1px solid #dee2e6 !important; color: #333333; }
    </style>
    """, unsafe_allow_html=True)

# عداد الثواني والترويسة بتصميم متناسق مع الخلفية البيضاء
st.markdown(f"""
    <div style="background-color: #00416d; padding: 15px; border-radius: 10px; text-align: center; border-bottom: 5px solid #CCFF00; margin-bottom: 20px;">
        <h2 style="color: white; margin:0; font-family: sans-serif;">🚀 رادار القناص: SPX والأسهم (V19)</h2>
        <p style="color: #CCFF00; margin:0; font-weight: bold; font-size: 18px;">🔄 التحديث التلقائي: كل 10 ثوانٍ</p>
    </div>
    """, unsafe_allow_html=True)

STOCKS = {
    '📊 مؤشر سباكس (SPY)': 'SPY', 'أبل (Apple)': 'AAPL', 'نيفيديا (Nvidia)': 'NVDA', 
    'تسلا (Tesla)': 'TSLA', 'مايكروسوفت (MSFT)': 'MSFT', 'أمازون (AMZN)': 'AMZN', 
    'ميتا (Meta)': 'META', 'غوغل (Google)': 'GOOGL', 'نيو (NIO)': 'NIO', 
    'AMD (AMD)': 'AMD', 'بالانتير (PLTR)': 'PLTR', 'نتفليكس (NFLX)': 'NFLX'
}

results = []

# --- محرك التحليل ---
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
            
            status, color = "⚪ هدوء", "transparent"
            
            # منطق الألوان
            if v_ratio > 1.2: status, color = "⚡ انفجار سيولة", "#CCFF00"
            if curr_p > p_high and macd_h > 0:
                status, color = "🔵 دخول Call مؤكد", "#0D47A1"
            elif curr_p < p_low and macd_h < 0:
                status, color = "🔴 دخول Put مؤكد", "#B71C1C"

            results.append({
                "الأداة": name, "الحالة": status, "السعر": f"{curr_p:.2f}",
                "قوة السيولة": f"{v_ratio:.2f}x", "RSI": f"{rsi:.1f}",
                "الاتجاه": "📈 صاعد" if macd_h > 0 else "📉 هابط",
                "_color": color 
            })
    except: continue

# --- عرض الجدول ---
if results:
    df_res = pd.DataFrame(results)
    
    def apply_row_style(row):
        color = row['_color']
        # إذا كانت الخلفية فسفورية نجعل النص أسود، غير ذلك أبيض
        text_color = "black" if color == "#CCFF00" else "white"
        if color == "transparent":
            return ['color: #333333'] * len(row)
        return [f'background-color: {color}; color: {text_color}; font-weight: bold; border: 1px solid #ccc'] * len(row)

    styled_df = df_res.style.apply(apply_row_style, axis=1)
    st.table(styled_df.hide(axis='columns', subset=['_color']))

st.sidebar.markdown(f"**توقيت التحديث:** {pd.Timestamp.now().strftime('%I:%M:%S %p')}")
