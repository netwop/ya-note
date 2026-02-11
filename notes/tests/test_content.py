from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm
from yanote.settings import NOTES_COUNT_ON_HOME_PAGE

User = get_user_model()

class TestHomePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(title='Заголовок', text = 'Текст', slug = 'slug', author=cls.author)
        cls.home_url = reverse('notes:list')

    def test_notes_list_for_reader(self):
        response = self.reader_client.get(self.home_url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_notes_list_for_author(self):
        response = self.author_client.get(self.home_url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)


class TestDetailPage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(title='Заголовок', text = 'Текст', slug = 'slug', author=cls.author)
        cls.add_url = reverse('notes:add')
        cls.list_url = reverse('notes:list')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))



    def test_notes_in_context_for_author(self):
        response = self.author_client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_notes_in_context_for_not_author(self):
        response = self.reader_client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_edit_pages_contains_form(self):
        response = self.author_client.get(self.edit_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_add_pages_contains_form(self):
        response = self.author_client.get(self.add_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)