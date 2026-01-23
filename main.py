import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث تلقائي كل دقيقتين لمواكبة الشموع
st_autorefresh(interval=120000, key="mega_spx_radar_v9")

st.set_page_config(page_title="رادار هادي V9", layout="wide")
st.markdown("<h1 style='text-align: center; color: white; background: linear-gradient(to right, #1e3c72, #2a5298); padding: 15px; border-radius: 10px;'>🚀 رادار القناص: SPX والأسهم (V9)</h1>", unsafe_allow_html=True)

# --- 1. القائمة المحدثة (استخدام SPY بدلاً من ^GSPC لإظهار الألوان) ---
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

# --- 2. محرك التحليل الفني ---
for i, (name, sym) in enumerate(STOCKS.items()):
    try:
        # جلب البيانات
        data = yf.download(sym, period='5d', interval='5m', progress=False)
        if not data.empty and len(data) > 30:
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
            
            # حماية الاختراق (الشموع السابقة)
            prev_high = float(data['High'].squeeze().iloc[-2])
            prev_low = float(data['Low'].squeeze().iloc[-2])
            
            # قوة السيولة (حساسية عالية جداً 1.2x)
            avg_vol = volumes.rolling(window=10).mean().iloc[-1]
            vol_ratio = volumes.iloc[-1] / avg_vol
            is_explosion = vol_ratio > 1.2

            status, color = "⚪ هدوء", "transparent"
            
            # --- منطق الألوان (الكرنفال) ---
            
            # أولاً: تشبع بيعي أو شرائي (مراقبة)
            if rsi_val < 35: status, color = "🟢 رخيص (مراقبة Call)", "#2E7D32"
            elif rsi_val > 65: status, color = "🟠 متضخم (مراقبة Put)", "#E65100"

            # ثانياً: انفجار السيولة (فسفوري) - يطغى على المراقبة
            if is_explosion:
                status, color = "⚡ انفجار سيولة", "#CCFF00"
            
            # ثالثاً: تأكيد الكول أو البوت (الأولوية القصوى)
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

# --- 3. عرض الجدول ---
if results:
    df = pd.DataFrame(results)
    def apply_style(row):
        txt_color = "black" if row['_color'] == "#CCFF00" else "white"
        if row['_color'] != "transparent":
            return [f'background-color: {row["_color"]}; color: {txt_color}; font-weight: bold'] * len(row)
        return [''] * len(row)
    
    st.dataframe(df.style.apply(apply_style, axis=1), 
                 column_order=("الأداة", "الحالة", "السعر", "قوة السيولة", "RSI", "الاتجاه"),
                 use_container_width=True, hide_index=True, height=600)

st.sidebar.markdown("""
### 💡 كيف تستخدم رادار السباكس؟
1. **راقب SPY أولاً:** إذا كان لونه **أزرق 🔵**، ففرص الـ Call في بقية الأسهم قوية جداً.
2. **السيولة هي السر:** إذا رأيت **2.00x** في خانة قوة السيولة، فهذا انفجار حقيقي.
3. **تطابق الإشارة:** أفضل دخول عندما يكون السهم والسباكس بنفس اللون.
""")
