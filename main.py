import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import time

# تحديث تلقائي كل 10 ثوانٍ
st_autorefresh(interval=10000, key="sniper_radar_v16")

st.set_page_config(page_title="رادار الثواني V16", layout="wide")

# --- قائمة الأسهم ---
STOCKS = {
    'SPY': 'SPY', 'AAPL': 'AAPL', 'NVDA': 'NVDA', 
    'TSLA': 'TSLA', 'META': 'META', 'AMZN': 'AMZN', 
    'AMD': 'AMD', 'NIO': 'NIO'
}

# --- إضافة عداد الثواني التنازلي بصرياً ---
# ملاحظة: العداد سيبدأ من 10 مع كل تحديث للصفحة
placeholder = st.empty()
with placeholder.container():
    st.markdown(f"""
        <div style="background-color: #1e1e1e; padding: 10px; border-radius: 10px; border: 1px solid #333; text-align: center;">
            <span style="color: #white; font-size: 18px;">🔄 التحديث القادم خلال: </span>
            <span style="color: #CCFF00; font-size: 24px; font-weight: bold;">10 ثوانٍ</span>
        </div>
    """, unsafe_allow_html=True)

all_data = []
golden_calls = []
golden_puts = []

# --- محرك التحليل السريع ---
try:
    tickers = yf.Tickers(' '.join(STOCKS.values()))
    
    # تحليل SPY
    spy_hist = tickers.tickers['SPY'].history(period="2d", interval="1m")
    spy_status = "⚪ أبيض"
    if not spy_hist.empty:
        s_c = float(spy_hist['Close'].iloc[-1])
        s_h = float(spy_hist['High'].iloc[-2])
        s_l = spy_hist['Low'].iloc[-2]
        if s_c > s_h: spy_status = "🔵 أزرق"
        elif s_c < s_l: spy_status = "🔴 أحمر"

    for name, sym in STOCKS.items():
        df = tickers.tickers[sym].history(period="2d", interval="1m")
        if df.empty: continue
        
        c_p = float(df['Close'].iloc[-1])
        p_h = float(df['High'].iloc[-2])
        p_l = float(df['Low'].iloc[-2])
        
        # حساب السيولة
        vol = df['Volume']
        v_ratio = float(vol.iloc[-1] / vol.rolling(10).mean().iloc[-1])
        
        status, color = "⚪ هدوء", "white"
        
        # شروط الدخول
        is_call = (c_p > p_h)
        is_put = (c_p < p_l)
        
        if is_call:
            status, color = "🔵 كول", "#0D47A1"
            if v_ratio > 1.1 and spy_status in ["🔵 أزرق", "⚪ أبيض"]:
                golden_calls.append(name)
        elif is_put:
            status, color = "🔴 بوت", "#B71C1C"
            if v_ratio > 1.1 and spy_status in ["🔴 أحمر", "⚪ أبيض"]:
                golden_puts.append(name)
        
        if v_ratio > 1.2 and status == "⚪ هدوء":
            status, color = "⚡ انفجار", "#CCFF00"

        all_data.append({"السهم": name, "الحالة": status, "السعر": f"{c_p:.2f}", "السيولة": f"{v_ratio:.2f}x", "_color": color})

except Exception as e:
    st.info("جاري مزامنة الأسعار...")

# --- العرض المرئي ---
st.markdown(f"<h2 style='text-align: center;'>📊 وضع السباكس الآن: {spy_status}</h2>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1: 
    if golden_calls:
        st.success(f"🔥 كول مضمون: {', '.join(golden_calls)}")
    else:
        st.write("🟢 لا توجد فرص كول حالياً")

with c2: 
    if golden_puts:
        st.error(f"📉 بوت مضمون: {', '.join(golden_puts)}")
    else:
        st.write("🔴 لا توجد فرص بوت حالياً")

st.divider()

if all_data:
    df_f = pd.DataFrame(all_data)
    def style_row(row):
        bg = row['_color']
        txt = "black" if bg in ["#CCFF00", "white"] else "white"
        return [f'background-color: {bg}; color: {txt}; font-weight: bold'] * len(row)
    
    st.table(df_f.drop(columns=['_color']))
