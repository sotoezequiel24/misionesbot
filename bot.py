import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CallbackQueryHandler, CommandHandler

TOKEN = os.getenv("TOKEN")

# ===== WEB (para Railway) =====
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot activo"

def run_web():
    app_web.run(host='0.0.0.0', port=8080)

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
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="👋 Bienvenido a MisionesChat\n\nElegí tu zona:",
        reply_markup=menu_principal()
    )


# ===== BOTONES =====
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
            "Elegí tu zona 👇",
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

        app.run_polling()

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
    chat_id=update.effective_chat.id,
    text="👋 Bienvenido a MisionesChat\n\nElegí tu zona:",
    reply_markup=menu()
)


# ===== NUEVOS USUARIOS =====
async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.new_chat_members:
        await update.message.reply_text(
            "👋 Bienvenido/a a MisionesChat\n\nElegí tu zona 👇",
            reply_markup=menu_principal()
        )


# ===== BOTONES =====
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
            "Elegí tu zona 👇",
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


# ===== INICIO =====
if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERROR: Falta TOKEN")
    else:
        print("✅ Bot funcionando...")

        keep_alive()

        app = ApplicationBuilder().token(TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(ChatMemberHandler(new_member, ChatMemberHandler.CHAT_MEMBER))
        app.add_handler(CallbackQueryHandler(botones))

        app.run_polling()
