from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import TestCase
# Импортируем функцию reverse(), она понадобится для получения адреса страницы.
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()

class TestHomePage(TestCase):
    HOME_URL = reverse('notes:home')


    @classmethod
    def setUpTestData(cls):
        all_notes = [
            Note(
                title=f'Новость {index}',
                text='Просто текст.'
            )
            for index in range(settings.NOTES_COUNT_ON_HOME_PAGE + 1)
        ]
        Note.objects.bulk_create(all_notes) 

    def test_note_in_list(self):
        # Загружаем главную страницу.
        response = self.client.get(self.HOME_URL)
        # Код ответа не проверяем, его уже проверили в тестах маршрутов.
        # Получаем список объектов из словаря контекста.
        object_list = response.context['object_list']
        # Определяем количество записей в списке.
        # news_count = object_list.count()
        # # Проверяем, что на странице именно 10 новостей.
        # self.assertEqual(news_count, settings.NEWS_COUNT_ON_HOME_PAGE)


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.notes = Note.objects.create(
            title='Тестовая заметка', text='Просто текст.'
        )
        # Сохраняем в переменную адрес страницы с новостью:
        cls.detail_url = reverse('notes:detail', args=(cls.notes.id,))
        cls.author = User.objects.create(username='Автор заметки')

    def test_notes_in_context(self):
        response = self.client.get(self.detail_url)
        # Проверяем, что объект новости находится в словаре контекста
        # под ожидаемым именем - названием модели.
        self.assertIn('notes', response.context)


    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.detail_url)
        self.assertNotIn('form', response.context)
        
    def test_authorized_client_has_form(self):
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
        # Проверим, что объект формы соответствует нужному классу формы.
        self.assertIsInstance(response.context['form'], NoteForm) 