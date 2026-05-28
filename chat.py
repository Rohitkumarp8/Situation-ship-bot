from telegram import Update
from telegram.ext import ContextTypes
from utils.helpers import get_active_chat_partner, end_active_chat, get_user


async def relay_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    partner_id = get_active_chat_partner(user_id)

    if not partner_id:
        return  # Koi active chat nahi, ignore karo

    me = get_user(user_id)
    name = me.name if me and me.name else "User"

    try:
        if update.message.text:
            await context.bot.send_message(
                chat_id=partner_id,
                text=f"💬 *{name}:*\n{update.message.text}",
                parse_mode="Markdown"
            )

        elif update.message.photo:
            caption = update.message.caption or ""
            await context.bot.send_photo(
                chat_id=partner_id,
                photo=update.message.photo[-1].file_id,
                caption=f"📸 *{name}:* {caption}",
                parse_mode="Markdown"
            )

        elif update.message.video:
            await context.bot.send_video(
                chat_id=partner_id,
                video=update.message.video.file_id,
                caption=f"🎥 *{name}*",
                parse_mode="Markdown"
            )

        elif update.message.voice:
            await context.bot.send_voice(
                chat_id=partner_id,
                voice=update.message.voice.file_id,
                caption=f"🎤 *{name}*",
                parse_mode="Markdown"
            )

        elif update.message.sticker:
            await context.bot.send_sticker(
                chat_id=partner_id,
                sticker=update.message.sticker.file_id
            )

        elif update.message.document:
            await context.bot.send_document(
                chat_id=partner_id,
                document=update.message.document.file_id,
                caption=f"📁 *{name}*",
                parse_mode="Markdown"
            )

        elif update.message.audio:
            await context.bot.send_audio(
                chat_id=partner_id,
                audio=update.message.audio.file_id,
                caption=f"🎵 *{name}*",
                parse_mode="Markdown"
            )

    except Exception as e:
        await update.message.reply_text("❌ Message deliver nahi hua. Partner unavailable hai.")


async def stop_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    partner_id = get_active_chat_partner(user_id)

    end_active_chat(user_id)

    await update.message.reply_text(
        "👋 Chat band ho gayi.\n\n"
        "/browse - Naye profiles dekhne ke liye\n"
        "/matches - Matches dekhne ke liye"
    )

    if partner_id:
        try:
            await context.bot.send_message(
                chat_id=partner_id,
                text="👋 Partner ne chat band kar di.\n\n"
                     "/browse - Naye profiles dekhne ke liye"
            )
        except Exception:
            pass
