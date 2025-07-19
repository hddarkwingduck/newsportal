from typing import Any

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group


class Publisher(models.Model):
    """
    Represents a Publisher entity in a database model.

    The Publisher class is used to define the attributes and
    relationships of a publisher within the system. It can be associated
    with multiple editors and journalists. This class also allows for
    restrictions in editor selection by limiting to users with the
    'editor' role.

    :ivar name: Name of the publisher.
    :type name: models.CharField
    :ivar editors: A many-to-many relationship to `CustomUser`, limited
        to users with the 'editor' role.
    :type editors: models.ManyToManyField
    :ivar journalists: A many-to-many relationship to `Journalist`.
    :type journalists: models.ManyToManyField
    """
    name = models.CharField(max_length=100)
    editors = models.ManyToManyField(
        'CustomUser',
        limit_choices_to={'role': 'editor'},
        related_name='editor_publishers',
        blank=True
    )
    journalists = models.ManyToManyField(
        'Journalist',
        related_name='journalist_publishers',
        blank=True
    )

    def __str__(self) -> str:

        """
            Converts the object to its string representation.

            This method generates a string representation for the object,
            which in this case is the name attribute of the object.

            :return: The name of the object as a string.
            :rtype: str
            """
        return self.name


class CustomUser(AbstractUser):
    """
    Represents a customized user model with additional fields
    and functionality extending the AbstractUser class.

    This class defines a user with different roles
    (reader, editor, journalist) and includes custom relational fields for
    managing subscriptions between users and publishers. It also provides
    logic for handling role-based constraints and managing associated
    Django groups.

    :ivar role: Role of the user, which could be 'reader', 'editor', or
        'journalist'. Determines the user's permissions and available
        actions.
    :type role: str
    :ivar subscriptions_publishers: A many-to-many relationship
        representing the publishers the user has subscribed to. Only
        applicable for users with the 'reader' role.
    :type subscriptions_publishers: models.ManyToManyField
    :ivar subscriptions_journalists: A many-to-many relationship
        representing the journalists the user has subscribed to. Only
        applicable for users with the 'reader' role, constrained to users
        with the 'journalist' role.
    :type subscriptions_journalists: models.ManyToManyField
    :ivar published_newsletters: A text field storing the content
        of newsletters  published by journalists. Only applicable to
        users with the 'journalist' role. Set to None for other roles.
    :type published_newsletters: str or None
    :ivar bio: An optional text field for storing the user's biography or
        personal description.
    :type bio: str
    """
    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('editor', 'Editor'),
        ('journalist', 'Journalist'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    subscriptions_publishers = models.ManyToManyField(
        'Publisher', blank=True, related_name='subscribed_readers'
    )
    subscriptions_journalists = models.ManyToManyField(
        'self',
        blank=True,
        related_name='subscribed_readers',
        symmetrical=False,
        limit_choices_to={'role': 'journalist'}
    )
    published_newsletters = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True)

    def save(self, *args: Any, **kwargs: Any) -> None:

        """
            Saves the current instance and performs additional operations
            based on the role attribute of the instance.

            When the role is 'journalist', it clears all the user's
            subscriptions to publishers and journalists.

            When the role is 'reader', it sets the user's published
            newsletters to None.

            Regardless of the role, the method ensures that the instance is
            associated with the corresponding group.
            If the group corresponding to the role of the instance does
            not exist, it creates the group. The association between the
            instance and the group is updated accordingly by first
            clearing the current associations and then adding the new group.

            :param args: Positional arguments passed to the parent
                class's save method.
            :param kwargs: Keyword arguments passed to the parent class's
                save method.
            :return: None
            """
        super().save(*args, **kwargs)
        if self.role == 'journalist':
            self.subscriptions_publishers.clear()
            self.subscriptions_journalists.clear()
        elif self.role == 'reader':
            self.published_newsletters = None
        if self.role:
            group_name = self.role.capitalize()
            group, created = Group.objects.get_or_create(name=group_name)
            self.groups.clear()
            self.groups.add(group)


class Journalist(models.Model):
    """
    Represents a journalist entity with a one-to-one relation
    to a custom user.

    The `Journalist` model is used to associate a user with additional
    information specific to a journalist. It extends the functionality
    of the user model by providing extra attributes such as a biography.
    It only allows users who have the role of 'journalist' to be
    associated with this model.

    :ivar user: A one-to-one relationship with the `CustomUser` model,
                constrained to users with the role of 'journalist'.
    :type user: models.OneToOneField

    :ivar bio: A field for storing the journalist's biography text.
               It is optional and can be left blank.
    :type bio: models.TextField
    """
    user = models.OneToOneField(CustomUser,
                                on_delete=models.CASCADE,
                                limit_choices_to={'role': 'journalist'})
    bio = models.TextField(blank=True)

    def __str__(self):
        """
        Provides a string representation of the object, returning the
        username associated with the `user` attribute. This implementation
        calls the `username` attribute from
        the `user` object and ensures this is used as the string output
        for the object.

        :return: The string representation of the object, which is
            the username of the associated `user` object.
        :rtype: str
        """
        return self.user.username


class Article(models.Model):
    """
    Represents an Article in a publishing system.

    The Article class defines the structure and attributes of an
    article within the system. It includes fields for storing the article's
    title, content,
    publisher, the journalist who created it, its approval status, and
    the timestamp it was created. Articles are linked to a publisher
    and journalist through foreign key relationships.

    :ivar title: The title of the article.
    :type title: models.CharField
    :ivar content: The main content/body of the article.
    :type content: models.TextField
    :ivar publisher: Reference to the publisher responsible for the article.
    :type publisher: models.ForeignKey
    :ivar journalist: Reference to the journalist who wrote the article.
    :type journalist: models.ForeignKey
    :ivar approved: Indicates whether the article is approved for
        publication.
    :type approved: models.BooleanField
    :ivar created_at: The timestamp when the article was created,
        automatically set.
    :type created_at: models.DateTimeField
    """
    title = models.CharField(max_length=255)
    content = models.TextField()  # or 'body', not both unless needed
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    journalist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='journalist_articles'
    )
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """
        Converts the object to its string representation.

        This method overrides the default string representation of
        the object to return its title attribute instead, providing a more
        meaningful and user-friendly representation when the object is cast
        to a string.

        :raises AttributeError: If the title attribute is not defined or is
            inaccessible for the object at runtime.
        :returns: A string representation of the object's title.
        :rtype: str
        """
        return self.title
