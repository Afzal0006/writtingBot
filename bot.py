from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging, os

# ===== CONFIG =====
BOT_TOKEN = "8411607342:AAHSDSB98MDYeuYMZUk6nHqKtZy2zquhVig"

logging.basicConfig(level=logging.INFO)

# Dictionary to store whispers
whispers = {}  # key = whisper_id, value = {"to": username, "text": message, "user_id": user_id}

# /whisper command
async def whisper_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /whisper @username secret message")
        return

    target_username = context.args[0]
    secret_text = " ".join(context.args[1:])

    # Whisper ID unique banane k liye
    whisper_id = str(update.message.message_id)

    # Store whisper data
    whispers[whisper_id] = {
        "to": target_username.lower(),
        "text": secret_text,
        "user_id": None  # target user id later fill hoga jab click karega
    }

    # Button banate hain
    button = InlineKeyboardButton("📩 View Whisper", callback_data=f"whisper_{whisper_id}")
    reply_markup = InlineKeyboardMarkup([[button]])

    # Group me placeholder bhej do
    await update.message.reply_text(
        f"🔒 Whisper ready for {target_username}",
        reply_markup=reply_markup
    )

# Handle button click
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("whisper_"):
        return

    whisper_id = data.split("_", 1)[1]

    if whisper_id not in whispers:
        await query.message.reply_text("⚠️ Whisper expired or not found.")
        return

    whisper_data = whispers[whisper_id]
    target_username = whisper_data["to"]
    secret_text = whisper_data["text"]

    # Check if this user is target
    if f"@{query.from_user.username}".lower() == target_username.lower():
        try:
            await context.bot.send_message(
                chat_id=query.from_user.id,
                text=f"🔑 Your Whisper:\n\n{secret_text}"
            )
            await query.edit_message_text("✅ Whisper delivered in your DM!")
        except:
            await query.message.reply_text("❌ Cannot send DM, please start the bot first!")
    else:
        await query.answer("❌ This whisper is not for you!", show_alert=True)

# ==== MAIN ====
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("whisper", whisper_command))
    app.add_handler(CallbackQueryHandler(button_click))

    print("🤖 WhisperBot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
