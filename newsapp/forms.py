from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import Article
from .models import Publisher



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


class PublisherForm(forms.ModelForm):
    """
    Represents a form for creating or updating a Publisher instance.

    This form is built for the Publisher model and includes fields
    to validate and process data related to a Publisher instance.
    It ensures that only the specified fields are exposed for
    form manipulation.

    :ivar Meta.model: Specifies the associated model, which is Publisher.
    :type Meta.model: Type[Publisher]
    :ivar Meta.fields: List of fields in the Publisher model included
        in the form.
    :type Meta.fields: list[str]
    """
    class Meta:
        model = Publisher
        fields = ['name']
