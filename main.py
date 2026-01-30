import streamlit as st
import yfinance as yf
import pandas_ta as ta
import time
from streamlit_autorefresh import st_autorefresh

# تحديث تلقائي
st_autorefresh(interval=10000, key="v48_ultra_clear")

st.set_page_config(page_title="رادار القناص V48.0", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    /* تصغير المسافات وتكبير الخط في العناوين */
    .header-box { 
        background-color: #0f172a; color: white; 
        padding: 5px; text-align: center; 
        font-size: 22px; font-weight: bold; 
        border: 1px solid white;
    }
    /* تنسيق الخلايا: خط كبير ومسافات مضغوطة */
    .row-g, .row-r, .num-box { 
        padding: 2px !important; 
        text-align: center; 
        font-size: 28px !important; /* خط كبير جداً */
        font-weight: bold; 
        height: 60px; 
        display: flex; align-items: center; justify-content: center;
        border: 1px solid #cbd5e1;
    }
    .row-g { background-color: #22c55e !important; color: black !important; }
    .row-r { background-color: #ef4444 !important; color: white !important; }
    .num-box { background-color: #f8fafc; color: #1e293b; }
    
    /* تنسيق لوحة الحيتان */
    .whale-card { 
        background-color: #f0f9ff; border: 3px solid #0369a1; 
        padding: 10px; border-radius: 10px; 
    }
    .whale-table td { 
        font-size: 24px !important; 
        font-weight: bold; 
        padding: 5px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🐋 رادار الحيتان V48.0 - نسخة سهم 🐋</h1>", unsafe_allow_html=True)

# الجدول الرئيسي - تقليل نسب العرض لضغط المسافات
cols = st.columns([0.8, 1.2, 1, 1, 1.2, 1.5])
titles = ["إشارة", "السهم", "السعر", "RSI %", "الاتجاه", "تنبيه"]

for col, title in zip(cols, titles):
    col.markdown(f'<div class="header-box">{title}</div>', unsafe_allow_html=True)

# محاكاة لبيانات سهم SPY مع الخط الكبير
r1, r2, r3, r4, r5, r6 = st.columns([0.8, 1.2, 1, 1, 1.2, 1.5])
r1.markdown('<div class="num-box">🔥</div>', unsafe_allow_html=True)
r2.markdown('<div class="row-r">SPY</div>', unsafe_allow_html=True)
r3.markdown('<div class="num-box">592.10</div>', unsafe_allow_html=True)
r4.markdown('<div class="row-r">42%</div>', unsafe_allow_html=True)
r5.markdown('<div class="row-r">هابط ↓</div>', unsafe_allow_html=True)
r6.markdown('<div class="num-box" style="font-size:20px !important;">فرصة PUT قوية</div>', unsafe_allow_html=True)

st.markdown("---")

# لوحة تتبع الحيتان مع الإضافات الجديدة (سعر الدخول، الحجم، الحالة)
st.markdown("### 🕵️‍♂️ سجل صيد الحيتان اللحظي")
st.markdown("""
    <div class="whale-card">
        <table class="whale-table" style="width:100%; text-align:center;">
            <tr style="color: #0369a1; font-size: 18px;">
                <td>العقد</td><td>السعر الدقيق 💰</td><td>الحجم (Size) 📊</td><td>القيمة 💵</td><td>الحالة 💎</td>
            </tr>
            <tr style="color: #ef4444;">
                <td>590 PUT</td>
                <td>$2.45</td>
                <td>4,500 عقد</td>
                <td>$1.1M</td>
                <td>متمسك 💎</td>
            </tr>
        </table>
    </div>
""", unsafe_allow_html=True)
