from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, PrefixHandler
import logging

# ==== CONFIG ====
BOT_TOKEN = "7643831340:AAGieuPJND4MekAutSf3xzta1qdoKo5mbZU"
CHANNEL_ID = "@sexxswcccx"  # Channel username

# Logging enable
logging.basicConfig(level=logging.INFO)

# ==== "+" command ====
async def plus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check ki user ne reply kiya hai ya nahi
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Please reply to the message you want to send.")
        return
    
    # Message forward to channel
    try:
        await update.message.reply_to_message.forward(chat_id=CHANNEL_ID)
        await update.message.reply_text("✅ Message posted to channel.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# ==== Main ====
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # "+" ko command ki tarah treat karne ke liye PrefixHandler
    app.add_handler(PrefixHandler("+", "", plus_command))

    app.run_polling()

if __name__ == "__main__":
    main()
