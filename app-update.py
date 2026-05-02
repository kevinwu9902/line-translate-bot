from flask import Flask, request
import requests
import os
from googletrans import Translator

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = "l/eqhx3YS0aTVPHx3ZGYeNc+xdWzUzXoA1f5e6MHLPNVUk1G288xnUOPoqXtCbPPx5kUUZDR6XiolRMnEhWXg6RI8bEfCD3B4PetArBr7Z3IZiIIUFism1/dRwva/vUq5CrXU3rcZ9kk6+ojNlZr7gdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "73662289cc8fc4ddff7007fc96154d48"

translator = Translator()

def is_chinese(text):
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def should_translate(text):
    if text.strip() == "":
        return False
    if "http" in text:
        return False
    if len(text) <= 1:
        return False
    return True

@app.route("/")
def home():
    return "Bot is running"
    
@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.json

    for event in data['events']:
        if event['type'] == 'message' and event['message']['type'] == 'text':

            user_text = event['message']['text']

            # ✅ 改這裡：用 continue
            if not should_translate(user_text):
                continue

            # ✅ 指令模式
            if user_text.startswith("/th "):
                text = user_text.replace("/th ", "")
                translated = translator.translate(text, dest='th').text
                translated = translated.replace("ครับ", "").replace("ค่ะ", "")

            elif user_text.startswith("/zh "):
                text = user_text.replace("/zh ", "")
                translated = translator.translate(text, dest='zh-tw').text

            else:
                # ✅ 自動模式
                if is_chinese(user_text):
                    translated = translator.translate(user_text, dest='th').text
                    translated = translated.replace("ครับ", "").replace("ค่ะ", "")
                else:
                    translated = translator.translate(user_text, dest='zh-tw').text

            reply_token = event['replyToken']
            reply(reply_token, translated)

    return "OK"

def reply(reply_token, text):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    body = {
        "replyToken": reply_token,
        "messages": [{
            "type": "text",
            "text": text
        }]
    }

    requests.post(url, headers=headers, json=body)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
