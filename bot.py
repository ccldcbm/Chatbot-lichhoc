import os
import datetime
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Khởi tạo Flask
app = Flask(__name__)

# Lấy token bot từ biến môi trường
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Lịch học
daily_schedule = {
    "Monday": ["📚 KT Phân tích trong CN sinh học (07:00 - 09:50, F303)", "🔥 Quá trình & TB truyền nhiệt (14:30 - 17:20, E114)"],
    "Tuesday": ["🧪 TN Quá trình và TB (07:00 - 10:50, D112)", "📖 Lịch sử Đảng Cộng sản VN (12:30 - 15:20, F110)"],
    "Wednesday": ["💡 Quá trình & TB truyền chất (07:00 - 09:50, F101)"],
    "Thursday": ["🏢 Kinh tế và quản lý doanh nghiệp (09:00 - 11:50, E205)"],
    "Friday": ["✅ Quản lý chất lượng CNSH (07:00 - 09:50, F309)", "🎤 Kỹ năng thuyết trình TA (10:00 - 11:50, E301A)", "🔬 PP kiểm nghiệm vi sinh (14:30 - 17:20, F401)"],
    "Saturday": ["📊 PBL 3: Quản lý CLSP (07:00 - 10:50, F107)"],
    "Sunday": ["🚫 Không có lịch học"]
}

# Hàm lấy lịch học theo ngày
def get_schedule(day=None):
    if day is None:
        day = datetime.datetime.today().strftime('%A')
    return daily_schedule.get(day, ["🚫 Không có lịch học"])

# Route chính nhận tin nhắn từ Telegram
@app.route("/webhook", methods=["POST"])
def handle_messages():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"].lower()
        response_text = process_user_message(user_message)
        send_message(chat_id, response_text)

    return jsonify({"status": "ok"}), 200

# Xử lý nội dung tin nhắn của người dùng
def process_user_message(user_input):
    today = datetime.datetime.today().strftime('%A')
    tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%A')

    if user_input in ["hôm nay", "today"]:
        day = today
    elif user_input in ["ngày mai", "tomorrow"]:
        day = tomorrow
    elif user_input == "/start":
        return "🤖 Xin chào! Tôi là chatbot lịch học 📅. Nhập ngày hoặc chọn menu để xem lịch học."
    else:
        day_map = {
            "thứ hai": "Monday", "thứ ba": "Tuesday", "thứ tư": "Wednesday",
            "thứ năm": "Thursday", "thứ sáu": "Friday", "thứ bảy": "Saturday",
            "chủ nhật": "Sunday"
        }
        day = day_map.get(user_input, None)
        if day is None:
            return "⚠ Xin lỗi, tôi không hiểu ngày này. Vui lòng nhập lại."

    schedule = get_schedule(day)
    return f"📅 Lịch học **{user_input.upper()}** ({day}):\n- " + "\n- ".join(schedule)

# Gửi tin nhắn về Telegram
def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id, 
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": {
            "keyboard": [["Hôm nay", "Ngày mai"], ["Thứ hai", "Thứ ba", "Thứ tư"], ["Thứ năm", "Thứ sáu", "Thứ bảy", "Chủ nhật"]],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
    }
    requests.post(url, json=payload)

# Cấu hình webhook Telegram
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    webhook_url = os.getenv("RENDER_URL") + "/webhook"
    response = requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}")
    return response.json()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
