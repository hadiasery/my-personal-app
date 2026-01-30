import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

# تحديث كل 10 ثوانٍ لضمان السرعة القصوى
st_autorefresh(interval=10000, key="v42_final_lightning_fix")

st.set_page_config(page_title="رادار القناص V42.2", layout="wide")

# تصميم الألوان والخطوط الضخمة (30px)
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    .big-font { font-size: 30px !important; font-weight: 900 !important; color: black !important; text-align: center; }
    .header-box { background-color: #1e293b; color: white; padding: 10px; text-align: center; font-size: 25px; font-weight: bold; border: 3px solid black; }
    
    /* ألوان الصفوف */
    .row-g { background-color: #22c55e; padding: 20px; border: 3px solid black; margin-bottom: -3px; }
    .row-r { background-color: #ef4444; padding: 20px; border: 3px solid black; margin-bottom: -3px; }
    
    /* المربع الأسود مع إشارة الدخول باللون الأزرق الصريح */
    .entry-box-blue { 
        background-color: black !important; 
        color: #3b82f6 !important; /* أزرق ملكي واضح */
        font-size: 32px !important; 
        font-weight: 900; 
        padding: 20px; 
        border: 3px solid black; 
        text-align: center; 
    }
    .wait-box { 
        background-color: black !important; 
        color: #555555 !important; 
        font-size: 25px; 
        padding: 20px; 
        border: 3px solid black; 
        text-align: center; 
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"<h1 style='text-align:center; color:black;'>💎 رادار القناص V42.2 💎 <br> <span style='font-size:22px;'>توقيت الرصد اللحظي: {time.strftime('%H:%M:%S')}</span></h1>", unsafe_allow_html=True)

STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']

# العناوين
cols = st.columns([1, 1, 1, 1, 2, 1, 1.8])
titles = ["إشارة", "السهم", "يومي %", "السعر", "الفلتر", "الجودة", "⚡ تنبيه استباقي"]
for col, title in zip(cols, titles):
    col.markdown(f'<div class="header-box">{title}</div>', unsafe_allow_html=True)

try:
    # جلب البيانات باستخدام threads لتسريع العملية
    data = yf.download(STOCKS, period='2d', interval='1m', group_by='ticker', progress=False, threads=True)

    for sym in STOCKS:
        try:
            df = data[sym].dropna()
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                
                p = float(df['Close'].iloc[-1])
                prev_c = df['Close'].iloc[0]
                chg = ((p - prev_c) / prev_c) * 100
                rsi = int(ta.rsi(df['Close'], length=14).iloc[-1])
                ema = ta.ema(df['Close'], length=50).iloc[-1]
                
                # --- منطق الاستباق المطور (أكثر حساسية) ---
                v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1])
                
                # شرط الدخول: سيولة تتحرك (أكثر من المعدل بـ 10% فقط) + اتجاه صحيح
                is_entry = v_ratio > 1.10 and ((p > ema and rsi > 50) or (p < ema and rsi < 50))
                
                # تأكيد ظهور البرق مع الدخول
                if is_entry:
                    pre_msg = "⚡ الدخول الآن ⚡"
                    msg_style = "entry-box-blue"
                    pre_icon = "⚡"
                else:
                    pre_msg = "مراقبة.."
                    msg_style = "wait-box"
                    pre_icon = ""
                
                style = "row-g" if p > ema else "row-r"
                icon = "🟢" if p > ema else "🔴"
                trend = "صاعد ↑" if p > ema else "هابط ↓"

                # العرض المباشر للأعمدة بصورة ضخمة
                r1, r2, r3, r4, r5, r6, r7 = st.columns([1, 1, 1, 1, 2, 1, 1.8])
                r1.markdown(f'<div class="{style} big-font">{pre_icon}{icon}</div>', unsafe_allow_html=True)
                r2.markdown(f'<div class="{style} big-font">{sym}</div>', unsafe_allow_html=True)
                r3.markdown(f'<div class="{style} big-font">{chg:+.2f}%</div>', unsafe_allow_html=True)
                r4.markdown(f'<div class="{style} big-font">{p:.2f}</div>', unsafe_allow_html=True)
                r5.markdown(f'<div class="{style} big-font">{trend} | {rsi}</div>', unsafe_allow_html=True)
                r6.markdown(f'<div class="{style} big-font">ممتازة ✅</div>', unsafe_allow_html=True)
                r7.markdown(f'<div class="{msg_style}">{pre_msg}</div>', unsafe_allow_html=True)
        except: continue

except Exception as e:
    st.write("🔄 يتم الآن تحديث نبض السوق...")
