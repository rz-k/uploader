import time

from apps.bot.models import Episode, Session
from apps.telegram._types import ReplyParameters
from apps.telegram.decorator import sponsor_required
from apps.telegram.handlers.base_handlers import BaseHandler
from apps.telegram.telegram import Telegram
from apps.telegram.telegram_models import Update
from utils.load_env import env
from utils.utils import update_object


class CommandHandler(BaseHandler):

    def __init__(self, update: Update, bot: Telegram):
        super().__init__(update, bot)
        self.bot = bot
        self.update = update

    @sponsor_required
    def start_handler(self):
        """
        Handles the /start command or entry point of the bot.

        - If the user does not exist, a new user will be created with the step set to "home".
        - If the user already exists, their current step will be updated to "home".
        - Finally, sends a "Home" message with the corresponding reply keyboard.

        This function serves as the main entry point of the bot and represents the home screen.
        """

        update_object(self.user_obj, step="home")
        return self.bot.send_message(
            chat_id=self.chat_id,
            text="Home",
            reply_markup=self.reply_keyboard.home_keyboard(),
            reply_parameters=ReplyParameters(
                chat_id=self.chat_id,
                message_id=self.update.message.message_id
            )
        )

    def admin_handler(self):
        update_object(self.user_obj, step="admin_home")
        return self.bot.send_message(
            chat_id=self.chat_id,
            text="Welcome To Admin panel",
            reply_markup=self.reply_keyboard.admin_home_keyboard(),
            reply_parameters=ReplyParameters(
                chat_id=self.chat_id,
                message_id=self.update.message.message_id
            )
        )

    def help_handler(self):
        return self.bot.send_message(chat_id=self.chat_id, text="Help Command")

    def send_file_to_user_handler(self):
        def send_message(message_id: int):
            result = self.bot.copy_message(
                chat_id=self.chat_id,
                from_chat_id=env.CHANNEL_ID,
                message_id=message_id
            )
            if env.AUTO_DELETE_FILE_SECOND:
                sleep_second = int(env.AUTO_DELETE_FILE_SECOND)
                time.sleep(sleep_second)
                self.bot.delete_message(chat_id=self.chat_id, message_id=result['result']['message_id'])
            return

        _, link = self.text.split(" ")
        if link.startswith("S_"):
            session = Session.objects.prefetch_related("episodes").get(link=link)
            for e in session.episodes.order_by("order"):
                self.run_function_in_thread(send_message, e.message_id)

        elif link.startswith("E_"):
            episode = Episode.objects.get(link=link)
            self.run_function_in_thread(send_message, episode.message_id)
        time.sleep(2)
        if env.AUTO_DELETE_FILE_SECOND:
            return self.bot.send_message(
                chat_id=self.chat_id,
                text=self.bot_messages.get_message("delete_file_and_save_file", time=env.AUTO_DELETE_FILE_SECOND),
                reply_parameters=ReplyParameters(
                    chat_id=self.chat_id,
                    message_id=self.update.message.message_id
                )
            )

    def handle(self):
        if self.is_update_mode():return  # noqa: E701
        if self.is_user_block():return  # noqa: E701

        if self.update.message.text.startswith("/start"):
            if self.update.message.text == "/start":
                self.start_handler()

            elif self.update.message.text.startswith("/start "):

                if self.user_obj.has_active_subscription() or env.FREE_DOWNLOAD:
                    return self.run_function_in_thread(self.send_file_to_user_handler)

                return self.bot.send_message(
                    chat_id=self.chat_id,
                    text=self.bot_messages.get_message("payment_plan_message"),
                    reply_markup=self.inline_keyboard.pay_plan_keyboard(),
                    parse_mode="markdown"
                )

        elif self.update.message.text.startswith("/help"):
            self.help_handler()

        elif self.update.message.text.startswith("/admin") and self.user_obj.is_superuser:
            self.admin_handler()

        print("Command Handlers")
