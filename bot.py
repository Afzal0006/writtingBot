import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ========= CONFIG =========
BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"
DATA_FILE = "habit_data.json"
IST = ZoneInfo("Asia/Kolkata")
REMINDER_DEFAULT_HOUR_IST = 21  # 9 PM IST

# ========= STORAGE =========
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"chats": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"chats": {}}

def save_data(data):
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)

data = load_data()

def ensure_chat(chat_id: int):
    c = str(chat_id)
    if c not in data["chats"]:
        data["chats"][c] = {
            "reminder_hour_ist": REMINDER_DEFAULT_HOUR_IST,
            "users": {}
        }

def ensure_user(chat_id: int, user_id: int, name: str):
    ensure_chat(chat_id)
    c, u = str(chat_id), str(user_id)
    if u not in data["chats"][c]["users"]:
        data["chats"][c]["users"][u] = {"name": name, "habits": {}}
    else:
        # keep latest name seen
        data["chats"][c]["users"][u]["name"] = name

def today_ist_str():
    return datetime.now(IST).date().isoformat()

def new_habit_dict(name: str):
    return {
        "name": name,
        "streak": 0,
        "best": 0,
        "total_done": 0,
        "total_days": 0,
        "done_today": False,
        "last_date": ""  # YYYY-MM-DD (IST)
    }

def normalize_new_day(h):
    """Ensure total_days increments exactly once per day, and reset done_today for a new day."""
    today = today_ist_str()
    if h["last_date"] != today:
        # If we skipped days, streak should not auto-increment; it's handled by user actions.
        # We count the new day starting.
        h["total_days"] += 1
        h["done_today"] = False
        h["last_date"] = today

def get_habits(chat_id: int, user_id: int):
    ensure_chat(chat_id)
    c, u = str(chat_id), str(user_id)
    users = data["chats"][c]["users"]
    if u not in users:
        return {}
    # normalize days for each habit before showing
    for hk, hv in users[u]["habits"].items():
        normalize_new_day(hv)
    save_data(data)
    return users[u]["habits"]

def habit_key_from_name(name: str):
    # simple stable key
    return name.strip().lower().replace(" ", "_")[:60]

# ========= HELPERS =========
def build_user_habit_keyboard(chat_id: int, user_id: int):
    """Inline keyboard with ✅/❌ per habit for the specific user."""
    habits = get_habits(chat_id, user_id)
    buttons = []
    for hk, h in habits.items():
        # Only show button if not done today
        if not h.get("done_today", False):
            done_cb = f"done|{chat_id}|{user_id}|{hk}|1"
            skip_cb = f"done|{chat_id}|{user_id}|{hk}|0"
            buttons.append([
                InlineKeyboardButton(f"✅ {h['name']}", callback_data=done_cb),
                InlineKeyboardButton(f"❌ {h['name']}", callback_data=skip_cb),
            ])
    if not buttons:
        buttons = [[InlineKeyboardButton("All done for today 🎉", callback_data="noop")]]
    return InlineKeyboardMarkup(buttons)

def completion_rate(h):
    days = max(h["total_days"], 1)
    return round(100.0 * h["total_done"] / days, 1)

# ========= COMMANDS =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == "private":
        await update.message.reply_text(
            "👋 Habit Tracker Bot mein swagat!\n\n"
            "Is bot ko **group** mein add karke use karein:\n"
            "• /addhabit <habit> – habit jodo\n"
            "• /myhabits – apne habits dekho\n"
            "• /stats – personal stats\n"
            "• /leaderboard – group ranking\n"
            "• /settime <0-23> – daily reminder IST hour set karein (default 21)\n\n"
            "Group me roz reminder aayega with ✅/❌ buttons."
        )
    else:
        await update.message.reply_text(
            "✅ Bot ready! Commands:\n"
            "/addhabit <habit>\n/myhabits\n/stats\n/leaderboard\n/settime <0-23>\n"
            "Daily reminder IST me bheja jayega."
        )

async def addhabit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type not in ("group", "supergroup"):
        await update.message.reply_text("❗ Yeh command group me use karein.")
        return
    if not context.args:
        await update.message.reply_text("Usage: `/addhabit Study 2 hours`", parse_mode="Markdown")
        return
    habit_name = " ".join(context.args).strip()
    if len(habit_name) < 2:
        await update.message.reply_text("Habit name thoda lamba rakho 🙂")
        return

    ensure_user(chat.id, user.id, user.mention_html() if user else "User")
    hk = habit_key_from_name(habit_name)
    users = data["chats"][str(chat.id)]["users"]
    habits = users[str(user.id)]["habits"]

    if hk in habits:
        await update.message.reply_text("⚠️ Yeh habit already added hai.")
        return

    habits[hk] = new_habit_dict(habit_name)
    save_data(data)
    await update.message.reply_text(f"✅ Added habit: <b>{habit_name}</b>", parse_mode="HTML")

async def myhabits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type not in ("group", "supergroup"):
        await update.message.reply_text("❗ Yeh command group me use karein.")
        return
    habits = get_habits(chat.id, user.id)
    if not habits:
        await update.message.reply_text("Aapne koi habit add nahi ki. `/addhabit <habit>` try karein.", parse_mode="Markdown")
        return
    lines = ["📝 <b>Your Habits</b>"]
    for h in habits.values():
        tick = "✅" if h.get("done_today") else "⬜"
        lines.append(f"{tick} {h['name']} — streak: {h['streak']} (best {h['best']}) | {completion_rate(h)}%")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML", reply_markup=build_user_habit_keyboard(chat.id, user.id))

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type not in ("group", "supergroup"):
        await update.message.reply_text("❗ Yeh command group me use karein.")
        return
    habits = get_habits(chat.id, user.id)
    if not habits:
        await update.message.reply_text("No habits yet. `/addhabit <habit>`")
        return
    total_done = sum(h["total_done"] for h in habits.values())
    total_days = sum(h["total_days"] for h in habits.values()) or 1
    avg_completion = round(100.0 * total_done / total_days, 1)
    best_streak = max((h["streak"] for h in habits.values()), default=0)
    msg = [
        f"📊 <b>Stats for</b> {user.mention_html()}",
        f"• Habits: {len(habits)}",
        f"• Best streak: {best_streak}",
        f"• Avg completion: {avg_completion}%",
    ]
    await update.message.reply_text("\n".join(msg), parse_mode="HTML")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type not in ("group", "supergroup"):
        await update.message.reply_text("❗ Yeh command group me use karein.")
        return
    ensure_chat(chat.id)
    users = data["chats"][str(chat.id)]["users"]

    board = []
    for uid, ud in users.items():
        habits = ud["habits"]
        if not habits:
            continue
        # Score = sum of streaks + slight weight on completion rate
        total_streak = sum(h["streak"] for h in habits.values())
        done = sum(h["total_done"] for h in habits.values())
        days = sum(h["total_days"] for h in habits.values()) or 1
        comp = 100.0 * done / days
        score = total_streak * 10 + comp  # tweakable
        board.append((score, ud["name"], total_streak, round(comp, 1)))

    if not board:
        await update.message.reply_text("No data yet. Sab log `/addhabit` se start karo!")
        return

    board.sort(reverse=True, key=lambda x: x[0])
    lines = ["🏆 <b>Leaderboard</b>"]
    for i, (_, name, streak_sum, comp) in enumerate(board[:15], start=1):
        lines.append(f"{i}. {name} — streak sum: {streak_sum}, avg: {comp}%")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

async def settime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type not in ("group", "supergroup"):
        await update.message.reply_text("❗ Yeh command group me use karein.")
        return
    if not context.args:
        await update.message.reply_text("Usage: `/settime <0-23>` (IST hour)", parse_mode="Markdown")
        return
    try:
        hour = int(context.args[0])
        if not (0 <= hour <= 23):
            raise ValueError
    except ValueError:
        await update.message.reply_text("Please provide a valid hour between 0 and 23 (IST).")
        return

    ensure_chat(chat.id)
    data["chats"][str(chat.id)]["reminder_hour_ist"] = hour
    save_data(data)
    await update.message.reply_text(f"⏰ Daily reminder time set to {hour:02d}:00 IST.\n(Change reflects from next cycle.)")

# ========= DAILY REMINDER JOB =========
async def daily_reminder_job(context: ContextTypes.DEFAULT_TYPE):
    """Runs every ~15 minutes; sends reminder at configured IST hour if not yet sent."""
    now_ist = datetime.now(IST)
    curr_date = now_ist.date().isoformat()
    minutes_window = range(0, 15)  # 15-min window

    for c_id, cdata in list(data["chats"].items()):
        chat_id = int(c_id)
        hour = cdata.get("reminder_hour_ist", REMINDER_DEFAULT_HOUR_IST)
        # Send within the 15-minute window right after the target hour
        if now_ist.hour == hour and now_ist.minute in minutes_window:
            # Prepare a single message with keyboards per user as a thread?
            # We'll send one group message tagging everyone and then one inline keyboard per user.
            users = cdata.get("users", {})
            if not users:
                continue

            # Tag users who have at least one habit
            mentions = []
            for uid, ud in users.items():
                if ud["habits"]:
                    mentions.append(ud["name"])
                    # Normalize their habits to the new day before sending buttons
                    for h in ud["habits"].values():
                        normalize_new_day(h)

            save_data(data)

            if mentions:
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text="⏰ <b>Daily Habit Check-in</b>\n" +
                             " ".join(mentions) +
                             "\nTap your buttons below to mark today's progress.",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass

                # Send a compact keyboard per user (so only that user can interact)
                for uid, ud in users.items():
                    if not ud["habits"]:
                        continue
                    try:
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=f"🧩 {ud['name']}: mark today’s status",
                            reply_markup=build_user_habit_keyboard(chat_id, int(uid))
                        )
                    except Exception:
                        continue

# ========= CALLBACKS =========
async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data_parts = (query.data or "").split("|")
    if data_parts[0] == "noop":
        return

    if len(data_parts) != 5 or data_parts[0] != "done":
        return

    _, chat_id_str, user_id_str, habit_key, done_flag = data_parts
    chat_id = int(chat_id_str)
    owner_id = int(user_id_str)
    actor_id = update.effective_user.id

    # Restrict button to owner
    if actor_id != owner_id:
        await query.edit_message_text("❗ Yeh buttons sirf mentioned user ke liye hain.")
        return

    ensure_chat(chat_id)
    users = data["chats"][str(chat_id)]["users"]
    if str(owner_id) not in users:
        await query.edit_message_text("User not found.")
        return
    habits = users[str(owner_id)]["habits"]
    if habit_key not in habits:
        await query.edit_message_text("Habit not found.")
        return

    h = habits[habit_key]
    normalize_new_day(h)

    if done_flag == "1":
        if not h["done_today"]:
            h["done_today"] = True
            h["streak"] += 1
            h["total_done"] += 1
            if h["streak"] > h["best"]:
                h["best"] = h["streak"]
        msg = f"✅ Marked done: <b>{h['name']}</b>\nStreak: {h['streak']} (best {h['best']})"
    else:
        # Explicit "No" breaks streak for today
        if h["streak"] > 0:
            h["streak"] = 0
        h["done_today"] = False
        msg = f"❌ Marked not done: <b>{h['name']}</b>\nStreak broken."

    save_data(data)

    # Refresh keyboard (may hide this habit if marked done)
    try:
        await query.edit_message_text(msg, parse_mode="HTML", reply_markup=build_user_habit_keyboard(chat_id, owner_id))
    except Exception:
        # If editing fails (e.g., message too old), just send a new status message
        await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="HTML")

# ========= FALLBACK (NAME REFRESH) =========
async def any_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # keep recent display names
    chat = update.effective_chat
    user = update.effective_user
    if chat and user and chat.type in ("group", "supergroup"):
        ensure_user(chat.id, user.id, user.mention_html())
        save_data(data)

# ========= MAIN =========
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addhabit", addhabit))
    app.add_handler(CommandHandler("myhabits", myhabits))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("settime", settime))

    # Buttons
    app.add_handler(CallbackQueryHandler(on_button))

    # Fallback to refresh names
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), any_message))

    # Scheduler: run every 15 minutes, which triggers at the right hour window
    app.job_queue.run_repeating(daily_reminder_job, interval=900, first=5)

    print("Bot running…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
