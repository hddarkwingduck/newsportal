from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group

class Publisher(models.Model):
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

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('editor', 'Editor'),
        ('journalist', 'Journalist'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    subscriptions_publishers = models.ManyToManyField('Publisher', blank=True, related_name='subscribed_readers')
    subscriptions_journalists = models.ManyToManyField('Journalist', blank=True, related_name='subscribed_readers')
    published_articles = models.ManyToManyField('Article', blank=True, related_name='journalist_articles')
    published_newsletters = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Mutual exclusivity logic
        super().save(*args, **kwargs)  # Save first to ensure self.id exists

        if self.role == 'journalist':
            self.subscriptions_publishers.clear()
            self.subscriptions_journalists.clear()
        elif self.role == 'reader':
            self.published_articles.clear()
            self.published_newsletters = None

        # --- Group assignment logic ---
        if self.role:
            group_name = self.role.capitalize()  # "reader" -> "Reader"
            group, created = Group.objects.get_or_create(name=group_name)
            self.groups.clear()  # Remove from all groups
            self.groups.add(group)


class Journalist(models.Model):
    user = models.OneToOneField(CustomUser,
                                on_delete=models.CASCADE,
                                limit_choices_to={'role': 'journalist'})
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    body = models.TextField()
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    journalist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='journalist_articles'
    )
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
