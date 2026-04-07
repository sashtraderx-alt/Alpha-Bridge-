import os
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# --- CONFIGURATIONS ---
# التوكن مدمج وجاهز للاستخدام
TOKEN = "8283237411:AAHVtnVZ2RDCxHh1K-Apgyx_frtU1ybZRpk"

# هدول بيعتمدوا على الإعدادات اللي حطيتها بـ Render
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

# Initialize Gemini
genai.configure(api_key=GEMINI_KEY)

SYSTEM_INSTRUCTION = """
ROLE: You are 'ALPHA', a high-tier professional trader. 
PERSONALITY: You are a real human. Confident, serious, and direct. You are a close friend to the traders. 
STYLE: Respond in Shami (Levantine) Arabic. Be professional and optimistic about the 'Conservative Million Roadmap'.
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_INSTRUCTION
)

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error: {e}")

@app.route('/')
def home():
    return "ALPHA PROTOCOL IS ONLINE"

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    update = request.json
    if not update:
        return jsonify({"status": "no data"}), 200

    if 'message' in update:
        msg = update['message']
        chat_id = msg['chat']['id']
        user_text = msg.get('text', '')
        user_name = msg['from'].get('first_name', 'Trader')

        if user_text:
            try:
                ai_response = model.generate_content(f"User {user_name} says: {user_text}").text
                send_telegram_message(chat_id, ai_response)
            except Exception as e:
                print(f"Gemini Error: {e}")

    return jsonify({"status": "success"}), 200

# دالة لتثبيت الويب هوك بشكل إجباري عند تشغيل الملف
def setup_webhook():
    webhook_url = "https://alpha-bridge.onrender.com/webhook"
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}"
    try:
        r = requests.get(url)
        print(f"Webhook Final Setup: {r.json()}")
    except Exception as e:
        print(f"Setup Error: {e}")

if __name__ == '__main__':
    setup_webhook() # تفعيل الربط فوراً
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
