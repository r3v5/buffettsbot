import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from subscription_service.views import TelegramMessageSender, TronTransactionAnalyzer


@pytest.mark.django_db
class TestTronTransactionAnalyzer:

    def test_convert_string_to_trc20(self):
        # Test the convert_string_to_trc20 method
        amount_str = "100000000"
        decimals = 6
        result = TronTransactionAnalyzer.convert_string_to_trc20(amount_str, decimals)
        assert result == 100

    @patch("requests.get")
    def test_validate_tx_hash_valid(self, mock_get):
        # Test case where amount_usdt >= plan_price
        tx_hash = "test_tx_hash"
        plan_price = 100
        mock_response_data = {
            "timestamp": 1623334000000,  # Example timestamp data
            "trc20TransferInfo": [
                {
                    "to_address": TronTransactionAnalyzer.STAS_TRC20_WALLET_ADDRESS,
                    "amount_str": "100000000",
                    "decimals": 6,
                }
            ],
        }
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_get.return_value = mock_response

        # Patch the convert_timestamp_to_date_format method to return today's date
        with patch.object(
            TronTransactionAnalyzer,
            "convert_timestamp_to_date_format",
            return_value=datetime.today().date(),
        ):
            result = TronTransactionAnalyzer.validate_tx_hash(tx_hash, plan_price)
            assert result

    @patch("requests.get")
    def test_validate_tx_hash_invalid(self, mock_get):
        # Test case where amount_usdt < plan_price
        tx_hash = "test_tx_hash"
        plan_price = 200
        mock_response_data = {
            "trc20TransferInfo": [
                {
                    "to_address": TronTransactionAnalyzer.STAS_TRC20_WALLET_ADDRESS,
                    "amount_str": "50000000",
                    "decimals": 6,
                }
            ],
        }
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_get.return_value = mock_response

        result = TronTransactionAnalyzer.validate_tx_hash(tx_hash, plan_price)
        assert not result

    @patch("requests.get")
    def test_validate_tx_hash_error_handling(self, mock_get):
        # Test error handling in validate_tx_hash method
        tx_hash = "test_tx_hash"
        plan_price = 100
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = TronTransactionAnalyzer.validate_tx_hash(tx_hash, plan_price)
        assert not result

    def test_convert_timestamp_to_date_format(self):
        # Test conversion of timestamp to date format
        timestamp = 1623334000000  # Example timestamp data
        expected_date = datetime.utcfromtimestamp(timestamp / 1000).date()

        result_date = TronTransactionAnalyzer.convert_timestamp_to_date_format(
            timestamp
        )

        assert result_date == expected_date

    def test_check_transaction_was_today(self):
        # Test transaction date checking function
        today_date = datetime.today().date()
        result_today = TronTransactionAnalyzer.check_transaction_was_today(today_date)
        assert result_today is True

        # Test with a date that is not today
        yesterday_date = today_date - timedelta(days=1)
        result_yesterday = TronTransactionAnalyzer.check_transaction_was_today(
            yesterday_date
        )
        assert result_yesterday is False

    def test_convert_string_to_trc20_boundary_conditions(self):
        # Test the convert_string_to_trc20 method with boundary conditions
        # Test with the maximum possible amount and decimals
        amount_str_max = str(10**18)  # Maximum possible amount
        decimals_max = 18
        result_max = TronTransactionAnalyzer.convert_string_to_trc20(
            amount_str_max, decimals_max
        )
        assert result_max == 1

        # Test with the minimum possible amount and decimals
        amount_str_min = "0"
        decimals_min = 0
        result_min = TronTransactionAnalyzer.convert_string_to_trc20(
            amount_str_min, decimals_min
        )
        assert result_min == 0

    @patch("requests.get")
    def test_validate_tx_hash_malformed_data(self, mock_get):
        # Test error handling in validate_tx_hash method when API returns malformed data
        tx_hash = "test_tx_hash"
        plan_price = 100
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid_key": "invalid_value"}
        mock_get.return_value = mock_response

        result = TronTransactionAnalyzer.validate_tx_hash(tx_hash, plan_price)
        assert not result


@pytest.mark.django_db
class TestTelegramMessageSender:

    @patch("requests.post")
    def test_send_message_to_chat_success(self, mock_post):
        # Mock the response from the API
        mock_post.return_value.status_code = 200

        # Test sending a message to the chat
        response = TelegramMessageSender.send_message_to_chat("Test Message", 123)

        # Assert that the response is successful
        assert response.status_code == 200

    @patch("requests.post")
    def test_send_message_to_chat_failure(self, mock_post):
        # Mock the response from the API
        mock_post.return_value.status_code = 500

        # Test sending a message to the chat
        response = TelegramMessageSender.send_message_to_chat("Test Message", 123)

        # Assert that the response is unsuccessful
        assert response.status_code == 500

    @patch("requests.post")
    def test_send_message_with_photo_to_chat_success(self, mock_post):
        # Mock the response from the API
        mock_post.return_value.status_code = 200

        # Test sending a message with photo to the chat
        response = TelegramMessageSender.send_message_with_photo_to_chat(
            "Test Message", "media/buffets-on-crows.jpg", 123
        )

        # Assert that the response is successful
        assert response.status_code == 200

    def test_create_message_about_add_user(self):
        # Test create_message_about_add_user method
        expected_message = (
            "Hi, John!\n\n"
            "Action: 🟢 add to private group\n\n"
            "Subscription Details 📁\n"
            "--------------------------------------\n"
            "User: @username\n"
            "--------------------------------------\n"
            "Purchased on: 2024-03-07\n"
            "--------------------------------------\n"
            "Will expire on: 2025-03-07\n"
            "--------------------------------------\n"
            "Subscription plan: 1 year\n"
            "--------------------------------------\n"
            "Subscription price: 1000 USDT\n"
            "--------------------------------------\n"
            "Hash: https://tronscan.org/#/transaction/abc123\n\n"
            "Click the link to copy the transaction hash."
        )

        message = TelegramMessageSender.create_message_about_add_user(
            admin_of_group="John",
            telegram_username="username",
            subscription_start_date="2024-03-07",
            subscription_end_date="2025-03-07",
            subscription_plan="1 year",
            subscription_price=1000,
            tx_hash="abc123",
        )

        assert message == expected_message

    def test_create_message_about_delete_user(self):
        # Test create_message_about_add_user method
        expected_message = (
            "Hi, admin!\n\n"
            "Action: 🔴 delete from private group\n\n"
            "Subscription Details 📁\n"
            "--------------------------------------\n"
            "User: @JOanix\n"
            "--------------------------------------\n"
            "Purchased on: 2024-03-07\n"
            "--------------------------------------\n"
            "Expired on: 2025-03-07\n"
            "--------------------------------------\n"
            "Subscription plan: 1 year\n"
            "--------------------------------------\n"
            "Subscription price: 1000 USDT\n"
            "--------------------------------------\n"
            "Hash: https://tronscan.org/#/transaction/x123\n\n"
            "Click the link to copy the transaction hash."
        )

        message = TelegramMessageSender.create_message_about_delete_user(
            admin_of_group="admin",
            telegram_username="JOanix",
            subscription_start_date="2024-03-07",
            subscription_end_date="2025-03-07",
            subscription_plan="1 year",
            subscription_price=1000,
            tx_hash="x123",
        )

        assert message == expected_message

    def test_create_message_about_keep_user(self):
        # Test create_message_about_add_user method
        expected_message = (
            "Hi, admin!\n\n"
            "Action: 🟡 keep in private group\n\n"
            "Subscription Details 📁\n"
            "--------------------------------------\n"
            "User: @JOanix\n"
            "--------------------------------------\n"
            "Extended on: 2024-03-07\n"
            "--------------------------------------\n"
            "Will expire on: 2025-03-07\n"
            "--------------------------------------\n"
            "Subscription plan: 1 year\n"
            "--------------------------------------\n"
            "Subscription price: 1000 USDT\n"
            "--------------------------------------\n"
            "Hash: https://tronscan.org/#/transaction/x123\n\n"
            "Click the link to copy the transaction hash."
        )

        message = TelegramMessageSender.create_message_about_keep_user(
            admin_of_group="admin",
            telegram_username="JOanix",
            subscription_start_date="2024-03-07",
            subscription_end_date="2025-03-07",
            subscription_plan="1 year",
            subscription_price=1000,
            tx_hash="x123",
        )

        assert message == expected_message

    def test_create_message_about_reminder(self):
        # Test create_message_about_add_user method
        expected_message = (
            "Привет, @JOanix!\n\n"
            "Пишу с напоминанием о том, что у тебя заканчивается подписка через 7 дней на закрытое сообщество «Баффеты на Уораннах»\n\n"
            "Продли прямо сейчас, что бы внезапно не потерять информацию о закрытии ранее открытых позиций. А также не пропустить новую точку входа.\n\n"
            "Вы можете продлить уже купленную вами раннее подписку. Вот ее детали:\n"
            "-------------------------------------\n"
            "План подписки: 1 year\n"
            "-------------------------------------\n"
            "Дата покупки: 2024-03-07\n"
            "-------------------------------------\n"
            "Дата окончания: 2025-03-07\n"
            "-------------------------------------\n"
            "Цена: 1000 USDT\n"
            "-------------------------------------\n\n"
            "Вы также можете изменить план подписки просто выбрав другой тариф и оплатив его. Таким образом подписка будет продлена согласно новому плану.\n\n"
            "Для нашей команды очень важно получить обратную связь, на пути построения типового сообщества по крипте. Заполни анкету, если конечно ты ранее этого не делал.\n\n"
            "По всем вопросам, пожалуйста, обращайтесь сюда @BaffetConcierge"
        )

        message = TelegramMessageSender.create_message_about_reminder(
            telegram_username="JOanix",
            subscription_start_date="2024-03-07",
            subscription_end_date="2025-03-07",
            subscription_plan="1 year",
            subscription_price=1000,
            day=7,
            syntax_word="дней",
        )

        assert message == expected_message
