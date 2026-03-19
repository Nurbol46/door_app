from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from app.users.models import Shop
from .models import Order, OrderFile, Notification, Service

User = get_user_model()


class OrderModelTestCase(TestCase):
    """Тестирование модели Order"""
    
    def setUp(self):
        # Создаем пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User',
            number='+998991234567'
        )
        
        # Создаем Shop для пользователя
        self.shop = Shop.objects.create(
            user=self.user,
            name='Test Shop',
            city='Tashkent',
            street='Amir Timur',
            house_number='123'
        )
    
    def test_order_creation(self):
        """Тестирование создания заказа"""
        order = Order.objects.create(
            order_type='Installation',
            user=self.user,
            city='Tashkent',
            street='Amir Timur',
            house='123',
            comment='Test comment'
        )
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, Order.OrderStatus.AWAITING_CALL)
        
    def test_order_number_generation(self):
        """Тестирование автоматической генерации номера заказа"""
        order = Order.objects.create(
            order_type='Repair',
            user=self.user,
            city='Tashkent',
            street='Amir Timur',
            house='123'
        )
        # Проверяем, что номер заказа сгенерирован (начинается с TS - первые буквы "Test Shop")
        self.assertIsNotNone(order.order_number)
        self.assertTrue(order.order_number.startswith('TE'))  # "Test Shop"[:2].upper()
        
    def test_order_unique_number(self):
        """Тестирование уникальности номера заказа"""
        order1 = Order.objects.create(
            order_type='Installation',
            user=self.user,
            city='Tashkent',
            street='Amir Timur',
            house='123'
        )
        
        order2 = Order.objects.create(
            order_type='Repair',
            user=self.user,
            city='Tashkent',
            street='Amir Timur',
            house='123'
        )
        
        self.assertNotEqual(order1.order_number, order2.order_number)
    
    def test_order_str_representation(self):
        """Тестирование строкового представления"""
        order = Order.objects.create(
            order_type='Installation',
            user=self.user,
            city='Tashkent',
            street='Amir Timur',
            house='123'
        )
        expected = f"Заявка {order.order_number} - {order.status}"
        self.assertEqual(str(order), expected)


class OrderAPITestCase(TestCase):
    """Тестирование API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Создаем пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User',
            number='+998991234567'
        )
        
        # Создаем другого пользователя
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123',
            full_name='Other User',
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
        
        # Создаем Shop для другого пользователя
        self.other_shop = Shop.objects.create(
            user=self.other_user,
            name='Other Shop',
            city='Samarkand',
            street='Registan',
            house_number='456'
        )
    
    def test_order_list_requires_authentication(self):
        """Тестирование, что список заказов требует аутентификации"""
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_order_list_authenticated(self):
        """Тестирование получения списка заказов аутентифицированным пользователем"""
        # Создаем заказы
        order1 = Order.objects.create(
            order_type='Installation',
            user=self.user,
            city='Tashkent',
            street='Amir Timur',
            house='123'
        )
        
        order2 = Order.objects.create(
            order_type='Repair',
            user=self.other_user,
            city='Samarkand',
            street='Registan',
            house='456'
        )
        
        # Логинимся как первый пользователь
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/orders/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Пользователь должен видеть только свои заказы
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], order1.id)
    
    def test_order_create_with_defaults(self):
        """Тестирование создания заказа с данными по умолчанию из Shop"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'order_type': 'Installation',
        }
        
        response = self.client.post('/api/orders/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['order_type'], 'Installation')
        self.assertEqual(response.data['city'], self.shop.city)
        self.assertEqual(response.data['street'], self.shop.street)
        self.assertEqual(response.data['house'], self.shop.house_number)
    
    def test_order_create_with_custom_location(self):
        """Тестирование создания заказа с пользовательским местоположением"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'order_type': 'Repair',
            'city': 'Bukhara',
            'street': 'Kalon',
            'house': '789',
            'comment': 'Urgent repair'
        }
        
        response = self.client.post('/api/orders/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['order_type'], 'Repair')
        self.assertEqual(response.data['city'], 'Bukhara')
        self.assertEqual(response.data['comment'], 'Urgent repair')
    
    def test_order_detail_view(self):
        """Тестирование получения деталей заказа"""
        order = Order.objects.create(
            order_type='Installation',
            user=self.user,
            city='Tashkent',
            street='Amir Timur',
            house='123',
            comment='Test order'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/orders/{order.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], order.id)
        self.assertEqual(response.data['order_type'], 'Installation')
    
    def test_order_detail_forbidden_for_other_user(self):
        """Тестирование, что пользователь не может видеть чужие заказы"""
        order = Order.objects.create(
            order_type='Installation',
            user=self.user,
            city='Tashkent',
            street='Amir Timur',
            house='123'
        )
        
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(f'/api/orders/{order.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_order_list_filtered_by_user(self):
        """Тестирование фильтрации заказов по пользователю"""
        # Создаем несколько заказов для разных пользователей
        for i in range(3):
            Order.objects.create(
                order_type=f'Type{i}',
                user=self.user,
                city='Tashkent',
                street='Amir Timur',
                house='123'
            )
        
        for i in range(2):
            Order.objects.create(
                order_type=f'OtherType{i}',
                user=self.other_user,
                city='Samarkand',
                street='Registan',
                house='456'
            )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/orders/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_search_order_by_number(self):
        """Тестирование поиска заказа по номеру"""
        # Создаем несколько заказов
        order1 = Order.objects.create(
            order_type='Installation',
            user=self.user,
            city='Tashkent',
            street='Amir Timur',
            house='123'
        )
        
        order2 = Order.objects.create(
            order_type='Repair',
            user=self.user,
            city='Tashkent',
            street='Amir Timur',
            house='123'
        )
        
        # Ищем по номеру первого заказа
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/orders/?search={order1.order_number}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['order_number'], order1.order_number)
    
    def test_search_order_partial_match(self):
        """Тестирование поиска с частичным совпадением номера"""
        # Создаем заказ
        order = Order.objects.create(
            order_type='Installation',
            user=self.user,
            city='Tashkent',
            street='Amir Timur',
            house='123'
        )
        
        # Ищем по части номера
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/orders/?search=TE')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        # Проверяем, что найден наш заказ
        found = any(item['order_number'] == order.order_number for item in response.data)
        self.assertTrue(found)
    
    def test_search_order_no_results(self):
        """Тестирование поиска без результатов"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/orders/?search=NONEXISTENT9999')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_search_order_case_insensitive(self):
        """Тестирование, что поиск регистронезависим"""
        order = Order.objects.create(
            order_type='Installation',
            user=self.user,
            city='Tashkent',
            street='Amir Timur',
            house='123'
        )
        
        # Ищем с разными регистрами
        self.client.force_authenticate(user=self.user)
        response1 = self.client.get(f'/api/orders/?search={order.order_number.upper()}')
        response2 = self.client.get(f'/api/orders/?search={order.order_number.lower()}')
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response1.data), len(response2.data))


class OrderFileAPITestCase(TestCase):
    """Тестирование API endpoints для файлов заказов"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Создаем пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User',
            number='+998991234567'
        )
        
        # Создаем другого пользователя
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123',
            full_name='Other User',
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
            house='123'
        )
        
        # Создаем заказ для другого пользователя
        self.other_shop = Shop.objects.create(
            user=self.other_user,
            name='Other Shop',
            city='Samarkand',
            street='Registan',
            house_number='456'
        )
        
        self.other_order = Order.objects.create(
            order_type='Repair',
            user=self.other_user,
            city='Samarkand',
            street='Registan',
            house='456'
        )
    
    def test_file_upload_requires_authentication(self):
        """Тест 1: Загрузка файла требует аутентификации"""
        test_file = SimpleUploadedFile(
            name='test.txt',
            content=b'Test content',
            content_type='text/plain'
        )
        
        response = self.client.post(
            f'/api/orders/{self.order.id}/files/',
            {'file': test_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_file_upload_success(self):
        """Тест 1: Успешная загрузка файла"""
        test_file = SimpleUploadedFile(
            name='test_document.txt',
            content=b'Test file content for order',
            content_type='text/plain'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/orders/{self.order.id}/files/',
            {'file': test_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('file', response.data)
        self.assertIn('uploaded_at', response.data)
    
    def test_file_upload_forbidden_for_other_user(self):
        """Тест: Пользователь не может загружать файлы в чужой заказ"""
        test_file = SimpleUploadedFile(
            name='test.txt',
            content=b'Test content',
            content_type='text/plain'
        )
        
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(
            f'/api/orders/{self.order.id}/files/',
            {'file': test_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_files_list_requires_authentication(self):
        """Тест 2: Получение списка файлов требует аутентификации"""
        response = self.client.get(f'/api/orders/{self.order.id}/files/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_files_list_empty(self):
        """Тест 2: Получение пустого списка файлов"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/orders/{self.order.id}/files/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_get_files_list_success(self):
        """Тест 2: Успешное получение списка файлов"""
        # Загружаем несколько файлов
        for i in range(3):
            test_file = SimpleUploadedFile(
                name=f'test_file_{i}.txt',
                content=f'Content {i}'.encode(),
                content_type='text/plain'
            )
            OrderFile.objects.create(
                order=self.order,
                file=test_file,
                uploaded_by=self.user
            )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/orders/{self.order.id}/files/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_get_files_list_filtered_by_user(self):
        """Тест: Пользователь видит только файлы своих заказов"""
        # Добавляем файлы в заказ первого пользователя
        test_file = SimpleUploadedFile(
            name='test.txt',
            content=b'Test content',
            content_type='text/plain'
        )
        OrderFile.objects.create(
            order=self.order,
            file=test_file,
            uploaded_by=self.user
        )
        
        # Пытаемся получить файлы из заказа второго пользователя
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/orders/{self.other_order.id}/files/')
        
        # Должен быть пустой список, так как заказ принадлежит другому пользователю
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_file_contains_metadata(self):
        """Тест: Ответ содержит всю необходимую информацию о файле"""
        test_file = SimpleUploadedFile(
            name='document.pdf',
            content=b'PDF content',
            content_type='application/pdf'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/orders/{self.order.id}/files/',
            {'file': test_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('file', response.data)
        self.assertIn('uploaded_by', response.data)
        self.assertIn('uploaded_at', response.data)

class NotificationAPITestCase(TestCase):
    """Тестирование API endpoints для уведомлений"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Создаем пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User',
            number='+998991234567'
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
            house='123'
        )
    
    def test_notification_list_requires_authentication(self):
        """Тест: Получение списка уведомлений требует аутентификации"""
        response = self.client.get('/api/orders/notifications/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_notification_list_empty(self):
        """Тест: Получение пустого списка уведомлений"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/orders/notifications/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class ServiceAPITestCase(TestCase):
    """Тестирование API endpoints для услуг"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Создаем услуги
        self.service1 = Service.objects.create(
            name='Installation',
            price='5000.00'
        )
        
        self.service2 = Service.objects.create(
            name='Repair',
            price='3000.00'
        )
        
        self.service3 = Service.objects.create(
            name='Maintenance',
            price='2000.00'
        )
    
    def test_service_list_public(self):
        """Тест: Список услуг доступен без аутентификации"""
        response = self.client.get('/api/orders/services/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_service_list_contains_all_services(self):
        """Тест: Список содержит все услуги"""
        response = self.client.get('/api/orders/services/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        service_names = [item['name'] for item in response.data]
        
        self.assertIn('Installation', service_names)
        self.assertIn('Repair', service_names)
        self.assertIn('Maintenance', service_names)
    
    def test_service_contains_required_fields(self):
        """Тест: Услуга содержит все необходимые поля"""
        response = self.client.get('/api/orders/services/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        service = response.data[0]
        
        self.assertIn('id', service)
        self.assertIn('name', service)
        self.assertIn('price', service)
    
    def test_service_pdf_generation(self):
        """Тест: Генерация PDF прайс-листа"""
        response = self.client.get('/api/orders/services/pdf/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('price_list.pdf', response['Content-Disposition'])
    
    def test_service_pdf_content_type(self):
        """Тест: PDF имеет корректный тип контента"""
        response = self.client.get('/api/orders/services/pdf/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
    
    def test_service_pdf_has_content(self):
        """Тест: PDF содержит данные"""
        response = self.client.get('/api/orders/services/pdf/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что ответ содержит PDF контент
        self.assertGreater(len(response.content), 0)