from dotenv import load_dotenv
import os
from django.conf import settings
from telegram import KeyboardButton, Update
import telegram
from telegram.ext import Filters
from telegram.ext import CallbackContext
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ParseMode
from .models import *
from .bot_tools import chunk, build_timetable

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
            text='Введите пожалуйста название компании, в которой вы работаете.',
            reply_markup=ReplyKeyboardMarkup([['Главное меню']], resize_keyboard=True, one_time_keyboard=True)
        )
        return 'REGISTRATION'

    elif user_reply == 'Донат':
        update.message.reply_text(
            text='Напишите, какую сумму вы хотели бы пожертвовать'
        )
        return ''


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
        user_name = update.message.from_user.first_name
        user_lastname = update.message.from_user.last_name
        user_telegram_id = update.message.from_user.id
        user, is_created = BotUser.objects.get_or_create(
            name=user_name,
            surname=user_lastname,
            company=update.message.text,
            defaults={'telegram_id':user_telegram_id}
        )
        if not is_created:
            update.message.reply_text(
                text='Вы уже зарегистрированы.',
                reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
            )
            return 'MAIN_MENU'
        elif is_created:
            update.message.reply_text(
                text='Введите пожалуйста вашу должность.',
                reply_markup=ReplyKeyboardMarkup([['Назад', 'В главное меню']], resize_keyboard=True, one_time_keyboard=True)
            )
            return 'REGISTRATION_END'


def registration_end(update: Update, context: CallbackContext):
    user_reply = update.message.text

    if user_reply:
        if user_reply == 'В главное меню':
            update.message.reply_text(
                text='Возврат в Главное меню',
                reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
                )
            return 'MAIN_MENU'

        elif user_reply == 'Назад':
            update.message.reply_text(
                text='Введите название компании.',
                reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
                )
            return 'REGISTRATION'
        user_db_info = BotUser.objects.get(telegram_id=update.message.from_user.id)
        user_db_info.position = user_reply
        user_db_info.save()
        update.message.reply_text(
            text='Вы успешно зарегистрированы.',
            reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'MAIN_MENU'


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
        'REGISTRATION_END': registration_end,
        'CHOOSE_BLOCK': choose_block,
    
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
    updater.start_polling()


if __name__ == '__main__':
    main()
