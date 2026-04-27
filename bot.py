import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters, ConversationHandler
)

BOT_TOKEN = "8647319022:AAEy5L1A9g2vGp0gFlXW0FDqrvQAdfG_vR0"
CHANNEL_ID = -1002180889746
REFERRAL_LINK = "https://www.lbank.com/signup?icode=TRADELAND"
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7274125873"))
INVITE_LINK = "https://t.me/+xM84o_i6j-pmODkx"
LTR = "\u200e"
UID_PHOTO_ID = None  # بعداً اضافه میشه

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


async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📝 ثبت‌نام":
        await start(update, context)
    elif text == "💬 پشتیبانی":
        await update.message.reply_text(
            "💬 برای ارتباط با پشتیبانی:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 پشتیبانی", url="tg://user?id=7274125873")]
            ])
        )
    elif text == "🌐 سایت":
        await update.message.reply_text(
            "🌐 وب‌سایت ما:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🌐 ashkaneftekhar.com", url="https://ashkaneftekhar.com")]
            ])
        )
    elif text == "📊 چارت‌ها":
        if not await is_member(context.bot, update.effective_user.id):
            await update.message.reply_text(
                "⛔️ برای استفاده از این قابلیت ابتدا باید ثبت‌نام کنید!\n\n"
                "روی دکمه 📝 ثبت‌نام بزنید."
            )
            return
        await update.message.reply_text(
            "📊 چارت مورد نظر را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔶 BTC/USDT", url="https://www.tradingview.com/chart/?symbol=BYBIT:BTCUSDT.P")],
                [InlineKeyboardButton("🥇 طلا (XAU/USD)", url="https://www.tradingview.com/chart/?symbol=XAUUSD")],
                [InlineKeyboardButton("📈 Total3", url="https://www.tradingview.com/chart/?symbol=TOTAL3")]
            ])
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    reply_keyboard = ReplyKeyboardMarkup([
        [KeyboardButton("📝 ثبت‌نام")],
        [KeyboardButton("💬 پشتیبانی"), KeyboardButton("🌐 سایت")],
        [KeyboardButton("📊 چارت‌ها")]
    ], resize_keyboard=True)

    if await is_member(context.bot, user.id):
        await update.message.reply_text(
            f"✅ سلام {user.first_name}!\n"
            f"شما عضو کانال {LTR}TradeMan هستید. 🚀",
            reply_markup=reply_keyboard
        )
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("📝 ثبت‌نام در LBank", url=REFERRAL_LINK)],
        [InlineKeyboardButton("✅ ثبت‌نام کردم!", callback_data="verify")]
    ]

    await update.message.reply_text(
        f"👋 سلام {user.first_name}\n\n"
        f"🎯 به ربات {LTR}TRADEMANVIP خوش آمدید!\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🏆 مزایای کانال {LTR}TradeMan:\n\n"
        "📊 سیگنال‌های روزانه\n"
        "📈 تحلیل بازارهای کریپتو، طلا و دلار\n"
        "🎓 آموزش‌های کاملاً رایگان\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "برای عضویت:\n\n"
        f"✅ روی \" ثبت‌نام در {LTR}LBank \" کلیک کنید\n\n"
        f"✅ در صرافی {LTR}LBank ثبت‌نام کنید\n\n"
        "✅ به همین صفحه برگردید و دکمه \" ثبت‌نام کردم! \" را بزنید\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "⚡️ کل این پروسه کمتر از ۳ دقیقه طول می‌کشه!\n\n"
        f"💎 بعد از تایید، لینک کانال {LTR}TradeMan برای شما ارسال می‌شود!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text(
        "از منوی زیر انتخاب کنید:",
        reply_markup=reply_keyboard
    )
    return ConversationHandler.END


async def verify_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if await is_member(context.bot, query.from_user.id):
        await query.edit_message_text("✅ شما قبلاً عضو کانال هستید!")
        return ConversationHandler.END

    await query.message.reply_text(
        "📤 لطفاً بعد از ثبت‌نام، کد شناسه (UID) حساب کاربری خود را برای ما بفرستید\n\n"
        "📌 مطابق تصویر زیر، UID خود را پیدا و ارسال کنید"
    )
    return WAITING_PROOF


async def handle_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message
    sent = False

    if msg.text in ["📝 ثبت‌نام", "💬 پشتیبانی", "🌐 سایت", "📊 چارت‌ها"]:
        await handle_menu(update, context)
        return ConversationHandler.END

    if msg.photo:
        sent = await send_to_admin(context, user, "اسکرین‌شات", file_id=msg.photo[-1].file_id)
    elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith("image/"):
        sent = await send_to_admin(context, user, "اسکرین‌شات", file_id=msg.document.file_id)
    elif msg.text:
        uid = msg.text.strip()
        if not uid.upper().startswith("LBA"):
            await msg.reply_text(
                "❌ کد وارد شده معتبر نیست!\n\n"
                "کد UID حساب LBank همیشه با LBA شروع می‌شود\n"
                "مانند تصویر بالا\n\n"
                "لطفاً دوباره امتحان کنید 🔄"
            )
            return WAITING_PROOF
        sent = await send_to_admin(context, user, "UID", text=uid)
    else:
        await msg.reply_text("❌ لطفاً UID حساب خود را بفرستید.")
        return WAITING_PROOF

    if sent:
        await msg.reply_text(
            "✅ درخواست شما ثبت شد و در حال بررسی می‌باشد\n\n"
            "⏱ معمولاً در کمتر از ۱ ساعت نتیجه اعلام خواهد شد"
        )
    else:
        await msg.reply_text("❌ خطا در ارسال. لطفاً دوباره امتحان کنید.")

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
                    "🎉 تبریک!\n\n"
                    "✅ ثبت‌نام شما تایید شد!\n"
                    "━━━━━━━━━━━━━━━━━━\n"
                    "🏆 به TradeMan خوش آمدید!\n\n"
                    "📊 توی این کانال هر روز با هم ترید می‌کنیم و موقعیت‌های طلایی بازار رو شکار می‌کنیم 🦇\n\n"
                    "⚠️ بلافاصله بعد از ورود، پیام‌های پین شده را مطالعه کنید ⚠️\n"
                    "━━━━━━━━━━━━━━━━━━\n"
                    "👇 از طریق لینک زیر وارد شوید:\n\n"
                    f"{INVITE_LINK}\n\n"
                    "موفق و پرسود باشید 🚀"
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
                    "لطفاً مطمئن شوید که از لینک رفرال ما در LBank ثبت‌نام کرده‌اید و از دکمه شروع مجدد استفاده کنید\n\n"
                    "در صورت نیاز به راهنمایی، از دکمه پشتیبانی کمک بگیرید 👇"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 شروع مجدد", url="https://t.me/trademanvipbot?start=start")],
                    [InlineKeyboardButton("💬 پشتیبانی", url="tg://user?id=7274125873")]
                ])
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


async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        await update.message.reply_text("File ID:\n" + file_id)
    else:
        await update.message.reply_text("یه عکس بفرست!")


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

    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.Regex("^(📝 ثبت‌نام|💬 پشتیبانی|🌐 سایت|📊 چارت‌ها)$"),
        handle_menu
    ))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^(approve|reject)_"))
    app.add_handler(MessageHandler(filters.PHOTO & filters.User(ADMIN_ID), get_file_id))

    logger.info("TRADEMANVIP Bot started!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
