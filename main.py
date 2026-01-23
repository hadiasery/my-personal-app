import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# تحديث تلقائي كل دقيقتين
st_autorefresh(interval=120000, key="sniper_radar_v12")

st.set_page_config(page_title="رادار القناص V12", layout="wide")

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
    # 1. تحليل وضع السباكس (SPY) أولاً
    spy_ticker = yf.Ticker("SPY")
    spy_df = spy_ticker.history(period="2d", interval="5m")
    
    spy_status = "⚪ أبيض"
    if not spy_df.empty and len(spy_df) > 1:
        # تحويل القيم لأرقام بسيطة لتجنب الخطأ السابق
        s_close = float(spy_df['Close'].iloc[-1])
        s_high = float(spy_df['High'].iloc[-2])
        s_low = float(spy_df['Low'].iloc[-2])
        
        if s_close > s_high: spy_status = "🔵 أزرق"
        elif s_close < s_low: spy_status = "🔴 أحمر"

    # 2. تحليل بقية الأسهم
    for name, sym in STOCKS.items():
        try:
            ticker = yf.Ticker(sym)
            df = ticker.history(period="5d", interval="5m")
            if df.empty or len(df) < 20: continue
            
            # تنظيف البيانات وتحويلها لأرقام
            c_p = float(df['Close'].iloc[-1])
            p_high = float(df['High'].iloc[-2])
            p_low = float(df['Low'].iloc[-2])
            
            # السيولة
            vol = df['Volume']
            avg_vol = vol.rolling(10).mean().iloc[-1]
            vol_ratio = float(vol.iloc[-1] / avg_vol)
            is_explosion = vol_ratio > 1.25
            
            # المؤشرات
            rsi_series = ta.rsi(df['Close'], length=14)
            rsi = float(rsi_series.iloc[-1]) if not rsi_series.empty else 50
            sma5 = float(ta.sma(df['Close'], 5).iloc[-1])
            sma13 = float(ta.sma(df['Close'], 13).iloc[-1])
            
            status, color = "⚪ هدوء", "transparent"
            
            # تطبيق شروط هادي "المضمونة"
            is_call = (c_p > p_high) and (sma5 > sma13) and is_explosion
            is_put = (c_p < p_low) and (sma5 < sma13) and is_explosion
            
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

            all_data.append({
                "الأداة": name, "الحالة": status, "السعر": f"{c_p:.2f}", 
                "السيولة": f"{vol_ratio:.2f}x", "RSI": int(rsi), "_color": color
            })
        except Exception as e:
            continue

# --- العرض المرئي ---
st.markdown(f"<h2 style='text-align: center;'>📊 وضع السوق الحالي (SPY): {spy_status}</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.success(f"✅ فرص Call مضمونة: {len(golden_calls)}")
    for s in golden_calls: st.warning(f"🚀 {s}: جـاهز للكول")

with col2:
    st.error(f"✅ فرص Put مضمونة: {len(golden_puts)}")
    for s in golden_puts: st.warning(f"📉 {s}: جـاهز للبوت")

st.divider()

if all_data:
    df_display = pd.DataFrame(all_data)
    def style_rows(row):
        bg = row['_color']
        text = "black" if bg == "#CCFF00" else "white"
        if bg == "transparent": return [''] * len(row)
        return [f'background-color: {bg}; color: {text}; font-weight: bold'] * len(row)

    st.dataframe(df_display.style.apply(style_rows, axis=1), 
                 column_order=("الأداة", "الحالة", "السعر", "السيولة", "RSI"),
                 use_container_width=True, hide_index=True)
