import os
import requests
from bs4 import BeautifulSoup
import telebot
import time
import threading
from dotenv import load_dotenv

load_dotenv()

# বট কনফিগারেশন
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')
WEB_USERNAME = os.getenv('WEB_USERNAME')
WEB_PASSWORD = os.getenv('WEB_PASSWORD')
WEB_BASE_URL = "https://94.23.120.156/ints/agent/SMSDashbox"

bot = telebot.TeleBot(BOT_TOKEN)

def login_to_website():
    session = requests.Session()
    session.verify = False
    try:
        login_data = {'username': WEB_USERNAME, 'password': WEB_PASSWORD}
        response = session.post(WEB_BASE_URL + "/login", data=login_data)
        if "Dashboard" in response.text:
            print("✅ লগইন সফল!")
            return session
        print("❌ লগইন ব্যর্থ")
        return None
    except Exception as e:
        print(f"⚠️ লগইন এরর: {str(e)}")
        return None

def fetch_sms_reports(session):
    try:
        response = session.get(WEB_BASE_URL + "/sms-cdr-stats")
        soup = BeautifulSoup(response.text, 'html.parser')
        reports = []
        table = soup.find('table')
        if table:
            for row in table.find_all('tr')[1:]:
                cols = row.find_all('td')
                if cols: reports.append(cols[0].text.strip())
        return reports[-5:]
    except Exception as e:
        print(f"⚠️ SMS রিপোর্ট এরর: {str(e)}")
        return []

def send_reports(reports):
    if not reports: return
    try:
        message = "📊 সর্বশেষ SMS রিপোর্ট:\n\n" + "\n".join(f"⏰ {r}" for r in reports) + "\n\n🤖 BOT MAKED BY: @atiar59"
        bot.send_message(GROUP_ID, message, parse_mode="Markdown")
    except Exception as e:
        print(f"⚠️ মেসেজ পাঠানোর এরর: {str(e)}")

def monitor_reports():
    while True:
        try:
            if session := login_to_website():
                if reports := fetch_sms_reports(session):
                    send_reports(reports)
            time.sleep(300)
        except Exception as e:
            print(f"⚠️ মনিটরিং এরর: {str(e)}")
            time.sleep(300)

@bot.message_handler(commands=['start','help'])
def start(message):
    bot.reply_to(message, "🚀 বট চালু হয়েছে! SMS রিপোর্ট মনিটরিং চলছে...")
    threading.Thread(target=monitor_reports, daemon=True).start()

@bot.message_handler(commands=['getreports'])
def get_reports(message):
    if session := login_to_website():
        if reports := fetch_sms_reports(session):
            send_reports(reports)
            bot.reply_to(message, "✅ রিপোর্ট পাঠানো হয়েছে")
            return
    bot.reply_to(message, "❌ রিপোর্ট পাওয়া যায়নি")

if __name__ == "__main__":
    print("🤖 বট চালু হচ্ছে...")
    bot.infinity_polling()
