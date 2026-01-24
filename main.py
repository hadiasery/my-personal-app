import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث تلقائي كل 10 ثوانٍ لضمان السرعة اللحظية
st_autorefresh(interval=10000, key="mega_spx_radar_v17_final")

st.set_page_config(page_title="رادار القناص V17", layout="wide")

# --- تنسيق الواجهة مثل الصورة (Dark Theme) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stTable"] { background-color: #1e2227; border-radius: 10px; }
    th { background-color: #262730 !important; color: #CCFF00 !important; }
    </style>
    """, unsafe_allow_html=True)

# عداد الثواني التنازلي في الأعلى
st.markdown(f"""
    <div style="background-color: #00416d; padding: 10px; border-radius: 10px; text-align: center; border-bottom: 4px solid #CCFF00;">
        <h2 style="color: white; margin:0;">🚀 رادار القناص: SPX والأسهم (V17)</h2>
        <p style="color: #CCFF00; margin:0; font-weight: bold;">🔄 تحديث البيانات خلال: 10 ثوانٍ</p>
    </div>
    """, unsafe_allow_html=True)

# قائمة الأسهم
STOCKS = {
    '📊 مؤشر سباكس (SPY)': 'SPY', 'أبل (Apple)': 'AAPL', 'نيفيديا (Nvidia)': 'NVDA', 
    'تسلا (Tesla)': 'TSLA', 'مايكروسوفت (MSFT)': 'MSFT', 'أمازون (AMZN)': 'AMZN', 
    'ميتا (Meta)': 'META', 'غوغل (Google)': 'GOOGL', 'نيو (NIO)': 'NIO', 
    'AMD (AMD)': 'AMD', 'بالانتير (PLTR)': 'PLTR', 'نتفليكس (NFLX)': 'NFLX'
}

results = []

# --- محرك التحليل السريع (Fast & Accurate) ---
for name, sym in STOCKS.items():
    try:
        ticker = yf.Ticker(sym)
        # جلب السعر اللحظي المباشر (أسرع من الشموع)
        curr_p = ticker.fast_info['last_price']
        
        # جلب بيانات الشموع للمؤشرات
        df = ticker.history(period='2d', interval='1m')
        if not df.empty:
            close_s = df['Close'].squeeze()
            # المؤشرات
            rsi = float(ta.rsi(close_s, length=14).iloc[-1])
            macd = ta.macd(close_s)
            macd_h = float(macd['MACDh_12_26_9'].iloc[-1])
            
            # حماية الاختراق
            p_high = float(df['High'].iloc[-2])
            p_low = float(df['Low'].iloc[-2])
            
            # السيولة
            v_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
            
            status, color = "⚪ هدوء", "transparent"
            
            # نفس منطق الألوان في الصورة
            if v_ratio > 1.2: status, color = "⚡ انفجار سيولة", "#CCFF00"
            
            if curr_p > p_high and macd_h > 0:
                status, color = "🔵 مؤكد Call دخول", "#0D47A1"
            elif curr_p < p_low and macd_h < 0:
                status, color = "🔴 مؤكد Put دخول", "#B71C1C"

            results.append({
                "الأداة": name, "الحالة": status, "السعر": f"{curr_p:.2f}",
                "قوة السيولة": f"{v_ratio:.2f}x", "RSI": f"{rsi:.1f}",
                "الاتجاه": "📈 صاعد" if macd_h > 0 else "📉 هابط", "_color": color
            })
    except: continue

# --- عرض الجدول المنسق ---
if results:
    df_res = pd.DataFrame(results)
    def style_v10(row):
        bg = row['_color']
        text = "black" if bg == "#CCFF00" else "white"
        if bg == "transparent": return ['color: #d1d1d1'] * len(row)
        return [f'background-color: {bg}; color: {text}; font-weight: bold; border: 1px solid #444'] * len(row)

    st.table(df_res.drop(columns=['_color']).style.apply(style_v10, axis=1))

st.sidebar.markdown(f"**آخر تحديث:** {pd.Timestamp.now().strftime('%H:%M:%S')}")
