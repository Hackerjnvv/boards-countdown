# File: bot.py (FINAL 2026 VERSION with TABLE)

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

# <<<--- UPDATE INTERVAL 5 SECOND KAR DIYA HAI --->>>
UPDATE_INTERVAL_SECONDS = 5

# <<<--- SAARI DATES 2026 KE LIYE UPDATE KAR DI HAIN --->>>
# Main exam date (pehla exam)
MAIN_EXAM_DATE = datetime(2026, 2, 17)

# Subject-wise dates
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
# ... (Ye saare functions bilkul same rahenge, koi change nahi) ...
def save_message_id(message_id):
    with open(MESSAGE_FILE, "w") as f: f.write(str(message_id))
def load_message_id():
    try:
        with open(MESSAGE_FILE, "r") as f: return int(f.read().strip())
    except (FileNotFoundError, ValueError): return None
def format_timedelta(td: timedelta):
    days, rem = divmod(td.total_seconds(), 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{int(days)}d, {int(hours)}h, {int(minutes)}m, {int(seconds)}s"

# ==============================================================================
#                               CORE COUNTDOWN LOGIC
# ==============================================================================
async def main_countdown_logic():
    print("COUNTDOWN BOT STARTED (2026 Table Version)")
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
            main_countdown = MAIN_EXAM_DATE - now
            main_countdown_str = format_timedelta(main_countdown) if main_countdown.total_seconds() > 0 else "EXAMS STARTED\!"

            # <<<--- YAHAN TABLE WALA FORMAT BANAYA GAYA HAI --->>>
            table_header = """```
| Date (2026)       | Subject                         | Days Left |
|-------------------|---------------------------------|-----------|
"""
            table_rows = []
            for subject, date in TARGET_DATES.items():
                date_str = date.strftime('%b %d, %A')
                days_left = (date - now).days
                days_left_str = f"{days_left} days" if days_left >= 0 else "✅ Done"
                # Table ko align karne ke liye padding add karna
                table_rows.append(f"| {date_str:<17} | {subject:<31} | {days_left_str:<9} |")
            
            table_body = "\n".join(table_rows)
            table_footer = "```"
            
            full_table = table_header + table_body + table_footer

            # Pura message text
            message_text = f"""📢 **BOARD EXAM COUNTDOWN \(2026\)**

*Live:* `{now.strftime('%I:%M:%S %p — %d %b %Y')}`
⏳ *Time Left \(First Exam\):* `{main_countdown_str}`

{full_table}

\—
*Managed By 🏢 {FOOTER_NAME}*
🔗 `{FOOTER_LINK}`
"""

            await bot.edit_message_text(
                chat_id=CHAT_ID,
                message_id=message_id,
                text=message_text,
                parse_mode='MarkdownV2'
            )
            # print(f"Message {message_id} updated at {now.strftime('%H:%M:%S')}") # Debugging ke liye on kar sakte hain

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
