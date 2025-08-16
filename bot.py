from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ==== CONFIG ====
BOT_TOKEN = "7607621887:AAHVpaKwitszMY9vfU2-s0n60QNL56rdbM0"
OWNER_ID = 7607621887  # Apna Telegram user ID (@userinfobot se le lo)

# Groups ka list manually daal lo (bot already in groups hai)
groups = [
    -1001234567890,  # group 1 ID
    -1009876543210,  # group 2 ID
]

# ==== BROADCAST ====
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Ye command sirf owner ke liye hai.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    text = " ".join(context.args)
    success = 0
    for gid in groups:
        try:
            await context.bot.send_message(gid, text)
            success += 1
        except Exception as e:
            print(f"Error in {gid}: {e}")

    await update.message.reply_text(f"✅ Broadcast sent to {success} groups.")

# ==== START ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Mai broadcast bot hu.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.run_polling()

if __name__ == "__main__":
    main()
