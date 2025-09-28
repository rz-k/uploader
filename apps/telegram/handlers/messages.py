from apps.bot.models import Session
from apps.telegram.decorator import sponsor_required
from apps.telegram.handlers.base_handlers import BaseHandler
from apps.telegram.telegram import Telegram
from apps.telegram.telegram_models import Update
from utils.utils import update_object
from apps.account.models import User


class AdminMessageHandler(BaseHandler):

    def __init__(self, update: Update, bot: Telegram):
        super().__init__(update, bot)
        self.update = update
        self.bot = bot

        self.steps = {
            "admin_home": self.admin_home,
            "admin_upload": self.admin_upload,
            "get_title": self.get_title,
            "get_episode": self.get_episode,
            "admin_user_info": self.admin_user_info,
        }

    def admin_handler(self):
        update_object(self.user_obj, step="admin_home")
        return self.bot.send_message(
            chat_id=self.chat_id,
            text="Welcome To Admin panel",
            reply_markup=self.reply_keyboard.admin_home_keyboard()
        )

    def admin_user_info(self):
        if self.update.message.text == "بازگشت":
            return self.admin_handler()
        else:
            try:
                _user = User.objects.get(user_id=self.text)
            except Exception:
                return self.bot.send_message(chat_id=self.chat_id,text="یوزر پیدا نشد",parse_mode="markdown")

            plan_title=_user.subscription_info()
            last_plan = 1
            payment_count = 1
            return self.bot.send_message(
                chat_id=self.chat_id,
                text=self.bot_messages.get_message(
                    "user_info",
                    user_id=self.text,
                    plan_title=plan_title,
                    last_plan=last_plan,
                    payment_count=payment_count
                ),
                reply_markup=self.reply_keyboard.back_keyboard(),
                parse_mode="markdown"
            )

    def admin_home(self):
        if self.update.message.text == "اپلود ⬇️":
            update_object(self.user_obj, step="admin_upload")
            return self.bot.send_message(
                chat_id=self.chat_id,
                text="برای اپلود سریال و یا فیلم تک قسمتی یکی رو انتخاب کن",
                # text=self.bot_messages.get_message("payment_plan_message"),
                reply_markup=self.reply_keyboard.admin_upload_keyboard(),
                parse_mode="markdown"
            )

        elif self.update.message.text == "اطلاعات کاربر 💹":
            update_object(self.user_obj, step="admin_user_info")
            return self.bot.send_message(
                chat_id=self.chat_id,
                text="لطفا ایدی عددی کاربر مورد نظر رو ارسال کن",
                # text=self.bot_messages.get_message("payment_plan_message"),
                reply_markup=self.reply_keyboard.back_keyboard(),
                parse_mode="markdown"
            )

    def admin_upload(self):
        if self.update.message.text == "بازگشت":
            return self.admin_handler()

        elif self.update.message.text == "اپلود فیلم ➕":
            update_object(self.user_obj, step="get_title:movie")
            return self.bot.send_message(
                chat_id=self.chat_id,
                text="اسم فیلم را ارسال کنید",
                # text=self.bot_messages.get_message("payment_plan_message"),
                reply_markup=self.reply_keyboard.back_keyboard(),
                parse_mode="markdown"
            )
        elif self.update.message.text == "اپلود سریال ➕":
            update_object(self.user_obj, step="get_title:series")
            return self.bot.send_message(
                chat_id=self.chat_id,
                text="اسم سریال را ارسال کنید",
                # text=self.bot_messages.get_message("payment_plan_message"),
                reply_markup=self.reply_keyboard.back_keyboard(),
                parse_mode="markdown"
            )

    def get_title(self):
        if self.update.message.text == "بازگشت":
            update_object(self.user_obj, step="admin_upload")
            return self.bot.send_message(
                chat_id=self.chat_id,
                text="برای اپلود سریال و یا فیلم تک قسمتی یکی رو انتخاب کن",
                # text=self.bot_messages.get_message("payment_plan_message"),
                reply_markup=self.reply_keyboard.admin_upload_keyboard(),
                parse_mode="markdown"
            )

        _, content_type = self.user_obj.step.split(":")

        session = Session.objects.create(
            title=self.text,
            content_type=content_type,
        )
        update_object(self.user_obj, step=f"get_episode:{session.id}")
        return self.bot.send_message(
            chat_id=self.chat_id,
            text="لطفا فایل مورد نظر رو ارسال کن",
            # text=self.bot_messages.get_message("payment_plan_message"),
            reply_markup=self.reply_keyboard.cancel_keyboard(),
            parse_mode="markdown"
        )

    def get_episode(self):
        _, session_id = self.user_obj.step.split(":")
        if self.update.message.text == "لغو اپلود ❌":
            Session.objects.get(id=session_id).delete()
            update_object(self.user_obj, step="admin_upload")
            return self.bot.send_message(
                chat_id=self.chat_id,
                text="برای اپلود سریال و یا فیلم تک قسمتی یکی رو انتخاب کن",
                # text=self.bot_messages.get_message("payment_plan_message"),
                reply_markup=self.reply_keyboard.admin_upload_keyboard(),
                parse_mode="markdown"
            )

        elif self.update.message.text == "اتمام اپلود ✅":
            update_object(self.user_obj, step="admin_home")
            session = Session.objects.get(id=session_id)
            epis = ""
            for e in session.episodes.order_by("order"):
                epis+=f"[E{e.order}]({e.get_link()})\n"
            text = (
                f"✅ آپلود با موفقیت انجام شد!\n\n"
                f"📌 لینک قسمت‌ها:\n{epis}\n"
                f"📂 لینک کل مجموعه:\n[S{session.title}]({session.get_link()})"
            )
            return self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                # text=self.bot_messages.get_message("payment_plan_message"),
                reply_markup=self.reply_keyboard.admin_home_keyboard(),
                parse_mode="markdown"
            )

    def handle(self):
        if self.is_update_mode():return  # noqa: E701
        if self.is_user_block():return  # noqa: E701

        if self.user_step:
            if callback := self.steps.get(self.user_step): # step : "home"
                return callback()

            if callback := self.steps.get(self.user_step.split(":")[0]): # step : "home:info"
                return callback()

class MessageHandler(BaseHandler):

    def __init__(self, update: Update, bot: Telegram):
        super().__init__(update, bot)
        self.update = update
        self.bot = bot

        self.steps = {
            "home": self.home,
        }

    @sponsor_required
    def home(self):
        if self.update.message.text == "🛒 خرید اشتراک":
            return self.bot.send_message(
                chat_id=self.chat_id,
                text=self.bot_messages.get_message("payment_plan_message"),
                reply_markup=self.inline_keyboard.pay_plan_keyboard(),
                parse_mode="markdown"
            )

        elif self.update.message.text == "اطلاعات حساب 👤":
            subscription_info = self.user_obj.subscription_info()
            plan_days = "نامحدود 💎" if subscription_info == "Unlimited" else ("بدون اشتراک" if subscription_info == "No Subscription" else subscription_info)
            return self.bot.send_message(
                chat_id=self.chat_id,
                text=self.bot_messages.get_message("info_plan_message", user_id=self.user_id, plan_days=plan_days),
                parse_mode="markdown"
            )

    # def second_button(self):
    #     """
    #     Handles user interactions when the user is at the "second_button" step.

    #     - If the user presses "بازگشت", their step is updated to "home"
    #     and the home screen message is sent with the main reply keyboard.

    #     This method allows the user to navigate back to the home screen.
    #     """

    #     if self.update.message.text == "بازگشت":
    #         # update user step
    #         update_object(self.user_obj, step="home")

    #         return self.bot.send_message(
    #             chat_id=self.chat_id,
    #             text="Home",
    #             reply_markup=self.reply_keyboard.home_keyboard(),
    #         )

    def handle(self):
        if self.is_update_mode():return  # noqa: E701
        if self.is_user_block():return  # noqa: E701

        if self.user_step:
            if callback := self.steps.get(self.user_step): # step : "home"
                return callback()

            if callback := self.steps.get(self.user_step.split(":")[0]): # step : "home:info"
                return callback()
            AdminMessageHandler(self.update, self.bot).handle()
