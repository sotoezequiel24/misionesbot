import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters
)
from flask import Flask
from threading import Thread

# ===== TOKEN =====
TOKEN = os.getenv("TOKEN")

# ===== WEB (Keep Alive) =====
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

# ===== SALUDO NUEVOS MIEMBROS =====
async def saludar_nuevo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("🟢 Evento de nuevo miembro recibido")  # Debug: ver si llega la actualización
    if not update.message or not update.message.new_chat_members:
        print("❌ No hay nuevos miembros")
        return

    for user in update.message.new_chat_members:
        nombre = user.first_name or "amigo"
        print(f"👤 Nuevo miembro detectado: {nombre}")  # Debug: nombre recibido

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

        # Handler solo para nuevos miembros
        app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, saludar_nuevo))

        # Ejecuta el bot
        app.run_polling()
