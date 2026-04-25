from flask import Flask, request, abort
import requests
import os
from googletrans import Translator

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = "RoLCYHJJ/WmzbpNvvvUK5XNlZLWoP/DH7VwNloZTkeLzcZNQ5GQ/j985g0bvt6WNx5kUUZDR6XiolRMnEhWXg6RI8bEfCD3B4PetArBr7Z25CcNZTZo2ZEE3/5AW/JX2aDqRFHX92ddy2uMVUaUvTgdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "73662289cc8fc4ddff7007fc96154d48"

translator = Translator()

# ✅ 放在外面（不要放在 webhook 裡）
def is_chinese(text):
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.json
    
    for event in data['events']:
        if event['type'] == 'message':
            if event['message']['type'] == 'text':
                
                user_text = event['message']['text']
                
                # ✅ 正確翻譯邏輯
                if is_chinese(user_text):
                    translated = translator.translate(user_text, dest='th').text
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
