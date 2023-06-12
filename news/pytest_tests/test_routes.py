# news/pytest_tests/test_routes.py
import pytest
from pytest_django.asserts import assertRedirects
from http import HTTPStatus

from django.urls import reverse

@pytest.mark.django_db
@pytest.mark.parametrize(
    'name', ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

@pytest.mark.django_db
def test_detail_page_availability_for_anonymous_user(client, news):
    url=reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    )
)
@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit')
)
def test_pages_availability_for_different_users(parametrized_client, comment, name, expected_status):
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status

@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit'))
def test_redirects(client, name,comment):
    login_url=reverse('users:login')
    url = reverse(name, args=(comment.pk,))
    expected_url = f'{login_url}?next={url}'
    response=client.get(url)
    assertRedirects(response, expected_url)
