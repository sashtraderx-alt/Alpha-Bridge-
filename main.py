from flask import Flask, request
import requests

app = Flask(__name__)

# Private Data
TOKEN = "8283237411:AAEXrzeTIsd7LwVDBhNmkfwhvLwxDEYyFCc"
CHAT_ID = "6922836215"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        msg_type = data.get('type', 'Signal')
        emoji = "🟢" if "Buy" in msg_type else "🔴"
        
        msg = f"{emoji} *ALPHA SIGNAL*\n\n" \
              f"📥 *Type:* {msg_type}\n" \
              f"💰 *Price:* {data.get('price')}\n" \
              f"🎯 *TP:* {data.get('tp')}\n" \
              f"🛑 *SL:* {data.get('sl')}"
        
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except:
        pass
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
