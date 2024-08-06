import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes

TOKEN = '7462646393:AAF2M9Isx-g4pudj32DIEgXLkVFZI8vxzGE'
CHAT_ID = 5316086823  
a = 1
update = Update
context = ContextTypes.DEFAULT_TYPE
context.bot.send_message(chat_id=update.effective_chat.id, text=f"서버가 온라인 상태입니다.")
