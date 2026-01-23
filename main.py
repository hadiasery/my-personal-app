import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

# --- إعدادات التنبيه ---
TOKEN = "7566263341:AAHadbOMY8BLpQgTj9eujY52mnKQxuawZjY"
CHAT_ID = "692583333"

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID, "text": text}, timeout=5)
    except: pass

st_autorefresh(interval=120000, key="pro_trader_radar")

st.set_page_config(page_title="رادار هادي الاحترافي", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1E88E5;'>🎯 رادار هادي: Call & Put + S&P 500</h1>", unsafe_allow_html=True)

# --- قائمة الأسهم والمؤشر ---
STOCKS = {
    '📈 مؤشر S&P 500': '^GSPC',
    'أبل': 'AAPL', 'نيفيديا': 'NVDA', 'تسلا': 'TSLA', 'مايكروسوفت': 'MSFT', 
    'أمازون': 'AMZN', 'لوسيد': 'LCID', 'نيو': 'NIO'
}

results = []
my_bar = st.progress(0)

for i, (name, sym) in enumerate(STOCKS.items()):
    try:
        data = yf.download(sym, period='7d', interval='5m', progress=False)
        if not data.empty and len(data) > 30:
            data = data.ffill().bfill()
            close_prices = data['Close'].squeeze()
            volumes = data['Volume'].squeeze()
            curr_p = float(close_prices.iloc[-1])
            
            # المؤشرات
            rsi_val = float(ta.rsi(close_prices, length=14).iloc[-1])
            prev_rsi = float(ta.rsi(close_prices, length=14).iloc[-2])
            sma_5 = float(ta.sma(close_prices, length=5).iloc[-1])
            sma_13 = float(ta.sma(close_prices, length=13).iloc[-1])
            macd_hist = float(ta.macd(close_prices)['MACDh_12_26_9'].iloc[-1])
            
            # بيانات الشمعة السابقة للحماية
            prev_high = float(data['High'].squeeze().iloc[-2])
            prev_low = float(data['Low'].squeeze().iloc[-2])
            
            # قوة الانفجار
            avg_vol = volumes.rolling(window=10).mean().iloc[-1]
            vol_ratio = volumes.iloc[-1] / avg_vol
            explosion_power = "🔥 عالية" if vol_ratio > 1.5 else "⚠️ عادية" if vol_ratio > 1.0 else "❄️ ضعيفة"

            # --- المنطق البرمجي المزدوج (Call & Put) ---
            status = "⚪ انتظار"
            color = "transparent"
            
            # 1. منطق الـ Call (اختراق للأعلى)
            if rsi_val < 35:
                if (curr_p > prev_high) and (sma_5 > sma_13) and (macd_hist > 0):
                    status = "🔵 دخول Call مؤكد"
                    color = "#0D47A1"
                    send_msg(f"🚀 إشارة Call: {name}\nالسعر: {curr_p:.2f}\nالقوة: {explosion_power}")
                else:
                    status = "🟢 مراقبة Call"
                    color = "#2E7D32"

            # 2. منطق الـ Put (كسر للأدنى)
            elif rsi_val > 65:
                if (curr_p < prev_low) and (sma_5 < sma_13) and (macd_hist < 0):
                    status = "🔴 دخول Put مؤكد"
                    color = "#B71C1C"
                    send_msg(f"📉 إشارة Put: {name}\nالسعر: {curr_p:.2f}\nالقوة: {explosion_power}")
                else:
                    status = "🟠 مراقبة Put"
                    color = "#E65100"
                
            results.append({
                "الأداة": name,
                "الحالة": status,
                "السعر": f"{curr_p:.2f}",
                "قوة الانفجار": explosion_power,
                "RSI": round(rsi_val, 1),
                "الاتجاه": "📈 صاعد" if macd_hist > 0 else "📉 هابط",
                "_color": color
            })
    except: continue
    my_bar.progress((i + 1) / len(STOCKS))

# --- العرض بصورة احترافية ---
if results:
    df = pd.DataFrame(results)
    def apply_style(row):
        if row['_color'] != "transparent":
            return [f'background-color: {row["_color"]}; color: white; font-weight: bold'] * len(row)
        return [''] * len(row)

    st.dataframe(df.drop(columns=['_color']).style.apply(apply_style, axis=1), use_container_width=True, hide_index=True)

st.sidebar.markdown("""
### 💡 دليل الألوان:
- **الأزرق 🔵:** شراء Call (اختراق حقيقي).
- **الأحمر 🔴:** شراء Put (كسر حقيقي).
- **الأخضر 🟢:** السهم رخيص (انتظر الاختراق).
- **البرتقالي 🟠:** السهم متضخم (انتظر الكسر).
""")
