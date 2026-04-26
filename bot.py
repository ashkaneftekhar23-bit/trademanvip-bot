import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters, ConversationHandler
)

# ========== تنظیمات ==========
BOT_TOKEN = "8647319022:AAEy5L1A9g2vGp0gFlXW0FDqrvQAdfG_vR0"
CHANNEL_ID = -1002180889746
REFERRAL_LINK = "https://www.lbank.com/en-US/login/?icode=TRADELAND"
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7274125873"))

WAITING_PROOF = 1

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def is_member(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


INVITE_LINK = "https://t.me/+BLcOh-oRGtI3ZGJk"

async def create_invite(context):
    try:
    return INVITE_LINK


async def send_to_admin(context, user, proof_type, file_id=None, text=None):
    # ساخت لینک دعوت از قبل
    invite_link = await create_invite(context)

    keyboard = [[
        InlineKeyboardButton("✅ تایید و ارسال لینک", callback_data=f"approve_{user.id}_{invite_link}"),
        InlineKeyboardButton("❌ رد", callback_data=f"reject_{user.id}")
    ]]
    markup = InlineKeyboardMarkup(keyboard)

    info = (
        f"🔔 درخواست عضویت جدید!\n\n"
        f"👤 نام: {user.full_name}\n"
        f"🆔 یوزرنیم: @{user.username or 'ندارد'}\n"
        f"🔢 آیدی: {user.id}\n"
        f"📋 نوع: {proof_type}\n\n"
        f"🔗 لینک دعوت آماده شده:\n{invite_link}"
    )

    try:
        if file_id:
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=file_id,
                caption=info,
                reply_markup=markup
            )
        else:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=info + f"\n\n📝 متن: {text}",
                reply_markup=markup
            )
        return True
    except Exception as e:
        logger.error(f"Send to admin error: {e}")
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if await is_member(context.bot, user.id):
        await update.message.reply_text(f"✅ سلام {user.first_name}!\nشما عضو کانال TRADEMANVIP هستید. 🚀")
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("📝 ثبت‌نام در LBank", url=REFERRAL_LINK)],
        [InlineKeyboardButton("✅ ثبت‌نام کردم!", callback_data="verify")]
    ]

    await update.message.reply_text(
        f"👋 سلام {user.first_name}!\n\n"
        f"🎯 به ربات TRADEMANVIP خوش آمدید!\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"برای عضویت در کانال VIP:\n\n"
        f"1️⃣ روی دکمه زیر کلیک کن\n"
        f"2️⃣ در صرافی LBank ثبت‌نام کن\n"
        f"3️⃣ برگرد و دکمه تایید رو بزن\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"⚠️ حتماً از لینک زیر ثبت‌نام کن!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END


async def verify_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if await is_member(context.bot, query.from_user.id):
        await query.edit_message_text("✅ شما قبلاً عضو کانال هستید!")
        return ConversationHandler.END

    await query.edit_message_text(
        "📤 لطفاً یکی از موارد زیر را ارسال کن:\n\n"
        "📸 اسکرین‌شات پروفایل یا داشبورد LBank\n\n"
        "یا\n\n"
        "🔢 UID حساب LBank خود را بنویس\n\n"
        "برای لغو /cancel را بنویس"
    )
    return WAITING_PROOF


async def handle_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message
    sent = False

    if msg.photo:
        sent = await send_to_admin(context, user, "اسکرین‌شات", file_id=msg.photo[-1].file_id)
    elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith("image/"):
        sent = await send_to_admin(context, user, "اسکرین‌شات", file_id=msg.document.file_id)
    elif msg.text:
        sent = await send_to_admin(context, user, "UID/متن", text=msg.text.strip())
    else:
        await msg.reply_text("❌ لطفاً اسکرین‌شات یا UID ارسال کن.")
        return WAITING_PROOF

    if sent:
        await msg.reply_text(
            "⏳ مدرک شما دریافت شد!\n\n"
            "در حال بررسی توسط ادمین هستید.\n"
            "معمولاً در کمتر از ۲۴ ساعت نتیجه اعلام می‌شود. 🙏"
        )
    else:
        await msg.reply_text("❌ خطا در ارسال. لطفاً دوباره امتحان کن.")

    return ConversationHandler.END


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if update.effective_user.id != ADMIN_ID:
        await query.answer("❌ شما ادمین نیستید!", show_alert=True)
        return

    await query.answer()
    data = query.data

    if data.startswith("approve_"):
        # فرمت: approve_userid_invitelink
        parts = data.split("_", 2)
        target_user_id = int(parts[1])
        invite_link = parts[2] if len(parts) > 2 else None

        if not invite_link:
            invite_link = await create_invite(context)

        # ارسال لینک به ادمین (کپی کنه و بفرسته)
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"✅ تایید شد!\n\n"
                f"🔗 لینک کانال برای کاربر {target_user_id}:\n"
                f"{invite_link}\n\n"
                f"این لینک رو برای کاربر بفرست یا forward کن."
            )
        )

        # سعی کن مستقیم هم بفرسته
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=(
                    f"🎉 تبریک!\n\n"
                    f"✅ ثبت‌نام شما تایید شد!\n\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"👇 لینک ورود به کانال VIP:\n"
                    f"{invite_link}\n"
                    f"━━━━━━━━━━━━━━━━━━\n\n"
                    f"⚠️ این لینک فقط یک‌بار قابل استفاده است!\n"
                    f"موفق باشی! 🚀"
                )
            )
        except Exception as e:
            logger.error(f"Direct send error: {e}")

        # آپدیت پیام ادمین
        try:
            if query.message.photo:
                await query.edit_message_caption(
                    caption=(query.message.caption or "") + "\n\n✅ تایید شد!",
                    reply_markup=None
                )
            else:
                await query.edit_message_text(
                    text=(query.message.text or "") + "\n\n✅ تایید شد!",
                    reply_markup=None
                )
        except:
            pass

    elif data.startswith("reject_"):
        target_user_id = int(data.split("_")[1])

        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=(
                    "❌ متاسفانه ثبت‌نام شما تایید نشد.\n\n"
                    "لطفاً مطمئن شو که:\n"
                    "• از لینک رفرال ما ثبت‌نام کردی\n"
                    "• اسکرین‌شات واضح باشه\n\n"
                    "دوباره امتحان کن: /start"
                )
            )
        except Exception as e:
            logger.error(f"Reject send error: {e}")
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"⚠️ نتونستم به کاربر پیام بدم. کاربر باید اول /start بزنه."
            )

        try:
            if query.message.photo:
                await query.edit_message_caption(
                    caption=(query.message.caption or "") + "\n\n❌ رد شد.",
                    reply_markup=None
                )
            else:
                await query.edit_message_text(
                    text=(query.message.text or "") + "\n\n❌ رد شد.",
                    reply_markup=None
                )
        except:
            pass


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ عملیات لغو شد.\n\nبرای شروع مجدد /start بزن.")
    return ConversationHandler.END


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(verify_button, pattern="^verify$")
        ],
        states={
            WAITING_PROOF: [
                MessageHandler(
                    filters.PHOTO | filters.Document.IMAGE | filters.TEXT & ~filters.COMMAND,
                    handle_proof
                )
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_user=True
    )

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^(approve|reject)_"))

    logger.info("✅ TRADEMANVIP Bot started!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
