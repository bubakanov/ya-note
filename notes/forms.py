from pytils.translit import slugify

from django import forms
from django.core.exceptions import ValidationError

from .models import Note

WARNING = ' - такой slug уже существует, придумайте уникальное значение!'


class NoteForm(forms.ModelForm):
    """Форма для создания или обновления заметки."""

    class Meta:
        model = Note
        fields = ('title', 'text', 'slug')

    def clean_slug(self):
        """Обрабатывает случай, если slug не уникален."""
        slug = self.cleaned_data.get('slug')
        if slug and Note.objects.filter(
                slug=slug
        ).exclude(pk=self.instance.pk).exists():
            raise ValidationError(slug + WARNING)
        return slug
