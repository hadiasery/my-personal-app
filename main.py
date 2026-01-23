import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

# --- 1. إعدادات التنبيه ---
TOKEN = "7566263341:AAHadbOMY8BLpQgTj9eujY52mnKQxuawZjY"
CHAT_ID = "692583333"

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID, "text": text}, timeout=5)
    except: pass

st_autorefresh(interval=120000, key="explosion_radar_v6")

st.set_page_config(page_title="رادار هادي المتفجر", layout="wide")
st.markdown("<h1 style='text-align: center; color: #CCFF00; background-color: black;'>💥 رادار القناص: نظام رصد الانفجار اللحظي</h1>", unsafe_allow_html=True)

# --- 2. القائمة الموسعة ---
STOCKS = {
    '📈 مؤشر S&P 500': '^GSPC', 'أبل': 'AAPL', 'نيفيديا': 'NVDA', 'تسلا': 'TSLA', 
    'أمازون': 'AMZN', 'ميتا': 'META', 'غوغل': 'GOOGL', 'نيو': 'NIO', 'لوسيد': 'LCID',
    'AMD': 'AMD', 'بالانتير': 'PLTR', 'كوين بيز': 'COIN', 'نتفليكس': 'NFLX'
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
            
            # حساب قوة الانفجار
            vol_ratio = volumes.iloc[-1] / volumes.rolling(window=10).mean().iloc[-1]
            is_explosion = vol_ratio > 1.8  # انفجار حقيقي

            status, color = "⚪ انتظار", "transparent"
            
            # --- منطق الألوان الجديد ---
            # 1. انفجار سيولة (فسفوري) - تنبيه مبكر جداً
            if is_explosion:
                status, color = "⚡ انفجار سيولة (تأهب)", "#CCFF00" # لون فسفوري
            
            # 2. تأكيد الدخول Call (أزرق) - شروط كاملة
            if rsi_val < 38 and (curr_p > prev_high) and (sma_5 > sma_13):
                status, color = "🔵 دخول Call مؤكد", "#0D47A1"
                send_msg(f"✅ Call confirmed: {name}")

            # 3. تأكيد الدخول Put (أحمر) - شروط كاملة
            elif rsi_val > 62 and (curr_p < prev_low) and (sma_5 < sma_13):
                status, color = "🔴 دخول Put مؤكد", "#B71C1C"
                send_msg(f"🔻 Put confirmed: {name}")

            results.append({
                "الأداة": name, "الحالة": status, "السعر": f"{curr_p:.2f}",
                "قوة السيولة": f"{vol_ratio:.1f}x", "RSI": round(rsi_val, 1),
                "الاتجاه": "📈 صاعد" if macd_h > 0 else "📉 هابط", "_color": color
            })
    except: continue
    my_bar.progress((i + 1) / len(STOCKS))

# --- 4. العرض الاحترافي ---
if results:
    df = pd.DataFrame(results)
    def apply_style(row):
        txt_color = "black" if row['_color'] == "#CCFF00" else "white"
        return [f'background-color: {row["_color"]}; color: {txt_color}; font-weight: bold' if row['_color'] != "transparent" else '' for _ in row]
    
    styled_df = df.style.apply(apply_style, axis=1)
    st.dataframe(styled_df, column_order=("الأداة", "الحالة", "السعر", "قوة السيولة", "RSI", "الاتجاه"), use_container_width=True, hide_index=True, height=550)

st.sidebar.markdown(f"""
### 💡 دليل القناص:
- **الفسفوري ⚡:** انفجار سيولة مفاجئ (راقب السعر الآن!)
- **الأزرق 🔵:** إشارة شراء Call مؤكدة.
- **الأحمر 🔴:** إشارة شراء Put مؤكدة.
""")
