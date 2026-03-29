import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
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


# ===== MENÚ PRINCIPAL =====
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


# ===== MENÚ BOTONES =====
async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    links = {
        "capital": ("🟣 Zona Capital\n\nPosadas, Garupá, Fachinal", "https://t.me/misioneschatzonacapital"),
        "sur": ("🟢 Zona Sur\n\nCandelaria, Santa Ana, Apóstoles", "https://t.me/misioneschatzonasur"),
        "norte": ("🟡 Zona Norte\n\nEldorado, Montecarlo, Iguazú", "https://t.me/misioneschatzonanorte"),
        "este": ("🟠 Zona Este\n\nSan Pedro, Irigoyen, San Antonio", "https://t.me/misioneschatzonaeste")
    }

    if data == "volver":
        await query.edit_message_text(
            "👇 Seleccioná tu zona:",
            reply_markup=menu_principal()
        )
        return

    texto, link = links.get(data, ("Error", "#"))

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Unirme", url=link)],
        [InlineKeyboardButton("⬅️ Volver", callback_data="volver")]
    ])

    await query.edit_message_text(texto, reply_markup=keyboard)


# ===== SALUDO AUTOMÁTICO NUEVOS MIEMBROS =====
async def saludar_nuevo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Solo saluda si alguien nuevo pasó a ser miembro
    if update.chat_member.new_chat_member.status == "member":
        user = update.chat_member.new_chat_member.user
        nombre = user.first_name or "amigo"
        text = (
            f"👋 ¡Hola {nombre}!\n\n"
            "Bienvenido/a a MisionesChat.\n\n"
            "📍 Seleccioná tu zona para unirte al grupo correspondiente:"
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=menu_principal()
        )


# ===== COMANDO /START PRIVADO =====
async def start_comando(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.effective_user.first_name or "amigo"
    text = (
        f"👋 ¡Hola {nombre}!\n\n"
        "Bienvenido/a a MisionesChat.\n\n"
        "📍 Seleccioná tu zona para unirte al grupo correspondiente:"
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=menu_principal()
    )


# ===== INICIO =====
if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERROR: Falta TOKEN")
    else:
        print("✅ Bot funcionando...")
        keep_alive()

        app = ApplicationBuilder().token(TOKEN).build()

        # Handlers
        app.add_handler(CommandHandler("start", start_comando))
        app.add_handler(CallbackQueryHandler(botones))
        app.add_handler(ChatMemberHandler(saludar_nuevo, ChatMemberHandler.CHAT_MEMBER))

        # Ejecuta el bot
        app.run_polling()
