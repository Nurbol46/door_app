from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import ProfileSerializer, RegisterSerializer
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
