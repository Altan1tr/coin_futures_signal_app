import streamlit as st
import yfinance as yf
import pandas as pd
import talib

# Başlık
st.title("📈 Coin Futures Sinyal Uygulaması")

# Kullanıcıdan işlem yapılacak coini ve periyodu al
symbol = st.text_input("Kripto Sembolü (örn: BTC-USD)", "BTC-USD")
period = st.selectbox("Zaman Periyodu", ["1d", "1h", "5m"])

# Veriyi al
data = yf.download(symbol, period="3mo", interval=period)

if not data.empty:
    # Hareketli Ortalamalar
    data["SMA_20"] = talib.SMA(data["Close"], timeperiod=20)
    data["EMA_10"] = talib.EMA(data["Close"], timeperiod=10)

    # RSI Göstergesi
    data["RSI"] = talib.RSI(data["Close"], timeperiod=14)

    # MACD Göstergesi
    macd, macdsignal, macdhist = talib.MACD(data["Close"], fastperiod=12, slowperiod=26, signalperiod=9)
    data["MACD"] = macd
    data["MACD_Signal"] = macdsignal

    # Al-Sat Sinyalleri
    buy_signal = (data["RSI"] < 30) & (data["MACD"] > data["MACD_Signal"])
    sell_signal = (data["RSI"] > 70) & (data["MACD"] < data["MACD_Signal"])

    # Grafik Gösterimi
    st.subheader("Fiyat Grafiği")
    st.line_chart(data[["Close", "SMA_20", "EMA_10"]])

    st.subheader("RSI Göstergesi")
    st.line_chart(data["RSI"])

    st.subheader("MACD Göstergesi")
    st.line_chart(data[["MACD", "MACD_Signal"]])

    # Sinyalleri Göster
    st.subheader("Al - Sat Sinyalleri")
    st.write(data[["Close", "RSI", "MACD", "MACD_Signal"]].tail(10))

    if buy_signal.iloc[-1]:
        st.success("✅ ALIM SİNYALİ: RSI düşük, MACD yukarı yönlü!")
    elif sell_signal.iloc[-1]:
        st.error("❌ SATIŞ SİNYALİ: RSI yüksek, MACD aşağı yönlü!")
    else:
        st.warning("⚠️ Şu an belirgin bir sinyal yok!")

else:
    st.warning("⚠️ Veri alınamadı, lütfen geçerli bir sembol girin.")
