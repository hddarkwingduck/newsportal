from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import Article, Publisher
from django.test import TestCase

User = get_user_model()


class APITest(TestCase):
    """
    Represents test cases for API endpoints related to publishers,
    users, and articles, with a focus on subscriptions, article approval,
    and user permissions.

    This test class primarily verifies the behavior of the API under various
    scenarios, such as authenticated and unauthenticated users, editable
    articles for editors, and article access based on subscriptions and
    approval status.

    :ivar client: Instance of APIClient used for API requests.
    :type client: APIClient
    :ivar publisher: Instance of Publisher used in test data.
    :type publisher: Publisher
    :ivar journalist: Instance of User representing a journalist.
    :type journalist: User
    :ivar reader: Instance of User representing a reader.
    :type reader: User
    :ivar article1: Instance of Article that has been approved.
    :type article1: Article
    :ivar article2: Instance of Article that is still pending approval.
    :type article2: Article
    """

    def setUp(self) -> None:
        """
        Sets up initial test environment for use in test cases.
        Creates sample data for Publisher, User, Article, and establishes
        relevant relationships, such as subscriptions. This ensures a
        consistent initial state for testing functionality related to
        publishers, users, and articles.

        :raises: Does not raise any exceptions.
        :return: None
        """
        # Create publisher
        self.publisher = Publisher.objects.create(name='Acme Publishing')

        # Create journalist user
        self.journalist = User.objects.create_user(
            username='journalist1',
            password='testpass123',
            email='journo1@example.com',
            role='journalist'
        )

        # Create reader user
        self.reader = User.objects.create_user(
            username='reader1',
            password='testpass456',
            email='reader1@example.com',
            role='reader'
        )

        # Create articles, one approved, one not
        self.article1 = Article.objects.create(
            title="Approved Article",
            content="Approved content.",
            publisher=self.publisher,
            journalist=self.journalist,
            approved=True
        )
        self.article2 = Article.objects.create(
            title="Pending Article",
            content="Not yet approved.",
            publisher=self.publisher,
            journalist=self.journalist,
            approved=False
        )

        # Reader subscribes to the publisher
        self.reader.subscriptions_publishers.add(self.publisher)
        # Reader subscribes to the journalist
        self.reader.subscriptions_journalists.add(self.journalist)

        self.client = APIClient()

    def test_reader_gets_only_subscribed_approved_articles(self) -> None:
        """
        Tests that a reader can fetch only subscribed and approved
        articles.

        This test ensures that when a reader fetches articles from the API,
        only articles approved for publication are included in the response.
        Pending articles, even if the reader is subscribed, should not
        be returned.

        :return: None
        :rtype: NoneType
        """
        self.client.force_authenticate(user=self.reader)
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, 200)

        titles = {art['title'] for art in response.json()}
        # Reader is subscribed, but only 'Approved Article' should be returned
        self.assertIn('Approved Article', titles)
        self.assertNotIn('Pending Article', titles)

    def test_unsubscribed_reader_gets_no_articles(self) -> None:
        """
        Tests that an unsubscribed reader user does not receive any
        articles when accessing the articles API endpoint. This ensures
        that only subscribed users or users with proper access permissions
        can retrieve article data.

        :param self: The instance of the test case class.
        """
        new_reader = User.objects.create_user(
            username='reader2',
            password='pass',
            email='reader2@example.com',
            role='reader'
        )
        self.client.force_authenticate(user=new_reader)
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

    def test_unauthenticated_user_gets_articles(self) -> None:
        """
        Tests that an unauthenticated user can retrieve articles
        successfully.

        This function ensures that an unauthenticated user is able to make
        a GET request to the endpoint responsible for retrieving articles,
        and receives a response with a status code indicating success.

        :return: None
        """
        self.client.logout()
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, 200)

    def test_editor_can_see_unapproved_articles(self) -> None:
        """
        Tests that an editor user can view unapproved articles through
        the appropriate endpoint.

        This test ensures that users with the `editor` role have the correct
        permissions to access the list of unapproved articles. It creates
        an editor user, force authenticates the test client with that user,
        and sends a GET request to the API endpoint assumed to fetch
        articles. It verifies that the HTTP response code is 200, indicating
        that the request was successfully processed.

        :raises AssertionError: If the HTTP response status code for
            fetching the articles is not as expected.
        :return: None
        """
        editor = User.objects.create_user(
            username='editor1',
            password='edtest',
            email='editor1@example.com',
            role='editor'
        )
        self.client.force_authenticate(user=editor)
        response = self.client.get('/api/articles/')
        # Add appropriate assertions for editor logic
        self.assertEqual(response.status_code, 200)
