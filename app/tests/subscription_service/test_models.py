from datetime import timedelta

import pytest
from django.db import IntegrityError
from django.utils import timezone
from subscription_service.models import Plan, Subscription, TelegramUser


@pytest.mark.django_db
def test_telegram_user_model():
    telegram_user = TelegramUser(
        chat_id=2141241241245,
        telegram_username="@TestUser",
        first_name="Conor",
        last_name="McGregor",
        at_private_group=False,
    )
    assert telegram_user.chat_id == 2141241241245
    assert telegram_user.telegram_username == "@TestUser"
    assert telegram_user.first_name == "Conor"
    assert telegram_user.last_name == "McGregor"
    assert telegram_user.at_private_group is False
    assert telegram_user.is_staff is False
    assert telegram_user.date_joined.date() == timezone.now().date()


@pytest.mark.django_db
def test_telegram_user_str_method():
    # Create a CustomUser object
    user = TelegramUser.objects.create(chat_id=32896732649, telegram_username="@user1")

    # Check if the __str__ method returns the telegram_username
    assert str(user) == "@user1"


@pytest.mark.django_db
def test_create_plan():
    # Test creating a plan
    Plan.objects.create(period="1 month", price=100)
    saved_plan = Plan.objects.get(period="1 month")
    assert Plan.objects.count() == 1
    assert saved_plan.period == "1 month"
    assert saved_plan.price == 100


@pytest.mark.django_db
def test_unique_period():
    # Test unique constraint on period field
    Plan.objects.create(period="1 month", price=100)
    with pytest.raises(Exception):
        Plan.objects.create(period="1 month", price=100)


@pytest.mark.django_db
def test_plan_string_representation():
    # Test string representation of Plan model
    plan = Plan.objects.create(period="1 month", price=100)
    assert str(plan) == "1 month Plan - $100"


@pytest.mark.django_db
def test_subscription_model():
    # Create a test plan
    plan = Plan.objects.create(period="1 month", price=100)

    # Create a test user
    user = TelegramUser.objects.create(
        chat_id=123456789, telegram_username="@test_user"
    )

    # Create a subscription
    subscription = Subscription.objects.create(
        customer=user,
        plan=plan,
        transaction_hash="0owq2i3nfqwiofnnqwoi",
        start_date=timezone.now(),
    )

    saved_subscription = Subscription.objects.get(
        transaction_hash="0owq2i3nfqwiofnnqwoi"
    )

    # Check if the end_date is calculated correctly
    expected_end_date = subscription.start_date + timedelta(days=30)

    # Check if the end_date is correctly set based on the plan's period
    assert saved_subscription.end_date == expected_end_date


@pytest.mark.django_db
def test_subscription_save():
    # Create a test plan
    plan = Plan.objects.create(period="1 month", price=100)

    # Create a test user
    user = TelegramUser.objects.create(
        chat_id=123456789, telegram_username="@test_user"
    )

    # Create a subscription with a plan
    subscription_with_plan = Subscription.objects.create(
        customer=user,
        plan=plan,
        transaction_hash="0owq2i3nfqwiofnnqwoi_with_plan",
        start_date=timezone.now(),
    )

    # Ensure that both subscriptions were saved successfully
    assert subscription_with_plan.pk is not None
    assert subscription_with_plan.plan.period == plan.period
    assert subscription_with_plan.customer == user
    assert subscription_with_plan.transaction_hash is not None
    assert subscription_with_plan.start_date is not None


@pytest.mark.django_db
def test_subscription_end_date_calculation():
    # Test if end_date is calculated correctly for different plan periods
    start_date = timezone.now()

    # Test 1 month plan
    plan_1_month = Plan.objects.create(period="1 month", price=29)
    subscription_1_month = Subscription.objects.create(
        customer=None,
        plan=plan_1_month,
        transaction_hash="0owq2i3nfqwiofnnqwoi_1_month",
        start_date=start_date,
    )
    assert subscription_1_month.end_date == start_date + timezone.timedelta(days=30)

    # Test 3 months plan
    plan_3_months = Plan.objects.create(period="3 months", price=79)
    subscription_3_months = Subscription.objects.create(
        customer=None,
        plan=plan_3_months,
        transaction_hash="0owq2i3nfqwiofnnqwoi_3_months",
        start_date=start_date,
    )
    assert subscription_3_months.end_date == start_date + timezone.timedelta(days=90)

    # Test 6 months plan
    plan_6_months = Plan.objects.create(period="6 months", price=149)
    subscription_6_months = Subscription.objects.create(
        customer=None,
        plan=plan_6_months,
        transaction_hash="0owq2i3nfqwiofnnqwoi_6_months",
        start_date=start_date,
    )
    assert subscription_6_months.end_date == start_date + timezone.timedelta(days=180)

    # Test 1 year plan
    plan_1_year = Plan.objects.create(period="1 year", price=279)
    subscription_1_year = Subscription.objects.create(
        customer=None,
        plan=plan_1_year,
        transaction_hash="0owq2i3nfqwiofnnqwoi_1_year",
        start_date=start_date,
    )
    assert subscription_1_year.end_date == start_date + timezone.timedelta(days=365)


@pytest.mark.django_db
def test_create_subscription_without_plan():
    # Test creating a subscription without specifying a plan
    with pytest.raises(ValueError):
        Subscription.objects.create(
            customer=None,
            plan=None,
            transaction_hash="0owq2i3nfqwiofnnqwoi_no_plan",
            start_date=timezone.now(),
        )


@pytest.mark.django_db
def test_unique_transaction_hash():
    # Test unique constraint on transaction_hash field
    Subscription.objects.create(
        customer=None,
        plan=Plan.objects.create(period="1 month", price=100),
        transaction_hash="0owq2i3nfqwiofnnqwoi_unique",
        start_date=timezone.now(),
    )
    with pytest.raises(Exception):
        Subscription.objects.create(
            customer=None,
            plan=Plan.objects.create(period="1 month", price=100),
            transaction_hash="0owq2i3nfqwiofnnqwoi_unique",
            start_date=timezone.now(),
        )


@pytest.mark.django_db
def test_negative_plan_price():
    # Test creating a plan with a negative price
    with pytest.raises(IntegrityError):
        Plan.objects.create(period="1 month", price=-10)


@pytest.mark.django_db
def test_subscription_model_relationships():
    # Test relationships in Subscription model
    user = TelegramUser.objects.create(
        chat_id=123456789, telegram_username="@test_user"
    )
    plan = Plan.objects.create(period="1 month", price=100)
    subscription = Subscription.objects.create(
        customer=user,
        plan=plan,
        transaction_hash="0owq2i3nfqwiofnnqwoi_relationships",
        start_date=timezone.now(),
    )

    assert subscription.customer == user
    assert subscription.plan == plan
