import os
from datetime import datetime
from typing import Union

import requests

from .models import TelegramUser


class TronTransactionAnalyzer:
    API_ENDPOINT = os.environ.get("API_ENDPOINT")
    API_KEY = os.environ.get("API_KEY")
    STAS_TRC20_WALLET_ADDRESS = os.environ.get("STAS_TRC20_WALLET_ADDRESS")

    @staticmethod
    def convert_string_to_trc20(amount_str: str, decimals: int) -> int:
        return int(int(amount_str) / (10**decimals))

    @staticmethod
    def convert_timestamp_to_date_format(timestamp: int) -> datetime:
        # Convert milliseconds to seconds
        timestamp_seconds = timestamp / 1000

        # Convert timestamp to datetime object
        date_time = datetime.fromtimestamp(timestamp_seconds)

        # Get the date from the timestamp
        date_from_timestamp = date_time.date()

        return date_from_timestamp

    @staticmethod
    def check_transaction_was_today(transaction_date: datetime) -> bool:
        # Get today's date
        today_date = datetime.today().date()

        if transaction_date == today_date:
            print("The date of transaction is today.")
            return True
        else:
            print("The date of transaction is not today.")
            return False

    @classmethod
    def validate_tx_hash(cls, tx_hash: str, plan_price: int) -> bool:
        # is_valid = False
        url = f"{cls.API_ENDPOINT}={tx_hash}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "TRON-PRO-API-KEY": f"{cls.API_KEY}",
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                valid_data = response.json()
                transaction_date = (
                    TronTransactionAnalyzer.convert_timestamp_to_date_format(
                        valid_data["timestamp"]
                    )
                )
                if TronTransactionAnalyzer.check_transaction_was_today(
                    transaction_date=transaction_date
                ):
                    for transfer_info in valid_data["trc20TransferInfo"]:
                        if transfer_info["to_address"] != cls.STAS_TRC20_WALLET_ADDRESS:
                            print(
                                f"Stanislav Ivankin {cls.STAS_TRC20_WALLET_ADDRESS} didn't get your USDT!",
                                False,
                            )
                            return False
                        else:
                            amount_usdt = cls.convert_string_to_trc20(
                                transfer_info["amount_str"], transfer_info["decimals"]
                            )
                            if amount_usdt >= plan_price:
                                result = {
                                    "tx_hash": tx_hash,
                                    "to_address": transfer_info["to_address"],
                                    "amount_usdt": amount_usdt,
                                    "subscription_price": plan_price,
                                }
                                print(result, True)
                                return True
                            else:
                                result = {
                                    "tx_hash": tx_hash,
                                    "to_address": transfer_info["to_address"],
                                    "amount_usdt": amount_usdt,
                                    "subscription_price": plan_price,
                                }
                                print(result, False)
                                return False
                else:
                    print(False)
                    return False
            else:
                print(f"Error: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error occurred: {e}")
            return False


class TelegramMessageSender:
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

    @classmethod
    def send_message_to_chat(
        cls, message: str, chat_id: Union[int, str]
    ) -> requests.Response:
        url = f"https://api.telegram.org/bot{cls.TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {"chat_id": chat_id, "text": message}

        response = requests.post(url=url, params=params)
        if response.status_code == 200:
            print("Message sent successfully!")
        else:
            print("Failed to send message:", response.text)
        return response

    @classmethod
    def send_message_with_photo_to_chat(
        cls, message: str, photo_path: str, chat_id: Union[int, str]
    ) -> requests.Response:
        url = f"https://api.telegram.org/bot{cls.TELEGRAM_BOT_TOKEN}/sendPhoto"
        files = {"photo": open(photo_path, "rb")}
        params = {"chat_id": chat_id, "caption": message}

        response = requests.post(url=url, params=params, files=files)
        if response.status_code == 200:
            print("Message with photo sent successfully!")
        else:
            print("Failed to send message with photo:", response.text)
        return response

    def create_message_about_add_user(
        admin_of_group: TelegramUser,
        telegram_username: str,
        subscription_start_date: str,
        subscription_end_date: str,
        subscription_plan: str,
        subscription_price: int,
        tx_hash: str,
    ) -> str:

        message = (
            f"Hi, {admin_of_group}!\n\n"
            f"Action: 🟢 add to private group\n\n"
            f"Subscription Details 📁\n"
            f"--------------------------------------\n"
            f"User: @{telegram_username}\n"
            f"--------------------------------------\n"
            f"Purchased on: {subscription_start_date}\n"
            f"--------------------------------------\n"
            f"Will expire on: {subscription_end_date}\n"
            f"--------------------------------------\n"
            f"Subscription plan: {subscription_plan}\n"
            f"--------------------------------------\n"
            f"Subscription price: {subscription_price} USDT\n"
            f"--------------------------------------\n"
            f"Hash: https://tronscan.org/#/transaction/{tx_hash}\n\n"
            "Click the link to copy the transaction hash."
        )

        return message

    def create_message_about_delete_user(
        admin_of_group: TelegramUser,
        telegram_username: str,
        subscription_start_date: str,
        subscription_end_date: str,
        subscription_plan: str,
        subscription_price: int,
        tx_hash: str,
    ) -> str:
        message = (
            f"Hi, {admin_of_group}!\n\n"
            f"Action: 🔴 delete from private group\n\n"
            f"Subscription Details 📁\n"
            f"--------------------------------------\n"
            f"User: @{telegram_username}\n"
            f"--------------------------------------\n"
            f"Purchased on: {subscription_start_date}\n"
            f"--------------------------------------\n"
            f"Expired on: {subscription_end_date}\n"
            f"--------------------------------------\n"
            f"Subscription plan: {subscription_plan}\n"
            f"--------------------------------------\n"
            f"Subscription price: {subscription_price} USDT\n"
            f"--------------------------------------\n"
            f"Hash: https://tronscan.org/#/transaction/{tx_hash}\n\n"
            "Click the link to copy the transaction hash."
        )

        return message

    def create_message_about_keep_user(
        admin_of_group: TelegramUser,
        telegram_username: str,
        subscription_start_date: str,
        subscription_end_date: str,
        subscription_plan: str,
        subscription_price: int,
        tx_hash: str,
    ) -> str:
        message = (
            f"Hi, {admin_of_group}!\n\n"
            f"Action: 🟡 keep in private group\n\n"
            f"Subscription Details 📁\n"
            f"--------------------------------------\n"
            f"User: @{telegram_username}\n"
            f"--------------------------------------\n"
            f"Extended on: {subscription_start_date}\n"
            f"--------------------------------------\n"
            f"Will expire on: {subscription_end_date}\n"
            f"--------------------------------------\n"
            f"Subscription plan: {subscription_plan}\n"
            f"--------------------------------------\n"
            f"Subscription price: {subscription_price} USDT\n"
            f"--------------------------------------\n"
            f"Hash: https://tronscan.org/#/transaction/{tx_hash}\n\n"
            "Click the link to copy the transaction hash."
        )

        return message

    def create_message_with_subscription_data(
        telegram_username: str,
        subscription_plan: str,
        subscription_start_date: str,
        subscription_end_date: str,
        subscription_price: int,
    ) -> str:
        message = (
            f"Вы можете продлить уже купленную вами раннее подписку. Вот ее детали:\n"
            f"-------------------------------------\n"
            f"План подписки: {subscription_plan}\n"
            f"-------------------------------------\n"
            f"Дата покупки: {subscription_start_date}\n"
            f"-------------------------------------\n"
            f"Дата окончания: {subscription_end_date}\n"
            f"-------------------------------------\n"
            f"Цена: {subscription_price} USDT\n"
            f"-------------------------------------\n\n"
            f"Вы также можете изменить план подписки просто выбрав другой тариф и оплатив его. Таким образом подписка будет продлена согласно новому плану."
        )

        return message

    def create_message_about_reminder(
        telegram_username: str,
        day: int,
        syntax_word: str,
    ) -> str:
        if day == 7:
            message = (
                f"Привет, @{telegram_username}!\n\n"
                f"Пишу с напоминанием о том, что у тебя заканчивается подписка через {day} {syntax_word} на закрытое сообщество «Баффеты на Уораннах»\n\n"
                f"Продли прямо сейчас, что бы внезапно не потерять информацию о закрытии ранее открытых позиций. А также не пропустить новую точку входа.\n\n"
                f"​В следующий раз я напомню за 3 дня до окончания доступа.\n\n"
                f"​Если у тебя есть мысли как улучшить наше сообщество, мы будем только рады стать еще лучше! Напиши мне или помощнику.\n\n"
                f"​​Если сообщение пришло по ошибке: у тебя по факту осталось большей дней или ты уже продлил, то напиши @BaffetnaYorannah\n\n"
            )
        elif day == 3:
            message = (
                f"​Осталось {day} {syntax_word} до окончания доступа в закрытое сообщество «Баффеты на Уораннах»\n\n"
                f"Привет, @{telegram_username}!\n\n"
                f"​Еще раз хочу поблагодарить тебя за оказанное доверие, каждый день мы улучшаем наше сообщество, и я очень хочу, чтобы мы остались вместе до конца.\n\n"
                f"​Есть несколько вариантов развития событий:\n"
                f"​1️⃣ ​Ты продлеваешь доступ в течение трех дней по самым выгодным условиям, плюс тебя не удаляет бот и не придется заново заходить и искать всю информацию по открытым позициям - самый лучший и комфортный вариант.\n"
                f"​2️⃣ ​Ты продлеваешься по тем же условиям в течение 14 дней после окончания доступа, но тогда придется заново искать информацию по открытым позициям - не самый комфортный, но по прежнему выгодный вариант.\n\n"
                f"​❗️ В случае, если ты не продлеваешь доступ через 14 дней после окончания доступа - все твои выгодные условия навсегда сгорают и дальше возможно вернуться только по актуальной высокой цене.\n\n"
            )

        elif day == 1:
            message = (
                f"​​ОСТАЛСЯ ПОСЛЕДНИЙ {syntax_word.upper()} ДОСТУПА\n\n"
                f"Привет, @{telegram_username}!\n\n"
                f"​​Грустно осознавать, что сегодня возможно последний день, когда мы вместе – на ближайшие полгода запланировано большой количество сильных изменений, напрямую влияющих на результат всех участников + рынок сейчас один из самых перспективных.\n\n"
                f"​​В принципе все слова уже были сказаны, но в любом случае если ты в ближайшие полгода готов окружить себя мнениями лучших аналитиков + нашими авторскими материала + сильным окружением + поддержкой по всем вопросам – поторопись с продлением, через 24 часа бот тебя отовсюду удалит.\n\n"
            )

        return message
