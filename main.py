import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

# تحديث كل 10 ثوانٍ
st_autorefresh(interval=10000, key="v42_blue_fire_box")

st.set_page_config(page_title="رادار القناص V42.2", layout="wide")

# تصميم الألوان والخطوط
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    .big-font { font-size: 30px !important; font-weight: 900 !important; color: black !important; text-align: center; }
    .header-box { background-color: #1e293b; color: white; padding: 10px; text-align: center; font-size: 25px; font-weight: bold; border: 3px solid black; }
    
    /* العمود الأول بخلفية بيضاء */
    .white-col-1 { 
        background-color: white !important; 
        padding: 10px; 
        border: 3px solid black; 
        display: flex;
        justify-content: center;
        align-items: center;
        height: 85px;
    }
    
    /* مربع النار الأزرق عند الدخول */
    .fire-box-blue {
        background-color: #0000FF !important;
        color: white !important;
        font-size: 35px !important;
        padding: 10px 25px;
        border-radius: 10px;
        font-weight: bold;
    }

    /* ألوان الصفوف المعتادة */
    .row-g { background-color: #22c55e; padding: 20px; border: 3px solid black; margin-bottom: -3px; }
    .row-r { background-color: #ef4444; padding: 20px; border: 3px solid black; margin-bottom: -3px; }
    
    /* إشارة الدخول في العمود الأخير */
    .entry-blue-text { 
        color: #0000FF !important; 
        font-size: 30px !important; 
        font-weight: 900; 
        text-align: center;
        background-color: white;
        padding: 20px;
        border: 3px solid black;
    }
    .wait-box { background-color: white; color: #aaaaaa; font-size: 25px; padding: 20px; border: 3px solid black; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"<h1 style='text-align:center; color:black;'>💎 رادار القناص V42.2 💎</h1>", unsafe_allow_html=True)

STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']

cols = st.columns([1, 1, 1, 1, 2, 1, 2.2])
titles = ["إشارة", "السهم", "يومي %", "السعر", "الفلتر", "الجودة", "⚡ تنبيه استباقي"]
for col, title in zip(cols, titles):
    col.markdown(f'<div class="header-box">{title}</div>', unsafe_allow_html=True)

try:
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
                v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1])
                
                # شرط الدخول الاستباقي
                is_entry = (v_ratio > 1.25) and ((p > ema and rsi > 52) or (p < ema and rsi < 48))
                
                style = "row-g" if p > ema else "row-r"
                icon = "🟢" if p > ema else "🔴"
                
                # إعداد المحتوى اللحظي
                if is_entry:
                    # يظهر مربع أزرق صغير داخل الخلفية البيضاء للعمود الأول
                    icon_html = f'<div class="white-col-1"><div class="fire-box-blue">🔥</div></div>'
                    entry_html = f'<div class="entry-blue-text">الدخول الآن 🔥</div>'
                else:
                    icon_html = f'<div class="white-col-1"><div style="font-size:35px;">{icon}</div></div>'
                    entry_html = f'<div class="wait-box">مراقبة..</div>'

                # العرض اللحظي
                r1, r2, r3, r4, r5, r6, r7 = st.columns([1, 1, 1, 1, 2, 1, 2.2])
                r1.markdown(icon_html, unsafe_allow_html=True)
                r2.markdown(f'<div class="{style} big-font">{sym}</div>', unsafe_allow_html=True)
                r3.markdown(f'<div class="{style} big-font">{chg:+.2f}%</div>', unsafe_allow_html=True)
                r4.markdown(f'<div class="{style} big-font">{p:.2f}</div>', unsafe_allow_html=True)
                r5.markdown(f'<div class="{style} big-font">{"صاعد" if p > ema else "هابط"} | {rsi}</div>', unsafe_allow_html=True)
                r6.markdown(f'<div class="{style} big-font">ممتازة ✅</div>', unsafe_allow_html=True)
                r7.markdown(entry_html, unsafe_allow_html=True)
        except: continue
except:
    st.write("🔄 جاري التحديث...")
