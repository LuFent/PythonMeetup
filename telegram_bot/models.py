from django.db import models

from django.utils.html import format_html


class BotUser(models.Model):
    name = models.CharField('Имя', max_length=30, blank=True)
    surname = models.CharField('Фамилия', max_length=50, blank=True)
    info  = models.TextField('О себе', blank=True)
    telegram_id = models.CharField(
        'ID в Telegram',
        max_length=10,
        unique=True
    )
    company = models.CharField('Комания, в которой работет', blank=True, max_length=50)
    position = models.CharField('Должность', blank=True, max_length=50)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        if self.name and self.surname:
            return f'{self.name} {self.surname}'
        return f'User {self.telegram_id}'


class EventQuerySet(models.QuerySet):
    def get_current(self):
        return self.filter(status=True).order_by('date').last()

class Event(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)
    date = models.DateField('Дата проведения')
    organizer = models.ForeignKey(
        BotUser,
        related_name='events',
        verbose_name='Организатор',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    status = models.BooleanField('Активно')
    objects = EventQuerySet.as_manager()

    def admin_unit_details(self):  # Button for admin to get to API
        return format_html(u'<div class="admin-message-container"><textarea type="text" id="MessageText" value=""></textarea> <div class="message-button-container"> ' 
                           u'<a href="#" onclick="SendMessage(1)" class="button admin-message-button" id="id_admin_send_message">Отправить сообщение всем пользователям</a>'
                           u'<a href="#" onclick="SendMessage(2)" class="button admin-message-button" id="id_admin_send_message">Отправить сообщение всем посетителям</a>'
                           u'<a href="#" onclick="SendMessage(3)" class="button admin-message-button" id="id_admin_send_message">Отправить сообщение всем модераторам</a>'
                           u'<a href="#" onclick="SendMessage(4)" class="button admin-message-button" id="id_admin_send_message">Отправить сообщение всем спикерам</a>'
                           u'</div> </div>')

    admin_unit_details.allow_tags = True
    admin_unit_details.short_description = "Рассылка сообщений"

    class Meta:
        verbose_name = 'мероприятие'
        verbose_name_plural = 'мероприятия'

    def __str__(self):
        return f'{self.date} {self.name}'


class Access(models.Model):
    level = models.CharField(
        'Уровень доступа',
        max_length=20,
        unique=True
    )
    info = models.TextField('Доступные функции', blank=True)

    class Meta:
        verbose_name = 'уровень доступа'
        verbose_name_plural = 'уровни доступа'

    def __str__(self):
        return self.level


class Participant(models.Model):
    user = models.OneToOneField(
        BotUser,
        related_name='participation',
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    event = models.ForeignKey(
        Event,
        related_name='participants',
        verbose_name='Мероприятие',
        on_delete=models.CASCADE,
        db_index=True,
    )
    level = models.ForeignKey(
        Access,
        related_name='users',
        verbose_name='Уровень доступа',
        on_delete=models.SET_NULL,
        null=True,
        db_index=True,
        default=1
    )

    class Meta:
        verbose_name = 'участник'
        verbose_name_plural = 'участники'

    def __str__(self):
        return f'{self.level} {self.user}'


class Section(models.Model):
    name = models.CharField('Название', max_length=50)
    event = models.ForeignKey(
        Event,
        related_name='sections',
        verbose_name='Мероприятие',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'часть'
        verbose_name_plural = 'части'

    def __str__(self):
        return f'{self.event} {self.name}'


class Block(models.Model):
    name = models.CharField('Название', max_length=50)
    info = models.TextField('Подробная информация', blank=True)
    start_time = models.TimeField('Время начала')
    finish_time = models.TimeField('Время завершения')
    moderator = models.ForeignKey(
        Participant,
        related_name='moderating_blocks',
        verbose_name='Модератор',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    section = models.ForeignKey(
        Section,
        related_name='blocks',
        verbose_name='Секция',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'блок'
        verbose_name_plural = 'блоки'

    def __str__(self):
        return f'{self.section} | {self.name}'


class Presentation(models.Model):
    name = models.CharField('Название', max_length=50)
    info = models.TextField('Подробная информация', blank=True)
    speaker = models.ForeignKey(
        Participant,
        related_name='presentations',
        verbose_name='Спикер',
        on_delete=models.CASCADE,
    )
    block = models.ForeignKey(
        Block,
        related_name='presentations',
        verbose_name='Блок',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'выступление'
        verbose_name_plural = 'выступления'

    def __str__(self):
        return f'{self.block} - {self.name}'


class Profile(models.Model):
    participant = models.OneToOneField(
        Participant,
        related_name='profile',
        verbose_name='Участник',
        on_delete=models.CASCADE,
    )
    experience = models.CharField('Опыт работы', max_length=10)
    language = models.CharField('Основной язык разработки', max_length=10)
    other_expecting = models.BooleanField('Ждем других анкет?')

    class Meta:
        verbose_name = 'анкета'
        verbose_name_plural = 'анкеты'

    def __str__(self):
        return self.participant


class Donation(models.Model):
    participant = models.ForeignKey(
        Participant,
        related_name='donations',
        verbose_name='Участник',
        on_delete=models.CASCADE,
    )
    event = models.ForeignKey(
        Event,
        related_name='donations',
        verbose_name='Мероприятие',
        on_delete=models.CASCADE,
    )
    reject = models.BooleanField('Отклонен')
    amount = models.IntegerField(
        'Сумма доната',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Донат'
        verbose_name_plural = 'Донаты'

    def __str__(self):
        return f'{self.participant} {self.amount}'


class Question(models.Model):
    text = models.TextField('Текст вопроса', blank=True)
    participant = models.ForeignKey(
        Participant,
        verbose_name='От кого вопрос',
        related_name='asked_questions',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    speaker = models.ForeignKey(
        Participant,
        verbose_name='Вопрос кому',
        related_name='got_questions',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return f'Вопрос для {self.speaker.user}'