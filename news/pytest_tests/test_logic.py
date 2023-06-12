from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    url = reverse('news:detail', args=(news.pk,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, news, author, form_data):
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == author

@pytest.mark.django_db
def test_user_cant_use_bad_words(news, author_client, bad_words_data):
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response, 'form', 'text',
        errors=WARNING)
    assert Comment.objects.count() == 0

@pytest.mark.django_db
def test_author_can_delete_comment(news, author_client, comment):
    url = reverse('news:delete', args=(comment.pk,))
    response = author_client.post(url)
    url_for_comment_block = reverse('news:detail', args=(news.pk,))
    assertRedirects(response, url_for_comment_block+'#comments')
    assert Comment.objects.count() == 0

@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(admin_client, news, comment):
    url = reverse('news:delete', args=(comment.pk,))
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1

@pytest.mark.django_db
def test_author_can_edit_comment(news, author_client, form_data, comment):
    url = reverse('news:edit', args=(comment.pk,))
    response = author_client.post(url, data=form_data)
    url_for_comment_block = reverse('news:detail', args=(news.pk,))
    assertRedirects(response, url_for_comment_block + '#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']

@pytest.mark.django_db
def test_other_user_cant_edit_comment(admin_client, form_data, news, comment):
    url = reverse('news:edit', args=(comment.pk,))
    response = admin_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_fr_db = Comment.objects.get(pk=comment.pk)
    assert comment.text == comment_fr_db.text
