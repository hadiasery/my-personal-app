import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import time

# تحديث تلقائي كل 10 ثوانٍ لمواكبة عقود الأوبشن اللحظية
st_autorefresh(interval=10000, key="mega_spx_radar_v9_fast")

st.set_page_config(page_title="رادار هادي V9 - العداد", layout="wide")

# --- إضافة عداد الثواني التنازلي في أعلى الصفحة ---
countdown_placeholder = st.empty()
with countdown_placeholder.container():
    st.markdown(f"""
        <div style="background-color: #1e1e1e; padding: 10px; border-radius: 10px; border: 1px solid #333; text-align: center; margin-bottom: 20px;">
            <span style="color: white; font-size: 18px;">🔄 تحديث البيانات القادم خلال: </span>
            <span style="color: #CCFF00; font-size: 24px; font-weight: bold;">10 ثوانٍ</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: white; background: linear-gradient(to right, #1e3c72, #2a5298); padding: 15px; border-radius: 10px;'>🚀 رادار القناص: SPX والأسهم (V9 + عداد)</h1>", unsafe_allow_html=True)

# --- قائمة الأسهم الأصلية لنسخة V9 ---
STOCKS = {
    '📊 مؤشر سباكس (SPY/SPX)': 'SPY', 
    'أبل (Apple)': 'AAPL', 
    'نيفيديا (Nvidia)': 'NVDA', 
    'تسلا (Tesla)': 'TSLA', 
    'مايكروسوفت (Microsoft)': 'MSFT', 
    'أمازون (Amazon)': 'AMZN', 
    'ميتا (Meta)': 'META', 
    'غوغل (Google)': 'GOOGL', 
    'نيو (NIO)': 'NIO', 
    'لوسيد (Lucid)': 'LCID',
    'AMD (AMD)': 'AMD', 
    'بالانتير (Palantir)': 'PLTR', 
    'كوين بيز (Coinbase)': 'COIN', 
    'نتفليكس (Netflix)': 'NFLX'
}

results = []
my_bar = st.progress(0)

# --- محرك التحليل الفني ---
for i, (name, sym) in enumerate(STOCKS.items()):
    try:
        # جلب البيانات بفاصل دقيقة واحدة لزيادة الحساسية
        data = yf.download(sym, period='2d', interval='1m', progress=False)
        if not data.empty and len(data) > 20:
            data = data.ffill().bfill()
            close_p = data['Close'].squeeze()
            volumes = data['Volume'].squeeze()
            curr_p = float(close_p.iloc[-1])
            
            # المؤشرات الفنية
            rsi_val = float(ta.rsi(close_p, length=14).iloc[-1])
            sma_5 = float(ta.sma(close_p, length=5).iloc[-1])
            sma_13 = float(ta.sma(close_p, length=13).iloc[-1])
            macd = ta.macd(close_p)
            macd_h = float(macd['MACDh_12_26_9'].iloc[-1])
            
            # حماية الاختراق
            prev_high = float(data['High'].squeeze().iloc[-2])
            prev_low = float(data['Low'].squeeze().iloc[-2])
            
            # قوة السيولة (1.2x)
            avg_vol = volumes.rolling(window=10).mean().iloc[-1]
            vol_ratio = volumes.iloc[-1] / avg_vol
            is_explosion = vol_ratio > 1.2

            status, color = "⚪ هدوء", "transparent"
            
            # منطق الألوان الأصلي لنسخة V9
            if rsi_val < 35: status, color = "🟢 رخيص (مراقبة Call)", "#2E7D32"
            elif rsi_val > 65: status, color = "🟠 متضخم (مراقبة Put)", "#E65100"

            if is_explosion: status, color = "⚡ انفجار سيولة", "#CCFF00"
            
            if (curr_p > prev_high) and (sma_5 > sma_13) and (macd_h > 0):
                status, color = "🔵 دخول Call مؤكد", "#0D47A1"
            elif (curr_p < prev_low) and (sma_5 < sma_13) and (macd_h < 0):
                status, color = "🔴 دخول Put مؤكد", "#B71C1C"

            results.append({
                "الأداة": name, "الحالة": status, "السعر": f"{curr_p:.2f}",
                "قوة السيولة": f"{vol_ratio:.2f}x", "RSI": round(rsi_val, 1),
                "الاتجاه": "📈 صاعد" if macd_h > 0 else "📉 هابط", "_color": color
            })
    except: continue
    my_bar.progress((i + 1) / len(STOCKS))

# --- عرض الجدول ---
if results:
    df = pd.DataFrame(results)
    def apply_style(row):
        txt_color = "black" if row['_color'] == "#CCFF00" else "white"
        if row['_color'] != "transparent":
            return [f'background-color: {row["_color"]}; color: {txt_color}; font-weight: bold'] * len(row)
        return [''] * len(row)
    
    # استخدام st.table لضمان استقرار العرض أثناء التحديثات السريعة
    st.table(df.drop(columns=['_color']))

st.sidebar.markdown("""
### 💡 نصائح نسخة الثواني:
1. **العداد:** يخبرك متى سيتم سحب أحدث سعر وسيولة من السوق.
2. **السيولة:** إذا رأيت الرقم يتجاوز **1.50x** مع لون أزرق أو أحمر، فهذا دخول مؤسساتي قوي.
3. **الدقة:** تم استخدام فاصل الدقيقة لضمان أعلى دقة ممكنة في السعر اللحظي.
""")
