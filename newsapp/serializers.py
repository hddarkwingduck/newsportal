from rest_framework import serializers
from .models import Article, Journalist, Publisher

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

class JournalistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journalist
        fields = '__all__'

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'
