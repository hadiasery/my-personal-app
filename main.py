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

st_autorefresh(interval=60000, key="desktop_radar_v5")

st.set_page_config(page_title="منصة هادي الاحترافية", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1E88E5;'>📊 رادار هادي: مراقبة التشبع والانعكاس</h1>", unsafe_allow_html=True)

# --- 2. القائمة ---
US_STOCKS = {'أبل': 'AAPL', 'مايكروسوفت': 'MSFT', 'نيفيديا': 'NVDA', 'تسلا': 'TSLA', 'أمازون': 'AMZN', 'لوسيد': 'LCID', 'نيو': 'NIO'}
SA_STOCKS = {'أرامكو': '2222.SR', 'الراجحي': '1120.SR', 'الأهلي': '1180.SR', 'stc': '7010.SR', 'سابك': '2010.SR'}

market = st.sidebar.radio("اختر السوق:", ["الأمريكي", "السعودي"])
stocks_dict = US_STOCKS if market == "الأمريكي" else SA_STOCKS

results = []
my_bar = st.progress(0)

for i, (name, sym) in enumerate(stocks_dict.items()):
    try:
        data = yf.download(sym, period='2d', interval='1m', progress=False)
        if not data.empty and len(data) > 15:
            close_prices = data['Close'].squeeze()
            rsi_val = float(ta.rsi(close_prices, length=14).iloc[-1])
            
            curr_p = float(close_prices.iloc[-1])
            prev_p = float(close_prices.iloc[-2]) # السعر في الدقيقة السابقة
            
            # منطق الحالات
            is_oversold = rsi_val < 35
            is_reversing = is_oversold and (curr_p > prev_p) # تشبع + بداية صعود
            
            if is_reversing:
                status = "🔵 بداية ارتداد"
                send_msg(f"🔵 تأكيد ارتداد: {name}\nالسعر الحالي: {curr_p:.2f}")
            elif is_oversold:
                status = "🟢 تشبع بيعي"
            else:
                status = "⚪ انتظار"
                
            results.append({
                "الشركة": name,
                "الحالة": status,
                "اتجاه السعر": "📈 صعود" if curr_p > prev_p else "📉 هبوط",
                "السعر الحالي": round(curr_p, 2),
                "RSI": round(rsi_val, 1)
            })
    except: continue
    my_bar.progress((i + 1) / len(stocks_dict))

# --- 3. العرض الملون ---
if results:
    df = pd.DataFrame(results)
    
    def apply_style(row):
        if row['الحالة'] == "🔵 بداية ارتداد":
            return ['background-color: #3498db; color: white; font-weight: bold'] * len(row)
        elif row['الحالة'] == "🟢 تشبع بيعي":
            return ['background-color: #2ecc71; color: white'] * len(row)
        return [''] * len(row)

    st.dataframe(df.style.apply(apply_style, axis=1), use_container_width=True, hide_index=True)
else:
    st.info("🔄 بانتظار البيانات...")

st.caption("🔵 الأزرق: يعني السهم رخيص (RSI < 35) وبدأ يرتفع الآن. | 🟢 الأخضر: يعني السهم رخيص جداً ولكن لا يزال ينزل أو مستقر.")
