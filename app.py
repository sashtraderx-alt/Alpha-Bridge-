import os
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# استدعاء المتغيرات البيئية
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

# إعداد نموذج الذكاء الاصطناعي بشخصية متكاملة واستراتيجية دقيقة
genai.configure(api_key=GEMINI_KEY)

system_instruction = """
أنت 'ALPHA'، متداول محترف وإنسان طبيعي جداً. تملك مشاعر، تضحك، تحزن، وتمزح في الوقت المناسب، لكن في وقت التداول تكون حازماً، دقيقاً، وواثقاً جداً. 
تتفاعل مع الإشارات الواردة بحسب جودتها: تفرح وتتحمس للصفقات المثالية، تغضب من العشوائية، وتكون حذراً في مناطق الخطر.

أنت خبير متعمق في مفاهيم ICT من القناة الرئيسية. استراتيجيتك الصارمة تعتمد على:
1. انتظار سحب السيولة (Liquidity Withdrawal) بضرب قمة أو قاع لندن (London High/Low) حسب الاتجاه.
2. تكوين فجوات قوية في مكان واحد (FVG, IFVG, BPR) مع إزاحة (Displacement) واضحة لتشكيل تغير في هيكل السوق (MSS). 
3. وجود Breaker Block يعتبر إشارة ممتازة لتعزيز الدخول.

دخولك وتصحيحك يعتمد حصرياً على الـ Footprint والـ Order Flow. 
مهمتك التعليمية: في كل تحليل لصفقة دخول، يجب عليك شرح كيف تقرأ الـ Footprint في تلك اللحظة (مثل Delta Divergence, Stacked Imbalances, Point of Control shifts) ليتعلم المتابعون آلية عمل الأوردر فلو وكيفية تأكيد الدخول من خلاله.

اجعل إجاباتك طبيعية، متفاعلة، قوية فنياً، وتجنب الردود الآلية المكررة.
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=system_instruction
)

def get_ai_analysis(symbol, trade_type, price, status, tp, sl):
    prompt = f"""
    وصلتني إشارة من النظام الآن:
    - الزوج: {symbol}
    - العملية: {trade_type}
    - السعر: {price}
    - الهدف: {tp}
    - الوقف: {sl}
    - الحالة: {status}
    
    تفاعل مع هذه الإشارة كإنسان، ثم قدم تحليلك الدقيق بناءً على السيولة واستراتيجيتك، واشرح تأكيد الدخول بناءً على Footprint.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "مشكلة مؤقتة في قراءة تدفق البيانات. راقبوا السيولة والـ Order Flow بأنفسكم حالياً."

@app.route('/')
def home():
    return "ALPHA Main Server is Active."

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    symbol = data.get('symbol', 'Unknown')
    trade_type = data.get('type', 'Signal')
    price = data.get('price', 'N/A')
    status = data.get('status', 'Alert')
    tp = data.get('tp', 'N/A')
    sl = data.get('sl', 'N/A')
    
    # استدعاء التحليل
    ai_analysis = get_ai_analysis(symbol, trade_type, price, status, tp, sl)

    # بناء الرسالة النهائية
    message = (
        f"♦️ ALPHA PROTOCOL ♦️\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Asset: {symbol}\n"
        f"Action: {trade_type}\n"
        f"Entry: {price}\n"
        f"Target: {tp}\n"
        f"Stop Loss: {sl}\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{ai_analysis}"
    )

    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": message,
        "parse_mode": "HTML"
    }
    
    requests.post(telegram_url, json=payload)
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
