from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import HttpResponse, HttpRequest
from rest_framework import status
from .serializers import TelegramUserSerializer, SubscriptionSerializer
import os, requests
from .models import TelegramUser, Subscription, Plan


'''class SubscriptionChecker:
    VALID_SUBSCRIPTIONS_USDT = set([19, 150, 400, 600, 1000])


    @classmethod
    def is_subscriber(cls, amount_usdt: int) -> bool:
        if amount_usdt in cls.VALID_SUBSCRIPTIONS_USDT or amount_usdt > max(cls.VALID_SUBSCRIPTIONS_USDT):
            return True
        else:
            return False


class TronConnector:
    API_ENDPOINT = os.environ.get("API_ENDPOINT")
    API_KEY = os.environ.get("API_KEY")
    STAS_TRC20_WALLET_ADDRESS = os.environ.get("STAS_TRC20_WALLET_ADDRESS")


    @staticmethod
    def convert_string_to_trc20(amount_str: str, decimals: int) -> int:
        return int(int(amount_str) / (10 ** decimals))


    @classmethod
    def is_tx_hash_valid(cls, tx_hash: str) -> bool:
        url = f'{cls.API_ENDPOINT}={tx_hash}'
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'TRON-PRO-API-KEY': f'{cls.API_KEY}'
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                valid_data = response.json()
                for transfer_info in valid_data["trc20TransferInfo"]:
                    if transfer_info["to_address"] != cls.STAS_TRC20_WALLET_ADDRESS:
                        print(f"Stanislav Ivankin {cls.STAS_TRC20_WALLET_ADDRESS} didn't get your USDT!")
                        return False
                    else:
                        amount_usdt = cls.convert_string_to_trc20(
                            transfer_info["amount_str"],
                            transfer_info["decimals"]
                        )
                        is_subscriber = SubscriptionChecker.is_subscriber(amount_usdt)
                        if is_subscriber:
                            result = {
                                "tx_hash": tx_hash,
                                "to_address": transfer_info["to_address"],
                                "amount_usdt": amount_usdt,
                                "is_subscriber": is_subscriber
                            }
                            print(result)
                            return True
                        else:
                            return False
            else:
                print(f"Error: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error occurred: {e}")
            return False
    

# Valid test case
tx = TronConnector.is_tx_hash_valid("357648462a7b472c7ac1123550023a0674aca4849fc385bd67e3a51aeb492564")
print(f"{tx}\n")


# Unvalid test case where to address isn't Stas's wallet address
tx = TronConnector.is_tx_hash_valid("bea676853563a236e355aae05622aae5f28a03f071280ac4b907cc9147667b41")
print(f"{tx}\n")


# Unvalid test case where there is no USDT token
tx = TronConnector.is_tx_hash_valid("b55cc2b0103ca8933e72bdd7e42269220b1b7e1b1a27448571aa03cb3c7875ea")
print(f"{tx}\n")'''


class TelegramUserAPIView(APIView):
    permission_classes = [AllowAny]


    def post(self, request: HttpRequest) -> HttpResponse:
        serializer = TelegramUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            res = {
                "status": status.HTTP_201_CREATED,
                "data": serializer.data
            }
            return Response(res, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionAPIView(APIView):
    permission_classes = [AllowAny]


    def post(self, request: HttpRequest) -> HttpResponse:
        data = request.data

        # Extract data from request JSON
        telegram_username = data.get('telegram_username')
        plan_id = data.get('plan')
        transaction_hash = data.get('transaction_hash')

        # Find the user with the given telegram_username
        try:
            user = TelegramUser.objects.get(telegram_username=telegram_username)
        except TelegramUser.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create the subscription data with primary key values
        subscription_data = {
            'customer': user.pk,  # Pass the primary key value instead of the object
            'plan': plan_id,      # Pass the primary key value instead of the object
            'transaction_hash': transaction_hash
        }
        serializer = SubscriptionSerializer(data=subscription_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)