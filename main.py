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
        requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text}")
    except: pass

# تحديث تلقائي كل دقيقة
st_autorefresh(interval=60000, key="horizontal_radar")

st.set_page_config(page_title="رادار هادي - عرض أفقي", layout="wide")
st.title("📊 رادار مراقبة الأسواق")

# --- القوائم (الاسم والرمز) ---
US_STOCKS = {
    'أبل': 'AAPL', 'مايكروسوفت': 'MSFT', 'نيفيديا': 'NVDA', 'تسلا': 'TSLA', 'أمازون': 'AMZN',
    'ميتا': 'META', 'جوجل': 'GOOGL', 'نتفلكس': 'NFLX', 'أيه إم دي': 'AMD', 'بايبال': 'PYPL'
}

SA_STOCKS = {
    'أرامكو': '2222.SR', 'الراجحي': '1120.SR', 'الأهلي': '1180.SR', 'stc': '7010.SR',
    'سابك': '2010.SR', 'معادن': '1211.SR', 'الإنماء': '1150.SR', 'لوبريف': '2223.SR'
}

market = st.sidebar.radio("اختر السوق:", ["الأمريكي", "السعودي"])
stocks_dict = US_STOCKS if market == "الأمريكي" else SA_STOCKS

results = []
my_bar = st.progress(0)

for i, (name, sym) in enumerate(stocks_dict.items()):
    data = yf.download(sym, period='1d', interval='1m', progress=False)
    if not data.empty and len(data) > 10:
        price = data['Close'].iloc[-1]
        rsi = ta.rsi(data['Close'], length=14).iloc[-1] if len(data) > 14 else 50
        
        # منطق التنبيه
        is_entry = rsi < 35
        status = "🟢 دخول الآن" if is_entry else "⚪ انتظار"
        entry_price = f"{price:.2f}" if is_entry else "-" # يظهر السعر فقط عند الدخول
        
        if is_entry:
            send_msg(f"🚀 إشارة شراء: {name}\nالسعر: {entry_price}")
            
        results.append({
            "اسم الشركة": name,
            "الحالة": status,
            "سعر الدخول المقترح": entry_price,
            "RSI": round(float(rsi), 1)
        })
    my_bar.progress((i + 1) / len(stocks_dict))

# عرض الجدول بشكل أفقي ومنظم
if results:
    df = pd.DataFrame(results)
    
    # تنسيق الألوان: صفوف "الدخول" ستكون باللون الأخضر
    def highlight_entry(row):
        return ['background-color: #d4edda' if row['الحالة'] == "🟢 دخول الآن" else '' for _ in row]

    st.table(df.style.apply(highlight_entry, axis=1))
else:
    st.info("🔄 بانتظار افتتاح السوق لجلب الأسعار اللحظية...")

st.caption("ملاحظة: سعر الدخول يظهر فقط عندما يعطي الرادار إشارة 'دخول الآن'.")
