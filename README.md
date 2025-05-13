📊 Crypto Bot (CoinLore API bilan)
Telegram orqali ishlaydigan kripto bot. CoinLore API’dan foydalanib, global statistika, eng yaxshi kriptolar, coin qidiruv, birjalar va sevimli coinlar haqida ma’lumot beradi.


🔗 API Manbasi:
CoinLore API hujjati

⚙️ O‘rnatish
bash
Copy
Edit
git clone https://github.com/yourusername/crypto-telegram-bot.git
cd crypto-telegram-bot
pip install -r requirements.txt
.env fayli yarating va quyidagilarni qo‘shing:

env
Copy
Edit
BOT_TOKEN=your_telegram_bot_token
🚀 Ishga tushirish
bash
Copy
Edit
python bot.py
🧩 Asosiy Funktsiyalar
Tugma	Tavsifi
🌐 Global Stats	Butun kripto bozorining statistikasi (marketcap, volume, BTC dominansi)
📈 Top Cryptos	Eng yuqori baholangan 10 ta kriptovalyuta
🔍 Search Coin	Coin nomi orqali qidiruv
📊 Exchanges	Yirik birjalar haqida ma’lumot
⭐ Favorites	Sevimli coinlarni saqlash
ℹ️ Help	Botdan foydalanish bo‘yicha yordam

🧠 Texnologiyalar
Python

python-telegram-bot

requests

CoinLore API

📦 CoinLore API-lari ishlatilgan
https://api.coinlore.net/api/global/
→ Umumiy kripto statistikasi

https://api.coinlore.net/api/tickers/?start=0&limit=10
→ Eng yaxshi 10 kriptovalyuta

https://api.coinlore.net/api/tickers/?start=0&limit=100
→ Qidiruv uchun barcha coinlar ro‘yxati

https://api.coinlore.net/api/exchanges/
→ Kripto birjalar ro‘yxati

📌 Foydalanish namunasi:
Top Cryptos tugmasini bosing → Eng kuchli 10 ta coin haqida yangilanayotgan ma'lumotlar chiqadi.

Search Coin tugmasini bosing → Coin nomini kiriting va batafsil ma’lumot oling.

Favorites orqali o'zingiz yoqtirgan coinlarni saqlab qo'yishingiz mumkin.

🤝 Hissa qo‘shing
Pull requestlar ochiq! Yangi imkoniyatlar qo‘shing, xatoliklarni tuzating yoki tajriba orttiring!
