from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import re

BOT_TOKEN = "8411607342:AAHSDSB98MDYeuYMZUk6nHqKtZy2zquhVig"
BOT_USERNAME = "@AfzWhisperBot"

# Store whispers
whispers = {}

# Handle whisper command
async def handle_whisper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Regex: @AfzWhisperBot <message> @username
    pattern = rf"{BOT_USERNAME}\s+(.+)\s+(@\w+)$"
    match = re.match(pattern, text, re.IGNORECASE)
    if not match:
        return  # Ignore if format not matched

    secret_text = match.group(1)
    target_username = match.group(2).lower()

    whisper_id = str(update.message.message_id)
    whispers[whisper_id] = {"text": secret_text, "target_username": target_username}

    # Placeholder in group
    button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔑 Open Whisper", callback_data=f"whisper:{whisper_id}")]]
    )

    await update.message.reply_text(
        f"🤫 Someone sent a whisper to {target_username}",
        reply_markup=button
    )

# Handle button click
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("whisper:"):
        return

    whisper_id = query.data.split(":")[1]
    if whisper_id not in whispers:
        await query.answer("❌ Whisper not found!", show_alert=True)
        return

    whisper = whispers[whisper_id]
    target_username = whisper["target_username"]
    secret_text = whisper["text"]

    user_username = "@" + query.from_user.username if query.from_user.username else None

    if user_username and user_username.lower() == target_username:
        await query.answer(f"💌 Secret: {secret_text}", show_alert=True)
    else:
        await query.answer("🚫 This whisper is not for you!", show_alert=True)

# Main
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_whisper))
    app.add_handler(CallbackQueryHandler(button_click))
    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
