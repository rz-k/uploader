from django.contrib import admin

from apps.bot.models import BotUpdateStatus, ChannelSponsor, Episode, Message, Plan, Session


@admin.register(BotUpdateStatus)
class BotUpdateStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "is_update", "text")
    list_editable = ("is_update", )

    def text(self, obj):
        return obj.update_msg[:30]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "_text")
    search_fields = ("name", )

    def _text(self, obj):
        return obj.text[:30]

@admin.register(ChannelSponsor)
class ChannelSponsorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "chat_id", "other", "_link")
    search_fields = ("name", )
    list_editable = ("name", "other")

    def _link(self, obj):
        return obj.link[:30]

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price_rial", "duration_days", "is_active")
    search_fields = ("name",)
    list_editable = ("name",)

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "message_id", "order")
    search_fields = ("message_id",)

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "content_type", "like_count", "view_count")
    search_fields = ("title",)
