from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):

    user_id = models.BigIntegerField(unique=True,verbose_name=_("user id"))

    step = models.CharField(max_length=30,default="home",verbose_name=_("current step"))

    is_send_ads = models.BooleanField(default=False,verbose_name=_("Advertising status"))

    subscription_expires_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["user_id"]

    def has_active_subscription(self) -> bool:
        # consider MAX_DATE as unlimited so still active
        if not self.subscription_expires_at:
            return False
        return self.subscription_expires_at > timezone.now()

    @transaction.atomic
    def add_subscription(self, days: int):
        if days < 0:
            self.subscription_expires_at = timezone.now() + timedelta(days=365000)  # unlimited
        else:
            if self.subscription_expires_at and self.subscription_expires_at > timezone.now():
                self.subscription_expires_at += timedelta(days=days)
            else:
                self.subscription_expires_at = timezone.now() + timedelta(days=days)
        self.save(update_fields=["subscription_expires_at"])

    def subscription_info(self) -> str:
        """
        Return subscription status as a string:
        - "No Subscription" if subscription is null or expired
        - "Unlimited" if subscription is effectively unlimited (>= MAX_DATE)
        - Otherwise, return the expiry datetime in local timezone
        """
        exp = self.subscription_expires_at
        now = timezone.now()

        if not exp or exp <= now:
            return "No Subscription"

        if now + timedelta(days=36500) < exp:
            return "Unlimited"

        # Convert to local timezone and format as string
        local_dt = timezone.localtime(exp)
        return local_dt.strftime("%Y-%m-%d|%H:%M")

    def __str__(self):
        return str(self.user_id)
