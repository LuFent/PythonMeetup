from email import message
from dotenv import load_dotenv
import os
from django.conf import settings
from telegram import KeyboardButton, Update
import telegram
from telegram.ext import Filters
from telegram.ext import CallbackContext
from telegram.ext import Updater, filters
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, PreCheckoutQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ParseMode, LabeledPrice
from .models import *
from .bot_tools import *


states_database = {}
main_menu_keyboard = [['Программа', 'Задать вопрос спикеру', 'Познакомиться'], ['Донат']]
contact_keyboard = [['Отправить контакты', 'Не отправлять контакты']]
accept_keyboard = [['Разрешить сохранение своих данных', 'Отказать от сохранения']]


def start(update: Update, context: CallbackContext):
    current_event = Event.objects.get_current()
    if not current_event:
        update.message.reply_text(
            text='Здравствуйте. Это официальный бот по поддержке участников. Необходимо создать мероприятие.',
        )
        return
    context.user_data['current_event'] = current_event
    context.user_data['sections'] = current_event.sections.all()

    visitor, _ = Access.objects.get_or_create(level="Посетитель")
    speaker, _ = Access.objects.get_or_create(level="Спикер")
    organizer, _ = Access.objects.get_or_create(level="Организатор")
    moderator, _ = Access.objects.get_or_create(level="Модератор")

    user, _ = BotUser.objects.get_or_create(telegram_id=update.message.from_user.id)
    context.user_data['participant'], _ = Participant.objects.get_or_create(
        user=user,
        event=current_event,
        defaults={'level': visitor},
    )
    if context.user_data['participant'].level == speaker:
        main_menu_keyboard = [
            ['Программа', 'Задать вопрос спикеру', 'Познакомиться'],
            ['Донат'],
            ['Посмотреть присланные вопросы'],
        ]
    else:
        main_menu_keyboard = [
            ['Программа', 'Задать вопрос спикеру', 'Познакомиться'],
            ['Донат'],
        ]
    update.message.reply_text(
        text='Здравствуйте. Это официальный бот по поддержке участников 🤖.',
        reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return 'MAIN_MENU'


def main_menu(update: Update, context: CallbackContext):
    current_event = context.user_data['current_event']
    participant = context.user_data['participant']
    if update.callback_query:
        user_reply = update.callback_query.data
        # chat_id = update.callback_query.message.chat_id
        # contact = update.effective_message.contact
        # update.effective_chat.send_contact()
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Посмотреть контакт", url=f'tg://User?id={participant.user.telegram_id}')]])
        context.bot.send_message(
            user_reply,
            text=f'С вами хочет пообщаться {participant.user.name} {participant.user.surname}\n{participant.user.company}\n{participant.user.position}',
            reply_markup=reply_markup,
        )

        return 'MAIN_MENU'
    user_reply = update.effective_message.text
    if user_reply == 'Программа':
        events_keyboard = list(map(lambda keyboard_row: [button.name for button in keyboard_row], chunk(current_event.sections.all(), 2)))
        events_keyboard.append(['В главное меню'])
        update.message.reply_text(
            text='Выберите пожалуйста, какое направление вас интересует',
            reply_markup=ReplyKeyboardMarkup(events_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'CHOOSE_SECTION'

    elif user_reply == 'Задать вопрос спикеру':
        events_keyboard = list(map(lambda keyboard_row: [button.name for button in keyboard_row], chunk(current_event.sections.all(), 2)))
        events_keyboard.append(['В главное меню'])
        update.message.reply_text(
            text='Выберите пожалуйста, какое направление вас интересует',
            reply_markup=ReplyKeyboardMarkup(events_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'CHOOSE_SECTION_FOR_QUESTION'

    elif user_reply == 'Познакомиться':
        if not participant.user.position:
            update.message.reply_text(
                text='Введите пожалуйста название компании, в которой вы работаете.',
                reply_markup=ReplyKeyboardMarkup([['Главное меню']], resize_keyboard=True, one_time_keyboard=True)
            )
            return 'REGISTRATION'
        for user in BotUser.objects.all():
            if user.position and user != participant.user:
                text = f'{user.name} {user.surname}\n{user.company}\n{user.position}'
                reply_markup = InlineKeyboardMarkup(
                    [[InlineKeyboardButton(
                        "Предложить пообщаться",
                        callback_data=user.telegram_id),
                    ]])
                update.message.reply_text(
                    text=text,
                    reply_markup=reply_markup,
                )
        return 'MAIN_MENU'
            

    elif user_reply == 'Донат':
        update.message.reply_text(
            text='Напишите, какую сумму вы хотели бы пожертвовать'
        )
        return 'DONATION'

    elif user_reply == 'Посмотреть присланные вопросы':
        for question in context.user_data['participant'].got_questions.all():
            update.message.reply_text(
                text=f'Вопрос от {question.participant.user}\n{question.text}',
                reply_markup=ReplyKeyboardMarkup([['Главное меню']], resize_keyboard=True, one_time_keyboard=True)
            )
        return 'REGISTRATION'


def choose_section(update: Update, context: CallbackContext):
    user_reply = update.effective_message.text
    current_event = context.user_data['current_event']
    sections = context.user_data['sections']
    if user_reply == 'В главное меню':
        update.message.reply_text(
            text='Возврат в Главное меню',
            reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
            )
        return 'MAIN_MENU'

    if user_reply == 'Назад':
        events_keyboard = list(map(lambda keyboard_row: [button.name for button in keyboard_row],
                                   chunk(current_event.sections.all(), 2)))
        events_keyboard.append(['В главное меню'])
        update.message.reply_text(
            text='Возврат к списку частей',
            reply_markup=ReplyKeyboardMarkup(events_keyboard, resize_keyboard=True, one_time_keyboard=True)
            )
        return 'CHOOSE_SECTION'

    try:
        chosen_section = sections.get(name=user_reply)
        possible_blocks = chosen_section.blocks.all()
        blocks_keyboard = [[f'{block.name} | {chosen_section.name}'] for block in chosen_section.blocks.all()]
        blocks_keyboard.append(['В главное меню', 'Назад'])
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
    current_event = context.user_data['current_event']
    if user_reply == 'В главное меню':
        update.message.reply_text(
            text='Возврат в Главное меню',
            reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
            )
        return 'MAIN_MENU'

    if user_reply == 'Назад':
        events_keyboard = list(map(lambda keyboard_row: [button.name for button in keyboard_row],
                                   chunk(current_event.sections.all(), 2)))
        events_keyboard.append(['В главное меню'])
        update.message.reply_text(
            text='Возврат к списку частей',
            reply_markup=ReplyKeyboardMarkup(events_keyboard, resize_keyboard=True, one_time_keyboard=True)
            )
        return 'CHOOSE_SECTION'

    try:
        chosen_block, chosen_section = map(lambda x: x.strip(), user_reply.split('|'))
        chosen_section = current_event.sections.get(name=chosen_section)
        chosen_block = chosen_section.blocks.get(name=chosen_block)

        blocks_keyboard = [[f'{block.name} | {chosen_section.name}'] for block in chosen_section.blocks.all()]
        blocks_keyboard.append(['В главное меню', 'Назад'])
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


def choose_section_for_question(update: Update, context: CallbackContext):
    user_reply = update.effective_message.text
    current_event = context.user_data['current_event']
    sections = context.user_data['sections']
    if user_reply == 'В главное меню':
        update.message.reply_text(
            text='Возврат в Главное меню',
            reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
            )
        return 'MAIN_MENU'

    if user_reply == 'Назад':
        events_keyboard = list(map(lambda keyboard_row: [button.name for button in keyboard_row],
                                   chunk(current_event.sections.all(), 2)))
        events_keyboard.append(['В главное меню'])
        update.message.reply_text(
            text='Возврат к списку частей',
            reply_markup=ReplyKeyboardMarkup(events_keyboard, resize_keyboard=True, one_time_keyboard=True)
            )
        return 'CHOOSE_SECTION'

    try:
        chosen_section = sections.get(name=user_reply)
        possible_blocks = chosen_section.blocks.all()
        blocks_keyboard = [[f'{block.name} | {chosen_section.name}'] for block in chosen_section.blocks.all()]
        blocks_keyboard.append(['В главное меню', 'Назад'])
        update.message.reply_text(text='Выберите из списка',
                                  reply_markup=ReplyKeyboardMarkup(blocks_keyboard,
                                                                   resize_keyboard=True,
                                                                   one_time_keyboard=True))
        return 'CHOOSE_BLOCK_FOR_QUESTION'

    except Exception:
        update.message.reply_text(text='Ошибка ❌',
                                  reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True,
                                                                   one_time_keyboard=True)
                                  )
        return 'MAIN_MENU'


def choose_block_for_question(update: Update, context: CallbackContext):
    user_reply = update.effective_message.text
    current_event = context.user_data['current_event']
    if user_reply == 'В главное меню':
        update.message.reply_text(
            text='Возврат в Главное меню',
            reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
            )
        return 'MAIN_MENU'

    if user_reply == 'Назад':
        events_keyboard = list(map(lambda keyboard_row: [button.name for button in keyboard_row],
                                   chunk(current_event.sections.all(), 2)))
        events_keyboard.append(['В главное меню'])
        update.message.reply_text(
            text='Возврат к списку частей',
            reply_markup=ReplyKeyboardMarkup(events_keyboard, resize_keyboard=True, one_time_keyboard=True)
            )
        return 'CHOOSE_SECTION_FOR_QUESTION'

    # try:
    chosen_block, chosen_section = map(lambda x: x.strip(), user_reply.split('|'))
    chosen_section = current_event.sections.get(name=chosen_section)
    chosen_block = chosen_section.blocks.get(name=chosen_block)

    author_keyboard = [[f'{presentation.speaker.user} | {presentation.name}'] for presentation in chosen_block.presentations.all()]
    author_keyboard.append(['В главное меню', 'Назад'])
    update.message.reply_text(text='Выберите спикера, которому хотите задать вопрос',
                                parse_mode=ParseMode.MARKDOWN,
                                reply_markup=ReplyKeyboardMarkup(author_keyboard,
                                                                resize_keyboard=True,
                                                                one_time_keyboard=True))

    return 'CHOOSE_SPEAKER'

    # except Exception:
    #     update.message.reply_text(text='Ошибка ❌',
    #                               reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True,
    #                                                                one_time_keyboard=True)
    #                               )
    #     return 'MAIN_MENU'


def choose_speaker(update: Update, context: CallbackContext):
    user_reply = update.message.text
    current_event = context.user_data['current_event']
    if user_reply == 'В главное меню':
        update.message.reply_text(
            text='Возврат в Главное меню',
            reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
            )
        return 'MAIN_MENU'

    if user_reply == 'Назад':
        chosen_block, chosen_section = map(lambda x: x.strip(), user_reply.split('|'))
        chosen_section = current_event.sections.get(name=chosen_section)
        chosen_block = chosen_section.blocks.get(name=chosen_block)
        blocks_keyboard = [[f'{block.name} | {chosen_section.name}'] for block in chosen_section.blocks.all()]
        blocks_keyboard.append(['В главное меню', 'Назад'])
        update.message.reply_text(
            text='Возврат к списку блоков',
            reply_markup=ReplyKeyboardMarkup(blocks_keyboard, resize_keyboard=True, one_time_keyboard=True)
            )
        return 'CHOOSE_BLOCK_FOR_QUESTION'

    name, surname = user_reply.split("|")[0].strip().split()
    context.user_data['speaker'] = Participant.objects.get(
        user__name=name,
        user__surname=surname,
    )
    update.message.reply_text(
        text='Напишите пожалуйста вопрос'
    )
    return 'ASK_QUESTION'


def ask_question(update: Update, context: CallbackContext):
    user_reply = update.effective_message.text
    current_event = context.user_data['current_event']
    if user_reply == 'В главное меню':
        update.message.reply_text(
            text='Возврат в Главное меню',
            reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
            )
        return 'MAIN_MENU'
    if user_reply == 'Назад':
        chosen_block, chosen_section = map(lambda x: x.strip(), user_reply.split('|'))
        chosen_section = current_event.sections.get(name=chosen_section)
        chosen_block = chosen_section.blocks.get(name=chosen_block)

        author_keyboard = [[f'{presentation.speaker.user} | {presentation.name}'] for presentation in chosen_block.presentations]
        author_keyboard.append(['В главное меню', 'Назад'])
        update.message.reply_text(text='Выберите спикера, которому хотите задать вопрос',
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=ReplyKeyboardMarkup(author_keyboard,
                                                                   resize_keyboard=True,
                                                                   one_time_keyboard=True))

        return 'CHOOSE_SPEAKER'
    
    text = user_reply
    participant = Participant.objects.get(
        user__telegram_id=update.effective_message.from_user.id
    )
    speaker = context.user_data['speaker']
    Question.objects.create(
        text=text,
        participant=participant,
        speaker=speaker,
    )
    update.message.reply_text(
        text='Ваш вопрос отправлен спикеру.',
        reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
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

        user = BotUser.objects.get(
            telegram_id=user_telegram_id
        )


        if user.position:
            re_registrate_keyboard = [['Изменить имя', 'Изменить фамилию'], ['Изменить компанию', 'Изменить должность']]
            update.message.reply_text(
                text=f'Вы уже зарегистрированы со следующими данными: \
                    {user.name} {user.surname} \
                    \nРаботаете в {user.company} на должности {user.position} ',

                reply_markup=ReplyKeyboardMarkup(re_registrate_keyboard, resize_keyboard=True, one_time_keyboard=True)
            )
            return 'RE_REGISTRATE'

        user.name = user_name
        user.surname = user_lastname
        user.company = user_reply
        user.save()


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
        user = BotUser.objects.get(telegram_id=update.message.from_user.id)
        user.position = user_reply
        user.save()
        update.message.reply_text(
            text='Вы успешно зарегистрированы. Чтобы познакомиться, нажмите кнопку "Познакомиться" еще раз.',
            reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'MAIN_MENU'


def re_registrate(update: Update, context: CallbackContext):
    user_reply = update.message.text

    if user_reply == 'Изменить имя':
        update.message.reply_text(text='Введите имя')
        return 'CHANGE_NAME'

    if user_reply == 'Изменить фамилию':
        update.message.reply_text(text='Введите фамилию')
        return 'CHANGE_SURNAME'

    if user_reply == 'Изменить компанию':
        update.message.reply_text(text='Введите компанию')
        return 'CHANGE_COMPANY'

    if user_reply == 'Изменить должность':
        update.message.reply_text(text='Введите должность')
        return 'CHANGE_POSITION'


def change_name(update: Update, context: CallbackContext):
    user_reply = update.message.text

    user_telegram_id = update.message.from_user.id

    user = BotUser.objects.get(
        telegram_id=user_telegram_id
    )

    user.name = user_reply
    user.save()
    update.message.reply_text(
        text='Имя изменено',
        reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return 'MAIN_MENU'


def change_surname(update: Update, context: CallbackContext):
    user_reply = update.message.text

    user_telegram_id = update.message.from_user.id

    user = BotUser.objects.get(
        telegram_id=user_telegram_id
    )

    user.surname = user_reply
    user.save()
    update.message.reply_text(
        text='Фамилия изменена',
        reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return 'MAIN_MENU'


def change_company(update: Update, context: CallbackContext):
    user_reply = update.message.text

    user_telegram_id = update.message.from_user.id

    user = BotUser.objects.get(
        telegram_id=user_telegram_id
    )

    user.company = user_reply
    user.save()
    update.message.reply_text(
        text='Компания изменена',
        reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return 'MAIN_MENU'


def change_position(update: Update, context: CallbackContext):
    user_reply = update.message.text

    user_telegram_id = update.message.from_user.id

    user = BotUser.objects.get(
        telegram_id=user_telegram_id
    )

    user.position = user_reply
    user.save()
    update.message.reply_text(
        text='Должность изменена',
        reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return 'MAIN_MENU'


def donate(update: Update, context: CallbackContext):
    payment_sum = validate_sum(update.message.text)
    
    chat_id = update.message.chat_id
    current_event = context.user_data['current_event']
    title = f"Донат мероприятию {current_event}"
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
    return 'MAIN_MENU'

def precheckout_callback(update: Update, context: CallbackContext):
    query = update.pre_checkout_query

    if query.invoice_payload != "Custom-Payload":
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        query.answer(ok=True)

def successful_payment_callback(update: Update, context: CallbackContext):
    update.message.reply_text(
        text='Спасибо за пожертвование <3',
        reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    participant = BotUser.objects.get(telegram_id=update.message.from_user.id).participation
    current_event = context.user_data['current_event']
    sum_ = update.message['successful_payment']['total_amount']/100
    Donation.objects.create(participant=participant, event=current_event, reject=False, amount=sum_)

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
        'DONATION': donate,
        'CHOOSE_SECTION_FOR_QUESTION': choose_section_for_question,
        'CHOOSE_BLOCK_FOR_QUESTION': choose_block_for_question,
        'CHOOSE_SPEAKER': choose_speaker,
        'ASK_QUESTION': ask_question,
        'RE_REGISTRATE': re_registrate,
        'CHANGE_NAME': change_name,
        'CHANGE_SURNAME': change_surname,
        'CHANGE_COMPANY': change_company,
        'CHANGE_POSITION': change_position,

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
    dispatcher.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
