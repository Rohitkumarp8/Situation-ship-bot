from telegram import Update
from telegram.ext import ContextTypes
from utils.helpers import (
    get_or_create_user, update_user, get_active_chat_partner,
    create_active_chat, end_active_chat, get_db
)
from models import User, ActiveChat
from sqlalchemy import or_

# Waiting queue for anonymous users
waiting_queue = []


async def start_anonymous(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        username = query.from_user.username
        send_func = query.message.reply_text
    else:
        user_id = update.effective_user.id
        username = update.effective_user.username
        send_func = update.message.reply_text

    # Already in chat check
    partner_id = get_active_chat_partner(user_id)
    if partner_id:
        await send_func("❌ Tum pehle se ek chat mein ho! /stop se pehle band karo.")
        return

    # User create/update
    get_or_create_user(user_id, username)
    update_user(user_id, is_anonymous=True)

    global waiting_queue

    # Agar queue mein koi wait kar raha hai
    if waiting_queue and waiting_queue[0] != user_id:
        partner_id = waiting_queue.pop(0)
        create_active_chat(user_id, partner_id, is_anonymous=True)

        await send_func(
            "🎭 *Anonymous Chat Shuru!*\n\n"
            "Ek stranger se connect ho gaye ho!\n"
            "Koi bhi message karo - text, photo, video sab chal sakta hai.\n\n"
            "/stop - Chat band karne ke liye",
            parse_mode="Markdown"
        )

        try:
            await context.bot.send_message(
                chat_id=partner_id,
                text="🎭 *Anonymous Chat Shuru!*\n\n"
                     "Ek stranger se connect ho gaye ho!\n"
                     "Koi bhi message karo - text, photo, video sab chal sakta hai.\n\n"
                     "/stop - Chat band karne ke liye",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    else:
        # Queue mein add karo
        if user_id not in waiting_queue:
            waiting_queue.append(user_id)

        await send_func(
            "⏳ *Partner dhundh rahe hain...*\n\n"
            "Koi stranger milega tab connect karenge!\n"
            "/cancel_wait - Wait cancel karne ke liye",
            parse_mode="Markdown"
        )


async def cancel_wait(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    global waiting_queue

    if user_id in waiting_queue:
        waiting_queue.remove(user_id)
        await update.message.reply_text(
            "✅ Wait cancel kar di.\n\n"
            "/anonymous - Dobara try karne ke liye\n"
            "/browse - Profiles dekhne ke liye"
        )
    else:
        await update.message.reply_text("Tum wait mein nahi ho.")


async def anonymous_relay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Anonymous chat relay - same as normal relay but hides name"""
    user_id = update.effective_user.id
    partner_id = get_active_chat_partner(user_id)

    if not partner_id:
        return

    try:
        if update.message.text:
            await context.bot.send_message(
                chat_id=partner_id,
                text=f"🎭 *Stranger:*\n{update.message.text}",
                parse_mode="Markdown"
            )
        elif update.message.photo:
            await context.bot.send_photo(
                chat_id=partner_id,
                photo=update.message.photo[-1].file_id,
                caption="📸 *Stranger*",
                parse_mode="Markdown"
            )
        elif update.message.video:
            await context.bot.send_video(
                chat_id=partner_id,
                video=update.message.video.file_id,
                caption="🎥 *Stranger*",
                parse_mode="Markdown"
            )
        elif update.message.voice:
            await context.bot.send_voice(
                chat_id=partner_id,
                voice=update.message.voice.file_id
            )
        elif update.message.sticker:
            await context.bot.send_sticker(
                chat_id=partner_id,
                sticker=update.message.sticker.file_id
            )
    except Exception:
        await update.message.reply_text("❌ Message deliver nahi hua.")
