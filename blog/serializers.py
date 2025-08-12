from rest_framework import serializers
from .models import Post, SubPost


class SubPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubPost
        fields = ['id', 'title', 'body', 'created_at', 'updated_at', 'post']
        read_only_fields = ['id', 'created_at', 'updated_at', 'post']


class PostSerializer(serializers.ModelSerializer):
    subposts = SubPostSerializer(many=True, required=False)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'body', 'author',
            'created_at', 'updated_at', 'subposts',
            'likes_count', 'views_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'likes_count', 'views_count']

    def create(self, validated_data):
        subposts_data = validated_data.pop('subposts', [])
        post = Post.objects.create(**validated_data)
        for subpost_data in subposts_data:
            SubPost.objects.create(post=post, **subpost_data)
        return post

    def update(self, instance, validated_data):
        subposts_data = validated_data.pop('subposts', None)

        # Update main post fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if subposts_data is not None:
            existing_ids = [sp.id for sp in instance.subposts.all()]
            sent_ids = [sp.get('id') for sp in subposts_data if sp.get('id')]

            # Delete subposts not in request
            for subpost in instance.subposts.all():
                if subpost.id not in sent_ids:
                    subpost.delete()

            # Create or update subposts
            for subpost_data in subposts_data:
                subpost_id = subpost_data.get('id')
                if subpost_id and subpost_id in existing_ids:
                    # Update existing
                    subpost_obj = SubPost.objects.get(id=subpost_id, post=instance)
                    subpost_obj.title = subpost_data.get('title', subpost_obj.title)
                    subpost_obj.body = subpost_data.get('body', subpost_obj.body)
                    subpost_obj.save()
                else:
                    # Create new
                    SubPost.objects.create(post=instance, **subpost_data)

        return instance