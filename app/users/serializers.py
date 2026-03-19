from rest_framework import serializers
from .models import User, Shop


class RegisterSerializer(serializers.ModelSerializer):

    shop_name = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'shop_name', 'full_name', 'number', 'email', 'role', 'password']
        read_only_fields = ['id', 'role']

    def create(self, validated_data):
        if validated_data['shop_name']:
            user = User.objects.create_user(
                username=validated_data['email'],
                full_name=validated_data['full_name'],
                number=validated_data['number'],
                email=validated_data['email'],
                role='user',
                password=validated_data['password']
            )
            shop = Shop.objects.create(
                user=user,
                name=validated_data['shop_name'],
                city='',
                street='',
                house_number=''
            )
            return user


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