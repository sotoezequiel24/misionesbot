import os
import random
import asyncio
import logging
from flask import Flask
from threading import Thread

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

# ===== LOGS =====
logging.basicConfig(level=logging.INFO)

# ===== TOKEN =====
TOKEN = os.getenv("TOKEN")

# ===== WEB (Railway) =====
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "🔥 Bot activo"

def run_web():
    app_web.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    Thread(target=run_web).start()

# ===== MENÚ ZONAS =====
def menu_principal():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🟣 Zona Capital", callback_data="capital"),
         InlineKeyboardButton("🟢 Zona Sur", callback_data="sur")],
        [InlineKeyboardButton("🟡 Zona Norte", callback_data="norte"),
         InlineKeyboardButton("🟠 Zona Centro", callback_data="centro")]
    ])

# ===== LINKS =====
links = {
    "capital": "https://t.me/misioneschatzonacapital",
    "sur": "https://t.me/+xqgDIa4CdDU1ZGQ5",
    "norte": "https://t.me/misioneschatzonanorte",
    "centro": "https://t.me/misioneschatzonacentro"
}

# ===== TEXTOS =====
textos = {
    "capital": "🟣 Zona Capital\n\n📍 Posadas, Garupá, Candelaria",
    "sur": "🟢 Zona Sur\n\n🔥 Unite al grupo de tu zona",
    "norte": "🟡 Zona Norte\n\n🔥 Unite al grupo de tu zona",
    "centro": "🟠 Zona Centro\n\n🔥 Unite al grupo de tu zona"
}

# ===== JUEGOS =====
adivinar_juego = {}
ahorcado_juego = {}
palabras = ["misiones", "posadas", "iguazu"]

# ===== CHAT GLOBAL =====
chat_id_global = None

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global chat_id_global
    chat_id_global = update.effective_chat.id

    await update.message.reply_text(
        "📍 Elegí tu zona:",
        reply_markup=menu_principal()
    )

# ===== BOTONES =====
async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "volver":
        await q.edit_message_text("📍 Elegí tu zona:", reply_markup=menu_principal())
        return

    await q.edit_message_text(
        textos[q.data],
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Unirme", url=links[q.data])],
            [InlineKeyboardButton("⬅️ Volver", callback_data="volver")]
        ])
    )

# ===== AUTO MENSAJE =====
async def mensaje_automatico(context: ContextTypes.DEFAULT_TYPE):
    if chat_id_global:
        mensajes = [
            "😏 ¿Aburrido?\n🎯 /adivinar\n🎮 /ahorcado",
            "🔥 Che activen un juego!\n🎲 /dado",
            "🤖 Usá /start para ver zonas"
        ]

        await context.bot.send_message(
            chat_id=chat_id_global,
            text=random.choice(mensajes)
        )

# ===== JUEGOS =====
async def adivinar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    adivinar_juego[user] = random.randint(1, 10)
    await update.message.reply_text("🎯 Adiviná número (1-10)")

async def ahorcado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    palabra = random.choice(palabras)

    ahorcado_juego[user] = {
        "palabra": palabra,
        "progreso": ["_"] * len(palabra)
    }

    await update.message.reply_text("🎮 " + " ".join(ahorcado_juego[user]["progreso"]))

async def dado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🎲 Salió: {random.randint(1,6)}")

# ===== MENSAJES =====
async def mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()
    user = update.effective_user.id

    # 🎯 ADIVINAR
    if user in adivinar_juego:
        try:
            n = int(texto)
            real = adivinar_juego[user]

            if n == real:
                await update.message.reply_text("🎉 Ganaste")
                del adivinar_juego[user]
            elif n < real:
                await update.message.reply_text("🔼 Más alto")
            else:
                await update.message.reply_text("🔽 Más bajo")
            return
        except:
            pass

    # 🎮 AHORCADO
    if user in ahorcado_juego and len(texto) == 1:
        juego = ahorcado_juego[user]

        for i, l in enumerate(juego["palabra"]):
            if l == texto:
                juego["progreso"][i] = texto

        estado = " ".join(juego["progreso"])

        if "_" not in juego["progreso"]:
            await update.message.reply_text(f"🎉 Era {juego['palabra']}")
            del ahorcado_juego[user]
        else:
            await update.message.reply_text("🎮 " + estado)
        return

    # 🤖 IA SIMPLE
    if "hola" in texto:
        await update.message.reply_text("👋 Hola!")
    elif "aburrido" in texto:
        await update.message.reply_text("😏 Jugá:\n/adivinar\n/ahorcado\n/dado")

# ===== MAIN =====
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("adivinar", adivinar))
    app.add_handler(CommandHandler("ahorcado", ahorcado))
    app.add_handler(CommandHandler("dado", dado))

    app.add_handler(CallbackQueryHandler(botones))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensajes))

    # ⏱ cada 20 min
    app.job_queue.run_repeating(mensaje_automatico, interval=1200, first=30)

    print("🔥 BOT FUNCIONANDO 24/7")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(60)

# ===== RUN =====
if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
