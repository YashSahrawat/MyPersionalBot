from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ChatPermissions
import time
import re
import schedule
import threading

# Replace with your bot token
BOT_TOKEN = "8006983223:AAGzxeiPqZx_jswGQ780EWGbyQqgij8-blA"

# Global variable for group ID
GROUP_CHAT_ID = -1002721754499

# Abusive words
BANNED_WORDS = [
    "idiot", "stupid", "dumb", "fool", "moron", "jerk", "asshole", "bastard",
    "bitch", "dick", "fuck", "fucker", "shit", "slut", "crap", "retard",
    "son of a bitch", "motherfucker", "bloody", "bollocks", "piss off",
    "wanker", "arsehole", "cunt", "suck", "douchebag", "jackass",
    "chutiya", "bhenchod", "madarchod", "gandu", "lund", "randi", "chod",
    "bhosdike", "gaand", "bkl", "mc", "bc", "chut", "launda", "laundiya",
    "kamina", "kaminey", "harami", "behen ke lode", "madar ke lode",
    "suar ke bacche", "kutta", "kutti", "loda", "lode", "gaand mara",
    "gaand fat gayi", "bhadwe", "rakhail", "jhatu", "chut ke baal"
]

def contains_banned_word(text):
    for word in BANNED_WORDS:
        if re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE):
            return True
    return False

def start(update, context):
    update.message.reply_text("🤖 I'm your group guard bot. Type /setgroupid to enable greetings!")

def set_group_id(update, context):
    global GROUP_CHAT_ID
    GROUP_CHAT_ID = update.effective_chat.id
    update.message.reply_text(f"✅ Group ID set to: {GROUP_CHAT_ID}")

def kick(update, context):
    user = update.message.from_user
    chat_id = update.message.chat_id
    admins = context.bot.get_chat_administrators(chat_id)
    admin_ids = [admin.user.id for admin in admins]

    if user.id not in admin_ids:
        update.message.reply_text("❌ Only admins can use this command.")
        return

    if context.args:
        username = context.args[0].replace("@", "")
        try:
            members = context.bot.get_chat_administrators(chat_id)
            for member in members:
                if member.user.username and member.user.username.lower() == username.lower():
                    context.bot.kick_chat_member(chat_id, member.user.id)
                    update.message.reply_text(f"👢 @{username} has been kicked.")
                    return
            update.message.reply_text("❌ User not found.")
        except Exception as e:
            update.message.reply_text(f"⚠ Kick failed: {e}")
    else:
        update.message.reply_text("Usage: /kick @username")

def handle_message(update, context):
    global GROUP_CHAT_ID
    message = update.message
    user = message.from_user
    text = message.text.lower().strip()
    chat_id = message.chat_id
    GROUP_CHAT_ID = chat_id  # auto-set if not manually set

    if text in ['hi', 'hello']:
        message.reply_text(f"👋 Hello, {user.first_name}!")

    elif contains_banned_word(text):
        try:
            context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            context.bot.send_message(chat_id, f"⚠ {user.first_name}, avoid using abusive language.")
            context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user.id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=int(time.time()) + 120
            )
            context.bot.send_message(chat_id, f"🚫 {user.first_name} has been muted for 2 minutes.")
        except Exception as e:
            print(f"Error muting user: {e}")

def send_morning_greeting():
    if GROUP_CHAT_ID:
        try:
            bot.send_message(chat_id=GROUP_CHAT_ID, text="🌞 Good morning everyone!")
        except Exception as e:
            print(f"Greeting error: {e}")

def send_night_greeting():
    if GROUP_CHAT_ID:
        try:
            bot.send_message(chat_id=GROUP_CHAT_ID, text="🌙 Good night everyone!")
        except Exception as e:
            print(f"Greeting error: {e}")

def run_scheduler():
    schedule.every().day.at("07:00").do(send_morning_greeting)  # Morning
    schedule.every().day.at("23:09").do(send_night_greeting)   # Night (10 PM)

    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    global bot
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    bot = updater.bot

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("setgroupid", set_group_id))
    dp.add_handler(CommandHandler("kick", kick))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    thread = threading.Thread(target=run_scheduler)
    thread.daemon = True
    thread.start()

    print("🤖 Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
