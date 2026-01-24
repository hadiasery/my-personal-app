import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث تلقائي كل 10 ثوانٍ
st_autorefresh(interval=10000, key="mega_spx_radar_v18")

st.set_page_config(page_title="رادار القناص V18", layout="wide")

# --- تنسيق الواجهة (Dark Mode) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stTable"] { background-color: #1e2227; border-radius: 10px; }
    th { background-color: #262730 !important; color: #CCFF00 !important; text-align: center !important; }
    td { text-align: center !important; }
    </style>
    """, unsafe_allow_html=True)

# عداد الثواني والترويسة
st.markdown(f"""
    <div style="background-color: #00416d; padding: 15px; border-radius: 10px; text-align: center; border-bottom: 4px solid #CCFF00; margin-bottom: 20px;">
        <h2 style="color: white; margin:0;">🚀 رادار القناص: SPX والأسهم (V18)</h2>
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
        # سحب السعر اللحظي (أسرع طريقة)
        curr_p = ticker.fast_info['last_price']
        
        # سحب البيانات للمؤشرات
        df = ticker.history(period='2d', interval='1m')
        if not df.empty and len(df) > 1:
            close_s = df['Close'].squeeze()
            
            # المؤشرات
            rsi = float(ta.rsi(close_s, length=14).iloc[-1])
            macd = ta.macd(close_s)
            macd_h = float(macd['MACDh_12_26_9'].iloc[-1])
            
            # حماية الاختراق (مقارنة بالسعر الحالي)
            p_high = float(df['High'].iloc[-2])
            p_low = float(df['Low'].iloc[-2])
            
            # قوة السيولة
            v_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
            
            status, color = "⚪ هدوء", "transparent"
            
            # منطق الألوان V10
            if v_ratio > 1.2: status, color = "⚡ انفجار سيولة", "#CCFF00"
            
            if curr_p > p_high and macd_h > 0:
                status, color = "🔵 دخول Call مؤكد", "#0D47A1"
            elif curr_p < p_low and macd_h < 0:
                status, color = "🔴 دخول Put مؤكد", "#B71C1C"

            results.append({
                "الأداة": name, "الحالة": status, "السعر": f"{curr_p:.2f}",
                "قوة السيولة": f"{v_ratio:.2f}x", "RSI": f"{rsi:.1f}",
                "الاتجاه": "📈 صاعد" if macd_h > 0 else "📉 هابط",
                "_color": color # هذا العمود سيتم استخدامه للتلوين ثم إخفاؤه
            })
    except: continue

# --- عرض الجدول المصلح ---
if results:
    df_res = pd.DataFrame(results)
    
    def apply_row_style(row):
        color = row['_color']
        text_color = "black" if color == "#CCFF00" else "white"
        if color == "transparent":
            return ['color: #d1d1d1'] * len(row)
        return [f'background-color: {color}; color: {text_color}; font-weight: bold; border: 1px solid #444'] * len(row)

    # التلوين يتم هنا بينما العمود _color موجود، ثم نقوم بإخفاء العمود بصرياً
    styled_df = df_res.style.apply(apply_row_style, axis=1)
    
    # إخفاء عمود الألوان من العرض النهائي فقط
    st.table(styled_df.hide(axis='columns', subset=['_color']))

st.sidebar.info(f"آخر تحديث: {pd.Timestamp.now().strftime('%I:%M:%S %p')}")
