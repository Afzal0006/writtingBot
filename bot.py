from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import logging
import re

# ===== CONFIG =====
BOT_TOKEN = "7607621887:AAHVpaKwitszMY9vfU2-s0n60QNL56rdbM0"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store whispers in memory {whisper_id: {"receiver_username": str, "receiver_id": int, "message": str}}
whispers = {}


# --- Handle Whisper Command in Group ---
async def whisper_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Format: @afz message @username
    pattern = r"@afz (.+) @([\w]+)"
    match = re.search(pattern, text)

    if not match:
        return  # Ignore messages not matching the pattern

    secret_message = match.group(1)
    receiver_username = match.group(2)

    # Try to resolve user_id (only works if user has interacted with bot)
    receiver_id = None
    try:
        chat = await context.bot.get_chat(update.effective_chat.id)
        members = await chat.get_administrators()
        for member in members:
            if member.user.username and member.user.username.lower() == receiver_username.lower():
                receiver_id = member.user.id
                break
    except Exception as e:
        logger.warning(f"Error getting chat members: {e}")

    whisper_id = str(update.message.message_id)
    whispers[whisper_id] = {
        "receiver_username": receiver_username,
        "receiver_id": receiver_id,
        "message": secret_message
    }

    # Inline button for opening whisper
    keyboard = [[InlineKeyboardButton("🔑 Open Whisper", callback_data=f"whisper:{whisper_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🤫 Whisper for @{receiver_username} (click below to open)",
        reply_markup=reply_markup
    )


# --- Handle Whisper Reveal ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("whisper:"):
        return

    whisper_id = data.split(":")[1]
    whisper = whispers.get(whisper_id)

    if not whisper:
        await query.message.reply_text("❌ Whisper not found or expired.")
        return

    if whisper["receiver_id"] and query.from_user.id == whisper["receiver_id"]:
        # If bot knows the receiver_id
        await query.answer(f"Secret Message: {whisper['message']}", show_alert=True)
    elif query.from_user.username and query.from_user.username.lower() == whisper["receiver_username"].lower():
        # If only username is available
        await query.answer(f"Secret Message: {whisper['message']}", show_alert=True)
    else:
        await query.answer("❌ This whisper is not for you!", show_alert=True)


# ====== MAIN ======
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, whisper_handler))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()


if __name__ == "__main__":
    main()
