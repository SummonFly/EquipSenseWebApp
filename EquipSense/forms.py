# equipment/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Request, Equipment
from django.utils import timezone


class EquipmentCreateForm(forms.ModelForm):
    """Форма создания/редактирования оборудования."""
    class Meta:
        model = Equipment
        fields = [
            'name',
            'description',
            'quantity_total',
        ]


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['name', 'description', 'quantity_total']


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


