from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from .models import Article, CustomUser

# --- 1. Notify subscribers when an article is approved ---
@receiver(post_save, sender=Article)
def notify_on_approval(sender, instance, created, **kwargs):
    if instance.approved:
        publisher_subs = instance.publisher.subscribed_readers.all()
        journalist_subs = instance.journalist.user.subscribed_readers.all()
        recipients = set([u.email for u in publisher_subs] + [u.email for u in journalist_subs])
        if recipients:
            send_mail(
                subject=f"New Article Approved: {instance.title}",
                message=instance.body,
                from_email='no-reply@newsportal.com',
                recipient_list=list(recipients),
            )

# --- 2. Automatically assign user to correct group based on role ---
@receiver(post_save, sender=CustomUser)
def assign_user_group(sender, instance, created, **kwargs):
    if instance.role:
        group, _ = Group.objects.get_or_create(name=instance.role.capitalize())
        instance.groups.clear()
        instance.groups.add(group)

