import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

# تحديث كل 15 ثانية
st_autorefresh(interval=15000, key="v42_2_final_fix")

st.set_page_config(page_title="رادار القناص V42.2", layout="wide")

def play_beep():
    st.markdown("""<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

# التنسيق البصري (ثابت كما تحبه)
st.markdown("""
    <style>
    .block-container { padding: 1rem; max-width: 98%; }
    .stApp { background-color: white; }
    .full-width-table { width: 100% !important; border-collapse: collapse; border: 3px solid black !important; }
    th { background-color: #1e293b !important; color: white !important; text-align: center !important; font-size: 20px; border: 2px solid black !important; }
    td { text-align: center !important; font-weight: 900 !important; border: 2px solid black !important; padding: 12px 5px !important; font-size: 20px !important; color: black !important; }
    .row-green { background-color: #22c55e !important; } 
    .row-red { background-color: #ef4444 !important; }   
    .iv-blue { background-color: #7dd3fc !important; } 
    </style>
    """, unsafe_allow_html=True)

STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']
results = []
sound_triggered = False

# دالة لجلب البيانات مع محاولات متعددة للفريمات
def fetch_data(symbol):
    intervals = ['1m', '5m', '15m', '1d']
    for inter in intervals:
        try:
            df = yf.download(symbol, period='5d', interval=inter, progress=False, show_errors=False)
            if not df.empty and len(df) > 20:
                return df, inter
        except:
            continue
    return pd.DataFrame(), None

try:
    for sym in STOCKS:
        df, used_interval = fetch_data(sym)
        
        if not df.empty:
            # معالجة بيانات Multi-index إذا وجدت
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            curr_p = float(df['Close'].iloc[-1])
            prev_close = float(df['Close'].iloc[-2])
            change_pct = ((curr_p - prev_close) / prev_close) * 100
            
            # حساب المؤشرات
            macd = ta.macd(df['Close'], fast=5, slow=13, signal=4)
            rsi_val = ta.rsi(df['Close'], length=14).iloc[-1]
            ema_fast = ta.ema(df['Close'], length=50).iloc[-1]
            
            # الاستباق (Squeeze)
            bbands = ta.bbands(df['Close'], length=20, std=2)
            bb_width = (bbands['BBU_20_2.0'] - bbands['BBL_20_2.0']) / bbands['BBM_20_2.0']
            is_squeeze = bb_width.iloc[-1] < bb_width.rolling(20).mean().iloc[-1]
            
            v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(5).mean().iloc[-1])
            iv_val = df['Close'].pct_change().std() * np.sqrt(252 * 390) * 100
            
            trend = "صاعد ↑" if curr_p > (ema_fast if not np.isnan(ema_fast) else 0) else "هابط ↓"
            icon, row_class, quality = "⚪", "row-calm", "-"
            
            pre_entry = "⚡" if (is_squeeze and v_ratio > 1.1) else ""
            
            m_val = float(macd.iloc[-1, 0]) if not macd.empty else 0
            s_val = float(macd.iloc[-1, 2]) if not macd.empty else 0
            
            if m_val > s_val:
                row_class, icon = "row-green", ("انفجار 🚀" if v_ratio > 1.2 else "🟢")
                quality = "ممتازة ✅" if trend == "صاعد ↑" else "عكس التيار ⚠️"
                if v_ratio > 1.2: sound_triggered = True
            elif m_val < s_val:
                row_class, icon = "row-red", ("انفجار 📉" if v_ratio > 1.2 else "🔴")
                quality = "ممتازة ✅" if trend == "هابط ↓" else "عكس التيار ⚠️"
                if v_ratio > 1.2: sound_triggered = True

            results.append({
                "⚡": f"{pre_entry}{icon}", "S": sym, "CH": f"{change_pct:+.2f}%", 
                "P": f"{curr_p:.2f}", "FLT": f"{trend} | RSI:{int(rsi_val)}", 
                "Q": quality, "IV": f"{iv_val:.1f}%", "class": row_class, "iv_val_num": iv_val
            })

    st.markdown("<h1 style='text-align:center; color:black;'>💎 رادار القناص V42.2 (استجابة سريعة) 💎</h1>", unsafe_allow_html=True)
    
    if results:
        html = "<table class='full-width-table'><thead><tr><th>إشارة</th><th>السهم</th><th>يومي %</th><th>السعر</th><th>الفلتر</th><th>الجودة</th><th>IV</th></tr></thead><tbody>"
        for r in results:
            iv_s = "class='iv-blue'" if r['iv_val_num'] < 10 else ""
            html += f"<tr class='{r['class']}'><td>{r['⚡']}</td><td>{r['S']}</td><td>{r['CH']}</td><td>{r['P']}</td><td>{r['FLT']}</td><td>{r['Q']}</td><td {iv_s}>{r['IV']}</td></tr>"
        st.markdown(html + "</tbody></table>", unsafe_allow_html=True)
        if sound_triggered: play_beep()
    else:
        st.error("فشل الرادار في العثور على بيانات نشطة. قد يكون السوق مغلقاً أو هناك مشكلة في الاتصال بمزود البيانات.")

except Exception as e:
    st.error(f"خطأ تقني: {e}")
