import json

from apps.bot.models import Plan, Session
from utils.load_env import env


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

    def admin_home_keyboard(self):
        markup = {
            "keyboard": [
                ["پیام همگانی 📡", "اپلود ⬇️"],
                ["ویرایش ⚙️", "اطلاعات کاربر 💹"]
            ],
            "resize_keyboard":True
        }
        return self.to_json(
            data=markup
        )

    def admin_upload_keyboard(self):
        markup = {
            "keyboard": [
                ["اپلود سریال ➕", "اپلود فیلم ➕"],
                ["بازگشت"]
            ],
            "resize_keyboard":True
        }
        return self.to_json(
            data=markup
        )

    def cancel_keyboard(self):
        markup = {
            "keyboard": [
                ["لغو اپلود ❌", "اتمام اپلود ✅"]
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

    def edit_session_keyboard(self, session: Session):
        child = []
        for episode in session.episodes.order_by("order"):
            child.append([
                {"text": f"🎞️ قسمت {episode.order}", "callback_data": "_"},
                {"text": "🗑️ حذف", "callback_data": f"edit_session:delete_e:{episode.id}"},
                {"text": "🔗 لینک", "url": f"https://t.me/c/{env.PRIVATE_CHANNEL_ID}/{episode.message_id}"},
            ])

        if child:
            child.append(
                [
                    {"text": "➕ افزودن پارت جدید", "callback_data": f"edit_session:add_e:{session.id}"}
                ]
            )
            child.append(
                [
                    {"text": "❌ حذف کل سشن", "callback_data": f"edit_session:delete_s:{session.id}"}
                ]
            )

        markup = {
            "inline_keyboard": child
        }
        return self.to_json(data=markup)

    def sure_delete_object_keyboard(self, object_id, object_type):
        markup = {
            "inline_keyboard": [
                [
                    {"text": "✅ بله، حذف کن", "callback_data": f"sure_delete_object:yes:{object_type}:{object_id}"},
                    {"text": "❌ نه، منصرف شدم", "callback_data": f"sure_delete_object:no:{object_type}:{object_id}"},
                ]
            ]
        }
        return self.to_json(data=markup)
