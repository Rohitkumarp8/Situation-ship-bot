from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, filters, CallbackQueryHandler
)
from utils.helpers import get_or_create_user, update_user, get_user

NAME, AGE, GENDER, LOOKING_FOR, CITY, BIO, PHOTO = range(7)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_or_create_user(
        update.effective_user.id,
        update.effective_user.username
    )

    keyboard = [
        [InlineKeyboardButton("👤 Profile Banao", callback_data="create_profile")],
        [InlineKeyboardButton("🎭 Anonymous Chat", callback_data="anonymous_mode")],
        [InlineKeyboardButton("💘 Profiles Browse Karo", callback_data="browse")],
        [InlineKeyboardButton("💬 Mere Matches", callback_data="my_matches")],
    ]

    if user.is_profile_complete:
        keyboard.insert(0, [InlineKeyboardButton("✏️ Profile Edit Karo", callback_data="create_profile")])

    await update.message.reply_text(
        "💕 *Dating Bot mein Welcome!*\n\n"
        "Yahan aap:\n"
        "✅ Profile bana sakte ho\n"
        "✅ Log dhundh sakte ho\n"
        "✅ Chat kar sakte ho\n"
        "✅ Anonymous mode bhi hai\n\n"
        "Kya karna chahte ho?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def start_profile_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        await query.message.reply_text(
            "👤 *Profile Setup Shuru!*\n\nApna naam batao:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await update.message.reply_text(
            "👤 *Profile Setup Shuru!*\n\nApna naam batao:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if len(name) < 2:
        await update.message.reply_text("❌ Sahi naam daalo!")
        return NAME
    context.user_data['name'] = name
    await update.message.reply_text(f"Nice {name}! 😊\n\nAbhi apni umar batao (sirf number):")
    return AGE


async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        age = int(update.message.text.strip())
        if age < 18:
            await update.message.reply_text("❌ Sirf 18+ log join kar sakte hain.")
            return AGE
        if age > 70:
            await update.message.reply_text("❌ Sahi umar daalo (18-70).")
            return AGE
        context.user_data['age'] = age
    except ValueError:
        await update.message.reply_text("❌ Sirf number daalo!")
        return AGE

    keyboard = [["Male", "Female"], ["Other"]]
    await update.message.reply_text(
        "Apna gender select karo:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return GENDER


async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gender = update.message.text
    if gender not in ["Male", "Female", "Other"]:
        await update.message.reply_text("❌ Neeche se select karo!")
        return GENDER
    context.user_data['gender'] = gender

    keyboard = [["Male", "Female"], ["Both"]]
    await update.message.reply_text(
        "Aap kise dhundh rahe ho?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return LOOKING_FOR


async def get_looking_for(update: Update, context: ContextTypes.DEFAULT_TYPE):
    looking_for = update.message.text
    if looking_for not in ["Male", "Female", "Both"]:
        await update.message.reply_text("❌ Neeche se select karo!")
        return LOOKING_FOR
    context.user_data['looking_for'] = looking_for

    await update.message.reply_text(
        "Apna sheher batao (ya Skip karo):",
        reply_markup=ReplyKeyboardMarkup([["Skip"]], one_time_keyboard=True, resize_keyboard=True)
    )
    return CITY


async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != "Skip":
        context.user_data['city'] = update.message.text.strip()

    await update.message.reply_text(
        "Apne baare mein kuch likho - Bio (ya Skip karo):",
        reply_markup=ReplyKeyboardMarkup([["Skip"]], one_time_keyboard=True, resize_keyboard=True)
    )
    return BIO


async def get_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != "Skip":
        context.user_data['bio'] = update.message.text.strip()

    await update.message.reply_text(
        "Apni ek achhi photo bhejo (ya Skip karo):",
        reply_markup=ReplyKeyboardMarkup([["Skip"]], one_time_keyboard=True, resize_keyboard=True)
    )
    return PHOTO


async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file_id = None

    if update.message.photo:
        photo_file_id = update.message.photo[-1].file_id
    elif update.message.text == "Skip":
        pass
    else:
        await update.message.reply_text("❌ Photo bhejo ya Skip karo!")
        return PHOTO

    # Save to DB
    user_id = update.effective_user.id
    update_user(
        user_id,
        name=context.user_data.get('name'),
        age=context.user_data.get('age'),
        gender=context.user_data.get('gender'),
        looking_for=context.user_data.get('looking_for'),
        city=context.user_data.get('city'),
        bio=context.user_data.get('bio'),
        photo_file_id=photo_file_id,
        is_profile_complete=True
    )

    await update.message.reply_text(
        "✅ *Profile ban gayi!*\n\n"
        "Ab aap profiles browse kar sakte ho.\n"
        "/browse - Profiles dekhne ke liye\n"
        "/matches - Apne matches dekhne ke liye\n"
        "/anonymous - Anonymous chat ke liye",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Cancel kar diya. /start se wapas shuru karo.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def show_my_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    if not user or not user.is_profile_complete:
        await update.message.reply_text("❌ Pehle profile banao! /start")
        return

    text = (
        f"👤 *Teri Profile*\n\n"
        f"📛 Naam: {user.name}\n"
        f"🎂 Umar: {user.age}\n"
        f"⚧ Gender: {user.gender}\n"
        f"💘 Dhundh raha/rahi: {user.looking_for}\n"
        f"🏙 Sheher: {user.city or 'Nahi bataya'}\n"
        f"📝 Bio: {user.bio or 'Koi bio nahi'}"
    )

    if user.photo_file_id:
        await update.message.reply_photo(
            photo=user.photo_file_id,
            caption=text,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(text, parse_mode="Markdown")


def get_profile_conversation():
    return ConversationHandler(
        entry_points=[
            CommandHandler("start", cmd_start),
            CommandHandler("profile", start_profile_creation),
            CallbackQueryHandler(start_profile_creation, pattern="^create_profile$"),
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)],
            LOOKING_FOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_looking_for)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_bio)],
            PHOTO: [
                MessageHandler(filters.PHOTO, get_photo),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_photo),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
