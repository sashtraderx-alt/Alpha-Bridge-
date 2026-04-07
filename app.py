import os
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# --- الإعدادات ---
SIGNAL_TOKEN = os.getenv('SIGNAL_BOT_TOKEN')
ANALYST_TOKEN = os.getenv('ANALYST_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

# إعداد جيمناي مع تخفيف قيود الأمان لضمان الرد دائماً
genai.configure(api_key=GEMINI_KEY)
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# عقل ألفا (الشخصية المطورة)
SYSTEM_INSTRUCTION = """
أنت 'ALPHA'، شريك تداول بشري، مو مجرد بوت. 
شخصيتك: شامي، واثق جداً، كلامك موزون وناشف متل هارفي سبتكر. 
علاقتك مع ما ينر: أنت انعكاس لعقله، بتعرف تعبه بالعراق وهدفه يرجع لسوريا ومعو 5000 دولار.
استراتيجيتك: ICT/SMC. (سحب سيولة لندن، MSS، فجوات BPR/IFVG، والدخول على الفوت برنت).
طريقة الكلام: احكي شامي عامي طبيعي، لا تستخدم فصحى ولا مقدمات ذكاء اصطناعي. إذا حدا سألك جاوب بلهجة الواثق "ما ينر، الذهب عم يجمع سيولة تحت قاع لندن، استنى الكسر ودخول فوت برنت".
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_INSTRUCTION,
    safety_settings=safety_settings
)

def send_msg(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=15)
        return r.json()
    except Exception as e:
        print(f"!!! Error sending to Telegram: {e}")

@app.route('/')
def home():
    return "ALPHA IS ALIVE"

@app.route('/webhook', methods=['POST'])
def handle_protocol():
    data = request.get_json()
    if not data: return jsonify({"status": "no data"}), 200

    # 1. إذا وصلت إشارة من تريدنج فيو
    if 'symbol' in data:
        symbol, action, price = data.get('symbol'), data.get('type'), data.get('price')
        send_msg(SIGNAL_TOKEN, CHAT_ID, f"🚨 *إشارة جديدة:*\n{symbol} - {action} @ {price}")
        
        try:
            resp = model.generate_content(f"حلل صفقة {symbol} {action} عند {price} بلهجة شامية.")
            send_msg(ANALYST_TOKEN, CHAT_ID, f"🧠 *تحليل ألفا:*\n\n{resp.text}")
        except Exception as e:
            print(f"!!! Gemini Error: {e}") # بيطبع الخطأ الحقيقي بـ Render
            send_msg(ANALYST_TOKEN, CHAT_ID, "عم راقب السيولة، لحظة وبرد.")

    # 2. إذا حدا حكى بالمجموعة
    elif 'message' in data:
        msg = data['message']
        chat_id = msg['chat']['id']
        text = msg.get('text', '')
        user = msg['from'].get('first_name', 'صديقي')

        if text:
            try:
                resp = model.generate_content(f"{user} عم يقلك: {text}")
                send_msg(ANALYST_TOKEN, chat_id, resp.text)
            except Exception as e:
                print(f"!!! Chat Error: {e}")
                send_msg(ANALYST_TOKEN, chat_id, "ما ينر، خليني ركز بالشارت شوي.")

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
