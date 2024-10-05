"""
План тестирования контента:

1. Кол-во новостей на главной странице — не более 10.
2. Новости отсортированы от самой свежей к самой старой. Свежие новости в начале списка.
3. Комментарии на странице отдельной новости отсортированы от старых к новым: старые в начале списка, новые — в конце.
4. Анонимному пользователю не видна форма для отправки комментария на странице отдельной новости, а авторизованному видна.
"""
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.test import TestCase
from django.contrib.auth import get_user_model
# Импортируем функцию reverse(), она понадобится для получения адреса страницы.
from django.urls import reverse

from news.models import Comment, News
from news.forms import CommentForm


User = get_user_model()


class TestHomePage(TestCase):
    # Вынесем ссылку на домашнюю страницу в атрибуты класса.
    HOME_URL = reverse('news:home')

    @classmethod
    def setUpTestData(cls):
        # Вычисляем текущую дату.
        today = datetime.today()
        all_news = [
            News(
                title=f'Новость {index}',
                text='Просто текст.',
                # Для каждой новости уменьшаем дату на index дней от today,
                # где index - счётчик цикла.
                date=today - timedelta(days=index)          # Установим для каждой новости в фикстуре собственную дату принудительно. 
                )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
        News.objects.bulk_create(all_news)  # метод bulk_create одновременн создаёт нескольких объектов

    def test_news_count(self):
        """Считаем кол-во постов на главной странице."""
        # Загружаем главную страницу.
        response = self.client.get(self.HOME_URL)
        # Код ответа не проверяем, его уже проверили в тестах маршрутов.
        # Получаем список объектов из словаря контекста.
        object_list = response.context['object_list']
        # Определяем количество записей в списке.
        news_count = object_list.count()
        # Проверяем, что на странице именно 10 новостей.
        self.assertEqual(news_count, settings.NEWS_COUNT_ON_HOME_PAGE)

    def test_news_order(self):
        """
        Проверка сортировки постов по дате.
        Сравниваются список дат новостей и он же отсортированный.
        """
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        # Получаем даты новостей в том порядке, как они выведены на странице.
        all_dates = [news.date for news in object_list]
        # Сортируем полученный список по убыванию.
        sorted_dates = sorted(all_dates, reverse=True)
        # Проверяем, что исходный список был отсортирован правильно.
        self.assertEqual(all_dates, sorted_dates)


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Создание тестовых комментов.
        На каждой итерации цикла после создания объекта
        меняется значение поля created
        через изменение атрибута, затем объект сохраняется.
        """
        cls.news = News.objects.create(
            title='Тестовая новость', text='Просто текст.'
        )
        # Сохраняем в переменную адрес страницы с новостью:
        cls.detail_url = reverse('news:detail', args=(cls.news.id,))
        cls.author = User.objects.create(username='Комментатор')
        # Запоминаем текущее время:
        now = timezone.now()  # БЫЛО: now = datetime.now() - исправили, п/ч settings.USE_TZ = True
        # Создаём комментарии в цикле.
        for index in range(10):
            # Создаём объект и записываем его в переменную.
            comment = Comment.objects.create(
                news=cls.news, author=cls.author, text=f'Tекст {index}',
            )
            # Сразу после создания меняем время создания комментария.
            comment.created = now + timedelta(days=index)
            # И сохраняем эти изменения.
            comment.save()

    def test_comments_order(self):
        """
        Тест сортировки комментариев (от старых к новым).
        """
        response = self.client.get(self.detail_url)
        # Проверяем, что объект новости находится в словаре контекста
        # под ожидаемым именем - названием модели.
        self.assertIn('news', response.context)
        # Получаем объект новости.
        news = response.context['news']
        # Получаем все комментарии к новости.
        all_comments = news.comment_set.all()
        # Собираем временные метки всех комментариев.
        all_timestamps = [comment.created for comment in all_comments]
        # Сортируем временные метки, менять порядок сортировки не надо.
        sorted_timestamps = sorted(all_timestamps)
        # Проверяем, что временные метки отсортированы правильно.
        self.assertEqual(all_timestamps, sorted_timestamps)

    def test_anonymous_client_has_no_form(self):
        """
        Проверка, что анону недоступна форма комментариев.
        """
        response = self.client.get(self.detail_url)
        self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        """
        Проверка, что при запросе авторизованного пользователя
        форма передаётся в словаре контекста.
        """
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
        # Проверим, что объект формы соответствует нужному классу формы.
        self.assertIsInstance(response.context['form'], CommentForm)








# БЫЛО

# news/tests/test_content.py
# from django.conf import settings
# from django.test import TestCase

# from news.models import News


# class TestHomePage(TestCase):

#     @classmethod
#     def setUpTestData(cls):
#         all_news = [
#             News(title=f'Новость {index}', text='Просто текст.')
#             for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
#         ]
#         News.objects.bulk_create(all_news) #одновременного создания нескольких объектов применяют метод bulk_create











# @pytest.mark.usefixtures('comments_list')
# def test_comment_sort(client, news_pk,):
#     """Сортировка комментариев от новых к старым."""
#     url = reverse('news:detail', args=news_pk)
#     response = client.get(url)
#     news = response.context['news']

#     comments_list = list(news.comment_set.all())
#     assert isinstance(comments_list[0].created, timezone.datetime)
#     assert comments_list == sorted(
#         comments_list,
#         key=lambda x: x.created,
#     )



#     @pytest.mark.django_db
# @pytest.mark.usefixtures('comments_list')
# @pytest.mark.parametrize(
#     'name, args',
#     (
#         (settings.DETAIL_URL, pytest.lazy_fixture('pk_for_args_news')),
#     ),
# )
# def test_comments_order(
#     news,
#     author_client,
#     name,
#     args
# ):
#     """
#     Комментарии на странице отдельной новости отсортированы в
#     хронологическом порядке: старые в начале списка, новые — в конце.
#     """
#     url = reverse(name, args=args)
#     response = author_client.get(url)
#     assert 'news' in response.context
#     news = response.context['news'].comment_set.all()
#     sorted_news_comments = sorted(
#         news,
#         key=lambda comment: comment.created)
#     for first_param, second_param in zip(news, sorted_news_comments):
#         assert first_param.created == second_param.created
# """


# @pytest.fixture
# def detail_url(news):
    # return reverse('news:detail', args=(news.pk,))