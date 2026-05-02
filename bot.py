import os
import io
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

WAITING_PROOF = 1

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_main_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("\U0001f4dd \u062b\u0628\u062a\u200c\u0646\u0627\u0645")],
        [KeyboardButton("\U0001f4ac \u067e\u0634\u062a\u06cc\u0628\u0627\u0646\u06cc"), KeyboardButton("\U0001f310 \u0633\u0627\u06cc\u062a")],
        [KeyboardButton("\U0001f4ca \u0686\u0627\u0631\u062a\u200c\u0647\u0627"), KeyboardButton("\U0001f393 \u062f\u0648\u0631\u0647 TCB")]
    ], resize_keyboard=True)


def get_main_inline_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("\U0001f4dd \u062b\u0628\u062a\u200c\u0646\u0627\u0645 \u062f\u0631 LBank", url=REFERRAL_LINK)],
        [InlineKeyboardButton("\u2705 \u062b\u0628\u062a\u200c\u0646\u0627\u0645 \u06a9\u0631\u062f\u0645!", callback_data="verify")]
    ])


def get_main_text(first_name):
    return (
        f"\U0001f44b \u0633\u0644\u0627\u0645 {first_name}\n\n"
        f"\U0001f3af \u0628\u0647 \u0631\u0628\u0627\u062a {LTR}TRADEMANVIP \u062e\u0648\u0634 \u0622\u0645\u062f\u06cc\u062f!\n\n"
        "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"\U0001f3c6 \u0645\u0632\u0627\u06cc\u0627\u06cc \u06a9\u0627\u0646\u0627\u0644 {LTR}TradeMan:\n\n"
        "\U0001f4ca \u0633\u06cc\u06af\u0646\u0627\u0644\u200c\u0647\u0627\u06cc \u0631\u0648\u0632\u0627\u0646\u0647\n"
        "\U0001f4c8 \u062a\u062d\u0644\u06cc\u0644 \u0628\u0627\u0632\u0627\u0631\u0647\u0627\u06cc \u06a9\u0631\u06cc\u067e\u062a\u0648\u060c \u0637\u0644\u0627 \u0648 \u062f\u0644\u0627\u0631\n"
        "\U0001f393 \u0622\u0645\u0648\u0632\u0634\u200c\u0647\u0627\u06cc \u06a9\u0627\u0645\u0644\u0627\u064b \u0631\u0627\u06cc\u06af\u0627\u0646\n"
        "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        "\u0628\u0631\u0627\u06cc \u0639\u0636\u0648\u06cc\u062a:\n\n"
        f"\u2705 \u0631\u0648\u06cc \" \u062b\u0628\u062a\u200c\u0646\u0627\u0645 \u062f\u0631 {LTR}LBank \" \u06a9\u0644\u06cc\u06a9 \u06a9\u0646\u06cc\u062f\n\n"
        f"\u2705 \u062f\u0631 \u0635\u0631\u0627\u0641\u06cc {LTR}LBank \u062b\u0628\u062a\u200c\u0646\u0627\u0645 \u06a9\u0646\u06cc\u062f\n\n"
        "\u2705 \u0628\u0647 \u0647\u0645\u06cc\u0646 \u0635\u0641\u062d\u0647 \u0628\u0631\u06af\u0631\u062f\u06cc\u062f \u0648 \u062f\u06a9\u0645\u0647 \" \u062b\u0628\u062a\u200c\u0646\u0627\u0645 \u06a9\u0631\u062f\u0645! \" \u0631\u0627 \u0628\u0632\u0646\u06cc\u062f\n"
        "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
        "\u26a1\ufe0f \u06a9\u0644 \u0627\u06cc\u0646 \u067e\u0631\u0648\u0633\u0647 \u06a9\u0645\u062a\u0631 \u0627\u0632 \u06f3 \u062f\u0642\u06cc\u0642\u0647 \u0637\u0648\u0644 \u0645\u06cc\u200c\u06a9\u0634\u0647!\n\n"
        f"\U0001f48e \u0628\u0639\u062f \u0627\u0632 \u062a\u0627\u06cc\u06cc\u062f\u060c \u0644\u06cc\u0646\u06a9 \u06a9\u0627\u0646\u0627\u0644 {LTR}TradeMan \u0628\u0631\u0627\u06cc \u0634\u0645\u0627 \u0627\u0631\u0633\u0627\u0644 \u0645\u06cc\u200c\u0634\u0648\u062f!"
    )


async def is_member(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


async def send_to_admin(context, user, proof_type, file_id=None, text=None):
    keyboard = [[
        InlineKeyboardButton("\u2705 \u062a\u0627\u06cc\u06cc\u062f", callback_data=f"approve_{user.id}"),
        InlineKeyboardButton("\u274c \u0631\u062f", callback_data=f"reject_{user.id}")
    ]]
    markup = InlineKeyboardMarkup(keyboard)

    info = (
        f"\U0001f514 \u062f\u0631\u062e\u0648\u0627\u0633\u062a \u0639\u0636\u0648\u06cc\u062a \u062c\u062f\u06cc\u062f!\n\n"
        f"\U0001f464 \u0646\u0627\u0645: {user.full_name}\n"
        f"\U0001f194 \u06cc\u0648\u0632\u0631\u0646\u06cc\u0645: @{user.username or '\u0646\u062f\u0627\u0631\u062f'}\n"
        f"\U0001f522 \u0622\u06cc\u062f\u06cc: {user.id}\n"
        f"\U0001f4cb \u0646\u0648\u0639: {proof_type}"
    )

    try:
        if file_id:
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=file_id, caption=info, reply_markup=markup)
        else:
            await context.bot.send_message(chat_id=ADMIN_ID, text=info + f"\n\n\U0001f4dd \u0645\u062a\u0646: {text}", reply_markup=markup)
        return True
    except Exception as e:
        logger.error(f"Send to admin error: {e}")
        return False


async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "\U0001f4dd \u062b\u0628\u062a\u200c\u0646\u0627\u0645":
        await start(update, context)
    elif text == "\U0001f4ac \u067e\u0634\u062a\u06cc\u0628\u0627\u0646\u06cc":
        await update.message.reply_text(
            "\U0001f4ac \u0628\u0631\u0627\u06cc \u0627\u0631\u062a\u0628\u0627\u0637 \u0628\u0627 \u067e\u0634\u062a\u06cc\u0628\u0627\u0646\u06cc:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("\U0001f4ac \u067e\u0634\u062a\u06cc\u0628\u0627\u0646\u06cc", url="tg://user?id=7274125873")],
                [InlineKeyboardButton("\U0001f519 \u0628\u0627\u0632\u06af\u0634\u062a", callback_data="go_back")]
            ])
        )
    elif text == "\U0001f310 \u0633\u0627\u06cc\u062a":
        await update.message.reply_text(
            "\U0001f310 \u0648\u0628\u200c\u0633\u0627\u06cc\u062a \u0645\u0627:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("\U0001f310 ashkaneftekhar.com", url="https://ashkaneftekhar.com")],
                [InlineKeyboardButton("\U0001f519 \u0628\u0627\u0632\u06af\u0634\u062a", callback_data="go_back")]
            ])
        )
    elif text == "\U0001f393 \u062f\u0648\u0631\u0647 TCB":
        await update.message.reply_text(
            "\U0001f393 \u062f\u0648\u0631\u0647 \u0622\u0645\u0648\u0632\u0634\u06cc TCB \u0631\u0627\u06cc\u06af\u0627\u0646:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("\U0001f4fa \u0645\u0634\u0627\u0647\u062f\u0647 \u062f\u0648\u0631\u0647 TCB", url="https://youtube.com/playlist?list=PLGhV--putKvKDXbR-x5UFd2dccBirQBUg&si=5GVhbWNBd2tplQsA")],
                [InlineKeyboardButton("\U0001f519 \u0628\u0627\u0632\u06af\u0634\u062a", callback_data="go_back")]
            ])
        )
    elif text == "\U0001f4ca \u0686\u0627\u0631\u062a\u200c\u0647\u0627":
        if not await is_member(context.bot, update.effective_user.id):
            await update.message.reply_text(
                "\u26d4\ufe0f \u0628\u0631\u0627\u06cc \u0627\u0633\u062a\u0641\u0627\u062f\u0647 \u0627\u0632 \u0627\u06cc\u0646 \u0642\u0627\u0628\u0644\u06cc\u062a \u0627\u0628\u062a\u062f\u0627 \u0628\u0627\u06cc\u062f \u062b\u0628\u062a\u200c\u0646\u0627\u0645 \u06a9\u0646\u06cc\u062f!\n\n"
                "\u0631\u0648\u06cc \u062f\u06a9\u0645\u0647 \U0001f4dd \u062b\u0628\u062a\u200c\u0646\u0627\u0645 \u0628\u0632\u0646\u06cc\u062f."
            )
            return
        await update.message.reply_text(
            "\U0001f4ca \u0686\u0627\u0631\u062a \u0645\u0648\u0631\u062f \u0646\u0638\u0631 \u0631\u0627 \u0627\u0646\u062a\u062e\u0627\u0628 \u06a9\u0646\u06cc\u062f:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("\U0001f536 BTC/USDT", url="https://www.tradingview.com/chart/?symbol=BYBIT:BTCUSDT.P")],
                [InlineKeyboardButton("\U0001f947 \u0637\u0644\u0627 (XAU/USD)", url="https://www.tradingview.com/chart/?symbol=XAUUSD")],
                [InlineKeyboardButton("\U0001f4c8 Total3", url="https://www.tradingview.com/chart/?symbol=TOTAL3")],
                [InlineKeyboardButton("\U0001f519 \u0628\u0627\u0632\u06af\u0634\u062a", callback_data="go_back")]
            ])
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    if await is_member(context.bot, user.id):
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"\u2705 \u0633\u0644\u0627\u0645 {user.first_name}!\n\u0634\u0645\u0627 \u0639\u0636\u0648 \u06a9\u0627\u0646\u0627\u0644 {LTR}TradeMan \u0647\u0633\u062a\u06cc\u062f. \U0001f680",
            reply_markup=get_main_keyboard()
        )
        return ConversationHandler.END

    await context.bot.send_message(
        chat_id=chat_id,
        text=get_main_text(user.first_name),
        reply_markup=get_main_inline_keyboard()
    )
    await context.bot.send_message(
        chat_id=chat_id,
        text="\u0627\u0632 \u0645\u0646\u0648\u06cc \u0632\u06cc\u0631 \u0627\u0646\u062a\u062e\u0627\u0628 \u06a9\u0646\u06cc\u062f:",
        reply_markup=get_main_keyboard()
    )
    return ConversationHandler.END


async def verify_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if await is_member(context.bot, query.from_user.id):
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="\u2705 \u0634\u0645\u0627 \u0642\u0628\u0644\u0627\u064b \u0639\u0636\u0648 \u06a9\u0627\u0646\u0627\u0644 \u0647\u0633\u062a\u06cc\u062f!"
        )
        return ConversationHandler.END

    with open("/app/uid_sample.png", "rb") as f:
        photo_bytes = f.read()

    await context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=io.BytesIO(photo_bytes),
        caption=(
            "\U0001f4e4 \u0644\u0637\u0641\u0627\u064b \u0628\u0639\u062f \u0627\u0632 \u062b\u0628\u062a\u200c\u0646\u0627\u0645\u060c \u06a9\u062f \u0634\u0646\u0627\u0633\u0647 (UID) \u062d\u0633\u0627\u0628 \u06a9\u0627\u0631\u0628\u0631\u06cc \u062e\u0648\u062f \u0631\u0627 \u0628\u0631\u0627\u06cc \u0645\u0627 \u0628\u0641\u0631\u0633\u062a\u06cc\u062f\n\n"
            "\U0001f4cc \u0645\u0637\u0627\u0628\u0642 \u062a\u0635\u0648\u06cc\u0631 \u0628\u0627\u0644\u0627\u060c UID \u062e\u0648\u062f \u0631\u0627 \u067e\u06cc\u062f\u0627 \u0648 \u0627\u0631\u0633\u0627\u0644 \u06a9\u0646\u06cc\u062f"
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("\U0001f519 \u0628\u0627\u0632\u06af\u0634\u062a", callback_data="go_back")]
        ])
    )
    return WAITING_PROOF


async def go_back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=get_main_text(user.first_name),
        reply_markup=get_main_inline_keyboard()
    )
    return ConversationHandler.END


async def handle_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message
    sent = False

    menu_items = [
        "\U0001f4dd \u062b\u0628\u062a\u200c\u0646\u0627\u0645",
        "\U0001f4ac \u067e\u0634\u062a\u06cc\u0628\u0627\u0646\u06cc",
        "\U0001f310 \u0633\u0627\u06cc\u062a",
        "\U0001f4ca \u0686\u0627\u0631\u062a\u200c\u0647\u0627",
        "\U0001f393 \u062f\u0648\u0631\u0647 TCB"
    ]

    if msg.text in menu_items:
        await handle_menu(update, context)
        return ConversationHandler.END

    if msg.photo:
        sent = await send_to_admin(context, user, "\u0627\u0633\u06a9\u0631\u06cc\u0646\u200c\u0634\u0627\u062a", file_id=msg.photo[-1].file_id)
    elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith("image/"):
        sent = await send_to_admin(context, user, "\u0627\u0633\u06a9\u0631\u06cc\u0646\u200c\u0634\u0627\u062a", file_id=msg.document.file_id)
    elif msg.text:
        uid = msg.text.strip()
        if not uid.upper().startswith("LBA"):
            with open("/app/uid_sample.png", "rb") as f:
                photo_bytes = f.read()
            await msg.reply_photo(
                photo=io.BytesIO(photo_bytes),
                caption=(
                    "\u274c \u06a9\u062f \u0648\u0627\u0631\u062f \u0634\u062f\u0647 \u0645\u0639\u062a\u0628\u0631 \u0646\u06cc\u0633\u062a!\n\n"
                    "\u06a9\u062f \u0634\u0646\u0627\u0633\u0647 (UID) \u062d\u0633\u0627\u0628 \u062e\u0648\u062f \u0647\u0645\u06cc\u0634\u0647 \u0628\u0627 LBA \u0634\u0631\u0648\u0639 \u0645\u06cc\u200c\u0634\u0648\u062f\n"
                    "\u0645\u0627\u0646\u0646\u062f \u062a\u0635\u0648\u06cc\u0631 \u0628\u0627\u0644\u0627\n\n"
                    "\u0644\u0637\u0641\u0627\u064b \u062f\u0648\u0628\u0627\u0631\u0647 \u0627\u0645\u062a\u062d\u0627\u0646 \u06a9\u0646\u06cc\u062f \U0001f504"
                )
            )
            return WAITING_PROOF
        sent = await send_to_admin(context, user, "UID", text=uid)
    else:
        await msg.reply_text("\u274c \u0644\u0637\u0641\u0627\u064b UID \u062d\u0633\u0627\u0628 \u062e\u0648\u062f \u0631\u0627 \u0628\u0641\u0631\u0633\u062a\u06cc\u062f.")
        return WAITING_PROOF

    if sent:
        await msg.reply_text(
            "\u2705 \u062f\u0631\u062e\u0648\u0627\u0633\u062a \u0634\u0645\u0627 \u062b\u0628\u062a \u0634\u062f \u0648 \u062f\u0631 \u062d\u0627\u0644 \u0628\u0631\u0631\u0633\u06cc \u0645\u06cc\u200c\u0628\u0627\u0634\u062f\n\n"
            "\u23f1 \u0645\u0639\u0645\u0648\u0644\u0627\u064b \u062f\u0631 \u06a9\u0645\u062a\u0631 \u0627\u0632 \u06f1 \u0633\u0627\u0639\u062a \u0646\u062a\u06cc\u062c\u0647 \u0627\u0639\u0644\u0627\u0645 \u062e\u0648\u0627\u0647\u062f \u0634\u062f"
        )
    else:
        await msg.reply_text("\u274c \u062e\u0637\u0627 \u062f\u0631 \u0627\u0631\u0633\u0627\u0644. \u0644\u0637\u0641\u0627\u064b \u062f\u0648\u0628\u0627\u0631\u0647 \u0627\u0645\u062a\u062d\u0627\u0646 \u06a9\u0646\u06cc\u062f.")

    return ConversationHandler.END


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if update.effective_user.id != ADMIN_ID:
        await query.answer("\u274c \u0634\u0645\u0627 \u0627\u062f\u0645\u06cc\u0646 \u0646\u06cc\u0633\u062a\u06cc\u062f!", show_alert=True)
        return

    await query.answer()
    data = query.data
    target_user_id = int(data.split("_")[1])

    if data.startswith("approve_"):
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=(
                    "\U0001f389 \u062a\u0628\u0631\u06cc\u06a9!\n\n"
                    "\u2705 \u062b\u0628\u062a\u200c\u0646\u0627\u0645 \u0634\u0645\u0627 \u062a\u0627\u06cc\u06cc\u062f \u0634\u062f!\n"
                    "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
                    "\U0001f3c6 \u0628\u0647 TradeMan \u062e\u0648\u0634 \u0622\u0645\u062f\u06cc\u062f!\n\n"
                    "\U0001f4ca \u062a\u0648\u06cc \u0627\u06cc\u0646 \u06a9\u0627\u0646\u0627\u0644 \u0647\u0631 \u0631\u0648\u0632 \u0628\u0627 \u0647\u0645 \u062a\u0631\u06cc\u062f \u0645\u06cc\u200c\u06a9\u0646\u06cc\u0645 \u0648 \u0645\u0648\u0642\u0639\u06cc\u062a\u200c\u0647\u0627\u06cc \u0637\u0644\u0627\u06cc\u06cc \u0628\u0627\u0632\u0627\u0631 \u0631\u0648 \u0634\u06a9\u0627\u0631 \u0645\u06cc\u200c\u06a9\u0646\u06cc\u0645 \U0001f987\n\n"
                    "\u26a0\ufe0f \u0628\u0644\u0627\u0641\u0627\u0635\u0644\u0647 \u0628\u0639\u062f \u0627\u0632 \u0648\u0631\u0648\u062f\u060c \u067e\u06cc\u0627\u0645\u200c\u0647\u0627\u06cc \u067e\u06cc\u0646 \u0634\u062f\u0647 \u0631\u0627 \u0645\u0637\u0627\u0644\u0639\u0647 \u06a9\u0646\u06cc\u062f \u26a0\ufe0f\n"
                    "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
                    "\U0001f447 \u0627\u0632 \u0637\u0631\u06cc\u0642 \u0644\u06cc\u0646\u06a9 \u0632\u06cc\u0631 \u0648\u0627\u0631\u062f \u0634\u0648\u06cc\u062f:\n\n"
                    f"{INVITE_LINK}\n\n"
                    "\u0645\u0648\u0641\u0642 \u0648 \u067e\u0631\u0633\u0648\u062f \u0628\u0627\u0634\u06cc\u062f \U0001f680"
                )
            )
        except Exception as e:
            logger.error(f"Send error: {e}")
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"\u26a0\ufe0f \u0646\u062a\u0648\u0646\u0633\u062a\u0645 \u067e\u06cc\u0627\u0645 \u0628\u062f\u0645!\n{INVITE_LINK}")

        try:
            if query.message.photo:
                await query.edit_message_caption(caption=(query.message.caption or "") + "\n\n\u2705 \u062a\u0627\u06cc\u06cc\u062f \u0634\u062f!", reply_markup=None)
            else:
                await query.edit_message_text(text=(query.message.text or "") + "\n\n\u2705 \u062a\u0627\u06cc\u06cc\u062f \u0634\u062f!", reply_markup=None)
        except:
            pass

    elif data.startswith("reject_"):
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=(
                    "\u274c \u0645\u062a\u0627\u0633\u0641\u0627\u0646\u0647 \u062b\u0628\u062a\u200c\u0646\u0627\u0645 \u0634\u0645\u0627 \u062a\u0627\u06cc\u06cc\u062f \u0646\u0634\u062f.\n\n"
                    "\u0644\u0637\u0641\u0627\u064b \u0645\u0637\u0645\u0626\u0646 \u0634\u0648\u06cc\u062f \u06a9\u0647 \u0627\u0632 \u0644\u06cc\u0646\u06a9 \u0631\u0641\u0631\u0627\u0644 \u0645\u0627 \u062f\u0631 LBank \u062b\u0628\u062a\u200c\u0646\u0627\u0645 \u06a9\u0631\u062f\u0647\u200c\u0627\u06cc\u062f \u0648 \u0627\u0632 \u062f\u06a9\u0645\u0647 \u0634\u0631\u0648\u0639 \u0645\u062c\u062f\u062f \u0627\u0633\u062a\u0641\u0627\u062f\u0647 \u06a9\u0646\u06cc\u062f\n\n"
                    "\u062f\u0631 \u0635\u0648\u0631\u062a \u0646\u06cc\u0627\u0632 \u0628\u0647 \u0631\u0627\u0647\u0646\u0645\u0627\u06cc\u06cc\u060c \u0627\u0632 \u062f\u06a9\u0645\u0647 \u067e\u0634\u062a\u06cc\u0628\u0627\u0646\u06cc \u06a9\u0645\u06a9 \u0628\u06af\u06cc\u0631\u06cc\u062f \U0001f447"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("\U0001f504 \u0634\u0631\u0648\u0639 \u0645\u062c\u062f\u062f", url="https://t.me/trademanvipbot?start=start")],
                    [InlineKeyboardButton("\U0001f4ac \u067e\u0634\u062a\u06cc\u0628\u0627\u0646\u06cc", url="tg://user?id=7274125873")]
                ])
            )
        except Exception as e:
            logger.error(f"Reject error: {e}")

        try:
            if query.message.photo:
                await query.edit_message_caption(caption=(query.message.caption or "") + "\n\n\u274c \u0631\u062f \u0634\u062f.", reply_markup=None)
            else:
                await query.edit_message_text(text=(query.message.text or "") + "\n\n\u274c \u0631\u062f \u0634\u062f.", reply_markup=None)
        except:
            pass


async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    reply = update.message.reply_to_message
    if reply and reply.photo:
        await update.message.reply_text("File ID:\n" + reply.photo[-1].file_id)
    elif update.message.photo:
        await update.message.reply_text("File ID:\n" + update.message.photo[-1].file_id)
    else:
        await update.message.reply_text("\u0631\u0648\u06cc \u0639\u06a9\u0633 reply \u06a9\u0646 \u0648 /getid \u0628\u0632\u0646!")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("\u274c \u0639\u0645\u0644\u06cc\u0627\u062a \u0644\u063a\u0648 \u0634\u062f.\n\n\u0628\u0631\u0627\u06cc \u0634\u0631\u0648\u0639 \u0645\u062c\u062f\u062f /start \u0628\u0632\u0646.")
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
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(go_back_handler, pattern="^go_back$")
        ],
        per_user=True
    )

    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.Regex(
            "^(\U0001f4dd \u062b\u0628\u062a\u200c\u0646\u0627\u0645|\U0001f4ac \u067e\u0634\u062a\u06cc\u0628\u0627\u0646\u06cc|\U0001f310 \u0633\u0627\u06cc\u062a|\U0001f4ca \u0686\u0627\u0631\u062a\u200c\u0647\u0627)$"
        ),
        handle_menu
    ))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(go_back_handler, pattern="^go_back$"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^(approve|reject)_"))
    app.add_handler(CommandHandler("getid", get_file_id))

    logger.info("TRADEMANVIP Bot started!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
