from Matching.models import Profile, DirectMessage, BookThoughts
from django import forms


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nickname', 'age', 'sex', 'introduction', 'favorite_book_category', 'like_book', 'favorite_author',
                  'face_image']


class DirectMessageForm(forms.ModelForm):
    class Meta:
        model = DirectMessage
        fields = ['message']


class BookThoughtsForm(forms.ModelForm):

    class Meta:
        model = BookThoughts
        fields = ['book_title', 'book_author', 'book_image_url', 'book_description', 'book_thoughts']

