import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث تلقائي كل دقيقتين
st_autorefresh(interval=120000, key="sniper_radar_v11")

st.set_page_config(page_title="رادار الصفقات المضمونة", layout="wide")

# --- قائمة الأسهم ---
STOCKS = {
    '📈 سباكس (SPY)': 'SPY', 'أبل': 'AAPL', 'نيفيديا': 'NVDA', 
    'تسلا': 'TSLA', 'مايكروسوفت': 'MSFT', 'أمازون': 'AMZN', 
    'ميتا': 'META', 'غوغل': 'GOOGL', 'نيو': 'NIO', 
    'لوسيد': 'LCID', 'بالانتير': 'PLTR', 'AMD': 'AMD'
}

all_data = []
golden_calls = []
golden_puts = []

# --- محرك التحليل ---
with st.spinner('جاري قنص الفرص...'):
    # جلب بيانات SPY أولاً لتحديد اتجاه السوق
    spy_data = yf.download('SPY', period='2d', interval='5m', progress=False)
    spy_close = spy_data['Close'].iloc[-1]
    spy_prev_high = spy_data['High'].iloc[-2]
    spy_prev_low = spy_data['Low'].iloc[-2]
    
    spy_status = "⚪ أبيض"
    if spy_close > spy_prev_high: spy_status = "🔵 أزرق"
    elif spy_close < spy_prev_low: spy_status = "🔴 أحمر"

    for name, sym in STOCKS.items():
        try:
            df = yf.download(sym, period='5d', interval='5m', progress=False)
            if df.empty: continue
            
            close_p = df['Close'].squeeze()
            curr_p = float(close_p.iloc[-1])
            prev_high = float(df['High'].squeeze().iloc[-2])
            prev_low = float(df['Low'].squeeze().iloc[-2])
            
            # السيولة
            vol = df['Volume'].squeeze()
            vol_ratio = vol.iloc[-1] / vol.rolling(10).mean().iloc[-1]
            is_explosion = vol_ratio > 1.25
            
            # المؤشرات
            rsi = ta.rsi(close_p, length=14).iloc[-1]
            sma5 = ta.sma(close_p, 5).iloc[-1]
            sma13 = ta.sma(close_p, 13).iloc[-1]
            
            status, color = "⚪ هدوء", "white"
            
            # فحص الشروط المضمونة (شروط هادي)
            is_call = (curr_p > prev_high) and (sma5 > sma13) and is_explosion
            is_put = (curr_p < prev_low) and (sma5 < sma13) and is_explosion
            
            if is_call:
                status, color = "🔵 دخول Call مؤكد", "#0D47A1"
                if spy_status in ["🔵 أزرق", "⚪ أبيض"]:
                    golden_calls.append(name)
            elif is_put:
                status, color = "🔴 دخول Put مؤكد", "#B71C1C"
                if spy_status in ["🔴 أحمر", "⚪ أبيض"]:
                    golden_puts.append(name)
            elif is_explosion:
                status, color = "⚡ انفجار سيولة", "#CCFF00"

            all_data.append({"الأداة": name, "الحالة": status, "السعر": f"{curr_p:.2f}", "السيولة": f"{vol_ratio:.2f}x", "RSI": int(rsi), "_color": color})
        except: continue

# --- العرض المرئي ---
st.markdown(f"### 🎯 حالة السوق الحالي (SPY): {spy_status}")

col1, col2 = st.columns(2)
with col1:
    st.success(f"✅ فرص Call مضمونة: {len(golden_calls)}")
    for s in golden_calls: st.button(f"🔥 {s} - جـاهز للكول", key=s+"c")

with col2:
    st.error(f"✅ فرص Put مضمونة: {len(golden_puts)}")
    for s in golden_puts: st.button(f"📉 {s} - جـاهز للبوت", key=s+"p")

st.divider()
df_final = pd.DataFrame(all_data)
st.dataframe(df_final.style.apply(lambda x: [f'background-color: {x["_color"]}; color: {"black" if x["_color"]=="#CCFF00" else "white"}' for _ in x], axis=1), use_container_width=True, hide_index=True)
