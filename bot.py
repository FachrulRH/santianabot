import os

from copilot import Copilot
from dotenv import load_dotenv
import data

from telegram import (
    ReplyKeyboardMarkup,
    Update,
    KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery,
)

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler,
)

(ENTRY_STATE, QUESTION_STATE, DESC_STATE) = range(3)


def _generate_copilot(prompt: str):
    copilot = Copilot()
    c = copilot.get_answer(prompt)

    return c


async def start(update: Update = None, context: ContextTypes.DEFAULT_TYPE = None, query: CallbackQuery = None):
    button = [[KeyboardButton(text="Santiana AI")], [KeyboardButton(text="Program Santiana NC")]]

    reply_markup = ReplyKeyboardMarkup(
        button, resize_keyboard=True,
    )

    if query:
        await query.message.reply_text(
            "Hai perkenalkan saya dengan Santiana Bot, Bot Telegram resmi dari Santiana Nutrition C. Silahkan pilih menu berikut",
            reply_markup=reply_markup,
        )
    elif update:
        await update.message.reply_text(
            "Hai perkenalkan saya dengan Santiana Bot, Bot Telegram resmi dari Santiana Nutrition C. Silahkan pilih menu berikut",
            reply_markup=reply_markup,
        )

    return ENTRY_STATE


async def desc_handler(update: Update, context: ContextTypes):
    keyboard = [
        [InlineKeyboardButton("Apa itu Santiana NC ?", callback_data='Apa itu Santiana NC ?')],
        [InlineKeyboardButton("Apa saja solusi yang ditawarkan Santiana NC ?",
                              callback_data='Apa saja solusi yang ditawarkan Santiana NC ?')],
        [InlineKeyboardButton("Program apa yang dapat dibantu oleh Santiana Nutrition Club ?",
                              callback_data='Program apa yang dapat  dibantu oleh Santiana Nutrition Club ?')],
        [InlineKeyboardButton("Menu Program Santiana NC", callback_data='Menu Program Santiana NC')],
        [InlineKeyboardButton("Menu Program Santiana Nutri Sharkepro",
                              callback_data='Menu Program Santiana Nutri Sharkepro')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Santiana Nutrition Club (Santiana NC) adalah bagian dari perusahaan Herbalife, sebuah komunitas yang diakui "
        "dalam bidang kesehatan dan kebugaran. Komunitas ini didirikan dengan tujuan mendukung customer dalam "
        "menerapkan pola hidup yang sehat dan aktif. Silakan pilih pertanyaan dari menu berikut.",
        reply_markup=reply_markup,
    )

    return DESC_STATE


async def inline_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    answer = data.answer

    if query.data == 'back':
        await query.delete_message()
        await start(context=context, query=query)
        return ENTRY_STATE
    else:
        response = answer.get(query.data, "Maaf kami tidak mengerti tentang apa yang anda tanyakan")
        await query.delete_message()
        await query.message.reply_text(f'pertanyaan terkait :\n{query.data}\n\n{response}')

        keyboard = [
            [InlineKeyboardButton("Apa itu Santiana NC ?", callback_data='Apa itu Santiana NC ?')],
            [InlineKeyboardButton("Apa saja solusi yang ditawarkan Santiana NC ?",
                                  callback_data='Apa saja solusi yang ditawarkan Santiana NC ?')],
            [InlineKeyboardButton("Program apa yang dapat dibantu oleh Santiana Nutrition Club ?",
                                  callback_data='Program apa yang dapat dibantu oleh Santiana Nutrition Club ?')],
            [InlineKeyboardButton("Menu Program Santiana NC", callback_data='Menu Program Santiana NC')],
            [InlineKeyboardButton("Menu Program Santiana Nutri Sharkepro",
                                  callback_data='Menu Program Santiana Nutri Sharkepro')],
            [InlineKeyboardButton("Back", callback_data='back')],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(chat_id=query.message.chat_id, text='Apakah ada yang ingin anda ketahui lagi ?',
                                       reply_markup=reply_markup)
        return DESC_STATE


async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text('Bye!')
    return ConversationHandler.END


async def pre_query_handler(update: Update, context: ContextTypes):
    button = [[KeyboardButton(text="Back")]]
    reply_markup = ReplyKeyboardMarkup(
        button, resize_keyboard=True
    )

    await update.message.reply_text(
        "Hai saya Santiana AI, silahkan berikan saya pertanyaan terkait keluhan anda mengenai gaya hidup sehat. Jika ingin kembali ke menu sebelumnya silahkan klik tombol back.",
        reply_markup=reply_markup,
    )

    return QUESTION_STATE


async def pre_query_answer_handler(update: Update, context: ContextTypes):
    button = [[KeyboardButton(text="Back")]]
    reply_markup = ReplyKeyboardMarkup(
        button, resize_keyboard=True
    )

    question = update.message.text

    answer = _generate_copilot(question)
    context.user_data['answer'] = answer

    await update.message.reply_text(
        answer + f"\n\nApakah ada yang ingin anda tanyakan kembali ?. Jika tidak tekan tombol back pada menu, Terima Kasih.",
        reply_markup=reply_markup,
    )
    return QUESTION_STATE


if __name__ == '__main__':
    load_dotenv()

    application = (
        Application.builder()
        .token(os.getenv("TELEGRAM_BOT_TOKEN"))
        .read_timeout(100)
        .get_updates_read_timeout(100).build()
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ENTRY_STATE: [
                CallbackQueryHandler(desc_handler),
                MessageHandler(filters.Regex('^Program Santiana NC$'), desc_handler),
                MessageHandler(filters.Regex('^Santiana AI$'), pre_query_handler),
            ],
            DESC_STATE: [
                CallbackQueryHandler(inline_button_callback),
            ],
            QUESTION_STATE: [
                MessageHandler(filters.Regex('^Back$'), start),
                MessageHandler(filters.TEXT, pre_query_answer_handler),
            ],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)

    print("Bot is running...")
    application.run_polling()
