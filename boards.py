import threading
import os
import telegram
import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from flask import Flask

# --- CONFIGURATION (HARDCODED FOR TESTING) ---
# ⚠️ Yahaan apna token aur chat ID daalein. Is code ko public mat karna.
# ⚠️ Put your token and chat ID here. Do not make this code public.
BOT_TOKEN = '8265096272:AAE4HTHAovCNaofsqkVqD_5kX8fGOYq0IP4'
CHAT_ID = -1003356902972 # Agar channel hai to minus sign (-) ke saath

UPDATE_INTERVAL_SECONDS = 2
MESSAGE_FILE = "message_info.txt"

# --- WEB SERVER (FLASK) PART ---
app = Flask(__name__)
@app.route('/')
def hello():
    return "Bot is alive and all features are running!"

def run_flask():
    # PORT environment variable abhi bhi zaroori hai agar aap hosting platform par deploy karte hain
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- TIMEZONE SETTING ---
IST = ZoneInfo("Asia/Kolkata")

# --- TARGET DATES & CONTENT ---
TARGET_DATES = {
    # ===============================
    # 📚 CLASS 10 BOARDS (2026)
    # ===============================
    '🧮 Maths': datetime(2026, 2, 17, 6, 0, tzinfo=IST),
    '📘 English': datetime(2026, 2, 21, 6, 0, tzinfo=IST),
    '🔬 Science': datetime(2026, 2, 25, 6, 0, tzinfo=IST),
    '🤖 AI/IT': datetime(2026, 2, 27, 6, 0, tzinfo=IST),
    '📜 Sanskrit': datetime(2026, 2, 28, 6, 0, tzinfo=IST),
    '🗣️ Hindi': datetime(2026, 3, 2, 6, 0, tzinfo=IST),
    '🏛️ SST': datetime(2026, 3, 7, 6, 0, tzinfo=IST),

    # ===============================
    # 🎓 CLASS 11 (PCM + PCB) 2026–27
    # ===============================
    '📐 Class 11 Physics Midterm': datetime(2026, 9, 15, 6, 0, tzinfo=IST),
    '⚗️ Class 11 Chemistry Midterm': datetime(2026, 9, 20, 6, 0, tzinfo=IST),
    '📊 Class 11 Maths Midterm': datetime(2026, 9, 25, 6, 0, tzinfo=IST),
    '🧬 Class 11 Biology Midterm': datetime(2026, 9, 30, 6, 0, tzinfo=IST),
    '📘 Class 11 Final Exams': datetime(2027, 2, 20, 6, 0, tzinfo=IST),

    # ===============================
    # 🧠 CLASS 11 PREP MILESTONES
    # ===============================
    '🧠 Syllabus 30% Complete (PCM+PCB)': datetime(2027, 4, 1, 0, 0, tzinfo=IST),
    '📊 First JEE Mock Test': datetime(2027, 5, 1, 6, 0, tzinfo=IST),
    '📊 First NEET Mock Test': datetime(2027, 5, 5, 6, 0, tzinfo=IST),
    '🧬 Biology NCERT 1st Revision': datetime(2027, 6, 15, 0, 0, tzinfo=IST),

    # ===============================
    # 🎓 CLASS 12 (PCM + PCB) 2027–28
    # ===============================
    '📐 Class 12 Pre-Boards': datetime(2027, 12, 10, 6, 0, tzinfo=IST),
    '📘 Class 12 Boards Start': datetime(2028, 3, 1, 6, 0, tzinfo=IST),

    # ===============================
    # 🔥 FINAL SYLLABUS COMPLETION
    # ===============================
    '🔥 Full Syllabus Complete (PCM+PCB)': datetime(2027, 11, 15, 0, 0, tzinfo=IST),
    '🔁 Physics & Chemistry 3rd Revision': datetime(2028, 3, 20, 0, 0, tzinfo=IST),
    '🔁 Biology NCERT 3rd Revision': datetime(2028, 3, 25, 0, 0, tzinfo=IST),
    '🔁 Maths Full Revision': datetime(2028, 3, 28, 0, 0, tzinfo=IST),

    # ===============================
    # 🏆 COMPETITIVE EXAMS – ENGINEERING
    # ===============================
    '💪 JEE Main (Jan Attempt)': datetime(2028, 1, 5, 0, 0, tzinfo=IST),
    '⚡ JEE Main (April Attempt)': datetime(2028, 4, 5, 0, 0, tzinfo=IST),
    '🚀 JEE Advanced (Target)': datetime(2028, 6, 2, 9, 0, tzinfo=IST),

    # ===============================
    # 🏥 COMPETITIVE EXAMS – MEDICAL
    # ===============================
    '🩺 NEET UG (Target)': datetime(2028, 5, 7, 14, 0, tzinfo=IST),
    '🏥 AIIMS / Other Medical Exams': datetime(2028, 6, 1, 0, 0, tzinfo=IST),

    # ===============================
    # 🎯 BACKUP / STATE EXAMS
    # ===============================
    '🏫 State CET / Other Engg Exams': datetime(2028, 5, 10, 0, 0, tzinfo=IST),
}
DAILY_QUOTES = [
    "The secret of getting ahead is getting started.", "The expert in anything was once a beginner.", "Don't wish for it. Work for it.",
    "The future belongs to those who believe in the beauty of their dreams.", "Success is the sum of small efforts, repeated day in and day out.",
    "It’s not whether you get knocked down, it’s whether you get up.", "Believe you can and you're halfway there.",
]
QUICK_CHECK_QUOTES = [
    "Are you hydrated? Go drink a glass of water!", "Sit straight! Your back will thank you.", "Take 5 deep breaths. Inhale positivity, exhale stress.",
    "Did you stretch your legs? A quick walk can help.", "Blink a few times. Give your eyes a break from the screen.",
]
# --- FOOTER ---
FOOTER_NAME = "Pranav International PVT\\. LTD\\."
WEBSITE_URL = "https://pranav-sharma.pages.dev"
INSTAGRAM_HANDLE = "itz_me_pranav_sharma"

# ==============================================================================
#                               HELPER FUNCTIONS
# ==============================================================================

def escape_markdown_v2(text: str) -> str:
    """Escapes characters for Telegram's MarkdownV2 parse mode."""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

def save_message_id(message_id):
    """Saves the message ID to a file. If message_id is None, deletes the file."""
    if message_id:
        with open(MESSAGE_FILE, "w") as f:
            f.write(str(message_id))
    else:
        if os.path.exists(MESSAGE_FILE):
            os.remove(MESSAGE_FILE)

def load_message_id():
    """Loads the message ID from a file. Returns None if not found or invalid."""
    try:
        if not os.path.exists(MESSAGE_FILE):
            return None
        with open(MESSAGE_FILE, "r") as f:
            content = f.read().strip()
            return int(content) if content else None
    except (ValueError, FileNotFoundError):
        return None

def format_timedelta(td: timedelta):
    """Formats a timedelta object into a 'Dd, Hh, Mm, Ss' string."""
    days, rem = divmod(td.total_seconds(), 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{int(days)}d, {int(hours)}h, {int(minutes)}m, {int(seconds)}s"

# ==============================================================================
#                               CORE COUNTDOWN LOGIC
# ==============================================================================
async def main_countdown_logic():
    print("COUNTDOWN BOT STARTED (Smart Send Logic)")
    bot = telegram.Bot(token=BOT_TOKEN)
    message_id = load_message_id()

    current_daily_quote = ""
    last_quote_update_day = None

    if message_id:
        print(f"Resuming with message ID: {message_id}")
    else:
        print("No previous message ID found. Will send a new message.")

    while True:
        now = datetime.now(IST)

        # --- Daily Quote Logic ---
        current_day = now.date()
        if last_quote_update_day != current_day and DAILY_QUOTES:
            last_quote_update_day = current_day
            day_of_year = now.timetuple().tm_yday
            quote_index = (day_of_year - 1) % len(DAILY_QUOTES)
            original_quote = DAILY_QUOTES[quote_index]
            current_daily_quote = escape_markdown_v2(original_quote)
            print(f"New Daily Quote set for {current_day}: '{original_quote}'")

        # --- Quick Check Logic ---
        current_quick_quote = ""
        if QUICK_CHECK_QUOTES:
            quarter_hour_index = (now.hour * 4) + (now.minute // 15)
            quote_index = quarter_hour_index % len(QUICK_CHECK_QUOTES)
            original_quote = QUICK_CHECK_QUOTES[quote_index]
            current_quick_quote = escape_markdown_v2(original_quote)

        # --- Subject Countdown Logic ---
        subject_lines = []
        for subject, date in TARGET_DATES.items():
            escaped_subject = escape_markdown_v2(subject)
            time_left = date - now
            if time_left.total_seconds() < 0:
                subject_lines.append(f"• {escaped_subject}: ✅ *Exam Over\\!*")
            else:
                countdown_str = format_timedelta(time_left)
                subject_lines.append(f"• {escaped_subject}: *{countdown_str}*")
        subject_countdown_str = "\n".join(subject_lines)

        # --- Construct Final Message ---
        message_text = f"""📢 *ALL EXAM CRITICAL COUNTDOWN*

*Live Time:* {now.strftime('%I:%M:%S %p')} — {now.strftime('%d %b %Y')} *IST*
\\-\\-\\-
🗓️ *Subject\\-wise Countdown:*
{subject_countdown_str}
\\-\\-\\-
💡 *Quote of the Day*
> {current_daily_quote}
\\-\\-\\-
🏃 *Quick Check*
> _{current_quick_quote}_
\\-\\-\\-
*Managed By 🏢 {FOOTER_NAME}*
🌐 [Website]({WEBSITE_URL})  •  📸 [Instagram](https://www.instagram.com/{INSTAGRAM_HANDLE}/)
"""
        
        try:
            if message_id is None:
                print("Sending new message...")
                sent_message = await bot.send_message(
                    chat_id=CHAT_ID, text=message_text, parse_mode='MarkdownV2', disable_web_page_preview=True
                )
                message_id = sent_message.message_id
                save_message_id(message_id)
                print(f"New message sent successfully. ID: {message_id}")
            else:
                await bot.edit_message_text(
                    chat_id=CHAT_ID, message_id=message_id, text=message_text, parse_mode='MarkdownV2', disable_web_page_preview=True
                )
            
        except telegram.error.BadRequest as e:
            if "message is not modified" in str(e):
                pass
            elif "message to edit not found" in str(e):
                print("[!] Message was deleted from chat. Resetting to send a new one.")
                message_id = None
                save_message_id(None)
            else: 
                print(f"[!] A Telegram BadRequest occurred: {e}")
                print(f"--- Failing Message Text ---\n{message_text}\n---------------------------")
        except Exception as e:
            print(f"[!] An unexpected error occurred: {e}")
            await asyncio.sleep(10)
        
        await asyncio.sleep(UPDATE_INTERVAL_SECONDS)

# ==============================================================================
#                               MAIN EXECUTION
# ==============================================================================
if __name__ == "__main__":
    # Check if token/ID are placeholders
    if 'YOUR_BOT_TOKEN_HERE' in BOT_TOKEN or 'YOUR_CHAT_ID_HERE' in str(CHAT_ID):
        print("FATAL ERROR: Please replace 'YOUR_BOT_TOKEN_HERE' and 'YOUR_CHAT_ID_HERE' in the script with your actual bot token and chat ID.")
        exit()

    print("Starting main application...")
    
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    try:
        asyncio.run(main_countdown_logic())
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
    except Exception as e:
        print(f"\nCRITICAL FAILURE in main loop: {e}")
