from http import HTTPStatus
from django.test import TestCase, Client

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNotesCreation(TestCase):

    NOTE_DATA = {
        'title': 'Title for note',
        'text': 'Text for note',
    }

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='User One')
        cls.url = reverse('notes:add')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

    def test_anonymous_user_cant_create_note(self):
        login_url = reverse('users:login')
        notes_count_before = Note.objects.count()
        response = self.client.post(self.url, data=self.NOTE_DATA)
        self.assertRedirects(response, f'{login_url}?next={self.url}')
        self.assertEqual(Note.objects.count(), notes_count_before)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.NOTE_DATA)
        note = Note.objects.last()
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(note.title, self.NOTE_DATA['title'])
        self.assertEqual(note.text, self.NOTE_DATA['text'])
        self.assertEqual(note.slug, slugify(self.NOTE_DATA['title']))

    def test_note_unique_slug(self):
        self.auth_client.post(self.url, data=self.NOTE_DATA)
        post_data = {**self.NOTE_DATA, 'slug': 'title-for-note'}
        response = self.auth_client.post(self.url, data=post_data)
        form = response.context['form']
        self.assertFormError(
            form,
            'slug',
            f"{post_data['slug']}{WARNING}")
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestNotesEditDelete(TestCase):

    NOTE_DATA = {
            'title': 'New note title',
            'text': 'New Text',
            'slug': 'new-slug',
    }

    @classmethod
    def setUpTestData(cls):
        cls.user_1 = User.objects.create(username="User One")
        cls.user_2 = User.objects.create(username="User Two")
        cls.first_user = Client()
        cls.first_user.force_login(cls.user_1)
        cls.second_user = Client()
        cls.second_user.force_login(cls.user_2)
        cls.note = Note.objects.create(
            title='Test Note',
            text='Test Note Text',
            slug='test-note',
            author=cls.user_1,
        )
        cls.delete_note = reverse('notes:delete', args=(cls.note.slug,))
        cls.edit_note = reverse('notes:edit', args=(cls.note.slug,))

    def test_author_can_delete_note(self):
        response = self.first_user.delete(self.delete_note)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.second_user.delete(self.delete_note)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        response = self.first_user.post(self.edit_note, data=self.NOTE_DATA)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        data = {
            'title': self.note.title,
            'text': self.note.text,
            'slug': self.note.slug,
        }
        self.assertEqual(data, self.NOTE_DATA)

    def test_user_cant_delete_other_user_note(self):
        response = self.second_user.post(self.edit_note, data=self.NOTE_DATA)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        data = {
            'title': self.note.title,
            'text': self.note.text,
            'slug': self.note.slug,
        }
        self.assertNotEqual(data, self.NOTE_DATA)
