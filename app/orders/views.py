from django.shortcuts import render
from rest_framework import generics, exceptions, filters
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .serializers import (OrderCreateSerializer, OrderListSerializer, OrderDetailSerializer, OrderFileSerializer, NotificationSerializer, ServiceSerializer)
from .models import Order, OrderFile, Service, Notification
from rest_framework.views import APIView
from rest_framework.response import Response



class OrderListCreateView(generics.ListCreateAPIView):
    """
    Список заявок пользователя и создание новой.
    Поиск по номеру заявки.
    """
    filter_backends = [filters.SearchFilter]
    search_fields = ['order_number']
    
    def get_queryset(self):
        """Только заявки текущего пользователя."""
        return Order.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Выбор сериализатора: для создания или чтения."""
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderListSerializer
    

class OrderDetailView(generics.RetrieveAPIView):
    """Полная информация о заявке пользователя."""
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        """Только заявки текущего пользователя."""
        return Order.objects.filter(user=self.request.user)


class OrderFileView(generics.ListCreateAPIView):
    """
    Управление файлами заявки: список и загрузка.
    Доступны только для владельца заявки.
    """
    serializer_class = OrderFileSerializer

    def get_queryset(self):
        """Файлы заявки текущего пользователя."""
        pk = self.kwargs.get('pk')
        return OrderFile.objects.filter(
            order__id=pk,
            order__user=self.request.user
        )
    
    def perform_create(self, serializer):
        """Загрузка файла и связь с заявкой."""
        pk = self.kwargs.get('pk')
        try:
            order = Order.objects.get(id=pk, user=self.request.user)
            serializer.save(order=order, uploaded_by=self.request.user)
        except Order.DoesNotExist:
            raise exceptions.NotFound(detail="Order not found.")
        
    
class NotificationListView(generics.ListAPIView):
    """
    Все уведомления пользователя, отсортированы по дате (новые первыми).
    Уведомления создаются при изменении статуса или даты работы заявки.
    """
    serializer_class = NotificationSerializer

    def get_queryset(self):
        """Все уведомления текущего пользователя."""
        return self.request.user.notifications.all().order_by('-created_at')
    

class NotificationReadView(generics.UpdateAPIView):
    """Отметить уведомление как прочитанное."""
    serializer_class = NotificationSerializer

    def get_queryset(self):
        """Только непрочитанные уведомления."""
        return self.request.user.notifications.filter(is_read=False)
    
    def perform_update(self, serializer):
        """Сохранение статуса 'прочитано'."""
        serializer.save(is_read=True)


class ServiceListView(generics.ListAPIView):
    """Публичный список всех услуг с ценами."""
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()
    permission_classes = [AllowAny]


class ServicePDFView(generics.GenericAPIView):
    """Скачивание прайс-листа в формате PDF (публичный доступ)."""
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Генерирует и возвращает PDF с услугами и ценами."""
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="price_list.pdf"'

        p = canvas.Canvas(response)
        
        p.setFont('Helvetica', 12)

        services = Service.objects.all()
        y = 750
        p.drawString(100, y, "Прайс-лист")

        for service in services:
            y -= 30
            p.drawString(100, y, service.name)
            p.drawString(400, y, f"{service.price} руб.")

        p.save()
        return response
    
class HasNewNotificationView(APIView):
    """Проверить наличие непрочитанных уведомлений (быстрая проверка)."""
    
    def get(self, request):
        """Возвращает {'has_new': true/false}."""
        has_new = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).exists()
        return Response({"has_new": has_new})