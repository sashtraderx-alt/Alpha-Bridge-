import os
from flask import Flask, request
import requests

app = Flask(__name__)

# بيانات التلغرام (سنجلبها من إعدادات Render للأمان)
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8283237411:AAHVtnVZ2RDCxHh1K-Apgyx_frtU1ybZRpk")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "-1002494852608")

@app.route('/')
def home():
    return "Alpha Bridge is Running..."

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        if not data:
            return "No Data", 400

        # استخراج التفاصيل من التنبيه
        symbol = data.get("symbol", "N/A")
        trade_type = data.get("type", "N/A")
        price = data.get("price", "N/A")
        tp = data.get("tp", "N/A")
        sl = data.get("sl", "N/A")
        status = data.get("status", "N/A")
        result = data.get("result", "")
        chart_url = data.get("chart", "")

        # تنسيق الرسالة (بدون إيموجي وبدون زخرفة)
        if status == "Entry":
            message = (
                f"Symbol: {symbol}\n"
                f"Type: {trade_type}\n"
                f"Entry Price: {price}\n"
                f"TP: {tp}\n"
                f"SL: {sl}"
            )
        else:
            message = (
                f"Symbol: {symbol}\n"
                f"Status: Trade Closed\n"
                f"Result: {result}\n"
                f"Exit Price: {price}"
            )

        # إرسال الصورة إذا وجدت، أو إرسال نص فقط
        if chart_url:
            send_photo_url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            payload = {
                "chat_id": CHAT_ID,
                "photo": chart_url,
                "caption": message
            }
            requests.post(send_photo_url, json=payload)
        else:
            send_msg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            payload = {
                "chat_id": CHAT_ID,
                "text": message
            }
            requests.post(send_msg_url, json=payload)

        return "Success", 200

    except Exception as e:
        print(f"Error: {e}")
        return "Internal Error", 500

if __name__ == "__main__":
    # استخدام المنفذ الذي يحدده Render تلقائياً
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
