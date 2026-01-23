import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

# --- 1. إعدادات التنبيه والربط ---
TOKEN = "7566263341:AAHadbOMY8BLpQgTj9eujY52mnKQxuawZjY"
CHAT_ID = "692583333"

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID, "text": text}, timeout=5)
    except:
        pass

# تحديث تلقائي للصفحة كل 60 ثانية لضمان حداثة الأسعار
st_autorefresh(interval=60000, key="final_radar_v2")

st.set_page_config(page_title="رادار هادي المطور", layout="wide")
st.title("📊 رادار مراقبة الأسواق (عرض أفقي)")

# --- 2. قوائم الشركات (الاسم والرمز) ---
US_STOCKS = {
    'أبل': 'AAPL', 'مايكروسوفت': 'MSFT', 'نيفيديا': 'NVDA', 'تسلا': 'TSLA', 'أمازون': 'AMZN',
    'ميتا': 'META', 'جوجل': 'GOOGL', 'نتفلكس': 'NFLX', 'أيه إم دي': 'AMD', 'بايبال': 'PYPL'
}

SA_STOCKS = {
    'أرامكو': '2222.SR', 'الراجحي': '1120.SR', 'الأهلي': '1180.SR', 'stc': '7010.SR',
    'سابك': '2010.SR', 'معادن': '1211.SR', 'الإنماء': '1150.SR', 'لوبريف': '2223.SR',
    'البحري': '4030.SR', 'كيان': '2310.SR', 'سليمان الحبيب': '4013.SR'
}

market = st.sidebar.radio("اختر السوق لمراقبته:", ["الأمريكي", "السعودي"])
stocks_dict = US_STOCKS if market == "الأمريكي" else SA_STOCKS

results = []
my_bar = st.progress(0)

# --- 3. جلب البيانات ومعالجتها ---
for i, (name, sym) in enumerate(stocks_dict.items()):
    try:
        # جلب بيانات يومين لضمان وجود عدد كافٍ من الشموع لحساب RSI
        data = yf.download(sym, period='2d', interval='1m', progress=False)
        
        if not data.empty:
            # حل مشكلة AttributeError: تحويل العمود لشكل بسيط (Series)
            close_prices = data['Close'].squeeze()
            
            # التأكد من وجود بيانات كافية للحساب (أكثر من 14 شمعة)
            if len(close_prices) > 14:
                rsi_series = ta.rsi(close_prices, length=14)
                rsi_val = float(rsi_series.iloc[-1])
            else:
                rsi_val = 50.0 # قيمة محايدة إذا كانت البيانات قليلة
            
            current_price = float(close_prices.iloc[-1])
            
            # منطق الإشارة: دخول إذا كان RSI تحت 35
            is_entry = rsi_val < 35
            status = "🟢 دخول الآن" if is_entry else "⚪ انتظار"
            entry_price = f"{current_price:.2f}" if is_entry else "-"
            
            if is_entry:
                send_msg(f"🚀 إشارة شراء: {name} ({sym})\nالسعر الحالي: {entry_price}\nRSI: {rsi_val:.1f}")
                
            results.append({
                "اسم الشركة": name,
                "الحالة": status,
                "سعر الدخول المقترح": entry_price,
                "RSI": round(rsi_val, 1)
            })
    except Exception as e:
        # في حال حدوث خطأ لأي سهم معين، يتم تخطيه لكي لا يتوقف البرنامج
        continue
    
    my_bar.progress((i + 1) / len(stocks_dict))

# --- 4. عرض الجدول النهائي ---
if results:
    df = pd.DataFrame(results)
    
    # دالة لتلوين الصفوف التي تعطي إشارة دخول
    def highlight_entry(row):
        return ['background-color: #d4edda; font-weight: bold' if row['الحالة'] == "🟢 دخول الآن" else '' for _ in row]

    st.table(df.style.apply(highlight_entry, axis=1))
else:
    st.info("🔄 جاري البحث عن بيانات... قد يكون السوق مغلقاً حالياً.")

st.divider()
st.caption("ملاحظة: تظهر الأسعار فقط عند تحقق شروط الدخول. يتم الفحص آلياً كل دقيقة.")
