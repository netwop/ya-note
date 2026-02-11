from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'note_slug'
    OTHER_NOTE_TEXT = 'Текст другой заметки'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'text': cls.NOTE_TEXT, 'title': cls.NOTE_TEXT, 'slug': cls.NOTE_SLUG}
        cls.add_url = reverse('notes:add')
        cls.url_to_notes = reverse('notes:success')

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.add_url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(),  0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.url_to_notes)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.user)

    def test_not_unique_slug(self):
        note = Note.objects.create(title='Заголовок', text = self.OTHER_NOTE_TEXT, slug = self.NOTE_SLUG, author=self.user)
        self.form_data['slug'] = note.slug
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertFormError(response.context['form'], 'slug', errors=(note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.url_to_notes)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённый текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(title='Заголовок', text = cls.NOTE_TEXT, author = cls.author)
        cls.notes_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.url_to_notes = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {'text': cls.NEW_NOTE_TEXT, 'title': cls.note.title, 'slug': cls.note.slug}


    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.url_to_notes)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.url_to_notes)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)



