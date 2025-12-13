# File: bot.py (FINAL EMOJI STYLE + FULL COUNTDOWN)

import threading
from flask import Flask
import os
import telegram
import asyncio
from datetime import datetime, timedelta

# --- WEB SERVER (FLASK) PART ---
app = Flask(__name__)
@app.route('/')
def hello():
    return "Bot is alive and countdown is running!"
def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- TELEGRAM BOT PART ---

# ==============================================================================
#                                 SETTINGS (2026)
# ==============================================================================
BOT_TOKEN = '8265096272:AAE4HTHAovCNaofsqkVqD_5kX8fGOYq0IP4' 
CHAT_ID = -1003356902972
UPDATE_INTERVAL_SECONDS = 5

# Dates for 2026
MAIN_EXAM_DATE = datetime(2026, 2, 17)
TARGET_DATES = {
    '🧮 Maths': datetime(2026, 2, 17),
    '📘 English': datetime(2026, 2, 21),
    '🔬 Science': datetime(2026, 2, 25),
    '🤖 AI/IT': datetime(2026, 2, 27),
    '📜 Sanskrit': datetime(2026, 2, 28),
    '🗣️ Hindi': datetime(2026, 3, 2),
    '🏛️ SST': datetime(2026, 3, 7),
}

# Footer
FOOTER_NAME = "Pranav International PVT\. LTD\."
FOOTER_LINK = "pranav\-sharma\.pages\.dev"
MESSAGE_FILE = "message_info.txt"
BOT_START_TIME = datetime.now()

# ==============================================================================
#                               HELPER FUNCTIONS
# ==============================================================================
def save_message_id(message_id):
    with open(MESSAGE_FILE, "w") as f: f.write(str(message_id))
def load_message_id():
    try:
        with open(MESSAGE_FILE, "r") as f: return int(f.read().strip())
    except (FileNotFoundError, ValueError): return None

# <<<--- COUNTDOWN FORMAT (d, h, m, s) --->>>
def format_timedelta(td: timedelta):
    days, rem = divmod(td.total_seconds(), 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{int(days)}d, {int(hours)}h, {int(minutes)}m, {int(seconds)}s"

# ==============================================================================
#                               CORE COUNTDOWN LOGIC
# ==============================================================================
async def main_countdown_logic():
    print("COUNTDOWN BOT STARTED (Emoji Style Version)")
    bot = telegram.Bot(token=BOT_TOKEN)
    message_id = load_message_id()

    if message_id is None:
        try:
            print("Sending a new message...")
            sent_message = await bot.send_message(chat_id=CHAT_ID, text="⏳ Initializing 2026 countdown...")
            message_id = sent_message.message_id
            save_message_id(message_id)
            print(f"New message sent. ID: {message_id}")
        except Exception as e:
            print(f"[!!!] FATAL: Could not send initial message: {e}")
            return
    else:
        print(f"Resuming for message ID: {message_id}")

    while True:
        try:
            now = datetime.now()

            # <<<--- HAR SUBJECT KE LIYE FULL COUNTDOWN BANANE KA LOGIC --->>>
            subject_lines = []
            for subject, date in TARGET_DATES.items():
                time_left = date - now
                if time_left.total_seconds() < 0:
                    countdown_str = "✅ Exam Over\!"
                else:
                    countdown_str = format_timedelta(time_left)
                
                subject_lines.append(f"• {subject}: `{countdown_str}`")

            subject_countdown_str = "\n".join(subject_lines)

            # <<<--- NAYA EMOJI WALA MESSAGE FORMAT --->>>
            message_text = f"""📢 **BOARD EXAM COUNTDOWN \(2026\)**

*Live Time:* `{now.strftime('%I:%M:%S %p — %d %b %Y')}`
\-\-\-
🗓️ **Subject\-wise Countdown:**

{subject_countdown_str}
\-\-\-
*Managed By 🏢 {FOOTER_NAME}*
🔗 `{FOOTER_LINK}`
"""

            await bot.edit_message_text(
                chat_id=CHAT_ID,
                message_id=message_id,
                text=message_text,
                parse_mode='MarkdownV2'
            )
            
        except telegram.error.BadRequest as e:
            if "message is not modified" in str(e): pass
            else: print(f"[!] FAILED to edit message: {e}")
        except Exception as e:
            print(f"[!] An unexpected error occurred: {e}")
        
        await asyncio.sleep(UPDATE_INTERVAL_SECONDS)

# ==============================================================================
#                               MAIN EXECUTION
# ==============================================================================
if __name__ == "__main__":
    print("Starting main application...")
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    try:
        asyncio.run(main_countdown_logic())
    except KeyboardInterrupt:
        print("\nApplication stopped.")
