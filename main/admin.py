from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, HelpRequest, Feedback, MentorProfile, Institution, TelegramMessageLog

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {
            'fields': ('avatar', 'telegram_id', 'role', 'city', 'phone_number', 'bio')
        }),
    )
    list_display = ('username', 'email', 'role', 'city', 'is_staff')
    list_filter = ('role', 'is_staff', 'city')
    search_fields = ('username', 'email', 'telegram_id')

@admin.register(HelpRequest)
class HelpRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'created_at', 'assigned_volunteer')
    list_filter = ('status',)
    search_fields = ('title', 'description', 'location')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('request', 'author', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('comment',)

@admin.register(MentorProfile)
class MentorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'expertise', 'available')
    list_filter = ('available',)
    search_fields = ('expertise', 'user__username')

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'address', 'phone')
    list_filter = ('category',)
    search_fields = ('name', 'description', 'address')

@admin.register(TelegramMessageLog)
class TelegramMessageLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'sent_at')
    search_fields = ('message', 'user__username')

