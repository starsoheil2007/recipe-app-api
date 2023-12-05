"""
Serializer for recipe
"""

from rest_framework import serializers
from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for """

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    """Recipe details"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
