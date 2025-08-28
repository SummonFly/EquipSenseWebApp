# equipment/models.py
from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
import uuid


class Category(models.Model):
    """Категория оборудования (проектор, ноутбук и т.д.)"""
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Тег для гибкой классификации оборудования."""
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name


class Equipment(models.Model):
    """Оборудование на складе"""

    # Основная информация
    name = models.CharField(max_length=200, help_text="Короткое название оборудования")
    description = models.TextField(blank=True, null=True)

    # Идентификация
    serial_number = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Serial number",
        help_text="Уникальный серийный номер устройства (если применимо)",
    )
    model = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="equipments",
        blank=True,
        null=True,
        verbose_name="Category"
    )

    # Локация и статус
    location = models.CharField(max_length=200, blank=True, null=True)
    status_choices = [
        ("available", "Available"),
        ("in_use", "In use"),
        ("maintenance", "Maintenance"),
        ("lost", "Lost"),
        ("retired", "Retired"),
    ]
    status = models.CharField(
        max_length=20,
        choices=status_choices,
        default="available",
        verbose_name= "Status"
    )

    # Количество
    quantity_total = models.PositiveIntegerField(default=1)

    # Фотография (необязательно)
    photo = models.ImageField(
        upload_to='equipment_photos/',
        blank=True,
        null=True,
        help_text= "Фотография оборудования"
    )

    # Даты и гарантии
    purchase_date = models.DateField(blank=True, null=True)
    warranty_expiry = models.DateField(blank=True, null=True)

    # Плановое обслуживание
    maintenance_interval_days = models.PositiveIntegerField(
        default=0,
        help_text="Кол-во дней между профилактическими осмотрами (0 – без плана)"
    )

    # Метки
    tags = models.ManyToManyField(Tag, blank=True, related_name="equipments")

    # Технические детали
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        verbose_name = "Equipment"
        verbose_name_plural = "Equipments"
        ordering = ["name", "serial_number"]

    def __str__(self):
        return f"{self.name} ({self.serial_number or ''})".strip()

    # ------------------------------------------------------------------
    # Прочие методы
    # ------------------------------------------------------------------

    @property
    def quantity_available(self) -> int:
        """Сколько единиц сейчас свободно"""
        used = Request.objects.filter(
            equipment=self,
            status__in=[Request.Status.APPROVED, Request.Status.IN_USE]
        ).aggregate(models.Sum("quantity"))["quantity__sum"] or 0
        return self.quantity_total - used

    def is_under_warranty(self) -> bool:
        """Проверка – оборудование ещё в гарантии."""
        if not self.warranty_expiry:
            return False
        from django.utils import timezone
        return self.warranty_expiry >= timezone.now().date()

    @property
    def next_maintenance_due(self):
        """Дата следующего планового обслуживания (если задан интервал)."""
        if not self.maintenance_interval_days or not self.purchase_date:
            return None
        from datetime import timedelta, date
        days_since_purchase = (timezone.now().date() - self.purchase_date).days
        intervals_passed = days_since_purchase // self.maintenance_interval_days
        next_due = self.purchase_date + timedelta(days=(intervals_passed + 1) * self.maintenance_interval_days)
        return next_due


class Request(models.Model):
    """Заявка на выдачу оборудования"""

    class Status(models.TextChoices):
        PENDING = 'P', 'Ожидает подтверждения'
        APPROVED = 'A', 'Одобрено'
        REJECTED = 'R', 'Отказано'
        IN_USE = 'U', 'В использовании'
        RETURNED = 'T', 'Вернул'

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='requests')
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    start_dt = models.DateTimeField()
    end_dt = models.DateTimeField()
    status = models.CharField(max_length=1,
                              choices=Status.choices,
                              default=Status.PENDING)
    comment = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('equipment', 'start_dt', 'end_dt')

    def __str__(self):
        return f'{self.equipment.name} x{self.quantity} от {self.start_dt:%d.%m.%Y %H:%M}'
