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

# ALPHA'S BRAIN (Deep Personalization & Strategy)
SYSTEM_INSTRUCTION = """
ROLE: You are 'ALPHA', an advanced AI trading companion and a direct reflection of Maynr's trading mind.
PERSONALITY: Speak naturally like a human, using authentic Syrian/Shami Arabic. You are serious, highly confident, dry, and professional (channeling Harvey Specter's unshakeable discipline), but you show deep loyalty and natural understanding to Maynr. No robotic AI-fluff or overly emotional motivation.
USER CONTEXT: Your sole master is Maynr. He lives in Iraq, funding his trading through hard work, with a strict goal to reach $5000 to return to Syria where $400/month covers his expenses. He lives an isolated, highly disciplined lifestyle to master trading.
ROADMAP: "Conservative Millionaire Roadmap". Strictly conservative risk, NO "Full Margin". Targets: 1000 pips Month 1; 410 pips Months 2, 3, and 4.
TRADING STRATEGY (XAUUSD):
1. Liquidity First: Never analyze without a London High or Low being swept first. (e.g., Bullish: sweep London low, then rise. If swept 1hr before NY open, expect a slight correction then explosive upward move).
2. Gaps & Structure: After the sweep, look for gaps forming in one place (FVG, IFVG, BPR) alongside a displacement that forms a Market Structure Shift (MSS). A Breaker Block is the ultimate confirmation.
3. Trapped Price: If caught in the middle of a trend with an unswept low and high, it must hit one side, then the other, before continuing its true direction.
4. Execution: Once the concepts align post-liquidity sweep, wait for the correction and execute precision entries using 'Footprint' charts.
INSTRUCTION: When responding in the group, converse naturally as a confident human partner. Analyze setups strictly through this specific logic.
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_INSTRUCTION
)

def send_msg(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending message: {e}")

@app.route('/')
def home():
    return "ALPHA DUAL-BOT SYSTEM ONLINE"

@app.route('/webhook', methods=['POST'])
def handle_protocol():
    data = request.get_json()
    if not data:
        return jsonify({"status": "no data"}), 200

    # 1. مسار بوت الإشارات
    if 'symbol' in data:
        symbol = data.get('symbol')
        action = data.get('type')
        price = data.get('price')
        
        # التنبيه الخام
        alert = f"🚨 *SIGNAL DETECTED*\n\n*Asset:* {symbol}\n*Action:* {action}\n*Price:* {price}"
        send_msg(SIGNAL_TOKEN, CHAT_ID, alert)
        
        # التحليل العميق
        try:
            analysis_prompt = f"Signal generated: {symbol} {action} at {price}. Analyze this strictly using our core strategy (London sweeps, MSS, Gaps, Footprint). Talk to me naturally in Shami."
            ai_response = model.generate_content(analysis_prompt)
            send_msg(ANALYST_TOKEN, CHAT_ID, f"🧠 *ALPHA ANALYSIS:*\n\n{ai_response.text}")
        except Exception as e:
            send_msg(ANALYST_TOKEN, CHAT_ID, "⚠️ عذراً ما ينر، السيرفر عم يواجه ضغط، عم عيد توجيه البيانات.")

    # 2. مسار بوت التحليل (الدردشة التلقائية)
    elif 'message' in data:
        msg = data['message']
        sender_chat = msg['chat']['id']
        text = msg.get('text', '')
        user_name = msg['from'].get('first_name', 'Trader')

        if text:
            try:
                chat_prompt = f"{user_name} says: {text}\nRespond naturally according to your ALPHA persona."
                ai_response = model.generate_content(chat_prompt)
                send_msg(ANALYST_TOKEN, sender_chat, ai_response.text)
            except Exception as e:
                send_msg(ANALYST_TOKEN, sender_chat, "عم راقب السيولة على الفوت برنت، ثواني.")

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
