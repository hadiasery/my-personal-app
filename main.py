import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

# تحديث كل 15 ثانية
st_autorefresh(interval=15000, key="v42_2_final_safe")

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

st.markdown("<h1 style='text-align:center; color:black;'>💎 رادار القناص V42.2 (استجابة سريعة) 💎</h1>", unsafe_allow_html=True)

try:
    # جلب البيانات بفريم 5 دقائق لضمان الاستجابة وعدم التعليق
    data = yf.download(STOCKS, period='5d', interval='5m', group_by='ticker', progress=False)
    
    for sym in STOCKS:
        try:
            df = data[sym].dropna()
            if not df.empty:
                # التأكد من فك تعارض الأعمدة
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                
                curr_p = float(df['Close'].iloc[-1])
                prev_p = float(df['Close'].iloc[-2])
                change_pct = ((curr_p - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
                
                # حسابات الاستباق والاتجاه
                rsi_val = ta.rsi(df['Close'], length=14).iloc[-1]
                ema_50 = ta.ema(df['Close'], length=50).iloc[-1]
                
                # Squeeze (الاستباق)
                bb = ta.bbands(df['Close'], length=20)
                width = (bb['BBU_20_2.0'] - bb['BBL_20_2.0']) / bb['BBM_20_2.0']
                is_squeeze = width.iloc[-1] < width.rolling(20).mean().iloc[-1]
                
                v_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1])
                iv_val = df['Close'].pct_change().std() * np.sqrt(252 * 78) * 100
                
                trend = "صاعد ↑" if curr_p > ema_50 else "هابط ↓"
                icon, row_class, quality = "⚪", "row-calm", "-"
                
                # إشارة الاستباق ⚡
                pre = "⚡" if (is_squeeze and v_ratio > 1.05) else ""

                if rsi_val > 55:
                    row_class, icon = "row-green", ("انفجار 🚀" if v_ratio > 1.2 else "🟢")
                    quality = "ممتازة ✅" if trend == "صاعد ↑" else "عكس التيار ⚠️"
                    if v_ratio > 1.2: sound_triggered = True
                elif rsi_val < 45:
                    row_class, icon = "row-red", ("انفجار 📉" if v_ratio > 1.2 else "🔴")
                    quality = "ممتازة ✅" if trend == "هابط ↓" else "عكس التيار ⚠️"
                    if v_ratio > 1.2: sound_triggered = True

                results.append({
                    "⚡": f"{pre}{icon}", "S": sym, "CH": f"{change_pct:+.2f}%", 
                    "P": f"{curr_p:.2f}", "FLT": f"{trend} | RSI:{int(rsi_val)}", 
                    "Q": quality, "IV": f"{iv_val:.1f}%", "class": row_class, "iv_val_num": iv_val
                })
        except: continue

    if results:
        html = "<table class='full-width-table'><thead><tr><th>إشارة</th><th>السهم</th><th>يومي %</th><th>السعر</th><th>الفلتر</th><th>الجودة</th><th>IV</th></tr></thead><tbody>"
        for r in results:
            iv_s = "class='iv-blue'" if r['iv_val_num'] < 10 else ""
            html += f"<tr class='{r['class']}'><td>{r['⚡']}</td><td>{r['S']}</td><td>{r['CH']}</td><td>{r['P']}</td><td>{r['FLT']}</td><td>{r['Q']}</td><td {iv_s}>{r['IV']}</td></tr>"
        st.markdown(html + "</tbody></table>", unsafe_allow_html=True)
        if sound_triggered: play_beep()
    else:
        st.warning("⚠️ لا توجد بيانات حالية.. تأكد من أن السوق مفتوح أو انتظر ثوانٍ.")

except Exception as e:
    st.error(f"خطأ: {e}")
