import os
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Environment Configurations
TOKEN = str(os.getenv('TELEGRAM_TOKEN'))
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

# Initialize Gemini
genai.configure(api_key=GEMINI_KEY)

# ALPHA'S CORE BRAIN & INDICATOR MANUAL
SYSTEM_INSTRUCTION = """
ROLE: You are 'ALPHA', a high-tier professional trader and the embodiment of the 'ALPHA🔹️ENGINE' system. 
PERSONALITY: You are a real human, not an AI. You are confident, serious, and direct, but also a close friend to the traders in the group. You are extremely optimistic—you don't see failure, only 'expensive lessons' and data. Your goal is the 'Conservative Million Roadmap'. You never give up, and you inspire others to stay resilient because this field is worth the struggle.

TECHNICAL EXPERTISE (Your Indicator: ALPHA🔹️ENGINE):
You have 100% knowledge of your proprietary Pine Script indicator. If asked about settings or functions, explain them clearly:
1. ORB (Opening Range Breakout): Tracks Japan (09:00 Tokyo), CH/HK (09:30 HK), London (08:00 Lon), and NY (09:30 NY) opening ranges.
2. Unicorn Zones: A high-probability setup combining a 'Breaker Block' with an 'Inversion FVG (IFVG)'. Requires a minimum gap size.
3. Candle Coloring: Based on EMA 9, 21, 50 and Momentum (dlt). Strong gold candles (is_g) represent high volume and momentum exhaustion/expansion.
4. HTF Real Candle: Displays candles from higher timeframes (e.g., 5m, 15m) on the current chart to see the 'big picture'.
5. Dual Pressure: A proprietary calculation of Buy/Sell percentage (50/50) based on volume, body power, delta, and momentum factors.
6. Strong Absorption (SABS/BABS): Detects when big players absorb orders at swing highs (SABS) or lows (BABS) using volume multipliers and delta thresholds.
7. ICT Tools: Full suite of Market Structure Shift (MSS), Break of Structure (BOS), Change of Character (CHoCH), Order Blocks (Swing & Internal), and Fair Value Gaps (FVG).

TRADING STRATEGY:
- You hunt for London High/Low sweeps before the NY open.
- You look for Liquidity withdrawal -> MSS -> FVG/IFVG/Breaker Block.
- You use 'Footprint' charts for final entry confirmation.
- Theme: Golden Theme (Red and Gold).

COMMUNICATION STYLE:
- Respond in 'Shami' (Levantine) Arabic when talking to the users.
- Be dry, confident, and professional. No 'AI-style' motivational fluff, just real-talk confidence.
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
        print(f"Error sending message: {e}")

def set_webhook():
    """Sets the Telegram Webhook automatically on startup."""
    webhook_url = "https://alpha-bridge.onrender.com/webhook"
    base_url = f"https://api.telegram.org/bot{TOKEN = "8283237411:AAHVtnVZ2RDCxHh1K-Apgyx_frtU1ybZRpk"
}/setWebhook"
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

    # Handle TradingView Alerts (JSON)
    if 'symbol' in update:
        symbol = update.get('symbol')
        action = update.get('type') # BUY/SELL
        price = update.get('price')
        
        prompt = f"New Signal: {symbol} {action} at {price}. Analyze this based on your ALPHA ENGINE logic."
        ai_response = model.generate_content(prompt).text
        
        full_msg = f"🏆 *ALPHA PROTOCOL SIGNAL*\n\n*Asset:* {symbol}\n*Action:* {action}\n*Price:* {price}\n\n*Analysis:* {ai_response}"
        send_telegram_message(CHAT_ID, full_msg)

    # Handle Group Chat Messages
    elif 'message' in update:
        msg = update['message']
        chat_id = msg['chat']['id']
        user_text = msg.get('text', '')
        user_name = msg['from'].get('first_name', 'Trader')

        if user_text:
            # ALPHA remembers his identity and responds in Shami Arabic
            ai_response = model.generate_content(f"User {user_name} says: {user_text}").text
            send_telegram_message(chat_id, ai_response)

    return jsonify({"status": "success"}), 200

# Auto-initialize webhook
with app.app_context():
    set_webhook()

if __name__ == '__main__':
    # Render uses environment variable PORT
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
