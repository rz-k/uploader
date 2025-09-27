from django.db import models


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
