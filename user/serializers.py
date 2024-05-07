from rest_framework import serializers
from .models import CustomUser,Profile
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'password','first_name', 'last_name')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class ProfileUpdateserializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id','email', 'first_name', 'last_name', 'dob', 'gender', 'phone', 'image']

    def validate(self, data):
        required_fields = ['email', 'first_name','last_name', 'dob', 'gender', 'phone']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(f"{field.capitalize()} field is required.")

        # Check if email already exists
        email = data.get('email')
        if email and Profile.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email address already exists.")

        return data
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    access_token = serializers.SerializerMethodField()
    # refresh_token = serializers.SerializerMethodField()
    #
    # def get_refresh_token(self, instance):
    #     refresh_token = RefreshToken.for_user(instance)
    #     return str(refresh_token)

    def get_access_token(self, instance):
        refresh_token = RefreshToken.for_user(instance)
        return str(refresh_token.access_token)



class ProfileDisplayserilizer(serializers.Serializer):
    user_id = serializers.IntegerField()