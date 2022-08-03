from django.contrib import admin

from .models import User
from .models import Event
from .models import Access
from .models import Participant
from .models import Section
from .models import Block
from .models import Presentation
from .models import Profile
from .models import Donation

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    readonly_fields = [
        'telegram_id',
    ]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    raw_id_fields = ('organizer',)
    readonly_fields = [
        'status',
    ]


@admin.register(Access)
class AccessAdmin(admin.ModelAdmin):
    readonly_fields = [
        'level',
    ]


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    readonly_fields = [
        'user',
        'event',
    ]


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    readonly_fields = [
        'event',
    ]


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    readonly_fields = [
        'section',
    ]
    raw_id_fields = ('moderator',)


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    readonly_fields = [
        'block',
    ]
    raw_id_fields = ('speaker',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = [
        'participant',
    ]


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    readonly_fields = [
        'participant',
        'event',
        'reject',
        'amount',
    ]