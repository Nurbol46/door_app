from rest_framework import generics
from app.orders.permissions import IsManager
from app.orders.serializers import OrderListSerializer, OrderDetailSerializer, OrderFileSerializer, ServiceSerializer
from .serializers import ManagerOrderUpdateSerializer
from app.orders.models import Order, OrderFile, Notification, Service


class ManagerServiceListCreateView(generics.ListCreateAPIView):
    """Управление услугами: список и создание (только менеджер)."""
    serializer_class = ServiceSerializer
    permission_classes = [IsManager]
    queryset = Service.objects.all()


class ManagerServiceDeleteView(generics.DestroyAPIView):
    """Удаление услуги (только менеджер)."""
    serializer_class = ServiceSerializer
    permission_classes = [IsManager]
    queryset = Service.objects.all()


class ManagerOrderListView(generics.ListAPIView):
    """Список всех заявок, отсортирован по дате создания (только менеджер)."""
    serializer_class = OrderListSerializer
    permission_classes = [IsManager]

    def get_queryset(self):
        """Все заявки в обратном хронологическом порядке."""
        return Order.objects.all().order_by('-created_at')


class ManagerOrderDetailView(generics.RetrieveUpdateAPIView):
    """
    Просмотр и обновление заявки (только менеджер).
    При изменении статуса или даты работы отправляется уведомление клиенту.
    """
    permission_classes = [IsManager]
    
    def get_queryset(self):
        """Все заявки для обновления."""
        return Order.objects.all()

    def get_serializer_class(self):
        """Выбор сериализатора: для обновления или чтения."""
        if self.request.method in ['PUT', 'PATCH']:
            return ManagerOrderUpdateSerializer
        return OrderDetailSerializer
    
    def perform_update(self, serializer):
        """Сохранение изменений и уведомление клиента об изменении статуса или даты."""
        old_status = self.get_object().status
        old_work_date = self.get_object().work_date
        order = serializer.save()
        
        if old_status != order.status:
            Notification.objects.create(
                user=order.user,
                order=order,
            )
        
        if old_work_date != order.work_date and order.work_date:
            Notification.objects.create(
                user=order.user,
                order=order,
            )
    

class ManagerOrderFileView(generics.ListCreateAPIView):
    """Управление файлами заявки: список и загрузка (только менеджер)."""
    serializer_class = OrderFileSerializer
    permission_classes = [IsManager]

    def get_queryset(self):
        """Файлы конкретной заявки."""
        pk = self.kwargs.get('pk')
        return OrderFile.objects.filter(order__id=pk)
    
    def perform_create(self, serializer):
        """Загрузка файла и связь с заявкой и пользователем."""
        pk = self.kwargs.get('pk')
        order = Order.objects.get(pk=pk)
        serializer.save(order=order, uploaded_by=self.request.user)