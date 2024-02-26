import pytest
from subscription_service.models import TelegramUser, Plan, Subscription
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
def test_telegram_user_model():
    telegram_user = TelegramUser(
        telegram_id=2141241241245,
        chat_id=2141241241245,
        telegram_username='@TestUser',
        first_name='Conor',
        last_name='McGregor',
    )
    assert telegram_user.telegram_id == 2141241241245
    assert telegram_user.chat_id == 2141241241245
    assert telegram_user.telegram_username == '@TestUser'
    assert telegram_user.first_name == 'Conor'
    assert telegram_user.last_name == 'McGregor'
    assert telegram_user.is_staff == False
    assert telegram_user.date_joined.date() == timezone.now().date()


@pytest.mark.django_db
def test_telegram_user_str_method():
    # Create a CustomUser object
    user = TelegramUser.objects.create(telegram_username='@user1')

    # Check if the __str__ method returns the telegram_username
    assert str(user) == '@user1'


@pytest.mark.django_db
def test_plan_model():
    plan = Plan.objects.create(period='2 days')
    assert plan.price == 19

    plan = Plan.objects.create(period='1 month')
    assert plan.price == 150

    plan = Plan.objects.create(period='3 months')
    assert plan.price == 400

    plan = Plan.objects.create(period='6 months')
    assert plan.price == 600

    plan = Plan.objects.create(period='1 year')
    assert plan.price == 1000


@pytest.mark.django_db
def test_save_method():
    plan = Plan(period='2 days')
    plan.save()
    assert plan.price == 19

    plan = Plan(period='1 month')
    plan.save()
    assert plan.price == 150

    plan = Plan(period='3 months')
    plan.save()
    assert plan.price == 400

    plan = Plan(period='6 months')
    plan.save()
    assert plan.price == 600

    plan = Plan(period='1 year')
    plan.save()
    assert plan.price == 1000


@pytest.mark.django_db
def test_subscription_model():
    # Create a test plan
    plan = Plan.objects.create(period='2 days', price=19)

    # Create a test user
    user = TelegramUser.objects.create(telegram_username='@test_user')

    # Create a subscription
    subscription = Subscription.objects.create(
        customer=user,
        plan=plan,
        start_date=timezone.now()
    )

    # Check if the end_date is correctly set based on the plan's period
    assert subscription.end_date == subscription.start_date + timedelta(days=2)

    # Check if the user's at_private_group field is updated to True
    user.refresh_from_db()
    assert user.at_private_group == True


@pytest.mark.django_db
def test_save_method():
    # Create a test plan
    plan = Plan.objects.create(period='1 month', price=150)

    # Create a test user
    user = TelegramUser.objects.create(telegram_username='@test_user')

    # Create a subscription
    subscription = Subscription(
        customer=user,
        plan=plan,
        start_date=timezone.now()
    )
    subscription.save()

    # Check if the end_date is correctly set based on the plan's period
    assert subscription.end_date == subscription.start_date + timedelta(days=30)

    # Check if the user's at_private_group field is updated to True
    user.refresh_from_db()
    assert user.at_private_group == True