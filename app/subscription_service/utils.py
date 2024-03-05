import os
from datetime import datetime
from typing import Union

import requests


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
    TELEGRAM_PRIVATE_GROUP_ID = os.environ.get("TELEGRAM_PRIVATE_GROUP_ID")

    @classmethod
    def send_message_to_admin_of_group(
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
