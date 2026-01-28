import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
import time
from streamlit_autorefresh import st_autorefresh

# تحديث كل 15 ثانية
st_autorefresh(interval=15000, key="v41_5_black_text")

st.set_page_config(page_title="رادار القناص V41.5", layout="wide")

def play_beep():
    st.markdown("""<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

# --- تنسيق CSS للنص الأسود والألوان المتوسطة ---
st.markdown("""
    <style>
    .block-container { padding: 1rem; max-width: 98%; }
    .stApp { background-color: white; }
    
    .main-container { display: flex; gap: 20px; align-items: flex-start; }
    .legend-box { width: 220px; padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px; background-color: #f8fafc; }
    
    .full-width-table { width: 100% !important; border-collapse: collapse; background-color: white; }
    th { background-color: #1e293b !important; color: white !important; text-align: center !important; padding: 10px; font-size: 14px; }
    
    /* جعل كل النصوص باللون الأسود الصريح */
    td { 
        text-align: center !important; 
        font-weight: 800 !important; /* خط أعرض قليلاً للوضوح */
        border: 1px solid #cbd5e1 !important; 
        padding: 8px; 
        font-size: 16px; 
        color: black !important; 
    }
    
    /* الألوان المتوسطة للخلفيات */
    .row-calm { background-color: #ffffff !important; }
    .row-call { background-color: #4ade80 !important; } /* أخضر متوسط */
    .row-put { background-color: #fb7185 !important; }  /* أحمر/وردي متوسط */
    .row-strong-call { background-color: #22c55e !important; } /* أخضر قوي */
    .row-strong-put { background-color: #ef4444 !important; }  /* أحمر قوي */
    
    /* تمييز الـ IV والهدف مع بقاء النص أسود */
    .iv-blue { background-color: #7dd3fc !important; } 
    .target-val { color: black !important; text-decoration: underline; }
    
    .leg-item { display: flex; align-items: center; margin-bottom: 8px; font-size: 13px; font-weight: bold; color: black; }
    .leg-color { width: 18px; height: 18px; margin-right: 10px; border-radius: 3px; border: 1px solid #94a3b8; }
    </style>
    """, unsafe_allow_html=True)

STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']

if 'signal_start' not in st.session_state: st.session_state.signal_start = {}
results = []
sound_triggered = False

try:
    data = yf.download(STOCKS, period='2d', interval='1m', group_by='ticker', progress=False)
    
    for sym in STOCKS:
        df = data[sym].dropna()
        if not df.empty and len(df) > 10:
            curr_p = float(df['Close'].iloc[-1])
            high_d, low_d = float(df['High'].max()), float(df['Low'].min())
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            m_val, s_val = float(macd.iloc[-1, 0]), float(macd.iloc[-1, 2])
            v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(5).mean().iloc[-1])
            returns = np.log(df['Close'] / df['Close'].shift(1))
            iv_val = returns.std() * np.sqrt(252 * 390) * 100
            
            icon, status, row_class, target = "⚪", "هدوء", "row-calm", "-"
            
            if m_val > s_val:
                target = f"{curr_p + (high_d - low_d)*0.04:.2f}"
                if v_ratio > 1.15: 
                    icon, status, row_class = "🔥", "قوي", "row-strong-call"
                    sound_triggered = True
                else: icon, status, row_class = "🟢", "كول", "row-call"
            elif m_val < s_val:
                target = f"{curr_p - (high_d - low_d)*0.04:.2f}"
                if v_ratio > 1.15: 
                    icon, status, row_class = "🔥", "قوي", "row-strong-put"
                    sound_triggered = True
                else: icon, status, row_class = "🔴", "بوت", "row-put"

            results.append({"⚡": icon, "S": sym, "ST": status, "P": f"{curr_p:.2f}", "TG": target, "IV": f"{iv_val:.1f}%", "class": row_class, "iv_val_num": iv_val})

    st.markdown("<h2 style='text-align:center; color:black;'>💎 رادار القناص V41.5 💎</h2>", unsafe_allow_html=True)

    col_leg, col_tab = st.columns([1, 5])

    with col_leg:
        st.markdown("""
            <div class="legend-box">
                <h5 style="margin:0 0 10px 0; color:black; border-bottom:1px solid #ddd;">دليل الإشارات</h5>
                <div class="leg-item"><div class="leg-color" style="background-color:#22c55e;"></div> صعود قوي</div>
                <div class="leg-item"><div class="leg-color" style="background-color:#4ade80;"></div> كول (متابعة)</div>
                <div class="leg-item"><div class="leg-color" style="background-color:#ef4444;"></div> هبوط قوي</div>
                <div class="leg-item"><div class="leg-color" style="background-color:#fb7185;"></div> بوت (متابعة)</div>
                <div class="leg-item"><div class="leg-color" style="background-color:#ffffff;"></div> هدوء</div>
                <div class="leg-item"><div class="leg-color" style="background-color:#7dd3fc;"></div> IV رخيص</div>
            </div>
        """, unsafe_allow_html=True)

    with col_tab:
        if results:
            html = "<table class='full-width-table'><thead><tr><th>🔥</th><th>السهم</th><th>الحالة</th><th>السعر</th><th>الهدف 🎯</th><th>IV</th></tr></thead><tbody>"
            for r in results:
                iv_style = "class='iv-blue'" if r['iv_val_num'] < 10 else ""
                html += f"<tr class='{r['class']}'><td>{r['⚡']}</td><td>{r['S']}</td><td>{r['ST']}</td><td>{r['P']}</td><td class='target-val'>{r['TG']}</td><td {iv_style}>{r['IV']}</td></tr>"
            st.markdown(html + "</tbody></table>", unsafe_allow_html=True)
            if sound_triggered: play_beep()
except:
    st.info("جاري التحديث...")
