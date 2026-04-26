import os
import logging
import base64
import json
import re
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters, ConversationHandler
)

# ========== تنظیمات ==========
BOT_TOKEN = "8647319022:AAEy5L1A9g2vGp0gFlXW0FDqrvQAdfG_vR0"
CHANNEL_ID = -1002180889746
REFERRAL_LINK = "https://www.lbank.com/en-US/login/?icode=TRADELAND"
REFERRAL_CODE = "TRADELAND"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDy6yfvPImhq27f6v2GVM2lOg4MgchNyug")

# آیدی عددی تلگرام تو (ادمین) - باید پر بشه
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# ========== مراحل ==========
WAITING_PROOF = 1

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== بررسی عضویت ==========
async def is_member(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ========== ارسال به ادمین برای تایید ==========
async def send_to_admin(context, user, proof_type, file_id=None, text=None):
    if ADMIN_ID == 0:
        return False

    keyboard = [
        [
            InlineKeyboardButton("✅ تایید", callback_data=f"approve_{user.id}"),
            InlineKeyboardButton("❌ رد", callback_data=f"reject_{user.id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = (
        f"🔔 درخواست عضویت جدید!\n\n"
        f"👤 نام: {user.full_name}\n"
        f"🆔 یوزرنیم: @{user.username or 'ندارد'}\n"
        f"🔢 آیدی: {user.id}\n"
        f"📋 نوع مدرک: {proof_type}\n\n"
        f"تایید یا رد کن:"
    )

    try:
        if file_id and proof_type == "اسکرین‌شات":
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=file_id,
                caption=caption,
                reply_markup=reply_markup
            )
        else:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=caption + f"\n\n📝 متن ارسالی: {text}",
                reply_markup=reply_markup
            )
        return True
    except Exception as e:
        logger.error(f"Error sending to admin: {e}")
        return False


# ========== هندلرها ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if await is_member(context.bot, user.id):
        await update.message.reply_text(
            f"✅ سلام {user.first_name}!\n\n"
            f"شما قبلاً عضو کانال TRADEMANVIP هستید.\n\n"
            f"موفق باشید! 🚀"
        )
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("📝 ثبت‌نام در LBank", url=REFERRAL_LINK)],
        [InlineKeyboardButton("✅ ثبت‌نام کردم، تاییدم کن!", callback_data="verify")]
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
        file_id = msg.photo[-1].file_id
        sent = await send_to_admin(context, user, "اسکرین‌شات", file_id=file_id)
    elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith("image/"):
        file_id = msg.document.file_id
        sent = await send_to_admin(context, user, "اسکرین‌شات", file_id=file_id)
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
        await msg.reply_text(
            "❌ خطا در ارسال. لطفاً دوباره امتحان کن."
        )

    return ConversationHandler.END


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        await query.answer("❌ شما ادمین نیستید!", show_alert=True)
        return

    data = query.data
    action, target_user_id = data.split("_", 1)
    target_user_id = int(target_user_id)

    if action == "approve":
        try:
            invite = await context.bot.create_chat_invite_link(
                CHANNEL_ID,
                member_limit=1,
                name=f"user_{target_user_id}"
            )
            await context.bot.send_message(
                chat_id=target_user_id,
                text=(
                    f"🎉 تبریک!\n\n"
                    f"✅ ثبت‌نام شما تایید شد!\n\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"👇 لینک ورود به کانال VIP:\n"
                    f"{invite.invite_link}\n"
                    f"━━━━━━━━━━━━━━━━━━\n\n"
                    f"⚠️ این لینک فقط یک‌بار قابل استفاده است!\n"
                    f"موفق باشی! 🚀"
                )
            )
            await query.edit_message_caption(
                caption=query.message.caption + "\n\n✅ تایید شد و لینک ارسال شد!",
                reply_markup=None
            ) if query.message.caption else await query.edit_message_text(
                text=query.message.text + "\n\n✅ تایید شد و لینک ارسال شد!",
                reply_markup=None
            )
        except Exception as e:
            logger.error(f"Approve error: {e}")
            await query.answer("❌ خطا در ارسال لینک!", show_alert=True)

    elif action == "reject":
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
            await query.edit_message_caption(
                caption=query.message.caption + "\n\n❌ رد شد.",
                reply_markup=None
            ) if query.message.caption else await query.edit_message_text(
                text=query.message.text + "\n\n❌ رد شد.",
                reply_markup=None
            )
        except Exception as e:
            logger.error(f"Reject error: {e}")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ عملیات لغو شد.\n\nبرای شروع مجدد /start بزن."
    )
    return ConversationHandler.END


async def get_my_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 آیدی شما: `{update.effective_user.id}`", parse_mode="Markdown")


# ========== اجرا ==========
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
    app.add_handler(CommandHandler("myid", get_my_id))

    logger.info("✅ TRADEMANVIP Bot started!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
