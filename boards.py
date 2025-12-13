import threading
from flask import Flask
import os
import telegram
import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo 

# --- WEB SERVER (FLASK) PART ---
app = Flask(__name__)
@app.route('/')
def hello():
    return "Bot is alive and all features are running!"
def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)


BOT_TOKEN = '8265096272:AAE4HTHAovCNaofsqkVqD_5kX8fGOYq0IP4' 
CHAT_ID = -1003356902972
UPDATE_INTERVAL_SECONDS = 3

# --- TIMEZONE SETTING ---
IST = ZoneInfo("Asia/Kolkata")

# --- TARGET DATES (Target: 6:00 AM IST) ---
TARGET_DATES = {
    '🧮 Maths': datetime(2026, 2, 17, 6, 0, tzinfo=IST),
    '📘 English': datetime(2026, 2, 21, 6, 0, tzinfo=IST),
    '🔬 Science': datetime(2026, 2, 25, 6, 0, tzinfo=IST),
    '🤖 AI/IT': datetime(2026, 2, 27, 6, 0, tzinfo=IST),
    '📜 Sanskrit': datetime(2026, 2, 28, 6, 0, tzinfo=IST),
    '🗣️ Hindi': datetime(2026, 3, 2, 6, 0, tzinfo=IST),
    '🏛️ SST': datetime(2026, 3, 7, 6, 0, tzinfo=IST),
}

# --- QUOTES & LINKS (Original text, will be escaped later) ---
DAILY_QUOTES = [
    "The secret of getting ahead is getting started.", "The expert in anything was once a beginner.", "Don't wish for it. Work for it.",
    "The future belongs to those who believe in the beauty of their dreams.", "Success is the sum of small efforts, repeated day in and day out.",
    "It’s not whether you get knocked down, it’s whether you get up.", "Believe you can and you're halfway there.",
    "Push yourself, because no one else is going to do it for you.", "The harder you work for something, the greater you'll feel when you achieve it.",
    "Dream bigger. Do bigger.", "Study while others are sleeping; work while others are loafing.", "Success doesn't just find you. You have to go out and get it.",
    "The pain you feel today will be the strength you feel tomorrow.", "Focus on your goal. Don't look in any direction but ahead.",
    "A little progress each day adds up to big results.", "Strive for progress, not perfection.", "Your future is created by what you do today, not tomorrow.",
    "The only way to do great work is to love what you do.", "Don't stop when you're tired. Stop when you're done.",
    "The difference between ordinary and extraordinary is that little extra.", "Discipline is the bridge between goals and accomplishment.",
    "Wake up with determination. Go to bed with satisfaction.", "It's going to be hard, but hard does not mean impossible.",
    "The key to success is to focus on goals, not obstacles.", "Doubt kills more dreams than failure ever will.", "You are stronger than you think.",
    "There are no shortcuts to any place worth going.", "Make today count. You'll never get it back.", "The grind never stops. Keep going.",
    "One day, all your hard work will pay off.", "Be so good they can't ignore you.", "Hustle in silence and let your success make the noise.",
    "If you get tired, learn to rest, not to quit.", "The secret to success is consistency.", "Small steps every day lead to massive results.",
    "Your only limit is your mind.", "Prove them wrong.", "It's a slow process, but quitting won't speed it up.",
    "Fall seven times, stand up eight.", "A year from now, you'll wish you had started today.", "Let your habits be stronger than your excuses."
]

QUICK_CHECK_QUOTES = [
    "Are you hydrated? Go drink a glass of water!", "Sit straight! Your back will thank you.", "Take 5 deep breaths. Inhale positivity, exhale stress.",
    "Did you stretch your legs? A quick walk can help.", "Blink a few times. Give your eyes a break from the screen.",
    "Is your study area clean? A tidy space equals a tidy mind.", "Quickly review what you just learned. Reinforce it!",
    "Think of one thing you're grateful for right now.", "Is your phone away? Avoid distractions!", "How's your posture? Straighten your spine.",
    "Time for a 2-minute mental break. Just close your eyes.", "Wiggle your toes and fingers to get the blood flowing.",
    "Did you eat a healthy snack? Fuel your brain.", "Recite a formula or definition from memory.", "Stand up and stretch your arms to the ceiling.",
    "Is there any background noise? Try to minimize it.", "Smile! It can improve your mood.", "Take a moment to appreciate your hard work.",
    "20-20-20 Rule: Look at something 20 feet away for 20 seconds.", "Positive thoughts only. You've got this!"
]

# --- FOOTER ---
FOOTER_NAME = "Pranav International PVT\\. LTD\\."
WEBSITE_URL = "https://pranav-sharma.pages.dev"
INSTAGRAM_HANDLE = "itz_me_pranav_sharma"

MESSAGE_FILE = "message_info.txt"
# ==============================================================================
#                               HELPER FUNCTIONS
# ==============================================================================
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
    print("COUNTDOWN BOT STARTED (Smart Send Logic)")
    bot = telegram.Bot(token=BOT_TOKEN)
    message_id = load_message_id()

    current_daily_quote = ""
    last_quote_update_day = None

    if message_id:
        print(f"Resuming for message ID: {message_id}")
    else:
        print("No previous message found. Will send a new message on the first run.")

    while True:
        now = datetime.now(IST)

        # --- Daily Quote Logic ---
        current_day = now.date()
        if last_quote_update_day != current_day and DAILY_QUOTES:
            last_quote_update_day = current_day
            day_of_year = now.timetuple().tm_yday
            quote_index = (day_of_year - 1) % len(DAILY_QUOTES)
            
            # **FIX:** Escape special characters in the quote for MarkdownV2
            original_quote = DAILY_QUOTES[quote_index]
            current_daily_quote = original_quote.replace('.', '\\.').replace('!', '\\!').replace('-', '\\-')
            
            print(f"New Daily Quote set for {current_day}: '{original_quote}'")

        # --- Quick Check Logic ---
        current_quick_quote = ""
        if QUICK_CHECK_QUOTES:
            quarter_hour_index = (now.hour * 4) + (now.minute // 15)
            quote_index = quarter_hour_index % len(QUICK_CHECK_QUOTES)

            # **FIX:** Escape special characters in the quote for MarkdownV2
            original_quote = QUICK_CHECK_QUOTES[quote_index]
            current_quick_quote = original_quote.replace('?', '\\?').replace('!', '\\!').replace('.', '\\.').replace('-', '\\-')

        # --- Subject Countdown Logic ---
        subject_lines = []
        for subject, date in TARGET_DATES.items():
            time_left = date - now
            if time_left.total_seconds() < 0:
                subject_lines.append(f"• {subject}: ✅ *Exam Over\\!*")
            else:
                countdown_str = format_timedelta(time_left)
                subject_lines.append(f"• {subject}: *{countdown_str}*")
        subject_countdown_str = "\n".join(subject_lines)

        # **FIX:** Correctly escape characters for MarkdownV2 in the main message string
        message_text = f"""📢 **BOARD EXAM COUNTDOWN \\(2026\\)**

*Live Time:* {now.strftime('%I:%M:%S %p')} — {now.strftime('%d %b %Y')} *IST*
\\-\\-\\-
🗓️ *Subject\\-wise Countdown:*
{subject_countdown_str}
\\-\\-\\-
💡 **Quote of the Day**
> _{current_daily_quote}_
\\-\\-\\-
🏃 **Quick Check**
> *{current_quick_quote}*
\\-\\-\\-
*Managed By 🏢 {FOOTER_NAME}*
🌐 [Website]({WEBSITE_URL})  •  📸 [Instagram](https://www.instagram.com/{INSTAGRAM_HANDLE}/)
"""
        
        try:
            if message_id is None:
                print("Sending the first complete message...")
                sent_message = await bot.send_message(
                    chat_id=CHAT_ID, text=message_text, parse_mode='MarkdownV2', disable_web_page_preview=True
                )
                message_id = sent_message.message_id
                save_message_id(message_id)
                print(f"First message sent successfully. ID: {message_id}")
            else:
                await bot.edit_message_text(
                    chat_id=CHAT_ID, message_id=message_id, text=message_text, parse_mode='MarkdownV2', disable_web_page_preview=True
                )
            
        except telegram.error.BadRequest as e:
            if "message is not modified" in str(e): pass
            else: 
                print(f"[!] FAILED to process message: {e}")
                if "message to edit not found" in str(e):
                    print("[!] Message was deleted. Resetting message_id to send a new one.")
                    message_id = None
                    save_message_id("")
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
