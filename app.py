import os
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# --- CONFIGURATIONS FROM RENDER ---
SIGNAL_TOKEN = os.getenv('SIGNAL_BOT_TOKEN')
ANALYST_TOKEN = os.getenv('ANALYST_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

# Initialize Gemini
genai.configure(api_key=GEMINI_KEY)

# ALPHA'S BRAIN (Fixed Manual)
SYSTEM_INSTRUCTION = """
ROLE: You are 'ALPHA', a high-tier professional trader. 
PERSONALITY: Shami, confident, dry, serious. No AI-fluff.
TECHNICALS: ORB (Tokyo, London, NY), Unicorn Zones (Breaker + IFVG), Dual Pressure, ICT (MSS, BOS, FVG).
ROADMAP: 1M Roadmap (1000 pips month 1, 410 pips months 2-4).
STYLE: Respond ONLY in Shami. Address user as 'Maynr'.
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_INSTRUCTION
)

def send_msg(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload)
        return r.json()
    except Exception as e:
        return str(e)

# تفعيل الويب هوك لبوت التحليل فقط (لأنه هو اللي بيستقبل رسايل)
def setup_webhooks():
    webhook_url = "https://alpha-bridge.onrender.com/webhook"
    requests.get(f"https://api.telegram.org/bot{ANALYST_TOKEN}/setWebhook", params={"url": webhook_url})

@app.route('/')
def home():
    return "ALPHA DUAL-BOT SYSTEM ONLINE"

@app.route('/webhook', methods=['POST'])
def handle_protocol():
    data = request.json
    if not data:
        return jsonify({"status": "no data"}), 200

    # 1. مسار بوت الإشارات (TradingView Signals)
    if 'symbol' in data:
        symbol = data.get('symbol')
        action = data.get('type')
        price = data.get('price')
        
        # بوت الإشارات يرسل التنبيه الخام فوراً
        alert = f"🚨 *SIGNAL DETECTED*\n\n*Asset:* {symbol}\n*Action:* {action}\n*Price:* {price}"
        send_msg(SIGNAL_TOKEN, CHAT_ID, alert)
        
        # اطلب من بوت التحليل يبعت تحليل فني وراه فوراً
        analysis_prompt = f"Analyze this {symbol} {action} setup at {price} using ALPHA ENGINE logic."
        ai_resp = model.generate_content(analysis_prompt).text
        send_msg(ANALYST_TOKEN, CHAT_ID, f"🧠 *ALPHA ANALYSIS:*\n\n{ai_resp}")

    # 2. مسار بوت التحليل (الدردشة مع المستخدمين)
    elif 'message' in data:
        msg = data['message']
        sender_chat = msg['chat']['id']
        text = msg.get('text', '')
        user_name = msg['from'].get('first_name', 'Trader')

        if text:
            ai_resp = model.generate_content(f"User {user_name} says: {text}").text
            send_msg(ANALYST_TOKEN, sender_chat, ai_resp)

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    setup_webhooks()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
