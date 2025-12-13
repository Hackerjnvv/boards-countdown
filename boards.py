# File: bot.py (Restart-Proof and Locked Version)

import os
import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import BadRequest, Forbidden

# --- CONFIGURATION ---
TOKEN = os.environ.get('TELEGRAM_TOKEN')
TARGET_CHAT_ID_STR = os.environ.get('TARGET_CHAT_ID') # Hum ID ko Render se lenge

if not TOKEN or not TARGET_CHAT_ID_STR:
    raise ValueError("TELEGRAM_TOKEN aur TARGET_CHAT_ID dono environment variables set hone chahiye!")

TARGET_CHAT_ID = int(TARGET_CHAT_ID_STR)
UPDATE_INTERVAL_SECONDS = 20
MAIN_EXAM_DATE = datetime(2025, 2, 26)
TARGET_DATES = {
    '📘 English': datetime(2025, 2, 26),
    '🧮 Maths': datetime(2025, 3, 11),
    '🔬 Science': datetime(2025, 3, 2),
    # ... baaki subjects ...
}
FOOTER_NAME = "Pranav International PVT. LTD."
FOOTER_LINK = "pranav-sharma.pages.dev"

# File jismein message ID save hoga
MESSAGE_FILE = "message_info.txt"

# --- SCRIPT LOGIC ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
BOT_START_TIME = datetime.now()

# Function to save message info
def save_message_info(chat_id, message_id):
    with open(MESSAGE_FILE, "w") as f:
        f.write(f"{chat_id},{message_id}")

# Function to load message info
def load_message_info():
    try:
        with open(MESSAGE_FILE, "r") as f:
            chat_id, message_id = f.read().strip().split(',')
            return int(chat_id), int(message_id)
    except FileNotFoundError:
        return None, None
    except Exception as e:
        logging.error(f"Message info file padhne mein error: {e}")
        return None, None

def format_timedelta(td: timedelta):
    days, rem = divmod(td.total_seconds(), 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{int(days)} days, {int(hours)} hrs, {int(minutes)} mins, {int(seconds)} sec"

async def update_countdown_message(context: ContextTypes.DEFAULT_TYPE):
    """The main loop to edit the message continuously."""
    job_data = context.job.data
    chat_id = job_data['chat_id']
    message_id = job_data['message_id']
    
    # Message ka text generate karna (ye function wahi hai jo pehle tha)
    now = datetime.now()
    main_countdown = MAIN_EXAM_DATE - now
    main_countdown_str = format_timedelta(main_countdown) if main_countdown.total_seconds() > 0 else "EXAMS HAVE STARTED!"
    subject_lines = [f"• {s}: {(d - now).days} days" if (d-now).days >= 0 else f"• {s}: ✅ Done" for s, d in TARGET_DATES.items()]
    subject_countdown_str = "\n".join(subject_lines)
    uptime = now - BOT_START_TIME
    uptime_str = format_timedelta(uptime)
    
    message_text = f"""📢 **BOARD EXAM COUNTDOWN**
*Live:* `{now.strftime('%I:%M:%S %p — %d %b %Y')}`
---
⏳ **TIME LEFT:** `{main_countdown_str}`

📚 **Days Left For Each Subject:**
{subject_countdown_str}

—
*Managed By 🏢 {FOOTER_NAME}*
🔗 `{FOOTER_LINK}`
⏱ `Uptime: {uptime_str}`"""
    
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=message_text,
            parse_mode='MarkdownV2'
        )
    except BadRequest as e:
        if "message is not modified" in str(e):
            pass # Koi baat nahi, agli baar update hoga
        else:
            logging.error(f"BadRequest: {e}. Job ruk sakta hai.")
            context.job_queue.stop()
    except Forbidden:
        logging.error("Bot blocked or kicked. Job ruk raha hai.")
        context.job_queue.stop()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

async def start_countdown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Naya countdown message bhejta hai aur purane ko rok deta hai."""
    chat_id = update.effective_chat.id
    
    # SIRF TARGET CHAT MEIN HI CHALEGA
    if chat_id != TARGET_CHAT_ID:
        await update.message.reply_text("Sorry, I can only run in the designated channel/group.")
        return

    # Purane chal rahe sabhi jobs ko rok do
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()
    
    initial_message = await context.bot.send_message(
        chat_id=chat_id,
        text="⏳ Initializing new countdown... Please wait."
    )
    message_id = initial_message.message_id
    
    # Nayi message ID ko file mein save karo
    save_message_info(chat_id, message_id)
    
    # Naya job shuru karo
    context.job_queue.run_repeating(
        update_countdown_message,
        interval=UPDATE_INTERVAL_SECONDS,
        first=1,
        name=str(chat_id),
        data={'chat_id': chat_id, 'message_id': message_id}
    )
    
    await initial_message.reply_text("✅ Countdown started! This message will now be updated automatically.")

async def post_init(application: Application):
    """Bot start hone ke baad chalega."""
    chat_id, message_id = load_message_info()
    if chat_id and message_id:
        logging.info(f"Purana message mila: Chat ID={chat_id}, Message ID={message_id}. Countdown resume kar raha hoon.")
        application.job_queue.run_repeating(
            update_countdown_message,
            interval=UPDATE_INTERVAL_SECONDS,
            first=1,
            name=str(chat_id),
            data={'chat_id': chat_id, 'message_id': message_id}
        )

def main() -> None:
    """Bot ko start karein."""
    print("Bot is starting...")
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    
    application.add_handler(CommandHandler("start", start_countdown))
    
    application.run_polling()
    print("Bot has stopped.")

if __name__ == '__main__':
    main()