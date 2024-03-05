import os
from datetime import datetime

import requests
from django.http import HttpRequest, HttpResponse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from subscription_service.utils import TronTransactionAnalyzer

from .models import Plan, Subscription, TelegramUser
from .serializers import (
    GetSubscriptionSerializer,
    PostSubscriptionSerializer,
    TelegramUserSerializer,
)


class TelegramUserAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: HttpRequest) -> HttpResponse:
        serializer = TelegramUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            res = {"status": status.HTTP_201_CREATED, "data": serializer.data}
            return Response(res, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: HttpRequest) -> HttpResponse:
        data = request.data

        # Get the username from the query parameters
        telegram_username = data.get("telegram_username")

        # Find the user with the given telegram_username
        try:
            user = TelegramUser.objects.get(telegram_username=telegram_username)
        except TelegramUser.DoesNotExist:
            return Response(
                {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Retrieve the subscription for the user
        try:
            subscription = Subscription.objects.get(customer=user)
        except Subscription.DoesNotExist:
            return Response(
                {"message": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Initialize the serializer with the subscription instance
        serializer = GetSubscriptionSerializer(instance=subscription)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: HttpRequest) -> HttpResponse:
        data = request.data

        # Extract data from request JSON
        telegram_username = data.get("telegram_username")
        plan_name = data.get("plan")
        transaction_hash = data.get("transaction_hash")

        # Find the user with the given telegram_username
        try:
            user = TelegramUser.objects.get(telegram_username=telegram_username)
        except TelegramUser.DoesNotExist:
            return Response(
                {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Find the plan with the given plan name
        try:
            plan = Plan.objects.get(period=plan_name)
        except Plan.DoesNotExist:
            return Response(
                {"message": "Plan not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Get the price of the plan
        plan_price = plan.price

        # Check if the transaction hash is already used
        if Subscription.objects.filter(transaction_hash=transaction_hash).exists():
            raise ValidationError("Transaction hash already used for subscription.")

        success = TronTransactionAnalyzer.validate_tx_hash(
            tx_hash=transaction_hash, plan_price=plan_price
        )
        if success:
            try:
                subscription = Subscription.objects.get(customer=user)
                subscription.delete()
                extended_subscription_data = {
                    "customer": user.chat_id,
                    "plan": plan.pk,
                    "transaction_hash": transaction_hash,
                }
                serializer = PostSubscriptionSerializer(data=extended_subscription_data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            except Subscription.DoesNotExist:
                # If the user does not have a subscription, create a new subscription
                subscription_data = {
                    "customer": user.chat_id,
                    "plan": plan.pk,
                    "transaction_hash": transaction_hash,
                }
                serializer = PostSubscriptionSerializer(data=subscription_data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            response = {
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Transaction is not valid",
                "success": success,
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
