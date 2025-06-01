from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Chat ID:", update.effective_chat.id)
    await update.message.reply_text(f"Chat ID: {update.effective_chat.id}")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, get_chat_id))

print("Запусти бот и напиши в нужный чат...")
app.run_polling()