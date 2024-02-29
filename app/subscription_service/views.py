from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import HttpResponse, HttpRequest
from rest_framework import status
from .serializers import TelegramUserSerializer, SubscriptionSerializer
import os
import requests
from .models import TelegramUser, Plan


class TronConnector:
    API_ENDPOINT = os.environ.get('API_ENDPOINT')
    API_KEY = os.environ.get('API_KEY')
    STAS_TRC20_WALLET_ADDRESS = os.environ.get('STAS_TRC20_WALLET_ADDRESS')


    @staticmethod
    def convert_string_to_trc20(amount_str: str, decimals: int) -> int:
        return int(int(amount_str) / (10 ** decimals))


    @classmethod
    # add plan_name: str as a parameter
    def is_tx_hash_valid(cls, tx_hash: str, plan_price: int) -> bool:
        is_valid = False
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
                        print(f"Stanislav Ivankin {cls.STAS_TRC20_WALLET_ADDRESS} didn't get your USDT!", is_valid)
                        return is_valid
                    else:
                        amount_usdt = cls.convert_string_to_trc20(
                            transfer_info["amount_str"],
                            transfer_info["decimals"]
                        )
                        if amount_usdt >= plan_price:
                            result = {
                                "tx_hash": tx_hash,
                                "to_address": transfer_info["to_address"],
                                "amount_usdt": amount_usdt,
                                "subscription_price": plan_price
                            }
                            is_valid = True
                            print(result, is_valid)
                            return is_valid
                        else:
                            result = {
                                "tx_hash": tx_hash,
                                "to_address": transfer_info["to_address"],
                                "amount_usdt": amount_usdt,
                                "subscription_price": plan_price
                            }
                            print(result, is_valid)
                            return is_valid
            else:
                print(f"Error: {response.status_code}")
                return is_valid
        except Exception as e:
            print(f"Error occurred: {e}")
            return is_valid
    

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
        plan_name = data.get('plan')
        transaction_hash = data.get('transaction_hash')


        # Find the user with the given telegram_username
        try:
            user = TelegramUser.objects.get(telegram_username=telegram_username)
        except TelegramUser.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


        # Find the plan with the given plan name
        try:
            plan = Plan.objects.get(period=plan_name)
        except Plan.DoesNotExist:
            return Response({'message': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
        

        # Get the price of the plan
        plan_price = plan.price


        success = TronConnector.is_tx_hash_valid(tx_hash=transaction_hash, plan_price=plan_price)
        if success:
            subscription_data = {
                'customer': user.pk,
                'plan': plan.pk,
                'transaction_hash': transaction_hash
            }
            serializer = SubscriptionSerializer(data=subscription_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)