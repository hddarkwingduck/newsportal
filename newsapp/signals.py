import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from .models import Article, CustomUser, Journalist


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

@receiver(post_save, sender=CustomUser)
def create_journalist_for_user(sender: type, instance: CustomUser,
                               created: bool, **kwargs: any) -> None:
    """
    Signal handler that creates a `Journalist` instance for a `CustomUser`
    when a new user with the role of "journalist" is saved.

    If the `created` flag is `True` and the role of the saved instance is
    `journalist`, this function will create a new `Journalist` instance
    associated with the `CustomUser` object.

    :param sender: The model class that sent the signal.
    :type sender: type
    :param instance: The actual instance being saved.
    :type instance: CustomUser
    :param created: A boolean indicating if a new record was created.
    :type created: bool
    :param kwargs: Additional keyword arguments provided by the signal.
    :type kwargs: any
    :return: None
    :rtype: None
    """
    if created and instance.role == 'journalist':
        # If a profile does not already exist, create one
        Journalist.objects.create(user=instance, name=instance.username)


@receiver(post_save, sender=Article)
def post_article_to_x(sender: type, instance: Article, created: bool,
                      **kwargs: dict) -> None:
    """
    Signal receiver function triggered after saving an Article instance.
    Its purpose is to post the approved article to X (formerly Twitter) by
    sending a POST request using the API. The function ensures that only
    newly approved articles are posted.
    No return value is expected.

    :param sender: The sender of the signal.
    :type sender: type
    :param instance: The instance of the Article model being saved.
    :type instance: Article
    :param created: Indicates whether the instance was created or updated.
    :type created: bool
    :param kwargs: Additional arguments passed to the signal receiver.
    :type kwargs: dict
    :return: None
    """
    # Only post if the article has just been approved
    if instance.approved:
        x_api_url = "https://api.twitter.com/2/tweets"
        bearer_token = "YOUR_X_BEARER_TOKEN"  # Store securely in environment variables!

        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
        data = {
            "text": f"{instance.title}\n\n{instance.content[:250]}..."  # Plaintext preview
        }
        try:
            response = requests.post(x_api_url, headers=headers, json=data)
            if response.status_code == 201 or response.status_code == 200:
                print("Article posted to X successfully.")
            else:
                print(f"Failed to post to X: {response.status_code} {response.text}")
        except Exception as e:
            print(f"Could not post article to X: {e}")
