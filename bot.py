import json
import telebot
import os
from flask import Flask
from threading import Thread

# --- SYSTÈME DE MAINTIEN POUR RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Le bot est opérationnel !"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- CONFIGURATION DU BOT ---
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

def charger_confession():
    try:
        base_dir = os.path.dirname(__file__)
        path = os.path.join(base_dir, 'confession.json')
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

confession_data = charger_confession()

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip()
    try:
        me = bot.get_me()
        bot_username = f"@{me.username}"
    except:
        bot_username = ""
    
    is_group = message.chat.type in ['group', 'supergroup']
    if is_group:
        if bot_username in text:
            clean_text = text.replace(bot_username, "").strip()
        else:
            return
    else:
        clean_text = text

    if '.' in clean_text:
        parts = clean_text.split('.')
        if len(parts) == 2:
            c_id = parts[0].strip()
            p_id = parts[1].strip()
            if c_id in confession_data and p_id in confession_data[c_id]:
                # LA LIGNE MODIFIÉE CI-DESSOUS
                rep = f"« {confession_data[c_id][p_id]} »\n\n— Confession de foi baptiste de Londres de 1689, {c_id}.{p_id}."
                bot.reply_to(message, rep)

if __name__ == "__main__":
    bot.delete_webhook()
    keep_alive()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
