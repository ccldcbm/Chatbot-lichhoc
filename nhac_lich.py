import datetime
import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "your_verify_token")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN", "your_page_access_token")

daily_schedule = {
    "Monday": ["KT Phân tích trong CN sinh học (07:00 - 09:50, F303)", "Quá trình & TB truyền nhiệt (14:30 - 17:20, E114)"],
    "Tuesday": ["TN Quá trình và TB (07:00 - 10:50, D112)", "Lịch sử Đảng Cộng sản VN (12:30 - 15:20, F110)"],
    "Wednesday": ["Quá trình & TB truyền chất (07:00 - 09:50, F101)"],
    "Thursday": ["Kinh tế và quản lý doanh nghiệp (09:00 - 11:50, E205)"],
    "Friday": ["Quản lý chất lượng trong CNSH (07:00 - 09:50, F309)", "Kỹ năng thuyết trình TA (10:00 - 11:50, E301A)", "PP kiểm nghiệm vi sinh (14:30 - 17:20, F401)"],
    "Saturday": ["PBL 3: Quản lý CLSP (07:00 - 10:50, F107)"],
    "Sunday": ["Không có lịch học"]
}

def get_schedule(day=None):
    if day is None:
        day = datetime.datetime.today().strftime('%A')
    return daily_schedule.get(day, ["Không có lịch học"])

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        return challenge
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def handle_messages():
    data = request.get_json()
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                sender_id = messaging_event["sender"]["id"]
                if "message" in messaging_event and "text" in messaging_event["message"]:
                    user_message = messaging_event["message"]["text"].lower()
                    response_text = process_user_message(user_message)
                    send_message(sender_id, response_text)
    return "EVENT_RECEIVED", 200

def process_user_message(user_input):
    if user_input in ["hôm nay", "today"]:
        day = datetime.datetime.today().strftime('%A')
    elif user_input in ["ngày mai", "tomorrow"]:
        day = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%A')
    else:
        day_map = {
            "thứ hai": "Monday", "thứ ba": "Tuesday", "thứ tư": "Wednesday", "thứ năm": "Thursday", 
            "thứ sáu": "Friday", "thứ bảy": "Saturday", "chủ nhật": "Sunday"
        }
        day = day_map.get(user_input, None)
        if day is None:
            return "Xin lỗi, tôi không hiểu ngày này. Vui lòng nhập lại."
    
    schedule = get_schedule(day)
    return f"Lịch học {user_input} ({day}):\n- " + "\n- ".join(schedule)

def send_message(recipient_id, text):
    url = "https://graph.facebook.com/v17.0/me/messages"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
        "messaging_type": "RESPONSE",
    }
    params = {"access_token": PAGE_ACCESS_TOKEN}
    requests.post(url, headers=headers, json=payload, params=params)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
