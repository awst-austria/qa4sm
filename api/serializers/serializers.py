from rest_framework import serializers

from validator.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def validate(self, attrs):
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({'email', 'Email already exists'})
        return super.validate(attrs)

    def create(self, validated_dto):
        return User.objects.create_user(validated_dto)
