
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Post, Tag


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "author",
            "tags",
            "tag_names",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "author",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        tag_names = validated_data.pop("tag_names", [])

        post = Post.objects.create(**validated_data)

        for name in tag_names:
            tag, created = Tag.objects.get_or_create(
                name=name.strip().lower()
            )
            post.tags.add(tag)

        return post

    def update(self, instance, validated_data):
        tag_names = validated_data.pop("tag_names", None)

        instance.title = validated_data.get(
            "title", instance.title
        )
        instance.content = validated_data.get(
            "content", instance.content
        )
        instance.save()

        if tag_names is not None:
            tags = []
            for name in tag_names:
                tag, created = Tag.objects.get_or_create(
                    name=name.strip().lower()
                )
                tags.append(tag)

            instance.tags.set(tags)

        return instance
