from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import Article


class CustomUserCreationForm(UserCreationForm):
    """
    CustomUserCreationForm inherits from UserCreationForm to provide
    additional fields or functionalities for creating a custom user.

    This class extends the default Django UserCreationForm to include
    an additional required email field. It customizes the user creation
    process to handle user registrations with extended fields and
    validation requirements defined in the Meta class.

    :ivar email: A required email field for user registration purposes.
    :type email: forms.EmailField
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'password1', 'password2')


class ArticleForm(forms.ModelForm):
    """
    This class represents a Django form for the ``Article`` model.

    The form allows for the creation and editing of ``Article``
    objects with specific fields ``title``, ``content``, and ``publisher``.
    It is derived from the ``ModelForm`` class provided by Django's forms
    framework.

    :ivar Meta: Metadata container for the form configuration.
    :type Meta: class
    """
    class Meta:
        model = Article
        fields = ['title', 'content', 'publisher']
