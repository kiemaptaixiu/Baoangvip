
import telebot
import json
import os
from datetime import datetime, timedelta

TOKEN = "YOUR_BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "users_data.json"
ADMIN_ID = YOUR_ADMIN_ID  # Replace with your Telegram user ID
ACCESS_KEY = "toolbaoang"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

users = load_data()

def init_user(user_id):
    if str(user_id) not in users:
        users[str(user_id)] = {
            "key_verified": False,
            "coins": 0,
            "time_expire": "",
        }

def check_access(user_id):
    u = users[str(user_id)]
    if u["coins"] > 0:
        return True
    if u["time_expire"]:
        expire = datetime.strptime(u["time_expire"], "%Y-%m-%d %H:%M:%S")
        return datetime.now() <= expire
    return False

def deduct_usage(user_id):
    if users[str(user_id)]["coins"] > 0:
        users[str(user_id)]["coins"] -= 1

@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.from_user.id
    init_user(user_id)
    save_data(users)
    bot.reply_to(message, "🎉Xin chào đây là bot vip Baoang!
Bạn cần gì ở tôi?
Mua xu hoặc thời gian để sử dụng tôi nhé!
Vui lòng nhập key để tiếp tục:")

@bot.message_handler(commands=["baoangid"])
def user_id(message):
    bot.reply_to(message, f"ID của bạn là: {message.from_user.id}")

@bot.message_handler(commands=["sodu"])
def check_balance(message):
    user_id = message.from_user.id
    init_user(user_id)
    u = users[str(user_id)]
    time_left = u["time_expire"] or "Không có"
    reply = f"🔐 KEY: {'Đã nhập' if u['key_verified'] else 'Chưa nhập'}
💰 Xu còn lại: {u['coins']}
⏳ Thời gian sử dụng: {time_left}"
    bot.reply_to(message, reply)

@bot.message_handler(commands=["nap"])
def pay_guide(message):
    bot.reply_to(message, "Liên hệ admin để mua xu hoặc thời gian:
FB: Trần Bảo Ang
Telegram: @Baoangbantool")

@bot.message_handler(commands=["addcoins", "addtime"])
def admin_add(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        cmd, uid, value = message.text.split()
        if uid not in users:
            bot.reply_to(message, "ID chưa có trong hệ thống.")
            return
        if cmd == "/addcoins":
            users[uid]["coins"] += int(value)
        elif cmd == "/addtime":
            current = datetime.now()
            extra = timedelta(hours=float(value))
            existing = datetime.strptime(users[uid]["time_expire"], "%Y-%m-%d %H:%M:%S") if users[uid]["time_expire"] else current
            users[uid]["time_expire"] = str((existing + extra).strftime("%Y-%m-%d %H:%M:%S"))
        save_data(users)
        bot.reply_to(message, f"Đã cập nhật cho ID {uid}.")
    except Exception as e:
        bot.reply_to(message, f"Lỗi: {e}")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    user_id = message.from_user.id
    init_user(user_id)
    u = users[str(user_id)]

    if not u["key_verified"]:
        if message.text.strip() == ACCESS_KEY:
            users[str(user_id)]["key_verified"] = True
            save_data(users)
            bot.reply_to(message, "✅ Key chính xác. Bạn đã truy cập bot!")
        else:
            bot.reply_to(message, "❌ Key không đúng. Vui lòng thử lại.")
        return

    if not check_access(user_id):
        bot.reply_to(message, "❌ Số dư không đủ. Liên hệ admin để gia hạn: @Baoangbantool")
        return

    if message.text.startswith("/md5"):
        md5 = message.text[5:].strip()
        if not md5:
            bot.reply_to(message, "Vui lòng nhập mã MD5 sau lệnh /md5.")
            return
        deduct_usage(user_id)
        # Fake sample result for now
        bot.reply_to(message, f"🔍 Phân tích MD5: {md5}
→ Xỉu (Demo)")
    
    elif message.text.startswith("/phien"):
        phien = message.text[7:].strip()
        if not phien:
            bot.reply_to(message, "Vui lòng nhập mã phiên sau lệnh /phien.")
            return
        deduct_usage(user_id)
        # Fake sample result for now
        bot.reply_to(message, f"🔍 Phân tích phiên: {phien}
→ Tài (Demo)")

    elif message.text == "/hotro":
        bot.reply_to(message, "Liên hệ hỗ trợ:
Facebook: Trần Bảo Ang
Telegram: @Baoangbantool")

    save_data(users)

bot.polling()
