import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import ta

# Streamlit başlığı
st.title("📈 Coin Futures Sinyal Uygulaması")

# Kullanıcının gireceği kripto para sembolü
symbol = st.text_input("Kripto Para Sembolü (Örn: BTC-USD, ETH-USD)", "BTC-USD")

# Veri çekme fonksiyonu
@st.cache_data
def get_data(symbol, period="90d", interval="1h"):
    try:
        df = yf.download(symbol, period=period, interval=interval)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
        return None

# Veriyi çek ve göster
df = get_data(symbol)
if df is not None:
    st.subheader("📊 Güncel Fiyat Verileri")
    st.write(df.tail(10))

    # **Veri tiplerini kontrol edip dönüştürme**
    df["Close"] = df["Close"].astype(float)

    # **RSI Hesaplama (Hata Düzeltildi!)**
    rsi_indicator = ta.momentum.RSIIndicator(df["Close"])
    df["RSI"] = rsi_indicator.rsi()

    # **MACD Hesaplama (Hata Düzeltildi!)**
    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd().astype(float)
    df["MACD_Signal"] = macd.macd_signal().astype(float)

    # **Bollinger Bandı Hesaplama**
    bb = ta.volatility.BollingerBands(df["Close"])
    df["BB_High"] = bb.bollinger_hband().astype(float)
    df["BB_Low"] = bb.bollinger_lband().astype(float)

    # **Veriyi göster**
    st.subheader("📊 Teknik Göstergeler")
    st.write(df.tail(10))

    # **RSI Grafiği**
    st.subheader("RSI Göstergesi")
    st.line_chart(df["RSI"])

    # **MACD Grafiği**
    st.subheader("MACD Göstergesi")
    st.line_chart(df[["MACD", "MACD_Signal"]])

    # **Bollinger Bandı Grafiği**
    st.subheader("Bollinger Bantları")
    st.line_chart(df[["Close", "BB_High", "BB_Low"]])

    # **Al-Sat Sinyalleri**
    st.subheader("📢 Al-Sat Sinyalleri")

    # **RSI Sinyali**
    if df["RSI"].iloc[-1] < 30:
        st.success("✅ **AL Sinyali:** RSI 30'un altında, fiyat aşırı satım bölgesinde.")
    elif df["RSI"].iloc[-1] > 70:
        st.warning("⚠️ **SAT Sinyali:** RSI 70'in üzerinde, fiyat aşırı alım bölgesinde.")
    else:
        st.info("ℹ️ **Nötr:** RSI normal aralıkta.")

    # **MACD Sinyali**
    if df["MACD"].iloc[-1] > df["MACD_Signal"].iloc[-1]:
        st.success("✅ **AL Sinyali:** MACD çizgisi sinyal çizgisinin üstünde.")
    else:
        st.warning("⚠️ **SAT Sinyali:** MACD çizgisi sinyal çizgisinin altında.")

else:
    st.error("❌ Veri yüklenemedi. Lütfen geçerli bir sembol girin.")
