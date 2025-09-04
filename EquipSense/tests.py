# equipment/tests.py
import io
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .models import Equipment, Category, Tag


class EquipListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # --- группы/права ----------------------------------------------------
        cls.manager_group = Group.objects.create(name='manager')
        cls.admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'pwd')
        cls.manager_user = User.objects.create_user('mgr', 'mgr@test.com', 'pwd')
        cls.manager_user.groups.add(cls.manager_group)
        cls.regular_user = User.objects.create_user('usr', 'usr@test.com', 'pwd')

        # --- категории и теги ------------------------------------------------
        cat1, cat2 = Category.objects.bulk_create([
            Category(name='Projector'),
            Category(name='Laptop')
        ])
        tag_hdmi, tag_usb = Tag.objects.bulk_create([
            Tag(name='HDMI'),
            Tag(name='USB')
        ])

        # --- оборудование ----------------------------------------------------
        cls.equipments = []
        for i in range(1, 6):
            equip = Equipment.objects.create(
                name=f'Equip{i}',
                description='Some very long description ' * 10,
                quantity_total=5 + i,
                location='Room A',
                category=cat1 if i % 2 else cat2,
                serial_number=str(1000 + i),
                status='available',
            )
            equip.tags.set([tag_hdmi, tag_usb] if i % 2 else [tag_usb])
            cls.equipments.append(equip)

    # --------------------------------------------------------------------
    def test_list_shows_all_equipment(self):
        """Страница списка должна вернуть все объекты."""
        url = reverse('EquipSense:equip_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Оборудование')
        # Проверяем, что в контексте есть `equipments` и их число совпадает
        self.assertIn('equipments', response.context)
        self.assertEqual(len(response.context['equipments']), Equipment.objects.count())

    def test_search_filter(self):
        """Поиск по имени возвращает только нужные объекты."""
        url = reverse('EquipSense:equip_list')
        response = self.client.get(url, {'search': 'Equip1'})
        self.assertEqual(response.status_code, 200)
        # В ответе должно быть ровно одно оборудование
        self.assertContains(response, 'Equip1')
        self.assertNotContains(response, 'Equip2')

    def test_sorting(self):
        """Проверяем сортировку по количеству."""
        url = reverse('EquipSense:equip_list')
        response = self.client.get(url, {'ordering': '-quantity_total'})
        self.assertEqual(response.status_code, 200)
        # Проверка порядка (первое должно быть самым большим qty)
        equipments = list(response.context['equipments'])
        self.assertGreater(equipments[0].quantity_total, equipments[-1].quantity_total)

    def test_add_button_visible_to_manager_and_admin(self):
        """Кнопка «Добавить оборудование» видна только менеджерам/админам."""
        url = reverse('EquipSense:equip_list')

        # как обычный пользователь
        self.client.login(username='usr', password='pwd')
        resp = self.client.get(url)
        self.assertNotContains(resp, 'Добавить оборудование')

        # как manager
        self.client.logout()
        self.client.login(username='mgr', password='pwd')
        resp = self.client.get(url)
        self.assertContains(resp, 'Добавить оборудование')

        # как admin
        self.client.logout()
        self.client.login(username='admin', password='pwd')
        resp = self.client.get(url)
        self.assertContains(resp, 'Добавить оборудование')


class EquipDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.equip = Equipment.objects.create(
            name='Special PC',
            description='A powerful workstation.',
            quantity_total=10,
            location='Server room',
            status='available'
        )
        cls.url = reverse('EquipSense:equip_detail', args=[cls.equip.pk])

    def test_detail_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Special PC')
        self.assertContains(response, 'A powerful workstation.')

class EquipCreateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager_user = User.objects.create_user('mgr', 'mgr@test.com', 'pwd')
        cls.category = Category.objects.create(name='Monitor')

    def test_create_equipment_success(self):
        """Менеджер может создать новое оборудование."""
        self.client.login(username='mgr', password='pwd')
        url = reverse('EquipSense:equip_add')

        # Временный «файл» для фото
        image = SimpleUploadedFile(
            name='test.jpg',
            content=b'\x47\x49\x46\x38\x39\x61',
            content_type='image/jpeg'
        )

        data = {
            'name': 'New Monitor',
            'description': '27" IPS display',
            'quantity_total': 15,
            'location': 'Office B',
            'category': self.category.pk,
            'serial_number': 'MON12345',
            'status': 'available',
            'photo': image
        }

        response = self.client.post(url, data, follow=True)
        # После создания перенаправляем на детальную страницу
        self.assertRedirects(response, reverse('EquipSense:equip_detail', args=[1]))
        self.assertTrue(Equipment.objects.filter(name='New Monitor').exists())

    def test_create_equipment_permission_denied(self):
        """Неподключённый пользователь не может создавать."""
        url = reverse('EquipSense:equip_add')
        response = self.client.get(url)
        # Должен редиректить на страницу логина
        self.assertRedirects(response, f'/accounts/login/?next={url}')

