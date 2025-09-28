from django.db import models

from utils.load_env import env
from utils.utils import generate_unique_link


class BotUpdateStatus(models.Model):
    is_update = models.BooleanField(
        default=False
    )
    update_msg = models.TextField(default="bot is updated !")

    def save(self, *args, **kwargs):
        self.id = 1
        return super().save(*args, **kwargs)

    def __str__(self):
        return str(f"Bot status is: {self.is_update}")

class Message(models.Model):

    name = models.CharField(max_length=100, null=True, blank=True, db_index=True)

    text = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.name}"

class ChannelSponsor(models.Model):

    name = models.CharField(max_length=70,null=True,blank=True)

    chat_id = models.CharField(max_length=70,unique=True,null=True,blank=True)

    link = models.CharField(max_length=70,unique=True)

    other = models.BooleanField(default=False,null=True,blank=True)

    def __str__(self) -> str:
        return self.name

class Plan(models.Model):
    """
    Subscription or service plan.
    """
    name = models.CharField(max_length=100)
    price_rial = models.PositiveBigIntegerField()
    duration_days = models.IntegerField(
        help_text="Number of days for the plan. Use a negative value for unlimited."
    )
    is_active = models.BooleanField(default=True)

    def is_unlimited(self) -> bool:
        """Check if the plan is unlimited."""
        return self.duration_days < 0

    def __str__(self):
        if self.is_unlimited():
            return f"{self.name} - Unlimited"
        return f"{self.name} - {self.duration_days} days"

class Session(models.Model):
    """
    Represents a movie or a series (as a whole).
    """
    CONTENT_TYPE_CHOICES = (
        ("movie", "Movie"),
        ("series", "Series"),
    )

    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES)
    link = models.CharField(max_length=20, unique=True, blank=True)  # unique shareable link
    view_count = models.PositiveIntegerField(default=0)  # total views
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.content_type})"

    def get_link(self):
        return f"https://t.me/{env.BOT_USERNAME}/?start={self.link}"

    def save(self, *args, **kwargs):
        if not self.link:
            self.link = generate_unique_link("S")  # auto generate if empty
        super().save(*args, **kwargs)

class Episode(models.Model):
    """
    Episodes of a series. Only used if Content.type == 'series'.
    """
    link = models.CharField(max_length=20, unique=True, blank=True)  # unique shareable link
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="episodes")
    # title = models.CharField(max_length=255)
    message_id = models.BigIntegerField(null=True, blank=True)  # Telegram message_id in backup channel
    order = models.PositiveIntegerField(blank=True, null=True)  # for ordering episodes

    def save(self, *args, **kwargs):
        if self._state.adding: # just if added new records
            if not self.link:
                self.link = generate_unique_link("E")
            self.order = self.calc_order(self.session.id)
        super().save(*args, **kwargs)

    @staticmethod
    def calc_order(session_id):
        present_orders = (
            Episode.objects.filter(session_id=session_id)
            .order_by("-order")
            .values_list("order", flat=True)
        )
        if present_orders:
            return present_orders[0] + 1
        return 1

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.order} (Episode of {self.session.title})"

    def get_link(self):
        return f"https://t.me/{env.BOT_USERNAME}/?start={self.link}"
