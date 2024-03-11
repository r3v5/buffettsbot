import pytz
from django.http import HttpRequest, HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from subscription_service.utils import TelegramMessageSender, TronTransactionAnalyzer

from .models import Plan, Subscription, TelegramUser
from .serializers import (
    GetSubscriptionSerializer,
    PostSubscriptionSerializer,
    TelegramUserSerializer,
)


class TelegramUserAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = ()

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "chat_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Chat id of the Telegram user",
                ),
                "telegram_username": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The username of the Telegram user",
                ),
            },
        ),
        operation_description="Create a Telegram User",
    )
    def post(self, request: HttpRequest) -> HttpResponse:
        serializer = TelegramUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            res = {"status": status.HTTP_201_CREATED, "data": serializer.data}
            return Response(res, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = ()

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "telegram_username",
                openapi.IN_QUERY,
                description="The username of the Telegram user",
                type=openapi.TYPE_STRING,
            )
        ],
        operation_description="Get a subscription",
    )
    def get(self, request: HttpRequest) -> HttpResponse:

        # Get the username from the query parameters
        telegram_username = request.query_params.get("telegram_username")

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

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "telegram_username": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The username of the Telegram user.",
                ),
                "plan": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The name of the plan for the subscription.",
                ),
                "transaction_hash": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The transaction hash for the subscription.",
                ),
            },
        ),
        operation_description="Buy a subscription",
    )
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
            # Allow user to extend his subscription
            try:
                subscription = Subscription.objects.get(customer=user)
                subscription.delete()
                user.delete_from_private_group()
                extended_subscription_data = {
                    "customer": user.chat_id,
                    "plan": plan.pk,
                    "transaction_hash": transaction_hash,
                }
                serializer = PostSubscriptionSerializer(data=extended_subscription_data)
                if serializer.is_valid():
                    user.add_to_private_group()
                    serializer.save()

                    # Convert time in Moscow time zone
                    moscow_tz = pytz.timezone("Europe/Moscow")

                    # Get extended subscription
                    extended_subscription = serializer.instance
                    telegram_username = extended_subscription.customer.telegram_username
                    subscription_plan = extended_subscription.plan.period
                    subscription_price = extended_subscription.plan.price
                    tx_hash = extended_subscription.transaction_hash
                    subscription_start_date = (
                        extended_subscription.start_date.astimezone(moscow_tz).strftime(
                            "%d/%m/%Y %H:%M:%S"
                        )
                    )
                    subscription_end_date = extended_subscription.end_date.astimezone(
                        moscow_tz
                    ).strftime("%d/%m/%Y %H:%M:%S")

                    # Get the admins
                    try:
                        admins_of_group = TelegramUser.objects.filter(is_staff=True)
                        print("Found users:", admins_of_group)
                    except TelegramUser.DoesNotExist:
                        print("Users not found.")

                    for admin in admins_of_group:
                        try:
                            message = (
                                TelegramMessageSender.create_message_about_keep_user(
                                    admin_of_group=admin.telegram_username,
                                    telegram_username=telegram_username,
                                    subscription_start_date=subscription_start_date,
                                    subscription_end_date=subscription_end_date,
                                    subscription_plan=subscription_plan,
                                    subscription_price=subscription_price,
                                    tx_hash=tx_hash,
                                )
                            )

                            response = TelegramMessageSender.send_message_to_chat(
                                message=message, chat_id=admin.chat_id
                            )
                            if response.status_code == 200:
                                print(
                                    f"User {telegram_username} must be kept in the group."
                                )
                            else:
                                print(
                                    f"Failed to keep user {telegram_username} in the group. Status code: {response.status_code}"
                                )
                        except Exception as e:
                            print(
                                f"Failed to keep user {telegram_username} in the group: {str(e)}"
                            )

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
