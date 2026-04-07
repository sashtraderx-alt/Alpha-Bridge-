import os
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# الإعدادات
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_KEY)

system_instruction = """
أنت 'ALPHA'، متداول محترف، إنسان طبيعي، فكاهي لكن جاد جداً وقت الشغل. 
أنت الآن في مجموعة تداول مع شباب محترفين. تفاعل معهم كصديق خبير.
استراتيجيتك: ICT (سيولة لندن، FVG، MSS، Breaker Blocks).
تأكيدك: Footprint و Order Flow.
تعليماتك: إذا سألك أحد عن صفقة أو شارت، حلل له بعمق وبشخصية ALPHA.
اضحك معهم، ازعل على الصفقات الخاسرة، وكن واثقاً بنفسك.
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=system_instruction
)

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route('/')
def home():
    return "ALPHA Group Bot is Active."

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    update = request.json
    
    # 1. التعامل مع تنبيهات TradingView (JSON)
    if 'symbol' in update:
        symbol = update.get('symbol', 'Unknown')
        trade_type = update.get('type', 'Signal')
        price = update.get('price', 'N/A')
        
        prompt = f"وصلت إشارة دخول: {symbol} {trade_type} عند {price}. تفاعل معها وحللها بناءً على السيولة والفوتبرينت."
        ai_response = model.generate_content(prompt).text
        
        message = f"♦️ ALPHA PROTOCOL ♦️\n━━━━━━━━━━━━━━━\nAsset: {symbol}\nAction: {trade_type}\nPrice: {price}\n━━━━━━━━━━━━━━━\n\n{ai_response}"
        send_telegram_message(CHAT_ID, message)
        return jsonify({"status": "success"}), 200

    # 2. التعامل مع رسائل الدردشة في المجموعة
    if 'message' in update:
        msg = update['message']
        chat_id = msg['chat']['id']
        user_text = msg.get('text', '')
        user_name = msg['from'].get('first_name', 'صديقي')

        # الرد فقط إذا تم ذكر اسم البوت أو الرد على رسالته (أو برمجته للرد على الكل)
        if user_text:
            ai_response = model.generate_content(f"المتداول {user_name} يقول: {user_text}").text
            send_telegram_message(chat_id, ai_response)

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
