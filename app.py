import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import ta

st.title("📈 Coin Futures Sinyal Uygulaması")

symbol = st.text_input("Kripto Para Sembolü (Örn: BTC-USD, ETH-USD)", "BTC-USD")

@st.cache_data
def get_data(symbol, period="90d", interval="1h"):
    try:
        df = yf.download(symbol, period=period, interval=interval)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
        return None

df = get_data(symbol)

if df is not None:
    st.subheader("📊 Güncel Fiyat Verileri")
    st.write(df.tail(10))

    # ✅ Hata düzeltilmiş RSI hesaplama
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"].squeeze(), window=14).rsi()

    # MACD Hesaplama
    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_Signal"] = macd.macd_signal()

    # Bollinger Bandı Hesaplama
    bb = ta.volatility.BollingerBands(df["Close"])
    df["BB_High"] = bb.bollinger_hband()
    df["BB_Low"] = bb.bollinger_lband()

    st.subheader("📊 Teknik Göstergeler")
    st.write(df.tail(10))

    # Grafikler
    st.subheader("RSI Göstergesi")
    st.line_chart(df["RSI"])

    st.subheader("MACD Göstergesi")
    st.line_chart(df[["MACD", "MACD_Signal"]])

    st.subheader("Bollinger Bantları")
    st.line_chart(df[["Close", "BB_High", "BB_Low"]])

    st.subheader("📢 Al-Sat Sinyalleri")

    if df["RSI"].iloc[-1] < 30:
        st.success("✅ **AL Sinyali:** RSI 30'un altında, fiyat aşırı satım bölgesinde.")
    elif df["RSI"].iloc[-1] > 70:
        st.warning("⚠️ **SAT Sinyali:** RSI 70'in üzerinde, fiyat aşırı alım bölgesinde.")
    else:
        st.info("ℹ️ **Nötr:** RSI normal aralıkta.")

    if df["MACD"].iloc[-1] > df["MACD_Signal"].iloc[-1]:
        st.success("✅ **AL Sinyali:** MACD çizgisi sinyal çizgisinin üstünde.")
    else:
        st.warning("⚠️ **SAT Sinyali:** MACD çizgisi sinyal çizgisinin altında.")

else:
    st.error("❌ Veri yüklenemedi. Lütfen geçerli bir sembol girin.")
