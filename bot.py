import random
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ===== CONFIG =====
BOT_TOKEN = "8411607342:AAHSDSB98MDYeuYMZUk6nHqKtZy2zquhVig"  # Replace this with your real token

# Logging
logging.basicConfig(level=logging.INFO)

# ===== GLOBAL DATA =====
user_scores = {}  # Keep track of user scores

# ===== COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎲 Welcome to Dice Roller Bot!\nUse /roll to roll a dice.\nUse /score to see your total score."
    )

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    dice_value = random.randint(1, 6)
    dice_faces = {1:"⚀",2:"⚁",3:"⚂",4:"⚃",5:"⚄",6:"⚅"}

    # Update user score
    user_scores[user.id] = user_scores.get(user.id, 0) + dice_value

    await update.message.reply_text(
        f"{user.first_name} rolled a {dice_value} {dice_faces[dice_value]}!\n"
        f"Your total score: {user_scores[user.id]}"
    )

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"{user.first_name}, your total score is: {user_scores.get(user.id, 0)}"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n/start - Welcome message\n/roll - Roll a dice\n/score - See your total score"
    )

# ===== MAIN =====
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("roll", roll))
    app.add_handler(CommandHandler("score", score))
    app.add_handler(CommandHandler("help", help_command))

    # Run the bot
    app.run_polling()

if __name__ == "__main__":
    main()
