import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث تلقائي كل دقيقتين
st_autorefresh(interval=120000, key="sniper_radar_v13")

st.set_page_config(page_title="رادار هادي - الألوان الكاملة", layout="wide")

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

# 1. تحليل وضع السباكس (SPY)
spy_df = yf.download("SPY", period="2d", interval="5m", progress=False)
spy_status = "⚪ أبيض"
if not spy_df.empty:
    s_close = float(spy_df['Close'].iloc[-1])
    s_prev_h = float(spy_df['High'].iloc[-2])
    s_prev_l = float(spy_df['Low'].iloc[-2])
    if s_close > s_prev_h: spy_status = "🔵 أزرق"
    elif s_close < s_prev_l: spy_status = "🔴 أحمر"

# 2. تحليل الأسهم
for name, sym in STOCKS.items():
    try:
        df = yf.download(sym, period="5d", interval="5m", progress=False)
        if df.empty: continue
        
        c_p = float(df['Close'].iloc[-1])
        p_h = float(df['High'].iloc[-2])
        p_l = float(df['Low'].iloc[-2])
        
        # السيولة (حساسية متوسطة 1.15)
        vol = df['Volume']
        vol_ratio = float(vol.iloc[-1] / vol.rolling(10).mean().iloc[-1])
        is_explosion = vol_ratio > 1.15
        
        # المؤشرات
        rsi = float(ta.rsi(df['Close'], length=14).iloc[-1])
        sma5 = float(ta.sma(df['Close'], 5).iloc[-1])
        sma13 = float(ta.sma(df['Close'], 13).iloc[-1])
        
        status, color = "⚪ هدوء", "white"
        
        # الشروط الجديدة للألوان (أكثر مرونة لتراها باستمرار)
        is_call = (c_p > p_h) and (sma5 > sma13)
        is_put = (c_p < p_l) and (sma5 < sma13)
        
        if is_call:
            status, color = "🔵 دخول Call مؤكد", "#0D47A1" # أزرق غامق
            if is_explosion and spy_status in ["🔵 أزرق", "⚪ أبيض"]:
                golden_calls.append(name)
        elif is_put:
            status, color = "🔴 دخول Put مؤكد", "#B71C1C" # أحمر غامق
            if is_explosion and spy_status in ["🔴 أحمر", "⚪ أبيض"]:
                golden_puts.append(name)
        elif is_explosion:
            status, color = "⚡ انفجار سيولة", "#CCFF00" # فسفوري

        all_data.append({
            "الأداة": name, "الحالة": status, "السعر": f"{c_p:.2f}", 
            "السيولة": f"{vol_ratio:.2f}x", "RSI": int(rsi), "_color": color
        })
    except: continue

# --- العرض ---
st.markdown(f"<h2 style='text-align: center;'>📊 وضع السوق (SPY): {spy_status}</h2>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1: st.success(f"✅ كول مضمون: {', '.join(golden_calls) if golden_calls else 'لا يوجد'}")
with c2: st.error(f"✅ بوت مضمون: {', '.join(golden_puts) if golden_puts else 'لا يوجد'}")

if all_data:
    df_final = pd.DataFrame(all_data)
    def style_table(row):
        bg = row['_color']
        txt = "black" if bg == "#CCFF00" else "white"
        if bg == "white": return ['color: black; background-color: white'] * len(row)
        return [f'background-color: {bg}; color: {txt}; font-weight: bold'] * len(row)

    st.dataframe(df_final.style.apply(style_table, axis=1), 
                 column_order=("الأداة", "الحالة", "السعر", "السيولة", "RSI"),
                 use_container_width=True, hide_index=True)
