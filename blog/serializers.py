from rest_framework import serializers
from django.db import transaction
from .models import Post, SubPost


class SubPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubPost
        fields = ['id', 'title', 'body', 'created_at', 'updated_at', 'post']
        read_only_fields = ['id', 'created_at', 'updated_at', 'post']


class PostSerializer(serializers.ModelSerializer):
    subposts = SubPostSerializer(many=True, required=False)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    author = serializers.ReadOnlyField(source='author.id')  # now read-only

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'body', 'author',
            'created_at', 'updated_at', 'subposts',
            'likes_count', 'views_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'likes_count', 'views_count', 'author']

    def create(self, validated_data):
        subposts_data = validated_data.pop('subposts', [])
        request = self.context.get('request')
        post = Post.objects.create(author=request.user, **validated_data)
        for subpost_data in subposts_data:
            SubPost.objects.create(post=post, **subpost_data)
        return post

    @transaction.atomic
    def update(self, instance, validated_data):
        subposts_data = validated_data.pop('subposts', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if subposts_data is not None:
            existing_subposts = {sp.id: sp for sp in instance.subposts.all()}
            sent_ids = [sp.get('id') for sp in subposts_data if sp.get('id')]

            # Delete missing
            for sub_id in set(existing_subposts.keys()) - set(sent_ids):
                existing_subposts[sub_id].delete()

            # Create & update in batches
            to_create = []
            to_update = []
            for sub_data in subposts_data:
                sub_id = sub_data.get('id')
                if sub_id and sub_id in existing_subposts:
                    sub_obj = existing_subposts[sub_id]
                    sub_obj.title = sub_data.get('title', sub_obj.title)
                    sub_obj.body = sub_data.get('body', sub_obj.body)
                    to_update.append(sub_obj)
                else:
                    to_create.append(SubPost(post=instance, **sub_data))

            if to_update:
                SubPost.objects.bulk_update(to_update, ['title', 'body'])
            if to_create:
                SubPost.objects.bulk_create(to_create)

        return instance
