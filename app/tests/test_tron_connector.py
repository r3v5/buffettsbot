import unittest
from unittest.mock import patch
from subscription_service.views import TronConnector


class TestTronConnector(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        # Set up environment variables for testing
        cls.API_ENDPOINT = 'test_endpoint'
        cls.API_KEY = 'test_api_key'
        cls.STAS_TRC20_WALLET_ADDRESS = 'test_wallet_address'


    def test_convert_string_to_trc20(self):
        # Test the convert_string_to_trc20 method
        amount_str = '100000000'
        decimals = 6
        result = TronConnector.convert_string_to_trc20(amount_str, decimals)
        self.assertEqual(result, 100)


    @patch('requests.get')
    def test_validate_tx_hash(self, mock_get):
        # Mock response data
        mock_response_data = {
            "trc20TransferInfo": [
                {
                    "to_address": TronConnector.STAS_TRC20_WALLET_ADDRESS,
                    "amount_str": "100000000",
                    "decimals": 6
                }
            ]
        }


        # Mock the response object
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_get.return_value = mock_response


        # Test case where amount_usdt >= plan_price
        tx_hash = 'test_tx_hash'
        plan_price = 100
        result = TronConnector.validate_tx_hash(tx_hash, plan_price)
        self.assertTrue(result)


        # Test case where amount_usdt < plan_price
        plan_price = 200
        result = TronConnector.validate_tx_hash(tx_hash, plan_price)
        self.assertFalse(result)


    @patch('requests.get')
    def test_validate_tx_hash_error_handling(self, mock_get):
        # Test error handling in is_tx_hash_valid method

        # Mock the response object to simulate a failed request
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        tx_hash = 'test_tx_hash'
        plan_price = 100
        result = TronConnector.validate_tx_hash(tx_hash, plan_price)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()