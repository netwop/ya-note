from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Читатель')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(title='Заголовок', text = 'Текст', slug = 'slug', author=cls.author)
        cls.add_url = reverse('notes:add')
        cls.list_url = reverse('notes:list')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))

    def test_notes_in_context_for_different_users(self):
        users_statuses = (
            (self.author_client, True),
            (self.not_author_client, False),
        )
        for client, note_in_list in users_statuses:
            with self.subTest(client=client, note_in_list=note_in_list):
                response = client.get(self.list_url)
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, note_in_list)

    def test_add_and_edit_pages_contains_form(self):
        urls = (
            self.add_url,
            self.edit_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)