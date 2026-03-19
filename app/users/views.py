from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import CustomTokenObtainPairSerializer, ProfileSerializer, RegisterSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User


class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    """Просмотр и обновление профиля текущего пользователя."""
    serializer_class = ProfileSerializer

    def get_object(self):
        """Возвращает профиль текущего авторизованного пользователя."""
        return self.request.user
    
class CustomTokenObtainPairView(TokenObtainPairView):
    """Получение JWT токенов с дополнительными данными пользователя (роль, имя)."""
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_summary="Авторизация",
        operation_description="Введите email и пароль для получения JWT токенов",
        tags=['Авторизация']
    )
    def post(self, request, *args, **kwargs):
        """Переопределение метода POST для получения токенов с дополнительными данными."""
        return super().post(request, *args, **kwargs)
