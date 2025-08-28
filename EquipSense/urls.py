# equipment/urls.py
from django.urls import path
from . import views

app_name = 'EquipSense'

urlpatterns = [
    # ----------------------------------------------------
    #   Список и карточки оборудования
    # ----------------------------------------------------
    path('',                 views.equip_list,          name='equip_list'),
    path('e/<int:pk>/',      views.equip_detail,        name='equip_detail'),

    # CRUD‑операции над оборудованием (только для заведующего)
    path('e/add/',           views.equip_create,        name='equip_add'),   # create
    path('e/<int:pk>/edit/', views.equip_update,        name='equip_edit'),  # update
    path('e/<int:pk>/delete/',views.equip_delete,       name='equip_delete'),# delete
    path('equipments/create/', views.equipment_create,
         name='equipment_create'),  # <-- новое имя

    # ----------------------------------------------------
    #   Заявки на выдачу оборудования
    # ----------------------------------------------------
    path('request/cancel/<int:pk>/',   views.cancel_request,  name='cancel_request'),
    path('requests/review/',           views.request_review,  name='request_review'),
    path('request/<int:pk>/', views.request_detail, name='request_detail'),
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
