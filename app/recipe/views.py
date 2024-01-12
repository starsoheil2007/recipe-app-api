"""
Views for rrecipe api
"""

from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
)

from core.models import Recipe, Tag
from recipe import serializer
from rest_framework.decorators import action
from rest_framework.response import Response


@extend_schema_view(
    list=extend_schema(
        OpenApiParameter(
            'tags',
            OpenApiTypes.STR,
            discription="Tags filter"
        )
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializer.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """return"""
        return [int(str_id) for str_id in
                qs.split(",")]

    def get_queryset(self):
        """By user"""
        tags = self.request.query_params.get("tags")
        queryset = self.queryset
        if tags:
            tags_id = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tags_id)

        return queryset.filter(user=self.request.user)\
            .order_by('-id').distinct()

    def get_serializer_class(self):
        """Change serializer"""
        if self.action == 'list':
            return serializer.RecipeSerializer
        elif self.action == 'upload_image':
            return serializer.RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create recipe"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializer.TagSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter query set to authenticated"""
        return self.queryset.filter(user=self.request.user).order_by("-name")
