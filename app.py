import streamlit as st
import pandas as pd
import yfinance as yf
import ta

# Başlık
st.title("Coin Futures Sinyal Uygulaması")

# Kullanıcıdan sembol alma
symbol = st.text_input("Kripto Sembolü (örn: BTC-USD)", "BTC-USD")

# Veriyi çekme
df = yf.download(symbol, period="6mo", interval="1d")

# Verinin düzgün formatta olup olmadığını kontrol etme
if df.empty:
    st.error("Veri çekilemedi. Lütfen geçerli bir sembol girin.")
else:
    # Veriyi işleme
    df = df[["Close"]].copy()

    # **HATA DÜZELTME:** 'Close' sütununun 1D olması sağlandı
    df["Close"] = df["Close"].squeeze()

    # **RSI Hesaplama**
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()

    # **MACD Hesaplama**
    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_Signal"] = macd.macd_signal()

    # **Bollinger Bantları Hesaplama**
    bb = ta.volatility.BollingerBands(df["Close"])
    df["BB_High"] = bb.bollinger_hband()
    df["BB_Low"] = bb.bollinger_lband()

    # **Grafikler**
    st.subheader("Fiyat Hareketi ve Teknik İndikatörler")
    st.line_chart(df[["Close"]])

    st.subheader("RSI Grafiği")
    st.line_chart(df[["RSI"]])

    st.subheader("MACD Grafiği")
    st.line_chart(df[["MACD", "MACD_Signal"]])

    st.subheader("Bollinger Bantları")
    st.line_chart(df[["BB_High", "Close", "BB_Low"]])
    
    # **Sinyal**
    st.subheader("Al / Sat Sinyali")
    latest_rsi = df["RSI"].iloc[-1]
    latest_macd = df["MACD"].iloc[-1]
    latest_macd_signal = df["MACD_Signal"].iloc[-1]

    if latest_rsi < 30 and latest_macd > latest_macd_signal:
        st.success("Güçlü AL Sinyali ✅")
    elif latest_rsi > 70 and latest_macd < latest_macd_signal:
        st.error("Güçlü SAT Sinyali ❌")
    else:
        st.warning("Nötr / Bekle ⏳")

    # Veri tablosunu göster
    st.subheader("Son 10 Günlük Veri")
    st.write(df.tail(10))
