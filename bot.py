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
INVITE_LINK = "https://t.me/+xM84o_i6j-pmODkx"
LTR = "\u200e"

WAITING_PROOF = 1

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def is_member(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


async def send_to_admin(context, user, proof_type, file_id=None, text=None):
    keyboard = [[
        InlineKeyboardButton("✅ تایید", callback_data=f"approve_{user.id}"),
        InlineKeyboardButton("❌ رد", callback_data=f"reject_{user.id}")
    ]]
    markup = InlineKeyboardMarkup(keyboard)

    info = (
        f"🔔 درخواست عضویت جدید!\n\n"
        f"👤 نام: {user.full_name}\n"
        f"🆔 یوزرنیم: @{user.username or 'ندارد'}\n"
        f"🔢 آیدی: {user.id}\n"
        f"📋 نوع: {proof_type}"
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
        await update.message.reply_text(
            f"✅ سلام {user.first_name}!\n"
            f"شما عضو کانال {LTR}TradeMan هستید. 🚀"
        )
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton(f"📝 ثبت‌نام در LBank", url=REFERRAL_LINK)],
        [InlineKeyboardButton("✅ ثبت‌نام کردم!", callback_data="verify")]
    ]

    await update.message.reply_text(
        f"👋 سلام {user.first_name}\n\n"
        f"🎯 به ربات {LTR}TRADEMANVIP خوش آمدید!\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🏆 مزایای کانال {LTR}TradeMan:\n\n"
        f"📊 سیگنال‌های روزانه\n"
        f"📈 تحلیل بازارهای کریپتو، طلا و دلار\n"
        f"🎓 آموزش‌های کاملاً رایگان\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"برای عضویت:\n\n"
        f"✅ روی \" ثبت‌نام در {LTR}LBank \" کلیک کنید\n\n"
        f"✅ در صرافی {LTR}LBank ثبت‌نام کنید\n\n"
        f"✅ به همین صفحه برگردید و دکمه \" ثبت‌نام کردم! \" را بزنید\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"⚡️ کل این پروسه کمتر از ۳ دقیقه طول می‌کشه!\n\n"
        f"💎 بعد از تایید، لینک کانال {LTR}TradeMan برای شما ارسال می‌شود!",
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
        f"📤 لطفاً بعد از ثبت‌نام:\n\n"
        f"📸 اسکرین‌شات پروفایل یا داشبورد {LTR}LBank\n\n"
        f"و یا\n\n"
        f"🚨 {LTR}UID حساب {LTR}LBank خود را بفرستید\n\n"
        f"برای لغو /cancel را بنویس"
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
    target_user_id = int(data.split("_")[1])

    if data.startswith("approve_"):
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=(
                    f"🎉 تبریک!\n\n"
                    f"✅ ثبت‌نام شما تایید شد!\n\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"👇 لینک ورود به کانال {LTR}TradeMan:\n"
                    f"{INVITE_LINK}\n"
                    f"━━━━━━━━━━━━━━━━━━\n\n"
                    f"موفق باشی! 🚀"
                )
            )
        except Exception as e:
            logger.error(f"Send error: {e}")
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"⚠️ نتونستم به کاربر پیام بدم!\nلینک رو خودت بفرست:\n{INVITE_LINK}"
            )

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
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=(
                    "❌ متاسفانه ثبت‌نام شما تایید نشد.\n\n"
                    "لطفاً مطمئن شو که:\n"
                    f"• از لینک رفرال ما در {LTR}LBank ثبت‌نام کردی\n"
                    "• اسکرین‌شات واضح باشه\n\n"
                    "دوباره امتحان کن: /start"
                )
            )
        except Exception as e:
            logger.error(f"Reject error: {e}")

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
