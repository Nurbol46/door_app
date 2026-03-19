from django.urls import path
from .views import (
    ManagerOrderFileView, 
    ManagerOrderListView, 
    ManagerOrderDetailView, 
    ManagerServiceListCreateView, 
    ManagerServiceDeleteView
)

urlpatterns = [
    path('orders/', ManagerOrderListView.as_view(), name='manager-order-list'),
    path('orders/<int:pk>/', ManagerOrderDetailView.as_view(), name='manager-order-detail'),
    path('orders/<int:pk>/files/', ManagerOrderFileView.as_view(), name='manager-order-file-list-create'),
    path('services/', ManagerServiceListCreateView.as_view(), name='manager-service-list-create'),
    path('services/<int:pk>/', ManagerServiceDeleteView.as_view(), name='manager-service-delete'),
]
