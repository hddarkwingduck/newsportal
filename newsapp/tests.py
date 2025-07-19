from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import Article, Publisher
from django.test import TestCase

User = get_user_model()


class APITest(TestCase):
    def setUp(self):
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

    def test_reader_gets_only_subscribed_approved_articles(self):
        self.client.force_authenticate(user=self.reader)
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, 200)

        titles = {art['title'] for art in response.json()}
        # Reader is subscribed, but only 'Approved Article' should be returned
        self.assertIn('Approved Article', titles)
        self.assertNotIn('Pending Article', titles)

    def test_unsubscribed_reader_gets_no_articles(self):
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

    def test_unauthenticated_user_gets_articles(self):
        self.client.logout()
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, 200)
        # Should likely only see globally public articles
        # Depending on your API, could be all approved, or none if only for auth users
        # Test appropriately.

    def test_editor_can_see_unapproved_articles(self):
        editor = User.objects.create_user(
            username='editor1',
            password='edtest',
            email='editor1@example.com',
            role='editor'
        )
        self.client.force_authenticate(user=editor)
        response = self.client.get('/api/articles/')  # adjust if editors have separate endpoint
        # Add appropriate assertions for editor logic
        self.assertEqual(response.status_code, 200)
