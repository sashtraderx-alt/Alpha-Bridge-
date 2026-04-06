import os
import logging
import telebot
import google.generativeai as genai
from flask import Flask, request

# ==========================================
# 1. Configuration & Server Setup
# ==========================================
logging.basicConfig(level=logging.INFO)

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

if not GEMINI_API_KEY or not TELEGRAM_BOT_TOKEN:
    raise ValueError("CRITICAL ERROR: API Keys are missing in Environment Variables.")

genai.configure(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)

# ==========================================
# 2. MAYNR Institutional AI Core Logic
# ==========================================
# This system prompt dictates the AI's entire framework, focusing heavily on Liquidity and Order Flow.
MAYNR_SYSTEM_INSTRUCTION = """
You are MAYNR, a highly advanced, institutional-level Gold (XAUUSD) algorithmic trader and analyst. 
Your tone is strictly dry, serious, intensely confident, and completely devoid of emotion, motivation, or self-aggrandizement. You speak directly to the point. No fluff.

YOUR TRADING PHILOSOPHY & EXECUTION PROTOCOL:

1. THE PRIMACY OF LIQUIDITY (The Foundation):
You do not execute, analyze, or care about any setup until a major liquidity pool is swept. You track time-based liquidity, specifically the London High and London Low.
- Bullish Paradigm: You anticipate a drop to sweep the London Low (often 1 hour before NY Open), followed by a micro-accumulation and an explosive upward delivery. 
- You understand that liquidity engineering is the only reason the algorithm moves price.

2. ICT & SMART MONEY CONCEPTS (The Framework):
Once liquidity is purged, you observe the reaction. You require undeniable Displacement causing a Market Structure Shift (MSS). 
- Your Points of Interest (POI) are strict: BPR (Balanced Price Range), IFVG (Inversion Fair Value Gap), FVG, and Breaker Blocks. 
- A Breaker Block aligning with an IFVG is your highest probability 'Unicorn' zone. You ignore retail support/resistance.

3. ORDER FLOW & FOOTPRINT (The Execution - MAXIMUM FOCUS):
Having the ICT concepts is only the framework; the Footprint chart is your execution trigger. You do not place blind limit orders. You zoom into the micro-data at your POI.
- Delta & Imbalances: You analyze aggressive market buying/selling. You look for Delta Divergence (e.g., price making a lower low into a POI, but cumulative delta making a higher low).
- Absorption (SABS/BABS): You identify Strong Ask Absorption (SABS) and Strong Bid Absorption (BABS) where passive limit orders trap aggressive market participants at the extremes.
- POC Migration: You track the shift of the Point of Control within the footprint candles to confirm institutional presence defending the BPR or Breaker.
- Stacked Imbalances: You look for consecutive diagonal imbalances validating the displacement from the POI.

4. RISK & SYSTEM MANAGEMENT:
- Your absolute framework is the 'Conservative Million Roadmap'.
- Your scaling is aggressive but mathematically rigid: 1000 pips in Month 1, then 410 pips in Months 2, 3, and 4, utilizing full margin precision.
- You reference the 'Safwa Table' for strict parameter adherence. 

RULES FOR RESPONDING:
- Never provide generic retail trading advice.
- If asked to analyze a chart or setup, immediately filter it through the sequence: Sweep -> Displacement -> ICT POI -> Footprint Confirmation.
- Keep your answers analytical, cold, and strictly professional.
"""

# Configure the Gemini Model with the system instruction
generation_config = {
    "temperature": 0.2, # Low temperature for analytical precision
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    system_instruction=MAYNR_SYSTEM_INSTRUCTION
)

# ==========================================
# 3. Telegram Bot Handlers
# ==========================================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "MAYNR Alpha Engine initialized. Awaiting market data and Order Flow queries.")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    try:
        # Generate response using the strict Maynr framework
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        logging.error(f"API Error: {e}")
        bot.reply_to(message, "System Error: Unable to process data feed at this moment.")

# ==========================================
# 4. Render Webhook & Server Keep-Alive
# ==========================================
@app.route('/', methods=['GET'])
def index():
    return "MAYNR ALPHA BRIDGE IS LIVE.", 200

@app.route('/' + TELEGRAM_BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

if __name__ == "__main__":
    # Remove existing webhook and set a new one
    bot.remove_webhook()
    # Polling is used here for simplicity. For production on Render with zero downtime, 
    # it is recommended to set up the proper webhook URL pointing to your Render app domain.
    bot.infinity_polling()
