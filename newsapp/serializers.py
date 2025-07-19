from rest_framework import serializers
from .models import Article, Journalist, Publisher


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Article model.

    This class is responsible for serializing and deserializing
    article objects, allowing them to be easily converted between
    Python native data types and JSON for APIs.

    :ivar Meta: Inner class providing metadata about the
        serializer, including the associated model and the
        fields to include in serialization/deserialization.
    :type Meta: type
    """
    class Meta:
        model = Article
        fields = '__all__'

class JournalistSerializer(serializers.ModelSerializer):
    """
    Handles serialization and deserialization for the Journalist model.

    This class is designed to serialize and deserialize instances of
    the Journalist model. It is based on Django's ModelSerializer,
    which simplifies working with database models by automatically
    handling the creation of serializers.

    :ivar Meta.model: The model associated with this serializer, which
        is the Journalist model.
    :type Meta.model: Type[Journalist]
    :ivar Meta.fields: Specifies that all fields of the Journalist model
        should be included in the serialized representation.
    :type Meta.fields: str
    """
    class Meta:
        model = Journalist
        fields = '__all__'

class PublisherSerializer(serializers.ModelSerializer):
    """
    Handles serialization for the Publisher model.

    This class is a serializer used to convert Publisher model instances
    to and from JSON representation. It inherits from
    serializers.ModelSerializer, which provides a declarative way to
    specify the fields to be serialized. Primarily used in Django REST
    Framework for APIs.

    :ivar Meta: Inner class to configure the serializer behavior.
    :type Meta: class
    """
    class Meta:
        model = Publisher
        fields = '__all__'
