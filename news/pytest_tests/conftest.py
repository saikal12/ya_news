import pytest
from datetime import datetime, timedelta
from django.utils import timezone

from news.forms import BAD_WORDS
from news.models import News, Comment
from yanews import settings


@pytest.fixture
def news():
    news = News.objects.create(title='Заголовок', text='текст')
    return news


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(news=news,
                                     author=author, text='текст комментария')
    return comment


@pytest.fixture
def news_data():
    all_news = []
    today = datetime.today()
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(title=f'Новость {index}', text='Просто текст.',date=today - timedelta(days=index))
        all_news.append(news)
    News.objects.bulk_create(all_news)


@pytest.fixture
def form_data():
    return {
        'text':'Текст комментария'
    }


@pytest.fixture
def bad_words_data():
    return {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}


@pytest.fixture
def comment_for_detail(news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
