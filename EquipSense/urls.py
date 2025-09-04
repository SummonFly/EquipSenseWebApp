# equipment/urls.py
from django.urls import path
from . import views
from .views import EquipmentCreateView, EquipmentUpdateView

app_name = 'EquipSense'

urlpatterns = [
    # ----------------------------------------------------
    #   Список и карточки оборудования
    # ----------------------------------------------------
    path('',                 views.equip_list,          name='equip_list'),
    path('e/<int:pk>/',      views.equip_detail,        name='equip_detail'),

    # CRUD‑операции над оборудованием (только для заведующего)
    path('e/<int:pk>/edit/', EquipmentUpdateView.as_view(), name='equip_update'),
    path('equipments/create/', EquipmentCreateView.as_view(), name='equip_create'),
    path('e/<int:pk>/delete/', views.equip_delete,    name='equip_delete'),

    # ----------------------------------------------------
    #   Заявки на выдачу оборудования
    # ----------------------------------------------------
    path('request/cancel/<int:pk>/',   views.cancel_request,  name='cancel_request'),
    path('requests/review/',           views.request_review,  name='request_review'),
    path('request/<int:pk>/', views.request_detail, name='request_detail'),
    path('request/<int:pk>/approve/', views.approve_request, name='approve_request'),
    path('request/<int:pk>/reject/', views.reject_request, name='reject_request'),
    path('request/<int:pk>/return/', views.return_request, name='return_request'),
    path('my-requests/', views.my_requests, name='my_requests'),


    # ----------------------------------------------------
    #   Управление менеджерами (только для администратора)
    # ----------------------------------------------------
    path('admin/manager/add/',         views.create_manager,  name='create_manager'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),

    path('pending-requests/', views.PendingRequestsListView.as_view(), name='pending_requests'),

    path('dashboard/employee/', views.employee_dashboard, name='employee_dashboard'),
    path('dashboard/manager/',  views.manager_dashboard,   name='manager_dashboard'),
    path('dashboard/admin/',    views.admin_dashboard,     name='admin_dashboard'),
]
