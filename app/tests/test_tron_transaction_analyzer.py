import unittest
from unittest.mock import patch

import pytest

from subscription_service.views import TronTransactionAnalyzer


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
            "trc20TransferInfo": [
                {
                    "to_address": TronTransactionAnalyzer.STAS_TRC20_WALLET_ADDRESS,
                    "amount_str": "100000000",
                    "decimals": 6,
                }
            ]
        }
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_get.return_value = mock_response

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
            ]
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
