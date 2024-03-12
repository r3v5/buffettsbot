from django.contrib.auth.models import BaseUserManager


class TelegramUserManager(BaseUserManager):
    def create_user(
        self,
        chat_id: int,
        telegram_username: str,
        first_name: str,
        last_name: str,
        at_private_group: bool,
        password=None,
    ):
        if not chat_id and not telegram_username:
            raise ValueError(
                "telegram_id field must be set\nchat_id field must be set\ntelegram_username field must be set"
            )
        user = self.model(
            chat_id=chat_id,
            telegram_username=telegram_username,
            first_name=first_name,
            last_name=last_name,
            at_private_group=at_private_group,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, telegram_username: str, chat_id: int, password=None):
        user = self.create_user(
            chat_id=chat_id,
            telegram_username=telegram_username,
            password=password,
            first_name="",
            last_name="",
            at_private_group=True,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
