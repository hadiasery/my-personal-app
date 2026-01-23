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

st_autorefresh(interval=60000, key="desktop_radar_v4")

st.set_page_config(page_title="منصة هادي الاحترافية", layout="wide")
# التصحيح هنا: تم تغيير unsafe_allow_index إلى unsafe_allow_html
st.markdown("<h1 style='text-align: center; color: #1E88E5;'>📊 رادار الأسهم العالمي - لوحة التحكم</h1>", unsafe_allow_html=True)

# --- 2. القائمة الموسعة ---
US_STOCKS = {
    'أبل': 'AAPL', 'مايكروسوفت': 'MSFT', 'نيفيديا': 'NVDA', 'تسلا': 'TSLA', 'أمازون': 'AMZN',
    'ميتا': 'META', 'جوجل': 'GOOGL', 'نتفلكس': 'NFLX', 'أيه إم دي': 'AMD', 'بايبال': 'PYPL',
    'أدوبي': 'ADBE', 'سيسكو': 'CSCO', 'إنتل': 'INTC', 'بايدو': 'BIDU', 'لوسيد': 'LCID'
}

SA_STOCKS = {
    'أرامكو': '2222.SR', 'الراجحي': '1120.SR', 'الأهلي': '1180.SR', 'stc': '7010.SR',
    'سابك': '2010.SR', 'معادن': '1211.SR', 'الإنماء': '1150.SR', 'لوبريف': '2223.SR'
}

market = st.sidebar.radio("اختر السوق لمراقبته:", ["الأمريكي (مباشر الآن)", "السعودي"])
stocks_dict = US_STOCKS if market == "الأمريكي (مباشر الآن)" else SA_STOCKS

results = []
my_bar = st.progress(0)

# --- 3. المعالجة ---
for i, (name, sym) in enumerate(stocks_dict.items()):
    try:
        data = yf.download(sym, period='2d', interval='1m', progress=False)
        if not data.empty:
            close_prices = data['Close'].squeeze()
            if len(close_prices) > 14:
                rsi_val = float(ta.rsi(close_prices, length=14).iloc[-1])
            else: rsi_val = 50.0
            
            price = float(close_prices.iloc[-1])
            is_entry = rsi_val < 35
            status = "🟢 دخول الآن" if is_entry else "⚪ انتظار"
            
            if is_entry:
                send_msg(f"🚀 فرصة شراء: {name} ({sym})\nالسعر: {price:.2f}")
                
            results.append({"الشركة": name, "الرمز": sym, "الحالة": status, "السعر": round(price, 2), "RSI": round(rsi_val, 1)})
    except: continue
    my_bar.progress((i + 1) / len(stocks_dict))

# --- 4. العرض ---
if results:
    df = pd.DataFrame(results)
    def apply_style(row):
        if row['الحالة'] == "🟢 دخول الآن":
            return ['background-color: #2ecc71; color: white; font-weight: bold'] * len(row)
        return [''] * len(row)

    st.dataframe(df.style.apply(apply_style, axis=1), use_container_width=True, hide_index=True)
