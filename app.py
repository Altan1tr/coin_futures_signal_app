import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import matplotlib.pyplot as plt

# Streamlit başlık
st.title("📈 Coin Futures Sinyal Uygulaması")
st.write("TradingView göstergeleri ile anlık al/sat sinyalleri")

# Kullanıcıdan kripto para çifti seçmesini isteme
symbol = st.text_input("Coin Sembolü (örn: BTC-USD)", "BTC-USD")

# Tarih aralığı seçimi
start_date = st.date_input("Başlangıç Tarihi", pd.to_datetime("2023-01-01"))
end_date = st.date_input("Bitiş Tarihi", pd.to_datetime("today"))

# Veriyi indirme
def get_data(symbol, start, end):
    df = yf.download(symbol, start=start, end=end)
    return df

# Veriyi al
df = get_data(symbol, start_date, end_date)

# Eğer veri varsa göstergeleri hesapla
if not df.empty:
    # RSI Hesaplama
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()

    # MACD Hesaplama
    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_Signal"] = macd.macd_signal()

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(df["Close"], window=20)
    df["BB_High"] = bb.bollinger_hband()
    df["BB_Low"] = bb.bollinger_lband()

    # AL/SAT sinyali oluşturma
    df["BUY_SIGNAL"] = (df["RSI"] < 30) & (df["MACD"] > df["MACD_Signal"])
    df["SELL_SIGNAL"] = (df["RSI"] > 70) & (df["MACD"] < df["MACD_Signal"])

    # Son kapanış fiyatını göster
    st.subheader("Son Kapanış Fiyatı: {:.2f} USD".format(df["Close"].iloc[-1]))

    # AL/SAT sinyalini göster
    if df["BUY_SIGNAL"].iloc[-1]:
        st.success("📈 **ALIM SİNYALİ!** RSI düşük ve MACD yükselişte.")
    elif df["SELL_SIGNAL"].iloc[-1]:
        st.error("📉 **SATIŞ SİNYALİ!** RSI yüksek ve MACD düşüşte.")
    else:
        st.warning("⚠ **NÖTR DURUM** - Henüz net bir sinyal yok.")

    # Grafikleri çiz
    st.subheader("Fiyat ve Göstergeler")

    fig, ax = plt.subplots(3, 1, figsize=(12, 8))

    # Fiyat grafiği
    ax[0].plot(df.index, df["Close"], label="Fiyat", color="blue")
    ax[0].plot(df.index, df["BB_High"], linestyle="dotted", color="red", label="Bollinger Üst Band")
    ax[0].plot(df.index, df["BB_Low"], linestyle="dotted", color="green", label="Bollinger Alt Band")
    ax[0].legend()
    ax[0].set_title("Fiyat ve Bollinger Bantları")

    # RSI Grafiği
    ax[1].plot(df.index, df["RSI"], color="purple", label="RSI")
    ax[1].axhline(70, linestyle="dashed", color="red")
    ax[1].axhline(30, linestyle="dashed", color="green")
    ax[1].legend()
    ax[1].set_title("RSI Göstergesi")

    # MACD Grafiği
    ax[2].plot(df.index, df["MACD"], label="MACD", color="orange")
    ax[2].plot(df.index, df["MACD_Signal"], label="MACD Signal", color="blue", linestyle="dotted")
    ax[2].legend()
    ax[2].set_title("MACD Göstergesi")

    # Grafikleri Streamlit'e ekle
    st.pyplot(fig)

    # Veriyi tablo olarak göster
    st.subheader("Son 10 Günlük Veriler")
    st.dataframe(df[["Close", "RSI", "MACD", "MACD_Signal", "BB_High", "BB_Low", "BUY_SIGNAL", "SELL_SIGNAL"]].tail(10))

else:
    st.error("❌ Hata: Veri yüklenemedi. Lütfen sembolü kontrol edin.")
