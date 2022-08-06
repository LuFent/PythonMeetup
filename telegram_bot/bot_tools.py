from .models import *
from itertools import islice


def chunk(list_, size):
    list_ = iter(list_)
    return list(iter(lambda: tuple(islice(list_, size)), ()))


def build_timetable(block):
    timetable = f'Блок {block.name}\n'
    timetable += f'{block.start_time} - {block.start_time}\n\n'

    for presentation in block.presentations.all():
        timetable += f'*-- {presentation.name}*\n'
        if presentation.speaker:
            timetable += f'Спикер - {presentation.speaker}\n'
        if presentation.info:
            timetable += f'Информация: {presentation.info}\n'

        timetable += '\n'

    return timetable


def validate_sum(payment_sum):
    try:
        payment_sum = int(payment_sum)
    except Exception:
        return "Введите число"

    if payment_sum < 10:
        return "Слишком маленькая сумма"

    if payment_sum > 1000:
        return "Слишком большая сумма"

    return payment_sum*100


