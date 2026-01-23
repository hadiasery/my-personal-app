import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث تلقائي كل دقيقة لسرعة الاستجابة
st_autorefresh(interval=60000, key="sniper_radar_v14")

st.set_page_config(page_title="رادار القناص V14", layout="wide")

# قائمة الأسهم المختصرة لضمان سرعة التحميل وعدم الحظر
STOCKS = {
    'SPY': 'SPY', 'AAPL': 'AAPL', 'NVDA': 'NVDA', 
    'TSLA': 'TSLA', 'META': 'META', 'AMZN': 'AMZN', 
    'AMD': 'AMD', 'NIO': 'NIO'
}

all_data = []
golden_calls = []
golden_puts = []

# --- محرك التحميل ---
st.write("🔍 جاري فحص الأسهم الآن...")

# 1. تحليل SPY
try:
    spy = yf.download("SPY", period="2d", interval="5m", progress=False)
    spy_status = "⚪ أبيض"
    if not spy.empty:
        s_c = spy['Close'].iloc[-1]
        s_h = spy['High'].iloc[-2]
        s_l = spy['Low'].iloc[-2]
        if s_c > s_h: spy_status = "🔵 أزرق"
        elif s_c < s_l: spy_status = "🔴 أحمر"
except:
    spy_status = "⚠️ خطأ في البيانات"

# 2. تحليل الأسهم
for name, sym in STOCKS.items():
    try:
        df = yf.download(sym, period="2d", interval="5m", progress=False)
        if df.empty: continue
        
        c_p = df['Close'].iloc[-1]
        p_h = df['High'].iloc[-2]
        p_l = df['Low'].iloc[-2]
        
        # السيولة
        vol = df['Volume']
        v_ratio = float(vol.iloc[-1] / vol.rolling(10).mean().iloc[-1])
        
        # المؤشرات
        sma5 = ta.sma(df['Close'], 5).iloc[-1]
        sma13 = ta.sma(df['Close'], 13).iloc[-1]
        
        status, color = "⚪ هدوء", "white"
        
        # الشروط
        if (c_p > p_h) and (sma5 > sma13):
            status, color = "🔵 كول", "#0D47A1"
            if v_ratio > 1.1: golden_calls.append(name)
        elif (c_p < p_l) and (sma5 < sma13):
            status, color = "🔴 بوت", "#B71C1C"
            if v_ratio > 1.1: golden_puts.append(name)
        elif v_ratio > 1.2:
            status, color = "⚡ انفجار", "#CCFF00"

        all_data.append({"السهم": name, "الحالة": status, "السعر": f"{c_p:.2f}", "السيولة": f"{v_ratio:.2f}x", "_color": color})
    except:
        continue

# --- العرض ---
st.markdown(f"### 📢 وضع السوق: {spy_status}")

c1, c2 = st.columns(2)
with c1: st.success(f"✅ كول مضمون: {', '.join(golden_calls)}")
with c2: st.error(f"✅ بوت مضمون: {', '.join(golden_puts)}")

st.divider()

# التأكد من وجود بيانات قبل رسم الجدول
if len(all_data) > 0:
    df_final = pd.DataFrame(all_data)
    
    def apply_style(row):
        bg = row['_color']
        text_color = "black" if bg == "#CCFF00" or bg == "white" else "white"
        return [f'background-color: {bg}; color: {text_color}; font-weight: bold'] * len(row)

    st.table(df_final.drop(columns=['_color'])) # استخدمنا st.table بدلاً من dataframe لضمان الظهور
else:
    st.warning("⚠️ لا توجد بيانات حالياً. تأكد من اتصال الإنترنت أو انتظر دقيقة للتحديث.")
