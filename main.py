import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث تلقائي كل دقيقتين
st_autorefresh(interval=120000, key="color_carnival_v8")

st.set_page_config(page_title="رادار هادي الملون", layout="wide")
st.markdown("<h1 style='text-align: center; color: white; background: linear-gradient(to right, #00c6ff, #0072ff); padding: 10px; border-radius: 10px;'>🌈 رادار القناص: نظام الألوان المتكامل</h1>", unsafe_allow_html=True)

# --- قائمة الشركات ---
STOCKS = {
    '📈 مؤشر S&P 500 (SPX)': '^GSPC', 'أبل (Apple)': 'AAPL', 'نيفيديا (Nvidia)': 'NVDA', 
    'تسلا (Tesla)': 'TSLA', 'مايكروسوفت (Microsoft)': 'MSFT', 'أمازون (Amazon)': 'AMZN', 
    'ميتا (Meta)': 'META', 'غوغل (Google)': 'GOOGL', 'نيو (NIO)': 'NIO', 
    'لوسيد (Lucid)': 'LCID', 'AMD (AMD)': 'AMD', 'بالانتير (Palantir)': 'PLTR', 
    'كوين بيز (Coinbase)': 'COIN', 'نتفليكس (Netflix)': 'NFLX'
}

results = []
my_bar = st.progress(0)

for i, (name, sym) in enumerate(STOCKS.items()):
    try:
        data = yf.download(sym, period='7d', interval='5m', progress=False)
        if not data.empty and len(data) > 30:
            data = data.ffill().bfill()
            close_p = data['Close'].squeeze()
            volumes = data['Volume'].squeeze()
            curr_p = float(close_p.iloc[-1])
            
            # المؤشرات
            rsi_val = float(ta.rsi(close_p, length=14).iloc[-1])
            sma_5 = float(ta.sma(close_p, length=5).iloc[-1])
            sma_13 = float(ta.sma(close_p, length=13).iloc[-1])
            macd_h = float(ta.macd(close_p)['MACDh_12_26_9'].iloc[-1])
            prev_high = float(data['High'].squeeze().iloc[-2])
            prev_low = float(data['Low'].squeeze().iloc[-2])
            
            # قوة السيولة (حساسية عالية)
            vol_ratio = volumes.iloc[-1] / volumes.rolling(window=10).mean().iloc[-1]
            is_explosion = vol_ratio > 1.25 

            status, color = "⚪ هدوء", "transparent"
            
            # --- منطق الألوان المتعدد (الكرنفال) ---
            
            # 1. حالة التشبع (مراقبة)
            if rsi_val < 35:
                status, color = "🟢 رخيص (مراقبة Call)", "#2E7D32"
            elif rsi_val > 65:
                status, color = "🟠 متضخم (مراقبة Put)", "#E65100"

            # 2. حالة الانفجار (أولوية أعلى)
            if is_explosion:
                status, color = "⚡ انفجار سيولة", "#CCFF00"
            
            # 3. حالة التأكيد (الأولوية القصوى - دخول)
            if (curr_p > prev_high) and (sma_5 > sma_13) and (macd_h > 0) and rsi_val < 50:
                status, color = "🔵 دخول Call مؤكد", "#0D47A1"
            elif (curr_p < prev_low) and (sma_5 < sma_13) and (macd_h < 0) and rsi_val > 50:
                status, color = "🔴 دخول Put مؤكد", "#B71C1C"

            results.append({
                "الأداة": name, "الحالة": status, "السعر": f"{curr_p:.2f}",
                "قوة السيولة": f"{vol_ratio:.2f}x", "RSI": round(rsi_val, 1),
                "الاتجاه": "📈 صاعد" if macd_h > 0 else "📉 هابط", "_color": color
            })
    except: continue
    my_bar.progress((i + 1) / len(STOCKS))

# --- العرض ---
if results:
    df = pd.DataFrame(results)
    def apply_style(row):
        txt_color = "black" if row['_color'] == "#CCFF00" else "white"
        return [f'background-color: {row["_color"]}; color: {txt_color}; font-weight: bold' if row['_color'] != "transparent" else '' for _ in row]
    
    st.dataframe(df.style.apply(apply_style, axis=1), column_order=("الأداة", "الحالة", "السعر", "قوة السيولة", "RSI", "الاتجاه"), use_container_width=True, hide_index=True, height=600)

st.sidebar.markdown("""
### 🎨 خريطة الألوان الجديدة:
- **الأزرق 🔵:** انفجار + اختراق (وقت الـ **Call**).
- **الأحمر 🔴:** انفجار + كسر (وقت الـ **Put**).
- **الفسفوري ⚡:** سيولة ضخمة تدخل الآن.
- **الأخضر 🟢:** السهم رخيص (صيد قادم).
- **البرتقالي 🟠:** السهم غالي (تصريف قادم).
""")
