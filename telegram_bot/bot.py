from dotenv import load_dotenv
import os
from django.conf import settings
from telegram import KeyboardButton, Update
from telegram.ext import Filters
from telegram.ext import CallbackContext
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup


states_database = {}
main_menu_keyboard = [['Программа', 'Задать вопрос спикеру', 'Зарегистрироваться'], ['Донат']]
events_keyboard =  [['Вступительные мероприятия', 'Поток "Эверест"'],['Поток "Альпы"', 'Заключительные мероприятия'], ['В главное меню']] 
contact_keyboard = [['Отправить контакты', 'Не отправлять контакты']]


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        text='Здравствуйте. Это официальный бот по поддержке участников 🤖.',
        reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return 'MAIN_MENU'


def main_menu(update: Update, context: CallbackContext):
    user_reply = update.effective_message.text
    if user_reply == 'Программа' or user_reply == 'Задать вопрос спикеру':
        update.message.reply_text(
            text='Выберите пожалуйста, какое направление вас интересует',
            reply_markup=ReplyKeyboardMarkup(events_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'CHOICE_EVENT'

    elif user_reply == 'Зарегистрироваться':
        update.message.reply_text(
            text='Мы сохраним ваши данные',
            # reply_markup=ReplyKeyboardMarkup(, resize_keyboard=True)
        )
        return 'REGISTRATION'

    elif user_reply == 'Донат':
        update.message.reply_text(
            text='Напишите, какую сумму вы хотели бы пожертвовать'
        )
        return ''


def choice_event(update: Update, context: CallbackContext):
    user_reply = update.effective_message.text

    if user_reply == 'Вступительные мероприятия':
        update.message.reply_text(
            text='Выберите из списка'
        )
    
    elif user_reply == 'В главное меню':
        update.message.reply_text(
            text='Возврат в Главное меню',
            reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
            )
        return 'MAIN_MENU'


def registration(update: Update, context: CallbackContext):
    if update.message.text:
        #Логика сохранения данных в БД
        contact = update.effective_message.contact
        print(contact)
        user_name = update.message.from_user.name
        user_lastname = update.message.from_user.last_name
        user_phonenumber = update.message.from_user
        user_telegram_id = update.message.from_user.id
        update.message.reply_text(
            text='Регистрация успешна.',
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
        'CHOICE_EVENT': choice_event,
        'REGISTRATION': registration
    
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
