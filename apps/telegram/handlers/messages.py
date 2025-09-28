from apps.telegram.decorator import sponsor_required
from apps.telegram.handlers.base_handlers import BaseHandler
from apps.telegram.telegram import Telegram
from apps.telegram.telegram_models import Update
from utils.utils import update_object


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
