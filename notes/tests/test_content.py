from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteList(TestCase):
    NOTES_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Test User')
        all_notes = [
            Note(
                title = f'Test Note {index}',
                text = f'Test Note Text #{index}',
                author = cls.user,
                slug=f'slug-{index}'
            )
            for index in range(20)
        ]
        Note.objects.bulk_create(all_notes)

    def setUp(self):
        self.client.force_login(self.user)

    def test_note_count(self):
        response = self.client.get(self.NOTES_URL)
        obj_list = response.context['object_list']
        notes_count = obj_list.count()
        self.assertEqual(notes_count, Note.objects.count())
