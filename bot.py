import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "7643831340:AAGieuPJND4MekAutSf3xzta1qdoKo5mbZU"
CHAT_ID = -1002760813128
URL = "https://marketapp.ws/gifts/?tab=history"

CHECK_INTERVAL = 10  # 30 seconds

bot = Bot(token=BOT_TOKEN)
last_item = None


def fetch_gifts():
    r = requests.get(URL, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.find_all(["div", "tr"])

    data = []
    for row in rows:
        text = row.get_text(" ", strip=True)
        if text and any(x in text.lower() for x in ["gift", "sell", "₹", "$"]):
            data.append(text)

    return data[:20]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gifts = fetch_gifts()
    if not gifts:
        return await update.message.reply_text("No data found.")
    msg = "Latest 10 Gifts:\n\n" + "\n".join(f"• {g}" for g in gifts[:10])
    await update.message.reply_text(msg)


async def monitor():
    global last_item
    while True:
        try:
            gifts = fetch_gifts()
            if gifts:
                newest = gifts[0]
                if last_item is None:
                    last_item = newest
                elif newest != last_item:
                    last_item = newest
                    await bot.send_message(
                        chat_id=CHAT_ID,
                        text=f"New Gift Sold:\n{newest}"
                    )
        except Exception:
            pass
        await asyncio.sleep(CHECK_INTERVAL)


async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    asyncio.create_task(monitor())
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
