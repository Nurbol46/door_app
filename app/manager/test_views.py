from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from app.users.models import Shop
from app.orders.models import Order, Notification, Service
import datetime

User = get_user_model()


class ManagerOrderDetailViewTestCase(TestCase):
    """Тестирование ManagerOrderDetailView"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Создаем менеджера
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='testpass123',
            full_name='Manager User',
            number='+998991234567',
            role='manager'
        )
        
        # Создаем обычного пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User',
            number='+998991234568'
        )
        
        # Создаем Shop для пользователя
        self.shop = Shop.objects.create(
            user=self.user,
            name='Test Shop',
            city='Tashkent',
            street='Amir Timur',
            house_number='123'
        )
        
        # Создаем заказ
        self.order = Order.objects.create(
            order_type='Installation',
            user=self.user,
            city='Tashkent',
            street='Amir Timur',
            house='123',
            status=Order.OrderStatus.AWAITING_CALL
        )
    
    def test_manager_order_list_requires_manager_role(self):
        """Тестирование, что список заказов требует роли менеджера"""
        # Попытка доступа как обычный пользователь (не менеджер)
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/manager/orders/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_manager_order_list_success(self):
        """Тестирование получения списка всех заказов менеджером"""
        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/api/manager/orders/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.order.id)
    
    def test_manager_can_retrieve_any_order(self):
        """Тестирование, что менеджер может просмотреть любой заказ"""
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(f'/api/manager/orders/{self.order.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order.id)
    
    def test_manager_no_notification_if_status_unchanged(self):
        """Тестирование, что уведомление не создается если статус не изменился"""
        self.client.force_authenticate(user=self.manager)
        
        # Обновляем тот же статус
        data = {
            'status': self.order.status
        }
        response = self.client.patch(f'/api/manager/orders/{self.order.id}/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что уведомление не создано
        notifications = Notification.objects.filter(order=self.order)
        self.assertEqual(notifications.count(), 0)


class ManagerServiceViewTestCase(TestCase):
    """Тестирование ManagerServiceListCreateView и ManagerServiceDeleteView"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Создаем менеджера
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='testpass123',
            full_name='Manager User',
            number='+998991234567',
            role='manager'
        )
        
        # Создаем обычного пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User',
            number='+998991234568'
        )
        
        # Создаем сервис
        self.service = Service.objects.create(
            name='Test Service',
            price=100.00
        )
    
    def test_manager_service_list_requires_manager_role(self):
        """Тестирование, что список сервисов требует роли менеджера"""
        # Попытка доступа как обычный пользователь (не менеджер)
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/manager/services/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_manager_service_list_success(self):
        """Тестирование получения списка сервисов менеджером"""
        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/api/manager/services/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
    
    def test_manager_create_service(self):
        """Тестирование создания сервиса менеджером"""
        self.client.force_authenticate(user=self.manager)
        
        data = {
            'name': 'New Service',
            'price': 200.00
        }
        response = self.client.post('/api/manager/services/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Service')
        
        # Проверяем, что сервис создан в БД
        self.assertTrue(Service.objects.filter(name='New Service').exists())
    
    def test_manager_delete_service(self):
        """Тестирование удаления сервиса менеджером"""
        self.client.force_authenticate(user=self.manager)
        
        service_id = self.service.id
        response = self.client.delete(f'/api/manager/services/{service_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Service.objects.filter(id=service_id).exists())
