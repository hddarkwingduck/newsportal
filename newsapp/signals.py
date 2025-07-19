from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from .models import Article, CustomUser

@receiver(post_save, sender=Article)
def notify_on_approval(sender, instance, created, **kwargs):
    """
    This function is a signal receiver that triggers on the post_save
    event of the Article model.
    When an article is approved, it gathers the email addresses
    of subscribers of the article's publisher and journalist,
    and sends a notification email to these recipients informing them about
    the approval of the new article.

    :param sender: The model class that is the sender of the signal.
    :param instance: The actual instance of the Article model that was saved.
    :param created: A boolean indicating whether a new instance was created.
    :param kwargs: Additional keyword arguments passed by the signal.
    :return: None
    """
    if instance.approved:
        publisher_subs = instance.publisher.subscribed_readers.all()
        journalist_subs = instance.journalist.subscribed_readers.all()
        recipients = set([u.email for u in publisher_subs]
                         + [u.email for u in journalist_subs])
        if recipients:
            send_mail(
                subject=f"New Article Approved: {instance.title}",
                message=instance.body,
                from_email='no-reply@newsportal.com',
                recipient_list=list(recipients),
            )

@receiver(post_save, sender=CustomUser)
def assign_user_group(sender, instance, created, **kwargs):
    """
    Signal handler that assigns a user to a group based on their role
    upon saving a CustomUser instance. This function ensures that the user
    is assigned to the
    appropriate group aligned with their role and clears any previous group
    assignments prior to updating.

    :param sender: The model class that sends the signal.
    :param instance: The instance of the model that is being saved.
    :param created: Boolean indicating if the instance was created (True)
        or updated (False).
    :param kwargs: Additional keyword arguments passed by the
        post_save signal.
    :return: None
    """
    if instance.role:
        group, _ = Group.objects.get_or_create(
            name=instance.role.capitalize()
        )
        instance.groups.clear()
        instance.groups.add(group)

