# equipment/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Request, Equipment
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class EquipmentCreateUpdateForm(forms.ModelForm):

    class Meta:
        model = Equipment
        fields = [
            # Базовая информация
            "name",
            "description",
            "quantity_total",

            # Идентификация
            "serial_number",
            "model",
            "category",

            # Локация/статус
            "location",
            "status",

            # Фотография
            "photo",

            # Технические данные
            "purchase_date",
            "warranty_expiry",
            "maintenance_interval_days",

            # Метки
            "tags",
        ]

        widgets = {
            # Идентификация
            "serial_number": forms.TextInput(
                attrs={"placeholder": _("e.g. SN123456")}
            ),
            "model": forms.TextInput(attrs={"placeholder": _("Model name")}),
            "category": forms.Select(),

            # Локация/статус
            "location": forms.TextInput(
                attrs={"placeholder": _("Room / Shelf / etc."), "class": "form-control"}
            ),
            "status": forms.Select(),

            # Фотография
            "photo": forms.ClearableFileInput(),
            # Если хотите, можно задать класс CSS: `attrs={'class': 'form-control-file'}`

            # Технические данные
            "purchase_date": forms.DateInput(
                attrs={"type": "date"},  # HTML5 date picker
                format="%Y-%m-%d",
            ),
            "warranty_expiry": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "maintenance_interval_days": forms.NumberInput(
                attrs={
                    "placeholder": _("Days"),
                    "min": 0,
                }
            ),

            # Метки
            "tags": forms.CheckboxSelectMultiple(),
        }

        labels = {
            "name": _("Name"),
            "description": _("Description"),
            "quantity_total": _("Total quantity"),
            "serial_number": _("Serial number"),
            "model": _("Model"),
            "category": _("Category"),
            "location": _("Location"),
            "status": _("Status"),
            "photo": _("Photo"),
            "purchase_date": _("Purchase date"),
            "warranty_expiry": _("Warranty expiry"),
            "maintenance_interval_days": _("Maintenance interval (days)"),
            "tags": _("Tags"),
        }

        help_texts = {
            "serial_number": _(
                "Unique serial number, if applicable. Leave blank if not used."
            ),
            "category": _(
                "Equipment category (projector, laptop, etc.). You can add a new one in the admin."
            ),
            "status": _(
                "Current status of the equipment. Defaults to 'Available'."
            ),
            "photo": _("Optional photo of the equipment."),
            "maintenance_interval_days": _(
                "Number of days between preventive checks (0 – no schedule)."
            ),
        }

    # ------------------------------------------------------------------
    # Дополнительная валидация
    # ------------------------------------------------------------------

    def clean_quantity_total(self):
        qty = self.cleaned_data.get("quantity_total")
        if qty is not None and qty < 1:
            raise forms.ValidationError(_("Quantity must be at least 1."))
        return qty

    def clean_purchase_date(self):
        date = self.cleaned_data.get("purchase_date")
        if date and date > timezone.now().date():
            raise forms.ValidationError(
                _("Purchase date cannot be in the future.")
            )
        return date

    def clean_warranty_expiry(self):
        expiry = self.cleaned_data.get("warranty_expiry")
        purchase = self.cleaned_data.get("purchase_date")
        if expiry and purchase and expiry < purchase:
            raise forms.ValidationError(
                _("Warranty expiry cannot be before the purchase date.")
            )
        return expiry


class RequestForm(forms.ModelForm):
    start_dt = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    end_dt   = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    class Meta:
        model = Request
        fields = ['equipment', 'quantity', 'start_dt', 'end_dt', 'comment']

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get('start_dt'), cleaned.get('end_dt')
        if start and end and start >= end:
            raise forms.ValidationError("Начало должно быть раньше окончания.")
        # Проверка доступности
        equipment = cleaned.get('equipment')
        quantity  = cleaned.get('quantity', 1)
        if equipment:
            available = equipment.quantity_available
            if quantity > available:
                raise forms.ValidationError(
                    f"Недостаточно свободного оборудования. Свободно: {available}"
                )
        return cleaned


class ManagerCreationForm(UserCreationForm):
    """Форма для регистрации менеджера (заведующего складом)."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name",
                  "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        # сохраняем дополнительные поля
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        if commit:
            user.save()
        return user


class EditUserForm(forms.ModelForm):
    """Форма для редактирования данных пользователя."""
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")


class RegistrationForm(UserCreationForm):
    """
    Расширяем стандартную форму регистрации,
    чтобы добавить поле e‑mail (необязательно).
    """

    email = forms.EmailField(
        required=False,
        help_text="(опционально) Введите ваш адрес электронной почты."
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        """
        Сохраняем пользователя и сохраняем e‑mail (если передан).
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email")
        if commit:
            user.save()
        return user
