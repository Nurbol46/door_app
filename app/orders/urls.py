from django.urls import path
from .views import NotificationReadView, OrderFileView, OrderListCreateView, OrderDetailView, NotificationListView, ServiceListView, ServicePDFView, HasNewNotificationView

urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order-list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/files/', OrderFileView.as_view(), name='order-files'),
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notification/<int:pk>/read/', NotificationReadView.as_view(), name='notification-read'),
    path('services/', ServiceListView.as_view(), name='service-list'),
    path('services/pdf/', ServicePDFView.as_view(), name='service-pdf'),
    path('has-new/', HasNewNotificationView.as_view(), name='has-new-notification'),
]