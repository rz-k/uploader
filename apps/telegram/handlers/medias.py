from apps.bot.models import Episode, Session
from apps.telegram.handlers.base_handlers import BaseHandler
from apps.telegram.telegram import Telegram
from apps.telegram.telegram_models import Update
from utils.load_env import env


class MediaHandler(BaseHandler):

    def __init__(self, update: Update, bot: Telegram):
        super().__init__(update, bot)
        self.update = update
        self.bot = bot

        self.steps = {
            "get_episode": self.get_episode,
        }

    def get_episode(self):
        _, session_id = self.user_obj.step.split(":")
        session = Session.objects.get(id=session_id)

        original_caption = self.update.message.caption or ""
        original_entities = self.update.message.caption_entities or []
        if env.EXTRA_CAPTION:
            original_caption = original_caption + env.EXTRA_CAPTION.replace("\\n", "\n")
            result = self.bot.copy_message(
                chat_id=env.CHANNEL_ID,
                from_chat_id=self.chat_id,
                message_id=self.update.message.message_id,
                caption=original_caption,
                caption_entities=original_entities
            )
        # # جایی که متن اضافه میشه
        # if env.EXTRA_CAPTION:
        #     extra_text = env.EXTRA_CAPTION
        #     # محاسبه offset شروع متن اضافه‌شده
        #     offset_start = len(original_caption)
        #     new_caption = original_caption + extra_text

        #     # اگر می‌خوای متن اضافه‌شده هم entity داشته باشه
        #     # مثلا bold
        #     extra_entities = [{
        #         "type": "bold",
        #         "offset": offset_start,
        #         "length": len(extra_text),
        #     }]

        #     # ترکیب entities قبلی و جدید
        #     entities = original_entities + extra_entities
        # else:
        #     new_caption = original_caption
        #     entities = original_entities

        # result = self.bot.copy_message(
        #     chat_id=env.CHANNEL_ID,
        #     from_chat_id=self.chat_id,
        #     message_id=self.update.message.message_id,
        #     caption=new_caption,
        #     caption_entities=entities
        # )

        if result['ok']:
            channel_message_id = result['result']['message_id']
            episode = Episode.objects.create(
                session=session,
                message_id=channel_message_id
            )
            text = (
                f"✅ آپلود با موفقیت انجام شد!\n\n"
                f"📌 لینک:\n [E-{episode.order}]({episode.get_link()})\n"
            )
            return self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                # text=self.bot_messages.get_message("payment_plan_message"),
                parse_mode="markdown"
            )
        return self.bot.send_message(
            chat_id=self.chat_id,
            text="اپلود انجام نشد مشکلی پیش امده",
            parse_mode="markdown"
        )

    def handle(self):
        if self.is_update_mode():return  # noqa: E701
        if self.is_user_block():return  # noqa: E701

        print("Media Handlers")
        if self.user_step:
            if callback := self.steps.get(self.user_step): # step : "home"
                return callback()

            if callback := self.steps.get(self.user_step.split(":")[0]): # step : "home:info"
                return callback()

