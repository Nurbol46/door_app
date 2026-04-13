from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Shop


class RegisterSerializer(serializers.ModelSerializer):

    shop_name = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'shop_name', 'full_name', 'number', 'email', 'role', 'password']
        read_only_fields = ['id', 'role']

    def create(self, validated_data):
        shop_name = validated_data.pop('shop_name')  # вытаскиваем и удаляем из данных
        
        user = User.objects.create_user(
            username=validated_data['email'],
            full_name=validated_data['full_name'],
            number=validated_data['number'],
            email=validated_data['email'],
            role='user',
            password=validated_data['password']
        )
        Shop.objects.create(
            user=user,
            name=shop_name,
            city='',
            street='',
            house_number=''
        )
        return user  # всегда возвращаем юзера

class ShopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shop
        fields = ['id', 'name', 'city', 'street', 'house_number']


class ProfileSerializer(serializers.ModelSerializer):

    shop = ShopSerializer(source='shops')

    class Meta:
        model = User
        fields = ['id', 'full_name', 'number', 'email', 'role', 'shop']

    def update(self, instance, validated_data):
    
        shop_data = validated_data.pop('shops', None)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.number = validated_data.get('number', instance.number)
        instance.email = validated_data.get('email', instance.email)
        

        if shop_data:
            Shop.objects.filter(user=instance).update(**shop_data)
    
        instance.save()
        return instance
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # добавляем доп. данные к ответу
        data['role'] = self.user.role
        data['full_name'] = self.user.full_name
        
        return data