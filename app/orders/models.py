from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Max

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        AWAITING_CALL = 'awaiting_call', _('Ожидает звонок')
        AWAITING_SERVICE = 'awaiting_service', _('Ожидает услугу')
        PAUSED = 'paused', _('Приостановлен')
        COMPLETED = 'completed', _('Завершен')
        CANCELLED = 'cancelled', _('Отменен')

    order_number = models.CharField(max_length=20, unique=True, blank=True)
    order_type = models.CharField(max_length=100)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='orders')
    manager = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_orders')
    specialist = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='specialist_orders')
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.AWAITING_CALL)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    house = models.CharField(max_length=20)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    work_date_start = models.DateField(null=True, blank=True)
    work_date_end = models.DateField(null=True, blank=True)
    work_date = models.DateField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            super().save(*args, **kwargs)  # сохраняем чтобы получить id
            from app.users.models import Shop
            shop = Shop.objects.get(user=self.user)
            
            last = Order.objects.filter(user=self.user).aggregate(Max('id'))['id__max']
            count = (last or 0) + 1
            
            prefix = shop.name[:2].upper()
            self.order_number = f"{prefix}{count:04d}"
            
            Order.objects.filter(pk=self.pk).update(order_number=self.order_number)
        else:
            super().save(*args, **kwargs)  

    def __str__(self):
        return f"Заявка {self.order_number} - {self.status}"
    

class OrderFile(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='order_files/')
    uploaded_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_files')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Файл к заявке {self.order.order_number}"
    

class Notification(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notifications')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Уведомление для {self.user.full_name}"
    

class Service(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    
