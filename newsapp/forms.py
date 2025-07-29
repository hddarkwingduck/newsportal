from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Newsletter
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


class NewsletterForm(forms.ModelForm):
    """
    Represents a form for managing Newsletter data.

    This class is used to create and validate forms based on the
    "Newsletter" model.
    It provides functionality to handle input related to the title and
    content of a newsletter, ensuring that the form fields correspond
    to the specified model fields.

    :ivar title: Title of the newsletter.
    :type title: str
    :ivar content: Content of the newsletter.
    :type content: str
    """
    class Meta:
        model = Newsletter
        fields = ['title', 'content']


class AssignPublisherForm(forms.Form):
    """
    Form class for assigning a publisher.

    This form is used to create or update publisher assignments, providing a
    selection field populated with all existing publishers.

    :ivar publisher: A ModelChoiceField allowing the selection of a Publisher
        object from the available queryset containing all Publisher instances.
    :type publisher: ModelChoiceField
    """
    publisher = forms.ModelChoiceField(queryset=Publisher.objects.all())
