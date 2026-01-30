import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

# تحديث تلقائي كل 10 ثواني
st_autorefresh(interval=10000, key="v42_fix_final")

st.set_page_config(page_title="رادار القناص V42.2", layout="wide")

# --- التنسيق البصري: خط ضخم 25، خلفية بيضاء، جدول أسود ---
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    .main-table { 
        width: 100%; 
        border-collapse: collapse; 
        border: 4px solid black !important;
        font-size: 25px !important; /* خط كبير جداً */
    }
    th { 
        background-color: #1e293b !important; 
        color: white !important; 
        padding: 15px; 
        border: 2px solid black !important;
    }
    td { 
        text-align: center !important; 
        font-weight: bold !important; 
        border: 2px solid black !important; 
        padding: 15px !important;
        color: black !important;
    }
    .row-green { background-color: #22c55e !important; } 
    .row-red { background-color: #ef4444 !important; }
    .row-white { background-color: #ffffff !important; }
    .iv-blue { background-color: #7dd3fc !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:black;'>💎 رادار القناص V42.2 (استجابة سريعة) 💎</h1>", unsafe_allow_html=True)

STOCKS = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NIO']

try:
    # جلب البيانات بطريقة مبسطة جداً لضمان عدم تعليق الصفحة
    data = yf.download(STOCKS, period='2d', interval='5m', group_by='ticker', progress=False)
    
    rows_html = ""
    for sym in STOCKS:
        df = data[sym].dropna()
        if not df.empty:
            # تنظيف الأعمدة
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            p = float(df['Close'].iloc[-1])
            change = ((p - df['Open'].iloc[0]) / df['Open'].iloc[0]) * 100
            rsi = ta.rsi(df['Close'], length=14).iloc[-1]
            ema = ta.ema(df['Close'], length=50).iloc[-1]
            
            # منطق الاستباق البسيط ⚡
            vol_ratio = float(df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1])
            pre = "⚡" if vol_ratio > 1.3 else ""
            
            # تحديد اللون والجودة
            bg_color = "row-white"
            icon = "⚪"
            quality = "عكس التيار ⚠️"
            
            if p > ema and rsi > 50:
                bg_color = "row-green"
                icon = "🟢"
                quality = "ممتازة ✅"
            elif p < ema and rsi < 50:
                bg_color = "row-red"
                icon = "🔴"
                quality = "ممتازة ✅"
            
            # بناء صف الجدول
            rows_html += f"""
            <tr class='{bg_color}'>
                <td>{pre}{icon}</td>
                <td>{sym}</td>
                <td>{change:+.2f}%</td>
                <td>{p:.2f}</td>
                <td>{'صاعد ↑' if p > ema else 'هابط ↓'} | RSI:{int(rsi)}</td>
                <td>{quality}</td>
                <td class='iv-blue'>-</td>
            </tr>
            """

    # عرض الجدول النهائي
    if rows_html:
        table_html = f"""
        <table class='main-table'>
            <thead>
                <tr>
                    <th>إشارة</th><th>السهم</th><th>يومي %</th><th>السعر</th><th>الفلتر</th><th>الجودة</th><th>IV</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        """
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.warning("جاري تحميل البيانات.. انتظر ثوانٍ")

except Exception as e:
    st.write("يتم التحديث الآن...")
