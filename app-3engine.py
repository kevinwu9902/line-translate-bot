from flask import Flask, request
import requests
import os, re, time, random
from deep_translator import GoogleTranslator, MyMemoryTranslator

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.getenv("l/eqhx3YS0aTVPHx3ZGYeNc+xdWzUzXoA1f5e6MHLPNVUk1G288xnUOPoqXtCbPPx5kUUZDR6XiolRMnEhWXg6RI8bEfCD3B4PetArBr7Z3IZiIIUFism1/dRwva/vUq5CrXU3rcZ9kk6+ojNlZr7gdB04t89/1O/w1cDnyilFU=")
CHANNEL_SECRET = os.getenv("73662289cc8fc4ddff7007fc96154d48")

# ===== 快取 =====
cache = {}

# ===== 判斷語言 =====
def detect_language(text):
    if re.search(r'[\u0E00-\u0E7F]', text):
        return "th"
    elif re.search(r'[\u4E00-\u9FFF]', text):
        return "zh-TW"
    return None

# ===== 是否需要翻譯 =====
def should_translate(text):
    if text.strip() == "":
        return False
    if "http" in text:
        return False
    if len(text) <= 1:
        return False
    return True

# ===== LibreTranslate（第三引擎）=====
def libre_translate(text, source, target):
    try:
        url = "https://libretranslate.de/translate"
        payload = {
            "q": text,
            "source": source,
            "target": target,
            "format": "text"
        }
        r = requests.post(url, data=payload, timeout=5)
        return r.json()["translatedText"]
    except:
        return None

# ===== 三引擎翻譯 =====
def smart_translate(text, source, target):

    key = f"{source}:{target}:{text}"
    if key in cache:
        return cache[key]

    time.sleep(random.uniform(0.8, 1.5))

    # 1️⃣ Google
    try:
        result = GoogleTranslator(source=source, target=target).translate(text)
        cache[key] = result
        return result
    except:
        pass

    # 2️⃣ MyMemory
    try:
        result = MyMemoryTranslator(source=source, target=target).translate(text)
        cache[key] = result
        return result
    except:
        pass

    # 3️⃣ LibreTranslate
    result = libre_translate(text, source, target)
    if result:
        cache[key] = result
        return result

    return None

@app.route("/")
def home():
    return "Bot is running"

@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.json

    for event in data['events']:
        if event['type'] == 'message' and event['message']['type'] == 'text':

            user_text = event['message']['text']

            if not should_translate(user_text):
                continue

            # ===== 指令模式 =====
            if user_text.startswith("/th "):
                text = user_text.replace("/th ", "")
                translated = smart_translate(text, "zh-TW", "th")

            elif user_text.startswith("/zh "):
                text = user_text.replace("/zh ", "")
                translated = smart_translate(text, "th", "zh-TW")

            else:
                # ===== 自動模式 =====
                source_lang = detect_language(user_text)

                if source_lang == "zh-TW":
                    translated = smart_translate(user_text, "zh-TW", "th")
                elif source_lang == "th":
                    translated = smart_translate(user_text, "th", "zh-TW")
                else:
                    continue

            if not translated:
                continue

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
