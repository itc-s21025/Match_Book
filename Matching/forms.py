from Matching.models import Profile, DirectMessage
from django import forms


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['age', 'sex', 'introduction', 'favorite_book_category', 'like_book', 'favorite_author', 'nickname',]


from django import forms

class DirectMessageForm(forms.ModelForm):
    class Meta:
        model = DirectMessage
        fields = ['message']