import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, ChatMemberHandler, CallbackQueryHandler

TOKEN = os.getenv("TOKEN")


def menu_principal():
    keyboard = [
        [
            InlineKeyboardButton("🟣 Zona Capital", callback_data="capital"),
            InlineKeyboardButton("🟢 Zona Sur", callback_data="sur")
        ],
        [
            InlineKeyboardButton("🔵 Zona Centro", callback_data="centro"),
            InlineKeyboardButton("🟡 Zona Norte", callback_data="norte")
        ],
        [
            InlineKeyboardButton("🟠 Zona Este", callback_data="este")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        await update.message.reply_text(
            "👋 ¡Bienvenido/a a MisionesChat!\n\nElegí tu zona 👇",
            reply_markup=menu_principal()
        )


async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "capital":
        texto = "🟣 Zona Capital\n\nIncluye:\n• Posadas\n• Garupá\n• Fachinal"
        keyboard = [
            [InlineKeyboardButton("✅ Unirme", url="https://t.me/MisionesChatCapital")],
            [InlineKeyboardButton("⬅️ Volver", callback_data="volver")]
        ]

    elif query.data == "sur":
        texto = "🟢 Zona Sur\n\nIncluye:\n• Candelaria\n• Santa Ana\n• Apóstoles\n• San José"
        keyboard = [
            [InlineKeyboardButton("✅ Unirme", url="https://t.me/MisionesChatSur")],
            [InlineKeyboardButton("⬅️ Volver", callback_data="volver")]
        ]

    elif query.data == "centro":
        texto = "🔵 Zona Centro\n\nIncluye:\n• Oberá\n• Cerro Azul\n• Campo Viera\n• San Vicente"
        keyboard = [
            [InlineKeyboardButton("✅ Unirme", url="https://t.me/MisionesChatCentro")],
            [InlineKeyboardButton("⬅️ Volver", callback_data="volver")]
        ]

    elif query.data == "norte":
        texto = "🟡 Zona Norte\n\nIncluye:\n• Eldorado\n• Montecarlo\n• Iguazú"
        keyboard = [
            [InlineKeyboardButton("✅ Unirme", url="https://t.me/MisionesChatNorte")],
            [InlineKeyboardButton("⬅️ Volver", callback_data="volver")]
        ]

    elif query.data == "este":
        texto = "🟠 Zona Este\n\nIncluye:\n• Irigoyen\n• San Antonio\n• San Pedro"
        keyboard = [
            [InlineKeyboardButton("✅ Unirme", url="https://t.me/MisionesChatEste")],
            [InlineKeyboardButton("⬅️ Volver", callback_data="volver")]
        ]

    elif query.data == "volver":
        await query.edit_message_text(
            "Elegí tu zona 👇",
            reply_markup=menu_principal()
        )
        return

    await query.edit_message_text(texto, reply_markup=InlineKeyboardMarkup(keyboard))


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(ChatMemberHandler(new_member, ChatMemberHandler.CHAT_MEMBER))
app.add_handler(CallbackQueryHandler(botones))

print("Bot funcionando...")
app.run_polling()
