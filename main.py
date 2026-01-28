import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
import time
from streamlit_autorefresh import st_autorefresh

# تحديث كل 15 ثانية
st_autorefresh(interval=15000, key="v42_pro_filters")

st.set_page_config(page_title="رادار القناص V42.0", layout="wide")

def play_beep():
    st.markdown("""<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

# --- تنسيق CSS المخطط والخط الكبير ---
st.markdown("""
    <style>
    .block-container { padding: 1rem; max-width: 98%; }
    .stApp { background-color: white; }
    .full-width-table { width: 100% !important; border-collapse: collapse; background-color: white; border: 2px solid black !important; }
    th { background-color: #1e293b !important; color: white !important; text-align: center !important; padding: 10px; font-size: 18px; border: 2px solid black !important; }
    td { text-align: center !important; font-weight: 900 !important; border: 2px solid black !important; padding: 10px 5px !important; font-size: 20px !important; color: black !important; }
    
    .row-calm { background-color: #ffffff !important; }
    .row-green { background-color: #22c55e !important; } 
    .row-red { background-color: #ef4444 !important; }   
    .iv-blue { background-color: #7dd3fc !important; } 
    
    .legend-box { width: 230px; padding: 10px; border: 2px solid black; border-radius: 8px; background-color: #f8fafc; }
    .leg-item { display: flex; align-items: center; margin-bottom: 6px; font-size: 14px; font-weight: bold; color: black; }
    .leg-color { width: 18px; height: 18px; margin-right: 8px; border-radius: 3px; border: 1px solid black; }
    </style>
    """, unsafe_allow_html=True)

STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']

results = []
sound_triggered = False

try:
    # جلب بيانات كافية لحساب المتوسطات (EMA 200 يتطلب بيانات أكثر)
    data = yf.download(STOCKS, period='5d', interval='1m', group_by='ticker', progress=False)
    
    for sym in STOCKS:
        df = data[sym].dropna()
        if not df.empty and len(df) > 200:
            curr_p = float(df['Close'].iloc[-1])
            prev_close = float(df['Close'].iloc[0]) # سعر بداية البيانات المجلوبة كتقريب
            change_pct = ((curr_p - prev_close) / prev_close) * 100
            
            # حساب المؤشرات الاحترافية
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            rsi = ta.rsi(df['Close'], length=14).iloc[-1]
            ema200 = ta.ema(df['Close'], length=200).iloc[-1]
            
            m_val, s_val = float(macd.iloc[-1, 0]), float(macd.iloc[-1, 2])
            v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(5).mean().iloc[-1])
            returns = np.log(df['Close'] / df['Close'].shift(1))
            iv_val = returns.std() * np.sqrt(252 * 390) * 100
            
            # تحديد الفلتر (الاتجاه)
            trend = "صاعد ↑" if curr_p > ema200 else "هابط ↓"
            filter_text = f"{trend} | RSI:{int(rsi)}"
            
            # منطق الإشارة
            icon, status, row_class = "⚪", "هدوء", "row-calm"
            if m_val > s_val:
                row_class = "row-green"
                if v_ratio > 1.2: 
                    icon, status = "انفجار 🚀", "كول قوي"
                    sound_triggered = True
                else: icon, status = "🟢", "كول"
            elif m_val < s_val:
                row_class = "row-red"
                if v_ratio > 1.2: 
                    icon, status = "انفجار 📉", "بوت قوي"
                    sound_triggered = True
                else: icon, status = "🔴", "بوت"

            results.append({
                "⚡": icon, "S": sym, "ST": status, "CH": f"{change_pct:+.2f}%", 
                "P": f"{curr_p:.2f}", "FLT": filter_text, "IV": f"{iv_val:.1f}%", 
                "class": row_class, "iv_val_num": iv_val
            })

    st.markdown("<h1 style='text-align:center; color:black;'>💎 رادار المحترفين V42.0 💎</h1>", unsafe_allow_html=True)
    col_leg, col_tab = st.columns([1, 5])

    with col_leg:
        st.markdown("""
            <div class="legend-box">
                <h5 style="margin:0 0 10px 0; border-bottom:1px solid black;">فلاتر المحترفين</h5>
                <div class="leg-item"><b>EMA 200:</b> يحدد أمان الاتجاه</div>
                <div class="leg-item"><b>RSI:</b> يمنع الدخول في القمم</div>
                <div class="leg-item"><b>% :</b> قوة السيولة اليومية</div>
                <hr style="margin:10px 0; border:0; border-top:1px solid black;">
                <div class="leg-item"><div class="leg-color" style="background-color:#22c55e;"></div> كول / انفجار صاعد</div>
                <div class="leg-item"><div class="leg-color" style="background-color:#ef4444;"></div> بوت / انفجار هابط</div>
            </div>
        """, unsafe_allow_html=True)

    with col_tab:
        if results:
            html = "<table class='full-width-table'><thead><tr><th>إشارة</th><th>السهم</th><th>تغير %</th><th>السعر</th><th>الفلتر (الاتجاه | RSI)</th><th>IV</th></tr></thead><tbody>"
            for r in results:
                iv_style = "class='iv-blue'" if r['iv_val_num'] < 10 else ""
                html += f"<tr class='{r['class']}'><td>{r['⚡']}</td><td>{r['S']}</td><td>{r['CH']}</td><td>{r['P']}</td><td>{r['FLT']}</td><td {iv_style}>{r['IV']}</td></tr>"
            st.markdown(html + "</tbody></table>", unsafe_allow_html=True)
            if sound_triggered: play_beep()
except:
    st.info("جاري فحص الاتجاهات... انتظر ثواني")
