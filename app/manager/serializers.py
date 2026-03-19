from app.orders.models import Order
from rest_framework import serializers

class ManagerOrderUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['status', 'specialist', 'work_date']

    def validate_work_date(self, value):
        order = self.instance
        if order.work_date_start and order.work_date_end:
            if not (order.work_date_start <= value <= order.work_date_end):
                raise serializers.ValidationError(
                    "Дата должна быть в диапазоне указанном пользователем"
                )
        return value