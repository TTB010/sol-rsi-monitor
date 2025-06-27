import yfinance as yf
import pandas as pd
import requests
import schedule
import time
from datetime import datetime

# === ДАННЫЕ ДЛЯ TELEGRAM ===
TELEGRAM_BOT_TOKEN = "7862408713:AAGN5V7Tfur0qssTNrknljtVfnCkYxYZ4Es"
TELEGRAM_CHAT_ID = "4837046740"

# Функция отправки уведомления
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"Ошибка Telegram: {response.text}")
    except Exception as e:
        print(f"Ошибка при отправке: {e}")

# Функция расчёта RSI
def compute_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Проверка RSI по SOL
def check_sol_rsi():
    try:
        df = yf.download("SOL-USD", period="30d", interval="1h", auto_adjust=True, progress=False)
        df['RSI'] = compute_rsi(df)
        latest_row = df.iloc[-1]
        latest_price = float(latest_row['Close'])
        latest_rsi = float(latest_row['RSI'])
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        print(f"[{now}] Цена: {latest_price:.2f} | RSI: {latest_rsi:.2f}")

        if latest_rsi < 25:
            send_telegram_message(f"📉 SOL RSI = {latest_rsi:.2f} (<25)\nСигнал на покупку")
        elif latest_rsi > 70:
            send_telegram_message(f"📈 SOL RSI = {latest_rsi:.2f} (>70)\nСигнал на продажу")

    except Exception as e:
        print(f"Ошибка: {e}")

# Планировщик
schedule.every(1).hours.do(check_sol_rsi)

print("▶️ Мониторинг SOL RSI запущен...")

check_sol_rsi()  # Первая проверка сразу

while True:
    schedule.run_pending()
    time.sleep(5)
