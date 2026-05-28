from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
from utils.helpers import (
    get_user, get_next_profile, add_like, get_matches,
    create_active_chat, get_or_create_user
)


async def browse_profiles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle both command and callback
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        send_func = query.message.reply_text
        send_photo_func = query.message.reply_photo
    else:
        user_id = update.effective_user.id
        send_func = update.message.reply_text
        send_photo_func = update.message.reply_photo

    me = get_user(user_id)
    if not me or not me.is_profile_complete:
        await send_func("❌ Pehle profile banao! /start")
        return

    profile = get_next_profile(user_id, me.looking_for)

    if not profile:
        await send_func(
            "😔 Abhi koi naya profile nahi mila.\n\n"
            "Baad mein try karo ya /anonymous se anonymous chat karo!"
        )
        return

    # Store current profile in context
    context.user_data['current_profile_id'] = profile.telegram_id

    text = (
        f"💘 *{profile.name}*, {profile.age}\n"
        f"⚧ {profile.gender}\n"
        f"🏙 {profile.city or 'Location nahi di'}\n"
        f"📝 {profile.bio or 'Koi bio nahi'}"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❤️ Like", callback_data=f"like_{profile.telegram_id}"),
            InlineKeyboardButton("❌ Skip", callback_data=f"skip_{profile.telegram_id}"),
        ],
        [InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]
    ])

    if profile.photo_file_id:
        await send_photo_func(photo=profile.photo_file_id, caption=text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await send_func(text, parse_mode="Markdown", reply_markup=keyboard)


async def handle_like_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    if data.startswith("like_"):
        target_id = int(data.split("_")[1])
        is_match = add_like(user_id, target_id)

        if is_match:
            # Match ho gaya!
            create_active_chat(user_id, target_id)
            target = get_user(target_id)

            await query.message.reply_text(
                f"🎉 *Match ho gaya!*\n\n"
                f"Tum aur *{target.name}* dono ne ek dusre ko like kiya!\n\n"
                f"Ab directly message karo - type karo aur send karo! 💬\n"
                f"/stop - Chat band karne ke liye",
                parse_mode="Markdown"
            )

            # Dusre user ko bhi notify karo
            me = get_user(user_id)
            try:
                await context.bot.send_message(
                    chat_id=target_id,
                    text=f"🎉 *Match ho gaya!*\n\n"
                         f"*{me.name}* ne tumhe like kiya aur tum bhi unhe like karte ho!\n\n"
                         f"Ab directly message karo! 💬\n"
                         f"/stop - Chat band karne ke liye",
                    parse_mode="Markdown"
                )
            except Exception:
                pass
        else:
            await query.message.reply_text("❤️ Like kiya! Agle profile ke liye /browse")

    elif data.startswith("skip_"):
        # Next profile dikhao
        me = get_user(user_id)
        profile = get_next_profile(user_id, me.looking_for if me else None)

        if not profile:
            await query.message.reply_text("😔 Aur koi profile nahi mila abhi. Baad mein try karo!")
            return

        context.user_data['current_profile_id'] = profile.telegram_id

        text = (
            f"💘 *{profile.name}*, {profile.age}\n"
            f"⚧ {profile.gender}\n"
            f"🏙 {profile.city or 'Location nahi di'}\n"
            f"📝 {profile.bio or 'Koi bio nahi'}"
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("❤️ Like", callback_data=f"like_{profile.telegram_id}"),
                InlineKeyboardButton("❌ Skip", callback_data=f"skip_{profile.telegram_id}"),
            ],
            [InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]
        ])

        if profile.photo_file_id:
            await query.message.reply_photo(
                photo=profile.photo_file_id,
                caption=text,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        else:
            await query.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)


async def show_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        send_func = query.message.reply_text
    else:
        user_id = update.effective_user.id
        send_func = update.message.reply_text

    matches = get_matches(user_id)

    if not matches:
        await send_func(
            "💔 Abhi koi match nahi hai.\n\n"
            "/browse se profiles dekhte raho!"
        )
        return

    text = "💘 *Tere Matches:*\n\n"
    for m in matches:
        text += f"• *{m.name}*, {m.age} - {m.city or 'N/A'}\n"

    text += "\n/browse - Aur profiles dekhne ke liye"
    await send_func(text, parse_mode="Markdown")
