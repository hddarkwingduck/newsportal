from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Article

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
