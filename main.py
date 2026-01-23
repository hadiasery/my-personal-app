import streamlit as st
import yfinance as yf
import pandas_ta as ta
import requests
from streamlit_autorefresh import st_autorefresh

# --- إعداداتك الخاصة (جاهزة) ---
TELEGRAM_TOKEN = "7566263341:AAHadbOMY8BLpQgTj9eujY52mnKQxuawZjY"
TELEGRAM_CHAT_ID = "692583333"

# دالة إرسال التلغرام
def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.get(url, params=params)
    except:
        pass

# --- تفعيل التحديث التلقائي (كل 60 ثانية) ---
# هذا الكود يجعل التطبيق يحدث نفسه آلياً بدون تدخل منك
st_autorefresh(interval=60000, key="stock_monitor")

st.set_page_config(page_title="رادار التداول", layout="centered")
st.title("📈 رادار الأسهم اللحظي")

# --- قائمة الشركات (تم توسيعها) ---
SA_STOCKS = {
    'الراجحي': '1120.SR', 'أرامكو': '2222.SR', 'الأهلي': '1180.SR', 'stc': '7010.SR', 
    'سابك': '2010.SR', 'معادن': '1211.SR', 'الإنماء': '1150.SR', 'لوبريف': '2223.SR'
}
US_STOCKS = {
    'Nvidia': 'NVDA', 'Apple': 'AAPL', 'Tesla': 'TSLA', 'Microsoft': 'MSFT', 
    'Amazon': 'AMZN', 'Meta': 'META', 'Google': 'GOOGL', 'AMD': 'AMD'
}

market = st.sidebar.radio("اختر السوق", ["السعودي", "الأمريكي"])
stocks = SA_STOCKS if market == "السعودي" else US_STOCKS
selected_label = st.selectbox("اختر السهم للمراقبة:", list(stocks.keys()))
symbol = stocks[selected_label]

# جلب بيانات الدقيقة الواحدة
df = yf.download(symbol, period='1d', interval='1m', progress=False)

if not df.empty:
    # التحليل الفني
    df['RSI'] = ta.rsi(df['Close'], length=14)
    current_price = df['Close'].iloc[-1]
    rsi_val = df['RSI'].iloc[-1]
    
    # عرض السعر الحالي
    st.metric(f"سعر {selected_label} (لحظي)", f"{current_price:.2f}")

    # --- منطق التنبيهات الذكي ---
    if rsi_val < 30:
        msg = f"🟢 فرصة شراء: {selected_label}\nالسعر: {current_price:.2f}\nRSI: {rsi_val:.2f}"
        st.success("🚨 تم رصد فرصة شراء!")
        send_telegram_msg(msg)
        # صوت التنبيه
        st.components.v1.html('<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3"></audio>', height=0)
    
    elif rsi_val > 70:
        msg = f"🔴 تنبيه بيع: {selected_label}\nالسعر: {current_price:.2f}\nRSI: {rsi_val:.2f}"
        st.warning("🚨 السهم في منطقة بيع!")
        send_telegram_msg(msg)

    # الرسم البياني
    st.line_chart(df['Close'])
    st.caption(f"آخر تحديث آلي: {df.index[-1].strftime('%H:%M:%S')}")

else:
    st.info("بانتظار بيانات السوق (تأكد من فتح السوق حالياً)")
