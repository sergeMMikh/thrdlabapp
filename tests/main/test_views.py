import datetime as dt

import pytest
from django.urls import reverse

from news.models import Articles
from users.models import Person


pytestmark = pytest.mark.django_db


@pytest.fixture
def person():
    return Person.objects.create(
        first_name='Sergey',
        surname='Mikhalev',
        email='sergey@example.com',
    )


def test_main_pages_render_successfully(client):
    pages = (
        ('home', 'main/index.html', 'Home'),
        ('about', 'main/about.html', 'About'),
        ('contacts', 'main/contacts.html', 'Contacts'),
    )

    for route_name, template_name, title in pages:
        response = client.get(reverse(route_name))
        assert response.status_code == 200
        assert template_name in [t.name for t in response.templates]
        assert response.context['title'] == title


def test_news_home_shows_latest_five_articles(client):
    for idx in range(6):
        Articles.objects.create(
            title=f'News {idx}',
            anons=f'Anons {idx}',
            full_text='Body',
            date=dt.date(2026, 1, 10 + idx),
        )

    response = client.get(reverse('news_home'))

    assert response.status_code == 200
    assert 'news/news_home.html' in [t.name for t in response.templates]
    news_list = list(response.context['news'])
    assert len(news_list) == 5
    assert [item.date for item in news_list] == sorted(
        [item.date for item in news_list],
        reverse=True,
    )


def test_create_news_get_renders_form(client):
    response = client.get(reverse('create_news'))

    assert response.status_code == 200
    assert 'news/create_news.html' in [t.name for t in response.templates]
    assert 'form' in response.context


def test_create_news_post_valid_creates_article_and_redirects(client, person):
    response = client.post(
        reverse('create_news'),
        data={
            'title': 'New title',
            'full_text': 'Long text',
            'author': person.id,
        },
    )

    assert response.status_code == 302
    assert response.url == reverse('news_home')
    assert Articles.objects.filter(title='New title').exists() is True


def test_create_news_post_invalid_returns_error(client):
    response = client.post(
        reverse('create_news'),
        data={
            'title': 'Missing author',
            'full_text': 'Long text',
        },
    )

    assert response.status_code == 200
    assert response.context['error'] == 'The form is not correct'
    assert Articles.objects.filter(title='Missing author').exists() is False


def test_news_detail_view_renders_article(client):
    article = Articles.objects.create(
        title='Detailed title',
        anons='Detailed anons',
        full_text='Detailed text',
        date=dt.date(2026, 1, 21),
    )

    response = client.get(reverse('news-detail', args=[article.pk]))

    assert response.status_code == 200
    assert response.context['article'] == article


def test_news_update_view_updates_article(client, person):
    article = Articles.objects.create(
        title='Old title',
        anons='Old anons',
        full_text='Old text',
        date=dt.date(2026, 1, 22),
    )

    response = client.post(
        reverse('news-update', args=[article.pk]),
        data={
            'title': 'Updated title',
            'full_text': 'Updated text',
            'author': person.id,
        },
    )
    article.refresh_from_db()

    assert response.status_code == 302
    assert response.url == article.get_absolute_url()
    assert article.title == 'Updated title'


def test_news_delete_view_deletes_article(client):
    article = Articles.objects.create(
        title='Delete title',
        anons='Delete anons',
        full_text='Delete text',
        date=dt.date(2026, 1, 24),
    )

    response = client.post(reverse('news-delete', args=[article.pk]))

    assert response.status_code == 302
    assert response.url == '/news/'
    assert Articles.objects.filter(pk=article.pk).exists() is False
