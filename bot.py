import json
import telebot
import os
from flask import Flask
from threading import Thread

# --- SYSTÈME DE MAINTIEN POUR RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Le bot Westminster est opérationnel !"

def run():
    # Render définit automatiquement le PORT, sinon 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    """Lance le serveur web pour éviter que Render ne coupe le bot"""
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- CONFIGURATION DU BOT ---
# Utilise ton nouveau Token fourni
TOKEN = os.environ.get('BOT_TOKEN', '8603258933:AAHWXfleEXidGCfSFDKt4ZtjNq1h0m0kfkQ')
bot = telebot.TeleBot(TOKEN)

def charger_confession():
    """Charge le fichier JSON contenant le texte de Westminster"""
    try:
        base_dir = os.path.dirname(__file__)
        path = os.path.join(base_dir, 'confession.json')
        if not os.path.exists(path):
            print("Erreur : confession.json introuvable !")
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur de lecture : {e}")
        return {}

confession_data = charger_confession()

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip()
    
    # Gestion du nom du bot pour les groupes
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

    # Format de commande : Chapitre.Paragraphe (ex: 1.1)
    if '.' in clean_text:
        parts = clean_text.split('.')
        if len(parts) == 2:
            c_id = parts[0].strip()
            p_id = parts[1].strip()
            
            if c_id in confession_data and p_id in confession_data[c_id]:
                content = confession_data[c_id][p_id]
                # SIGNATURE MISE À JOUR POUR WESTMINSTER
                rep = f"« {content} »\n\n— Confession de foi de Westminster, {c_id}.{p_id}."
                bot.reply_to(message, rep)

if __name__ == "__main__":
    # Nettoyage des anciennes sessions et lancement
    bot.delete_webhook()
    keep_alive()
    print("🚀 Bot Westminster prêt !")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
