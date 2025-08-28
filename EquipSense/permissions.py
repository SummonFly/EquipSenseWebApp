# equipment/permissions.py
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from EquipSense.models import Equipment


def init_groups_and_perms():
    """Запускаем один раз (например в миграциях)"""
    # Группы
    staff_group, _   = Group.objects.get_or_create(name='Заведующий')
    admin_group, _   = Group.objects.get_or_create(name='Администратор')

    # Права
    ct_eq = ContentType.objects.get_for_model(Equipment)
    perm_add  = Permission.objects.get(codename='add_equipment', content_type=ct_eq)
    perm_del  = Permission.objects.get(codename='delete_equipment', content_type=ct_eq)
    perm_change = Permission.objects.get(codename='change_equipment', content_type=ct_eq)

    staff_group.permissions.set([perm_add, perm_del, perm_change])
    # Администратор получает всё
    admin_group.permissions.set(Permission.objects.all())
    print("Группы пользователей настроенны")
