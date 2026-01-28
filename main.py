import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
import time
from streamlit_autorefresh import st_autorefresh

# تحديث تلقائي كل 12 ثانية
st_autorefresh(interval=12000, key="v40_white_bg_final")

# إعداد الصفحة لتكون بعرض الشاشة الكامل
st.set_page_config(page_title="رادار القناص V40", layout="wide")

# دالة التنبيه الصوتي
def play_beep():
    audio_html = """
    <audio autoplay>
    <source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# --- تنسيق CSS لإجبار الخلفية البيضاء الكاملة ---
st.markdown("""
    <style>
    .block-container { padding: 2rem 1rem; }
    .full-width-table { width: 100% !important; border-collapse: collapse; table-layout: fixed; background-color: white; }
    
    th { background-color: #00416d !important; color: white !important; text-align: center !important; padding: 15px; }
    td { text-align: center !important; font-weight: bold !important; border: 1px solid #dddddd !important; padding: 12px !important; }
    
    /* حالة الهدوء: خلفية بيضاء نص رمادي */
    .row-calm { background-color: #ffffff !important; color: #94a3b8 !important; }
    
    /* حالة كول وبوت: خلفيات ملونة صريحة كما طلبت */
    .row-call { background-color: #006400 !important; color: white !important; }
    .row-put { background-color: #8B0000 !important; color: white !important; }
    
    /* حالة القوة: ألوان فاقعة ونار */
    .row-strong-call { background-color: #00FF00 !important; color: black !important; }
    .row-strong-put { background-color: #FF0000 !important; color: white !important; }

    .target-cell { color: #00d4ff !important; font-size: 1.1em; }
    .iv-blue { background-color: #00d4ff !important; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']
if 'signal_start' not in st.session_state: st.session_state.signal_start = {}

results = []
sound_triggered = False

for sym in STOCKS:
    try:
        ticker = yf.Ticker(sym)
        df = ticker.history(period='2d', interval='1m')
        
        if not df.empty and len(df) > 10:
            curr_p = float(df['Close'].iloc[-1])
            high_d, low_d = float(df['High'].max()), float(df['Low'].min())
            
            # المؤشرات
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            m_val, s_val = float(macd.iloc[-1, 0]), float(macd.iloc[-1, 2])
            v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(5).mean().iloc[-1])
            returns = np.log(df['Close'] / df['Close'].shift(1))
            iv_val = returns.std() * np.sqrt(252 * 390) * 100
            
            # --- تحديد الحالة واللون ---
            # الافتراضي: هدوء
            icon, status, row_class, target = "⚪", "هدوء", "row-calm", "-"
            
            if m_val > s_val:
                target = f"{curr_p + (high_d - low_d)*0.04:.2f}"
                if v_ratio > 1.10: 
                    icon, status, row_class = "🔥", "كول قوي الآن", "row-strong-call"
                    sound_triggered = True
                else: 
                    icon, status, row_class = "🟢", "كول", "row-call"
            elif m_val < s_val:
                target = f"{curr_p - (high_d - low_d)*0.04:.2f}"
                if v_ratio > 1.10: 
                    icon, status, row_class = "🔥", "بوت قوي الآن", "row-strong-put"
                    sound_triggered = True
                else: 
                    icon, status, row_class = "🔴", "بوت", "row-put"

            # وقت الإشارة
            if "قوي" in status:
                if sym not in st.session_state.signal_start: st.session_state.signal_start[sym] = time.time()
                time_str = f"{int(time.time() - st.session_state.signal_start[sym])}ث"
            else:
                st.session_state.signal_start.pop(sym, None)
                time_str = "-"

            results.append({
                "⚡": icon, "S": sym, "ST": status, "T": time_str, "P": f"{curr_p:.2f}", 
                "TG": target, "IV": f"{iv_val:.1f}%", "class": row_class, "iv_val_num": iv_val
            })
    except: continue

if sound_triggered: play_beep()

st.markdown("<h1 style='text-align:center;'>💎 رادار القناص V40 💎</h1>", unsafe_allow_html=True)

if results:
    html = "<table class='full-width-table'><thead><tr><th>🔥</th><th>السهم</th><th>الحالة</th><th>الوقت</th><th>السعر</th><th>الهدف 🎯</th><th>IV</th></tr></thead><tbody>"
    for r in results:
        # تحديد كلاس خلية الـ IV بناءً على النسبة
        iv_cell_class = "class='iv-blue'" if r['iv_val_num'] < 10 else ""
        
        html += f"<tr class='{r['class']}'>"
        html += f"<td>{r['⚡']}</td><td>{r['S']}</td><td>{r['ST']}</td><td>{r['T']}</td><td>{r['P']}</td><td class='target-cell'>{r['TG']}</td>"
        html += f"<td {iv_cell_class}>{r['IV']}</td></tr>"
    st.markdown(html + "</tbody></table>", unsafe_allow_html=True)
