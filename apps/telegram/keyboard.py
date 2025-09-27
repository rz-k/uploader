import json

from apps.bot.models import Plan


class BaseKeyboard:

    def to_json(self, data: dict):
        return json.dumps(data)


class ReplyKeyboardMarkup(BaseKeyboard):

    def home_keyboard(self):
        markup = {
            "keyboard": [
                ["اطلاعات حساب 👤", "🛒 خرید اشتراک"],
                ["گیفت اشتراک به دوستان 🎁", "💌 حمایت از مجموعه"]
            ],
            "resize_keyboard":True
        }
        return self.to_json(
            data=markup
        )

    def back_keyboard(self):
        markup = {
            "keyboard": [
                ["بازگشت"]
            ],
            "resize_keyboard":True
        }
        return self.to_json(
            data=markup
        )

    def remove_keyboard(self):
        markup = {"keyboard": []}
        return self.to_json(
            data=markup
        )

class InlineKeyboardMarkup(BaseKeyboard):

    def pay_plan_keyboard(self):
        plans = Plan.objects.filter(is_active=True)
        child = []
        for plan in plans.order_by("pk"):
            child.append(
                [{"text": f"{plan.name}", "callback_data": f"pay:{plan.pk}"}]
            )
        markup = {
            "inline_keyboard": child
        }
        return self.to_json(data=markup)

    def remove_keyboard(self):
        markup = {"inline_keyboard": []}
        return self.to_json(
            data=markup
        )

    def sponsor_channel_keyboard(self, channels):

        child = []
        for channel in channels.order_by("-other"):
            child.append(
                [{"text": f"{channel.name}", "url": channel.link}]
            )
        if child:
            child.append(
                [
                    {"text": "تایید عضویت ✅", "callback_data": "joined_to_sponsor"}  # noqa: F541
                ]
            )
        markup = {
            "inline_keyboard": child
        }
        return self.to_json(data=markup)

    def remove_keyboard(self):
        markup = {"inline_keyboard": []}
        return self.to_json(data=markup)

