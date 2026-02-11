import datetime as dt

import pytest
from django.db import IntegrityError

from furnace_booking.models import (
    BookingOfEquipment,
    BookingOfFurnace,
    Equipment,
    Furnace,
)
from news.models import Articles
from users.models import ConfirmEmailToken, Person, User


pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(
        email='USER@Example.COM',
        password='strong-pass-123',
        first_name='Ivan',
        last_name='Petrov',
    )


@pytest.fixture
def token_user():
    return User.objects.create_user(
        email='token-user@example.com',
        password='strong-pass-123',
        first_name='Token',
        last_name='Owner',
    )


@pytest.fixture
def token_unique_user():
    return User.objects.create_user(
        email='token-unique@example.com',
        password='strong-pass-123',
    )


@pytest.fixture
def person():
    return Person.objects.create(first_name='Petr', surname='Sidorov')


@pytest.fixture
def furnace():
    return Furnace.objects.create(
        name='Furnace-1',
        location='Lab A',
        serviceable=True,
        max_temperature=1200,
        min_temperature=200,
        is_clean=True,
    )


@pytest.fixture
def equipment():
    return Equipment.objects.create(name='Press-1', location='Lab B')


@pytest.fixture
def furnace_booking_date():
    return dt.date(2026, 1, 15)


@pytest.fixture
def equipment_booking_date():
    return dt.date(2026, 1, 16)


def test_user_create_user_and_str(user):
    assert user.email == 'USER@example.com'
    assert user.username == 'unlnown'
    assert str(user) == 'Ivan Petrov'
    assert user.is_staff is False
    assert user.is_superuser is False


def test_user_create_user_requires_email_and_password():
    with pytest.raises(ValueError):
        User.objects.create_user(email='', password='x')

    with pytest.raises(ValueError):
        User.objects.create_user(email='u@example.com', password=None)


def test_user_create_superuser_flags_and_validation():
    admin = User.objects.create_superuser(
        email='admin@example.com',
        password='strong-pass-123',
    )

    assert admin.is_staff is True
    assert admin.is_superuser is True

    with pytest.raises(ValueError):
        User.objects.create_superuser(
            email='bad-admin@example.com',
            password='strong-pass-123',
            is_staff=False,
        )


def test_person_str(person):
    assert str(person) == 'Petr Sidorov'


def test_confirm_email_token_autogenerates_key_and_str(token_user):
    token = ConfirmEmailToken.objects.create(user=token_user)

    assert token.key
    assert len(token.key) > 0
    assert str(token) == f'Password reset token for user {token_user}'


def test_confirm_email_token_unique_key(token_unique_user):
    ConfirmEmailToken.objects.create(user=token_unique_user, key='fixed-key-123')

    with pytest.raises(IntegrityError):
        ConfirmEmailToken.objects.create(user=token_unique_user, key='fixed-key-123')


def test_furnace_and_equipment_str_and_person_relation(person, furnace, equipment):
    furnace.user.add(person)
    equipment.user.add(person)

    assert str(furnace) == 'Furnace-1'
    assert str(equipment) == 'Press-1'
    assert person in furnace.user.all()
    assert person in equipment.user.all()


def test_booking_of_furnace_unique_constraint(
    person,
    furnace,
    furnace_booking_date,
):
    BookingOfFurnace.objects.create(
        date=furnace_booking_date,
        furnace=furnace,
        person=person,
    )

    with pytest.raises(IntegrityError):
        BookingOfFurnace.objects.create(
            date=furnace_booking_date,
            furnace=furnace,
            person=person,
        )


def test_booking_of_equipment_unique_constraint(
    person,
    equipment,
    equipment_booking_date,
):
    BookingOfEquipment.objects.create(
        date=equipment_booking_date,
        equipment=equipment,
        person=person,
    )

    with pytest.raises(IntegrityError):
        BookingOfEquipment.objects.create(
            date=equipment_booking_date,
            equipment=equipment,
            person=person,
        )


def test_articles_str_get_absolute_url_and_defaults():
    article = Articles.objects.create(
        date=dt.date(2026, 1, 20),
        full_text='Full article text',
    )

    assert article.title == 'News'
    assert article.anons == 'Anons'
    assert str(article) == 'News'
    assert article.get_absolute_url() == f'/news/{article.id}'
