from django.contrib import admin

from .models import BotUser
from .models import Event
from .models import Access
from .models import Participant
from .models import Section
from .models import Block
from .models import Presentation
from .models import Profile
from .models import Donation


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    pass
    # readonly_fields = [
    #     'telegram_id',
    # ]



@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    raw_id_fields = ('organizer',)
    readonly_fields = ('admin_unit_details',)

    # readonly_fields = [
    #     'status',
    # ]
    class Media:
        js = ('admin_custom/myjs.js', )  # in static
        css = {'all': ('admin_custom/mycss.css',)}


@admin.register(Access)
class AccessAdmin(admin.ModelAdmin):
    pass
    # readonly_fields = [
    #     'level',
    # ]


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    pass
    # readonly_fields = [
    #     'user',
    #     'event',
    # ]


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    pass
    # readonly_fields = [
    #     'event',
    # ]


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    # readonly_fields = [
    #     'section',
    # ]
    raw_id_fields = ('moderator',)


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    # readonly_fields = [
    #     'block',
    # ]
    raw_id_fields = ('speaker',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = [
        'participant',
    ]


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    pass
    # readonly_fields = [
    #     'participant',
    #     'event',
    #     'reject',
    #     'amount',
    # ]

