from dotenv import load_dotenv
import os
from django.conf import settings
from telegram import KeyboardButton, Update
import telegram
from telegram.ext import Filters
from telegram.ext import CallbackContext
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, PreCheckoutQueryHandler
from telegram import ReplyKeyboardMarkup, ParseMode, LabeledPrice
from .models import *
from .bot_tools import *


CURRENT_EVENT = Event.objects.get_current()
SECTIONS = CURRENT_EVENT.sections.all()

states_database = {}
main_menu_keyboard = [['Программа', 'Задать вопрос спикеру', 'Зарегистрироваться'], ['Донат']]
contact_keyboard = [['Отправить контакты', 'Не отправлять контакты']]
accept_keyboard = [['Разрешить сохранение своих данных', 'Отказать от сохранения']]


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        text='Здравствуйте. Это официальный бот по поддержке участников 🤖.',
        reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return 'MAIN_MENU'


def main_menu(update: Update, context: CallbackContext):
    user_reply = update.effective_message.text
    if user_reply == 'Программа' or user_reply == 'Задать вопрос спикеру':
        events_keyboard = list(map(lambda keyboard_row: [button.name for button in keyboard_row], chunk(CURRENT_EVENT.sections.all(), 2)))
        events_keyboard.append(['В главное меню'])
        update.message.reply_text(
            text='Выберите пожалуйста, какое направление вас интересует',
            reply_markup=ReplyKeyboardMarkup(events_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'CHOOSE_SECTION'

    elif user_reply == 'Зарегистрироваться':
        update.message.reply_text(
            text='Введите пожалуйста название компании и вашу должность, желательно в такой порядке и через запятую.',
            reply_markup=ReplyKeyboardMarkup([['Главное меню']], resize_keyboard=True, one_time_keyboard=True)
        )
        return 'REGISTRATION'

    elif user_reply == 'Донат':
        update.message.reply_text(
            text='Напишите, какую сумму вы хотели бы пожертвовать'
        )
        return 'DONATION'


def choose_section(update: Update, context: CallbackContext):
    user_reply = update.effective_message.text

    if user_reply == 'В главное меню':
        update.message.reply_text(
            text='Возврат в Главное меню',
            reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
            )
        return 'MAIN_MENU'

    try:
        chosen_section = SECTIONS.get(name=user_reply)
        possible_blocks = chosen_section.blocks.all()
        blocks_keyboard = [[f'{block.name} | {chosen_section.name}'] for block in possible_blocks]
        blocks_keyboard.append(['В главное меню'])
        update.message.reply_text(text='Выберите из списка',
                                  reply_markup=ReplyKeyboardMarkup(blocks_keyboard,
                                                                   resize_keyboard=True,
                                                                   one_time_keyboard=True))
        return 'CHOOSE_BLOCK'

    except Exception:
        update.message.reply_text(text='Ошибка ❌',
                                  reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True,
                                                                   one_time_keyboard=True)
                                  )
        return 'MAIN_MENU'


def choose_block(update: Update, context: CallbackContext):
    user_reply = update.effective_message.text
    if user_reply == 'В главное меню':
        update.message.reply_text(
            text='Возврат в Главное меню',
            reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
            )
        return 'MAIN_MENU'
    try:
        chosen_block, chosen_section = map(lambda x: x.strip(), user_reply.split('|'))
        chosen_section = CURRENT_EVENT.sections.get(name=chosen_section)
        chosen_block = chosen_section.blocks.get(name=chosen_block)

        blocks_keyboard = [[f'{block.name} | {chosen_section.name}'] for block in chosen_section.blocks.all()]
        blocks_keyboard.append(['В главное меню'])
        update.message.reply_text(text=build_timetable(chosen_block),
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=ReplyKeyboardMarkup(blocks_keyboard,
                                                                   resize_keyboard=True,
                                                                   one_time_keyboard=True))

        return 'CHOOSE_BLOCK'
    except Exception:
        update.message.reply_text(text='Ошибка ❌',
                                  reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True,
                                                                   one_time_keyboard=True)
                                  )
        return 'MAIN_MENU'


def registration(update: Update, context: CallbackContext):
    user_reply = update.message.text

    if user_reply:
        if user_reply == 'В главное меню':
            update.message.reply_text(
                text='Возврат в Главное меню',
                reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
                )
            return 'MAIN_MENU'
        user_name = update.message.from_user.name
        user_lastname = update.message.from_user.last_name
        user_telegram_id = update.message.from_user.id
        BotUser.objects.create(
            name=user_name,
            surname=user_lastname,
            company_position=update.message.text,
            telegram_id=user_telegram_id
        )
        print(BotUser.objects.all())
        update.message.reply_text(
            text='Регистрация успешна.',
            reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'MAIN_MENU'


def donate(update: Update, context: CallbackContext):
    payment_sum = validate_sum(update.message.text)

    chat_id = update.message.chat_id
    title = f"Донат мероприятию {CURRENT_EVENT}"
    description = "Добровольное пожертвование организаторам мероприятию"
    payload = "Custom-Payload"
    currency = "RUB"
    prices = [LabeledPrice("Test", payment_sum)]

    context.bot.send_invoice(
        provider_token='381764678:TEST:40794',
        chat_id=chat_id,
        title=title,
        description=description,
        payload=payload,
        currency=currency,
        prices=prices,
        start_parameter=None
    )

def precheckout_callback(update: Update, context: CallbackContext):
    query = update.pre_checkout_query

    if query.invoice_payload != "Custom-Payload":
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        query.answer(ok=True)

def handle_user_reply(update: Update, context: CallbackContext):
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
        user_id = update.message.from_user.id

    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return

    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = states_database.get(chat_id)

    states_functions = {
        'START': start,
        'MAIN_MENU': main_menu,
        'CHOOSE_SECTION': choose_section,
        'REGISTRATION': registration,
        'CHOOSE_BLOCK': choose_block,
        'DONATION': donate,
    
    }

    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    states_database.update({chat_id: next_state})


def main():
    load_dotenv()
    token = os.getenv('TG_API_TOKEN')
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', handle_user_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_user_reply))
    dispatcher.add_handler(CallbackQueryHandler(handle_user_reply))
    dispatcher.add_handler(MessageHandler(Filters.contact, registration))
    dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    updater.start_polling()


if __name__ == '__main__':
    main()
