from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_1 = User.objects.create(username='Лев Толстой')
        cls.user_2 = User.objects.create(username='Томас Андерсон')
        cls.note = Note.objects.create(
            title='Note Title',
            text='Note Text',
            slug='note-1',
            author=cls.user_1,
        )

    def test_pages_availability(self):
        urls = [
            'notes:home',
            'users:login',
            'users:signup',
        ]
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:list', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:success', None),
        )
        for path, subpath in urls:
            with self.subTest(path=path, subpath=subpath):
                url = reverse(path, args=subpath)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_detail_page(self):
        users_statuses = (
            (self.user_1, HTTPStatus.OK),
            (self.user_2, HTTPStatus.NOT_FOUND),
        )
        url = reverse('notes:detail', args=(self.note.slug,))
        for user, status in users_statuses:
            with self.subTest(user=user):
                self.client.force_login(user)
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.user_1, HTTPStatus.OK),
            (self.user_2, HTTPStatus.NOT_FOUND),
        )
        urls = (
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
