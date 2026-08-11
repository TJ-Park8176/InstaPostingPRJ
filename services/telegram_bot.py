import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from models.database import SessionLocal
from models.post import Post, PostStatus

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_approval_request(post_id: int, image_paths: list, caption: str):
    """
    Sends the generated card news and caption to the Telegram chat for approval.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bot not configured.")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    keyboard = [
        [
            InlineKeyboardButton("👍 승인 및 포스팅", callback_data=f"approve_{post_id}"),
            InlineKeyboardButton("❌ 취소", callback_data=f"cancel_{post_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Note: For multiple images, we could use send_media_group, but inline keyboards
    # only work with the last message or a separate text message.
    
    message = f"새로운 포스팅 초안이 생성되었습니다.\n\n캡션:\n{caption}"
    await application.bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=message,
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    action, post_id_str = data.split("_")
    post_id = int(post_id_str)

    db = SessionLocal()
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        await query.edit_message_text(text="해당 포스트를 찾을 수 없습니다.")
        db.close()
        return

    if action == "approve":
        post.status = PostStatus.APPROVED
        db.commit()
        await query.edit_message_text(text=f"포스트 #{post_id} 승인 완료. 곧 업로드됩니다.")
        
        # Here we would trigger the Instagram publisher
        # ...
        
    elif action == "cancel":
        post.status = PostStatus.FAILED
        db.commit()
        await query.edit_message_text(text=f"포스트 #{post_id} 취소됨.")

    db.close()

def start_bot():
    if not TELEGRAM_TOKEN:
        return
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CallbackQueryHandler(button_callback))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

# Run start_bot() in a separate thread/process if starting the app
