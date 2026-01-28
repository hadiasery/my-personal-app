import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
import time
from streamlit_autorefresh import st_autorefresh

# تحديث كل 15 ثانية
st_autorefresh(interval=15000, key="v41_4_legend")

st.set_page_config(page_title="رادار القناص V41.4", layout="wide")

def play_beep():
    st.markdown("""<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

# --- تنسيق CSS للجدول ودليل الألوان ---
st.markdown("""
    <style>
    .block-container { padding: 1rem; max-width: 98%; }
    .stApp { background-color: white; }
    
    /* تقسيم الشاشة: دليل يسار وجدول يمين */
    .main-container { display: flex; gap: 20px; align-items: flex-start; }
    .legend-box { width: 250px; padding: 15px; border: 1px solid #e2e8f0; border-radius: 8px; background-color: #f8fafc; }
    .table-box { flex-grow: 1; }
    
    .full-width-table { width: 100% !important; border-collapse: collapse; background-color: white; }
    th { background-color: #1e293b !important; color: white !important; text-align: center !important; padding: 10px; font-size: 14px; }
    td { text-align: center !important; font-weight: bold !important; border: 1px solid #e2e8f0 !important; padding: 8px; font-size: 15px; }
    
    /* الألوان المتوسطة */
    .row-calm { background-color: #ffffff !important; color: #64748b !important; }
    .row-call { background-color: #22c55e !important; color: white !important; }
    .row-put { background-color: #ef4444 !important; color: white !important; }
    .row-strong-call { background-color: #15803d !important; color: white !important; }
    .row-strong-put { background-color: #b91c1c !important; color: white !important; }
    .iv-blue { background-color: #0ea5e9 !important; color: white !important; }
    
    /* ستايل دليل الألوان */
    .leg-item { display: flex; align-items: center; margin-bottom: 8px; font-size: 13px; font-weight: bold; }
    .leg-color { width: 20px; height: 20px; margin-right: 10px; border-radius: 4px; border: 1px solid #ddd; }
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

    st.markdown("<h2 style='text-align:center;'>💎 رادار القناص V41.4 💎</h2>", unsafe_allow_html=True)

    # إنشاء واجهة العرض (دليل + جدول)
    col_leg, col_tab = st.columns([1, 4])

    with col_leg:
        st.markdown("""
            <div class="legend-box">
                <h4 style="margin-top:0; border-bottom:1px solid #ddd; padding-bottom:5px;">دليل الألوان</h4>
                <div class="leg-item"><div class="leg-color" style="background-color:#15803d;"></div> صعود قوي (انفجار)</div>
                <div class="leg-item"><div class="leg-color" style="background-color:#22c55e;"></div> اتجاه صاعد (كول)</div>
                <div class="leg-item"><div class="leg-color" style="background-color:#b91c1c;"></div> هبوط قوي (انفجار)</div>
                <div class="leg-item"><div class="leg-color" style="background-color:#ef4444;"></div> اتجاه هابط (بوت)</div>
                <div class="leg-item"><div class="leg-color" style="background-color:#ffffff; border:1px solid #ccc;"></div> هدوء / انتظار</div>
                <div class="leg-item"><div class="leg-color" style="background-color:#0ea5e9;"></div> IV رخيص (عقود لقطة)</div>
            </div>
        """, unsafe_allow_html=True)

    with col_tab:
        if results:
            html = "<table class='full-width-table'><thead><tr><th>🔥</th><th>السهم</th><th>الحالة</th><th>السعر</th><th>الهدف 🎯</th><th>IV</th></tr></thead><tbody>"
            for r in results:
                iv_style = "class='iv-blue'" if r['iv_val_num'] < 10 else ""
                html += f"<tr class='{r['class']}'><td>{r['⚡']}</td><td>{r['S']}</td><td>{r['ST']}</td><td>{r['P']}</td><td style='color:#2563eb;'>{r['TG']}</td><td {iv_style}>{r['IV']}</td></tr>"
            st.markdown(html + "</tbody></table>", unsafe_allow_html=True)
            if sound_triggered: play_beep()

except:
    st.info("تحديث...")
