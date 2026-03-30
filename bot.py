import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    ChatMemberHandler
)

TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app_web = Flask(__name__)

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
        "📍 Elegí tu zona para unirte al grupo:"
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

    links = {
        "capital": ("🟣 Zona Capital", "https://t.me/misioneschatzonacapital"),
        "sur": ("🟢 Zona Sur", "https://t.me/misioneschatzonasur"),
        "norte": ("🟡 Zona Norte", "https://t.me/misioneschatzonanorte"),
        "este": ("🟠 Zona Este", "https://t.me/misioneschatzonaeste")
    }

    data = query.data

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

    if old in ["left", "kicked"] and new == "member":
        user = update.chat_member.new_chat_member.user
        nombre = user.first_name or "amigo"

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"👋 ¡Hola {nombre}! Usá el bot 👉 /start para elegir tu zona"
        )

# ===== APP TELEGRAM =====
application = ApplicationBuilder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(botones))
application.add_handler(ChatMemberHandler(nuevo_miembro, ChatMemberHandler.CHAT_MEMBER))

# ===== WEBHOOK ROUTE =====
@app_web.route("/", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "ok"

# ===== CONFIGURAR WEBHOOK =====
async def set_webhook():
    await application.bot.set_webhook(url=WEBHOOK_URL)

# ===== INICIO =====
if __name__ == "__main__":
    if not TOKEN or not WEBHOOK_URL:
        print("❌ Falta TOKEN o WEBHOOK_URL")
    else:
        print("🚀 Bot con WEBHOOK activo")

        # Configura webhook correctamente (async)
        asyncio.run(set_webhook())

        # Ejecuta servidor Flask
        app_web.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
