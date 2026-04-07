import os
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# --- CONFIGURATIONS ---
# حطيت التوكن هون مباشرة عشان ما يضيع بالـ Environment Variables
TOKEN = "8283237411:AAHVtnVZ2RDCxHh1K-Apgyx_frtU1ybZRpk"

# هدول اسحبهم من Render
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

# إعداد Gemini
genai.configure(api_key=GEMINI_KEY)

# ALPHA'S CORE BRAIN
SYSTEM_INSTRUCTION = """
ROLE: You are 'ALPHA', a high-tier professional trader and the embodiment of the 'ALPHA🔹️ENGINE' system. 
PERSONALITY: Real human, confident, serious, direct. Optimistic (no failure, only expensive lessons).
STRATEGY: ORB (Tokyo, London, NY), Unicorn Zones (Breaker + IFVG), Dual Pressure, SABS/BABS, ICT (MSS, BOS, FVG).
ROADMAP: Conservative Million Roadmap (1000 pips month 1, 410 pips months 2-4).
STYLE: Respond ONLY in Shami (Levantine) Arabic. Dry and professional. Address the user as 'Maynr'.
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_INSTRUCTION
)

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        response = requests.post(url, json=payload)
        print(f"Telegram Response: {response.json()}") # عشان نشوف النتيجة بالـ Logs
    except Exception as e:
        print(f"Telegram Error: {e}")

def setup_webhook():
    webhook_url = "https://alpha-bridge.onrender.com/webhook"
    base_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    try:
        requests.get(base_url, params={"url": webhook_url})
    except Exception:
        pass

@app.route('/')
def home():
    return "ALPHA PROTOCOL IS ONLINE"

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    update = request.json
    if not update:
        return jsonify({"status": "no data"}), 200

    # 1. إشارات التداول (TradingView)
    if 'symbol' in update:
        try:
            symbol = update.get('symbol')
            action = update.get('type')
            price = update.get('price')
            
            prompt = f"New Signal: {symbol} {action} at {price}. Analyze using ALPHA ENGINE logic."
            ai_response = model.generate_content(prompt).text
            
            full_msg = f"🏆 ALPHA SIGNAL\n\nAsset: {symbol}\nAction: {action}\nPrice: {price}\n\nAnalysis: {ai_response}"
            send_telegram_message(CHAT_ID, full_msg)
        except Exception as e:
            print(f"Signal Error: {e}")

    # 2. رسائل الدردشة
    elif 'message' in update:
        try:
            msg = update['message']
            target_chat = msg['chat']['id']
            user_text = msg.get('text', '')
            user_name = msg['from'].get('first_name', 'Trader')

            if user_text:
                ai_response = model.generate_content(f"User {user_name} says: {user_text}").text
                send_telegram_message(target_chat, ai_response)
        except Exception as e:
            print(f"Chat Error: {e}")

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    setup_webhook()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
