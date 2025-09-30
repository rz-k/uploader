from apps.bot.models import Episode, Plan, Session
from apps.telegram.decorator import sponsor_required
from apps.telegram.handlers.base_handlers import BaseHandler
from apps.telegram.telegram import Telegram
from apps.telegram.telegram_models import Update
from utils.utils import update_object


class CallBackQueryHandler(BaseHandler):

    def __init__(self, update: Update, bot: Telegram):
        super().__init__(update, bot)

        self.callback_handlers = {
            "joined_to_sponsor": self.joined_channel_sponsor_handler,
            "edit_session": self.edit_session_handler,
            "sure_delete_object": self.sure_delete_object_handler,
            "pay": self.payment_plan_handler,
        }

    @sponsor_required
    def joined_channel_sponsor_handler(self):
        self.bot.delete_message(chat_id=self.chat_id, message_id=self.update.callback_query.message.message_id)
        update_object(self.user_obj, step="home")
        return self.bot.send_message(
            chat_id=self.chat_id,
            text="Home"
        )

    def payment_plan_handler(self):
        _, plan_id = self.update.callback_query.data.split(":")
        plan = Plan.objects.get(id=plan_id)

        # self.bot.delete_message(chat_id=self.chat_id, message_id=self.update.callback_query.message.message_id)
        # update_object(self.user_obj, step="home")
        # return self.bot.send_message(
        #     chat_id=self.chat_id,
        #     text="Home"
        # )

    def edit_session_handler(self):
        """
            edit_session:delete_e:6
            edit_session:add_e:4
            edit_session:delete_s:4
        """
        _, operation, object_id = self.update.callback_query.data.split(":")

        handlers = {
            "delete_e": lambda: self._confirm_delete(Episode, object_id, "e"),
            "delete_s": lambda: self._confirm_delete(Session, object_id, "s"),
            "add_e": lambda: self._add_episode(object_id),
        }

        handler = handlers.get(operation)
        if handler:
            return handler()
        else:
            return self.bot.send_message(
                chat_id=self.chat_id,
                text="❌ عملیات ناشناخته است."
            )

    def _confirm_delete(self, model, object_id, object_type):
        try:
            obj = model.objects.get(pk=object_id)
        except model.DoesNotExist:
            return self.bot.send_message(
                chat_id=self.chat_id,
                text="❌ مورد مورد نظر پیدا نشد."
            )

        warning_msg = "🚨 هشدار: این عملیات غیرقابل بازگشت است!\nآیا مطمئن هستید؟"
        return self.bot.edit_message_text(
            chat_id=self.chat_id,
            text=warning_msg,
            message_id=self.update.callback_query.message.message_id,
            reply_markup=self.inline_keyboard.sure_delete_object_keyboard(obj.pk, object_type),
        )

    def _add_episode(self, session_id):
        try:
            session = Session.objects.get(pk=session_id)
        except Session.DoesNotExist:
            return self.bot.send_message(
                chat_id=self.chat_id,
                text="❌ سشن پیدا نشد."
            )

        update_object(self.user_obj, step=f"get_episode:{session.id}")
        return self.bot.send_message(
            chat_id=self.chat_id,
            text="لطفا فایل مورد نظر رو ارسال کن",
            reply_markup=self.reply_keyboard.cancel_keyboard(),
            parse_mode="markdown"
    )

    # edit session part
    def _build_session_info_message(self, session):
        session.refresh_from_db()
        _type = "سریال" if session.content_type == "series" else "فیلم"
        return (
            "📌 *اطلاعات سشن*\n\n"
            f"🎬 *اسم سشن:* `{session.title}`\n"
            f"📺 *تعداد قسمت‌ها:* `{session.episodes.count()}`\n"
            f"📂 *نوع:* `{_type}`\n"
        )

    def _cancel_delete(self, session):
        msg = self._build_session_info_message(session)
        return self.bot.edit_message_text(
            chat_id=self.chat_id,
            text=msg,
            message_id=self.update.callback_query.message.message_id,
            reply_markup=self.inline_keyboard.edit_session_keyboard(session),
            parse_mode="markdown",
        )

    def _get_session(self, object_type, object_id):
        try:
            if object_type == "s":
                return Session.objects.get(pk=object_id)
            elif object_type == "e":
                episode = Episode.objects.get(pk=object_id)
                return episode.session
        except (Session.DoesNotExist, Episode.DoesNotExist):
            return None

    def _delete_session(self, session):
        update_object(self.user_obj, step="admin_home")
        session.delete()
        return self.bot.send_message(
            chat_id=self.chat_id,
            text="✅ سشن مورد نظر حذف شد.",
            reply_markup=self.reply_keyboard.admin_home_keyboard(),
            parse_mode="markdown",
        )

    def _delete_episode(self, session, episode_id):
        Episode.objects.filter(pk=episode_id).delete()
        msg = self._build_session_info_message(session)
        session.refresh_from_db()
        return self.bot.edit_message_text(
            chat_id=self.chat_id,
            text=msg,
            message_id=self.update.callback_query.message.message_id,
            reply_markup=self.inline_keyboard.edit_session_keyboard(session),
            parse_mode="markdown",
        )

    def sure_delete_object_handler(self):
        _, operation, object_type, object_id = self.update.callback_query.data.split(":")

        session = self._get_session(object_type, object_id)
        if not session:
            return self.bot.send_message(
                chat_id=self.chat_id,
                text="❌ سشن یا اپیزود مورد نظر پیدا نشد.",
            )
        if operation == "no":
            return self._cancel_delete(session)

        if object_type == "s":
            return self._delete_session(session)

        if object_type == "e":
            return self._delete_episode(session, object_id)

    def handle(self):
        print("CallBackQueryHandler Handlers")
        # check update bot
        if self.is_update_mode():return  # noqa: E701
        if self.is_user_block():return  # noqa: E701


        callback_data = self.update.callback_query.data or ""
        base_key = callback_data.split(":", 1)[0] # callback_data is "check_joined_channel_sponsor" or "check_joined_channel_sponsor:user_id"

        handler = self.callback_handlers.get(base_key)
        if handler:
            return handler()
