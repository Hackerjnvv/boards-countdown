# File: bot.py

import os
import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import BadRequest, Forbidden

# --- CONFIGURATION (YAHAN APNE HISAB SE CHANGE KAREIN) ---

# 1. Bot Token (Render par daalna hai, yahan nahi)
TOKEN = os.environ.get('TELEGRAM_TOKEN')

# 2. Message kitni der mein update hoga (seconds mein)
#    Telegram ki limit se bachne ke liye 15-30 second se kam na rakhein.
UPDATE_INTERVAL_SECONDS = 20

# 3. Apne sabhi target dates yahan daalein (SAAL-MAHINA-DIN)
MAIN_EXAM_DATE = datetime(2025, 2, 26)  # Maan lijiye ye pehla exam hai

TARGET_DATES = {
    '📘 English': datetime(2025, 2, 26),
    '🧮 Maths': datetime(2025, 3, 11),
    '🔬 Science': datetime(2025, 3, 2),
    '📕 Hindi': datetime(2025, 2, 21),
    '🌍 SST': datetime(2025, 3, 7),
    '💻 IT': datetime(2025, 3, 13),
    # Aap aur bhi subjects add kar sakte hain
}

# 4. Footer ke liye details
FOOTER_NAME = "Pranav International PVT. LTD."
FOOTER_LINK = "pranav-sharma.pages.dev"

# --- SCRIPT LOGIC (ISE CHANGE KARNE KI ZAROORAT NAHI) ---

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Bot kab start hua, ye record karein (Uptime ke liye)
BOT_START_TIME = datetime.now()

def format_timedelta(td: timedelta):
    """Timespan ko 'days, hrs, mins, sec' format mein badalta hai."""
    days = td.days
    total_seconds = td.seconds
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{days} days, {hours} hrs, {minutes} mins, {seconds} sec"

# Ye function message ko lagatar update karega
async def update_countdown_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int):
    """The main loop to edit the message continuously."""
    while True:
        try:
            now = datetime.now()
            
            # 1. Main countdown calculate karein
            main_countdown = MAIN_EXAM_DATE - now
            if main_countdown.total_seconds() < 0:
                main_countdown_str = "EXAMS HAVE STARTED!"
            else:
                main_countdown_str = format_timedelta(main_countdown)

            # 2. Subject-wise countdowns banayein
            subject_lines = []
            for subject, date in TARGET_DATES.items():
                days_left = (date - now).days
                if days_left < 0:
                    subject_lines.append(f"• {subject}: ✅ Done")
                else:
                    subject_lines.append(f"• {subject}: {days_left} days")
            subject_countdown_str = "\n".join(subject_lines)

            # 3. Uptime calculate karein
            uptime = now - BOT_START_TIME
            uptime_str = format_timedelta(uptime)

            # 4. Poora message taiyar karein
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

            # 5. Message ko edit karein
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=message_text,
                parse_mode='MarkdownV2'
            )
            
            # Thodi der wait karein
            await asyncio.sleep(UPDATE_INTERVAL_SECONDS)

        except Forbidden:
            # Agar user ne bot ko block kar diya to loop tod dein
            logging.warning(f"Bot blocked in chat {chat_id}. Stopping job.")
            break
        except BadRequest as e:
            # Agar message delete ho gaya ya koi aur problem hui
            if "message to edit not found" in str(e):
                logging.warning(f"Message {message_id} in chat {chat_id} not found. Stopping job.")
                break
            else:
                logging.error(f"BadRequest in chat {chat_id}: {e}")
                await asyncio.sleep(60) # Lambi der wait karein
        except Exception as e:
            # Baaki sabhi errors ke liye
            logging.error(f"An unexpected error occurred in chat {chat_id}: {e}")
            await asyncio.sleep(60)


# /start command ke liye function
async def start_countdown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    
    # Check karein ki is chat mein pehle se countdown to nahi chal raha
    if 'job_running' in context.chat_data and context.chat_data['job_running']:
        await update.message.reply_text("Countdown is already running in this chat!")
        return
        
    initial_message = await update.message.reply_text("⏳ Initializing countdown... Please wait.")
    message_id = initial_message.message_id
    
    context.chat_data['job_running'] = True
    
    # Background mein message update karne wala task shuru karein
    asyncio.create_task(update_countdown_message(context, chat_id, message_id))


def main() -> None:
    """Bot ko start karein."""
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN environment variable not set!")

    print("Bot is starting...")
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_countdown))

    application.run_polling()
    print("Bot has stopped.")

if __name__ == '__main__':
    main()
