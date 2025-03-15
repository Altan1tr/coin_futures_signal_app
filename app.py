import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
from sklearn.preprocessing import MinMaxScaler
import talib  # TA-Lib teknik analiz kütüphanesi

# Streamlit başlığı
st.title("📈 Coin Futures Sinyal Uygulaması")

# Kullanıcının sembol ve zaman aralığını seçmesini sağlayan girişler
symbol = st.text_input("Kripto Sembolü (örn: BTC-USD)", "BTC-USD")
interval = st.selectbox("Zaman Aralığı", ["1d", "1h", "15m", "5m"])
start_date = st.date_input("Başlangıç Tarihi")
end_date = st.date_input("Bitiş Tarihi")

# Veriyi Çekme
if st.button("Veriyi Getir"):
    try:
        data = yf.download(symbol, start=start_date, end=end_date, interval=interval)
        st.write("📊 Veriler başarıyla çekildi!")
        st.dataframe(data.tail())  # Son 5 satırı göster
    except Exception as e:
        st.error(f"Veri çekilirken hata oluştu: {e}")

# Teknik Analiz Göstergeleri
if not data.empty:
    # RSI Hesaplama
    data["RSI"] = talib.RSI(data["Close"], timeperiod=14)

    # MACD Hesaplama
    data["MACD"], data["MACD_signal"], _ = talib.MACD(data["Close"], fastperiod=12, slowperiod=26, signalperiod=9)

    # Bollinger Bandları
    data["upper_band"], data["middle_band"], data["lower_band"] = talib.BBANDS(data["Close"], timeperiod=20)

    # Hareketli Ortalamalar
    data["SMA_50"] = talib.SMA(data["Close"], timeperiod=50)
    data["EMA_20"] = talib.EMA(data["Close"], timeperiod=20)

    # Grafikleri Çizme
    st.subheader("📉 Fiyat Grafiği ve Teknik Göstergeler")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(data.index, data["Close"], label="Kapanış Fiyatı", color="blue")
    ax.plot(data.index, data["SMA_50"], label="SMA 50", linestyle="dashed", color="orange")
    ax.plot(data.index, data["EMA_20"], label="EMA 20", linestyle="dotted", color="red")
    ax.set_xlabel("Tarih")
    ax.set_ylabel("Fiyat (USD)")
    ax.legend()
    st.pyplot(fig)

    # RSI Grafiği
    fig_rsi, ax_rsi = plt.subplots(figsize=(12, 4))
    ax_rsi.plot(data.index, data["RSI"], label="RSI", color="purple")
    ax_rsi.axhline(70, linestyle="dashed", color="red")
    ax_rsi.axhline(30, linestyle="dashed", color="green")
    ax_rsi.set_xlabel("Tarih")
    ax_rsi.set_ylabel("RSI Değeri")
    ax_rsi.legend()
    st.pyplot(fig_rsi)

    # MACD Grafiği
    fig_macd, ax_macd = plt.subplots(figsize=(12, 4))
    ax_macd.plot(data.index, data["MACD"], label="MACD", color="blue")
    ax_macd.plot(data.index, data["MACD_signal"], label="MACD Sinyal", linestyle="dashed", color="orange")
    ax_macd.set_xlabel("Tarih")
    ax_macd.set_ylabel("MACD Değeri")
    ax_macd.legend()
    st.pyplot(fig_macd)

    # Sinyal Üretme
    st.subheader("📢 Al / Sat Sinyalleri")

    buy_signals = data[(data["RSI"] < 30) & (data["MACD"] > data["MACD_signal"])]
    sell_signals = data[(data["RSI"] > 70) & (data["MACD"] < data["MACD_signal"])]

    st.write(f"✅ **{len(buy_signals)} Alım Sinyali** bulundu!")
    st.dataframe(buy_signals[["Close", "RSI", "MACD", "MACD_signal"]].tail())

    st.write(f"❌ **{len(sell_signals)} Satım Sinyali** bulundu!")
    st.dataframe(sell_signals[["Close", "RSI", "MACD", "MACD_signal"]].tail())

st.write("📢 **Veriler gerçek zamanlı değildir, sadece analiz içindir!**")
