import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import matplotlib.pyplot as plt

# Başlık
st.title("📊 Coin Futures Sinyal Uygulaması")

# Kullanıcıdan kripto para sembolü ve zaman aralığı al
ticker = st.text_input("Kripto Para Sembolü (örn: BTC-USD)", "BTC-USD")
days = st.slider("Veri süresi (gün)", 1, 365, 30)

# Veriyi çek
st.write(f"📈 **{ticker} - Son {days} Günlük Veri**")
try:
    df = yf.download(ticker, period=f"{days}d")

    # Hareketli Ortalamalar
    df["SMA_20"] = df["Close"].rolling(window=20).mean()
    df["SMA_50"] = df["Close"].rolling(window=50).mean()

    # RSI Hesaplama
    df["RSI"] = ta.rsi(df["Close"], length=14)

    # MACD Hesaplama
    df["MACD"], df["Signal"], df["Hist"] = ta.macd(df["Close"])

    # Fiyat Grafiği
    fig, ax = plt.subplots(figsize=(10,5))
    ax.plot(df.index, df["Close"], label="Fiyat", color="blue")
    ax.plot(df.index, df["SMA_20"], label="SMA 20", color="red", linestyle="dashed")
    ax.plot(df.index, df["SMA_50"], label="SMA 50", color="green", linestyle="dashed")
    ax.set_title(f"{ticker} Fiyat Grafiği")
    ax.legend()
    st.pyplot(fig)

    # RSI Gösterimi
    fig, ax = plt.subplots(figsize=(10,3))
    ax.plot(df.index, df["RSI"], label="RSI", color="purple")
    ax.axhline(70, color="red", linestyle="dashed")
    ax.axhline(30, color="green", linestyle="dashed")
    ax.set_title("RSI (Relative Strength Index)")
    ax.legend()
    st.pyplot(fig)

    # MACD Gösterimi
    fig, ax = plt.subplots(figsize=(10,3))
    ax.plot(df.index, df["MACD"], label="MACD", color="orange")
    ax.plot(df.index, df["Signal"], label="Signal", color="blue", linestyle="dashed")
    ax.set_title("MACD (Moving Average Convergence Divergence)")
    ax.legend()
    st.pyplot(fig)

    # Sinyal Üretme
    latest_rsi = df["RSI"].iloc[-1]
    latest_macd = df["MACD"].iloc[-1]
    latest_signal = df["Signal"].iloc[-1]

    st.subheader("📢 Al / Sat Sinyali")
    if latest_rsi < 30 and latest_macd > latest_signal:
        st.success("🔵 **AL** sinyali oluştu! RSI düşük ve MACD yukarı yönlü kesişti.")
    elif latest_rsi > 70 and latest_macd < latest_signal:
        st.error("🔴 **SAT** sinyali oluştu! RSI yüksek ve MACD aşağı yönlü kesişti.")
    else:
        st.warning("🟡 **NÖTR** sinyal. Beklemede kal.")

except Exception as e:
    st.error(f"❌ Veri çekilirken hata oluştu: {e}")
