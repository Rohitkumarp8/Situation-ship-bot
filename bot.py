import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

from database import init_db
from handlers.profile import (
    get_profile_conversation, cmd_start, show_my_profile
)
from handlers.matching import browse_profiles, handle_like_skip, show_matches
from handlers.chat import relay_message, stop_chat
from handlers.anonymous import start_anonymous, cancel_wait

load_dotenv()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Profile Banao", callback_data="create_profile")],
        [InlineKeyboardButton("🎭 Anonymous Chat", callback_data="anonymous_mode")],
        [InlineKeyboardButton("💘 Profiles Browse Karo", callback_data="browse")],
        [InlineKeyboardButton("💬 Mere Matches", callback_data="my_matches")],
    ])

    await query.message.reply_text(
        "💕 *Main Menu*\n\nKya karna chahte ho?",
        parse_mode="Markdown",
        reply_markup=keyboard
    )


async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "anonymous_mode":
        await start_anonymous(update, context)
    elif data == "browse":
        await browse_profiles(update, context)
    elif data == "my_matches":
        await show_matches(update, context)
    elif data == "main_menu":
        await main_menu_callback(update, context)
    elif data.startswith("like_") or data.startswith("skip_"):
        await handle_like_skip(update, context)


async def smart_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sab messages yahan aate hain.
    Check karo user active chat mein hai ya nahi.
    """
    from utils.helpers import get_active_chat_partner, get_user

    user_id = update.effective_user.id
    partner_id = get_active_chat_partner(user_id)

    if partner_id:
        user = get_user(user_id)
        if user and user.is_anonymous:
            from handlers.anonymous import anonymous_relay
            await anonymous_relay(update, context)
        else:
            await relay_message(update, context)


def main():
    init_db()
    logger.info("Database initialized ✅")

    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN environment variable nahi mila!")

    app = Application.builder().token(token).build()

    # Profile conversation (start + profile banao)
    app.add_handler(get_profile_conversation())

    # Commands
    app.add_handler(CommandHandler("myprofile", show_my_profile))
    app.add_handler(CommandHandler("browse", browse_profiles))
    app.add_handler(CommandHandler("matches", show_matches))
    app.add_handler(CommandHandler("anonymous", start_anonymous))
    app.add_handler(CommandHandler("cancel_wait", cancel_wait))
    app.add_handler(CommandHandler("stop", stop_chat))

    # Callback buttons
    app.add_handler(CallbackQueryHandler(handle_callbacks))

    # Sab messages relay karo (text, photo, video, voice, sticker, document)
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO | filters.VIDEO |
         filters.VOICE | filters.STICKER | filters.Document.ALL |
         filters.AUDIO) & ~filters.COMMAND,
        smart_message_handler
    ))

    logger.info("Bot chal raha hai... 🚀")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
