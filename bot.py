import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    ChatMemberHandler
)

# ===== TOKEN =====
TOKEN = os.getenv("TOKEN")

# ===== WEB (Railway) =====
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot activo"

def run_web():
    app_web.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    Thread(target=run_web).start()

# ===== MENÚ =====
def menu_principal():
    keyboard = [
        [
            InlineKeyboardButton("🟣 Zona Capital", callback_data="capital"),
            InlineKeyboardButton("🟢 Zona Sur", callback_data="sur")
        ],
        [
            InlineKeyboardButton("🟡 Zona Norte", callback_data="norte"),
            InlineKeyboardButton("🟠 Zona Este", callback_data="este")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.effective_user.first_name or "amigo"

    text = (
        f"👋 ¡Hola {nombre}!\n\n"
        "Bienvenido/a a MisionesChat.\n\n"
        "Este bot es el acceso a los grupos por zona.\n\n"
        "📍 Elegí tu zona para unirte:\n"
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=menu_principal()
    )

# ===== BOTONES =====
async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    links = {
        "capital": ("🟣 Zona Capital\nPosadas, Garupá, Fachinal", "https://t.me/misioneschatzonacapital"),
        "sur": ("🟢 Zona Sur\nCandelaria, Santa Ana, Apóstoles", "https://t.me/misioneschatzonasur"),
        "norte": ("🟡 Zona Norte\nEldorado, Montecarlo, Iguazú", "https://t.me/misioneschatzonanorte"),
        "este": ("🟠 Zona Este\nSan Pedro, Irigoyen, San Antonio", "https://t.me/misioneschatzonaeste")
    }

    if data == "volver":
        await query.edit_message_text(
            "👇 Seleccioná tu zona:",
            reply_markup=menu_principal()
        )
        return

    texto, link = links.get(data, ("Error", "#"))

    keyboard = [
        [InlineKeyboardButton("✅ Unirme", url=link)],
        [InlineKeyboardButton("⬅️ Volver", callback_data="volver")]
    ]

    await query.edit_message_text(
        texto,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===== NUEVOS MIEMBROS =====
async def nuevo_miembro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    old = update.chat_member.old_chat_member.status
    new = update.chat_member.new_chat_member.status

    # Detecta cuando alguien entra
    if old in ["left", "kicked"] and new == "member":
        user = update.chat_member.new_chat_member.user
        nombre = user.first_name or "amigo"

        text = (
            f"👋 ¡Hola {nombre}!\n\n"
            "Este grupo es solo de acceso.\n\n"
            "📍 Usá el bot para elegir tu zona:\n"
            "👉 Escribí /start\n\n"
            "⚠️ Los chats están separados por zona."
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text
        )

# ===== INICIO =====
if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERROR: Falta TOKEN")
    else:
        print("✅ Bot funcionando...")

        keep_alive()

        app = ApplicationBuilder().token(TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(botones))
        app.add_handler(ChatMemberHandler(nuevo_miembro, ChatMemberHandler.CHAT_MEMBER))

        app.run_polling()
