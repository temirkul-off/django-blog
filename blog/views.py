from django.db.models import F
from django.utils.timezone import now
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Post, SubPost
from .serializers import PostSerializer, SubPostSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer.validated_data, request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, validated_data_list, user):
        timestamp = now()
        posts = [Post(author=user, created_at=timestamp, updated_at=timestamp, **item) for item in validated_data_list]
        Post.objects.bulk_create(posts)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        if user in post.likes.all():
            post.likes.remove(user)
            return Response({'status': 'unliked'})
        else:
            post.likes.add(user)
            return Response({'status': 'liked'})

    @action(detail=True, methods=['get'])
    def view(self, request, pk=None):
        post = self.get_object()
        Post.objects.filter(pk=post.pk).update(views_count=F('views_count') + 1)
        post.refresh_from_db()
        return Response({'views_count': post.views_count})


class SubPostViewSet(viewsets.ModelViewSet):
    queryset = SubPost.objects.all().order_by('-created_at')
    serializer_class = SubPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
