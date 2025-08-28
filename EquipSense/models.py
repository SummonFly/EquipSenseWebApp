# equipment/models.py
from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone


class Equipment(models.Model):
    """Товар / оборудование"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quantity_total = models.PositiveIntegerField(default=1)
    # можно добавить фото, тип и т.п.

    def __str__(self):
        return self.name

    @property
    def quantity_available(self):
        """сколько сейчас свободно"""
        used = Request.objects.filter(
            equipment=self,
            status__in=[Request.Status.APPROVED, Request.Status.IN_USE]
        ).aggregate(models.Sum('quantity'))['quantity__sum'] or 0
        return self.quantity_total - used


class Request(models.Model):
    """Заявка на выдачу оборудования"""
    class Status(models.TextChoices):
        PENDING   = 'P', 'Ожидает подтверждения'
        APPROVED  = 'A', 'Одобрено'
        REJECTED  = 'R', 'Отказано'
        IN_USE    = 'U', 'В использовании'
        RETURNED  = 'T', 'Вернул'

    user      = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='requests')
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT)
    quantity  = models.PositiveIntegerField(default=1)
    start_dt  = models.DateTimeField()
    end_dt    = models.DateTimeField()
    status    = models.CharField(max_length=1,
                                 choices=Status.choices,
                                 default=Status.PENDING)
    comment   = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('equipment', 'start_dt', 'end_dt')

    def __str__(self):
        return f'{self.equipment.name} x{self.quantity} от {self.start_dt:%d.%m.%Y %H:%M}'
