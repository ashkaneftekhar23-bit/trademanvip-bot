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
BOT_TOKEN = "8647319022:AAF_Ij5kwhIaQMNFK07XXfjrehHSPeajemM"
CHANNEL_ID = -1002180889746
REFERRAL_LINK = "https://www.lbank.com/en-US/login/?icode=TRADELAND"
REFERRAL_CODE = "TRADELAND"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDy6yfvPImhq27f6v2GVM2lOg4MgchNyug")

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


# ========== تایید با Gemini ==========
async def verify_with_gemini(image_data: bytes = None, uid_text: str = None) -> tuple[bool, str]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    if image_data:
        b64 = base64.b64encode(image_data).decode()
        parts = [
            {
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": b64
                }
            },
            {
                "text": f"""این اسکرین‌شات را بررسی کن:
1. آیا مربوط به صرافی LBank است؟
2. آیا نشان می‌دهد کاربر ثبت‌نام کرده یا وارد شده؟
3. آیا کد رفرال '{REFERRAL_CODE}' یا نشانه‌ای از ثبت‌نام با رفرال دیده می‌شود؟

فقط با JSON پاسخ بده (بدون کد بلاک):
{{"valid": true یا false, "reason": "دلیل به فارسی"}}"""
            }
        ]
    else:
        parts = [
            {
                "text": f"""کاربر این متن را برای تایید ثبت‌نام در LBank ارسال کرده: "{uid_text}"

بررسی کن:
- آیا این یک UID عددی معتبر LBank به نظر می‌رسد؟ (معمولاً ۸ تا ۱۲ رقم)
- یا آیا اطلاعات ثبت‌نام معتبری است؟

فقط با JSON پاسخ بده (بدون کد بلاک):
{{"valid": true یا false, "reason": "دلیل به فارسی"}}"""
            }
        ]

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 200}
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(url, json=payload)
            data = r.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            text = text.replace("```json", "").replace("```", "").strip()
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                result = json.loads(match.group())
                return result.get("valid", False), result.get("reason", "")
    except Exception as e:
        logger.error(f"Gemini error: {e}")

    return False, "خطا در بررسی. لطفاً دوباره امتحان کن."


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

    await msg.reply_text("⏳ در حال بررسی... لطفاً چند ثانیه صبر کن")

    valid = False
    reason = ""

    if msg.photo:
        photo = msg.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        image_data = await file.download_as_bytearray()
        valid, reason = await verify_with_gemini(image_data=bytes(image_data))

    elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith("image/"):
        file = await context.bot.get_file(msg.document.file_id)
        image_data = await file.download_as_bytearray()
        valid, reason = await verify_with_gemini(image_data=bytes(image_data))

    elif msg.text:
        valid, reason = await verify_with_gemini(uid_text=msg.text.strip())

    else:
        await msg.reply_text("❌ لطفاً اسکرین‌شات یا UID ارسال کن.")
        return WAITING_PROOF

    if valid:
        try:
            invite = await context.bot.create_chat_invite_link(
                CHANNEL_ID,
                member_limit=1,
                name=f"user_{user.id}"
            )
            await msg.reply_text(
                f"🎉 تبریک {user.first_name}!\n\n"
                f"✅ ثبت‌نام تایید شد!\n\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"👇 لینک ورود به کانال VIP:\n"
                f"{invite.invite_link}\n"
                f"━━━━━━━━━━━━━━━━━━\n\n"
                f"⚠️ این لینک فقط یک‌بار قابل استفاده است!\n"
                f"موفق باشی! 🚀"
            )
            return ConversationHandler.END
        except Exception as e:
            logger.error(f"Invite error: {e}")
            await msg.reply_text("❌ خطا در ساخت لینک. لطفاً با ادمین تماس بگیر.")
            return ConversationHandler.END
    else:
        await msg.reply_text(
            f"❌ تایید نشد!\n\n"
            f"دلیل: {reason}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"لطفاً:\n"
            f"• اسکرین‌شات واضح‌تری بفرست\n"
            f"• یا UID حسابت رو بنویس\n"
            f"• یا از لینک رفرال دوباره ثبت‌نام کن"
        )
        return WAITING_PROOF


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ عملیات لغو شد.\n\n"
        "برای شروع مجدد /start بزن."
    )
    return ConversationHandler.END


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

    logger.info("✅ TRADEMANVIP Bot started!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
