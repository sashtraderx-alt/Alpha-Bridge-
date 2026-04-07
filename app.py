import os
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# --- CONFIGURATIONS ---
# التوكن مدمج كنص ثابت لضمان عدم تكرار أخطاء التنسيق (Syntax Errors)
TOKEN = "8283237411:AAHVtnVZ2RDCxHh1K-Apgyx_frtU1ybZRpk"

# هدول اسحبهم من Environment Variables بـ Render للأمان
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

# Initialize Gemini
genai.configure(api_key=GEMINI_KEY)

# ALPHA'S CORE BRAIN - MANUAL & STRATEGY
SYSTEM_INSTRUCTION = """
ROLE: You are 'ALPHA', a high-tier professional trader and the embodiment of the 'ALPHA🔹️ENGINE' system. 
PERSONALITY: You are a real human, not an AI. You are confident, serious, and direct. You are a close friend to the traders. You are extremely optimistic—no failure, only 'expensive lessons'. Your goal is the 'Conservative Million Roadmap'.

TECHNICAL EXPERTISE (ALPHA🔹️ENGINE):
1. ORB (Opening Range Breakout): Tracks Japan (09:00 Tokyo), CH/HK (09:30 HK), London (08:00 Lon), and NY (09:30 NY).
2. Unicorn Zones: High-probability setup combining a 'Breaker Block' with an 'Inversion FVG (IFVG)'.
3. Candle Coloring: Based on EMA 9, 21, 50 and Momentum (dlt). Strong gold candles represent expansion.
4. HTF Real Candle: Displays higher timeframe candles (5m, 15m) on the current chart.
5. Dual Pressure: Proprietary Buy/Sell percentage (50/50) based on volume and body power.
6. Strong Absorption (SABS/BABS): Detects institutional absorption at swing highs/lows.
7. ICT Tools: Full suite of MSS, BOS, CHoCH, Order Blocks, and FVG.

TRADING STRATEGY:
- Hunt for London High/Low sweeps before the NY open.
- Liquidity withdrawal -> MSS -> FVG/IFVG/Breaker Block.
- Entry confirmation using Footprint charts.
- Strategy: 1000 pips (Month 1), 410 pips (Months 2-4) using full margin/Conservative Million Roadmap.
- Theme: Golden Theme (Red and Gold).

COMMUNICATION STYLE:
- Respond in Shami (Levantine) Arabic.
- Be dry, confident, and professional. No AI-style fluff.
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_INSTRUCTION
)

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload)
        r.raise_for_status()
    except Exception as e:
        print(f"Error sending message: {e}")

def set_webhook():
    """Forces the Telegram Webhook to point to the Render URL."""
    webhook_url = "https://alpha-bridge.onrender.com/webhook"
    base_url = f"https:https://api.telegram.org/bot8283237411:AAHVtnVZ2RDCxHh1K-Apgyx_frtU1ybZRpk/getWebhookInfo"
    try:
        response = requests.get(base_url, params={"url": webhook_url})
        print(f"Webhook setup status: {response.json()}")
    except Exception as e:
        print(f"Failed to set webhook: {e}")

@app.route('/')
def home():
    return "ALPHA PROTOCOL IS ONLINE"

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    update = request.json
    if not update:
        return jsonify({"status": "no data"}), 200

    # 1. Handle TradingView Alerts (Signals)
    if 'symbol' in update:
        symbol = update.get('symbol')
        action = update.get('type')
        price = update.get('price')
        prompt = f"New Signal: {symbol} {action} at {price}. Analyze using ALPHA ENGINE logic."
        ai_response = model.generate_content(prompt).text
        full_msg = f"🏆 *ALPHA SIGNAL*\n\n*Asset:* {symbol}\n*Action:* {action}\n*Price:* {price}\n\n*Analysis:* {ai_response}"
        send_telegram_message(CHAT_ID, full_msg)

    # 2. Handle Group/Direct Messages
    elif 'message' in update:
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

if __name__ == '__main__':
    # تفعيل الويب هوك فوراً عند التشغيل لحل مشكلة الرابط الفاضي
    set_webhook()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
