from django.conf import settings
from django.urls import reverse
from pytest_django.asserts import assertIn


def test_paginator_in_home_page(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(news, client):
    url = reverse('news:detail', args=news.pk)
    response = client.get(url)
    assertIn('news', response.context)
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


def test_anonymous_client_has_no_form(client, news):
    url = reverse('news:detail', args=news.pk)
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news):
    url = reverse('news:detail', args=news.pk)
    response = author_client(url)
    assert 'form' in response.context
