from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# === CONFIG ===
BOT_TOKEN = "7607621887:AAHVpaKwitszMY9vfU2-s0n60QNL56rdbM0"

# === Start Command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🧬 NFT", url="https://t.me/Multicellular"),
            InlineKeyboardButton("🎁 Gifts", url="https://t.me/GiftysView")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Welcome! Choose an option below:", reply_markup=reply_markup)

# === Main ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("✅ Bot started with inline buttons...")
    app.run_polling()

if __name__ == "__main__":
    main()
