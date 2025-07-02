from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from newsapp.models import Article

class Command(BaseCommand):
    help = 'Set up user groups and permissions'

    def handle(self, *args, **kwargs):
        reader_group, _ = Group.objects.get_or_create(name='Reader')
        editor_group, _ = Group.objects.get_or_create(name='Editor')
        journalist_group, _ = Group.objects.get_or_create(name='Journalist')

        article_ct = ContentType.objects.get_for_model(Article)

        reader_group.permissions.set([Permission.objects.get(codename='view_article')])
        editor_group.permissions.set([
            Permission.objects.get(codename='view_article'),
            Permission.objects.get(codename='change_article'),
            Permission.objects.get(codename='delete_article'),
        ])
        journalist_group.permissions.set([
            Permission.objects.get(codename='add_article'),
            Permission.objects.get(codename='view_article'),
            Permission.objects.get(codename='change_article'),
            Permission.objects.get(codename='delete_article'),
        ])
        self.stdout.write(self.style.SUCCESS('Groups and permissions set up successfully.'))
