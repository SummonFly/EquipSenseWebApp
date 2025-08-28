# equipment/views.py
from django.contrib.auth.models import User, Group
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.views.generic import ListView

from .models import Equipment, Request
from .forms import EquipmentForm, RequestForm, ManagerCreationForm, EditUserForm, EquipmentCreateForm


class PendingRequestsListView(ListView):
    model = Request
    template_name = 'equipment/pending_requests.html'
    context_object_name = 'requests'

    def get_queryset(self):
        """
        Возвращаем только те заявки, у которых статус «P» (Pending).
        Если в вашей модели поле называется иначе – поменяйте его.
        """
        return Request.objects.filter(status='P')


class UserListView(ListView):
    model = User
    template_name = 'equipment/user_list.html'   # создайте этот шаблон
    context_object_name = 'users'


@login_required
@permission_required('auth.view_user')
def admin_dashboard(request):
    # --- данные для карточек
    equipment_count = Equipment.objects.count()
    user_count = User.objects.count()
    pending_requests_count = Request.objects.filter(status='pending').count()

    # --- список менеджеров (люди, которые находятся в группе 'manager')
    try:
        manager_group = Group.objects.get(name='manager')
        managers = User.objects.filter(groups=manager_group).order_by('first_name', 'last_name')
    except Group.DoesNotExist:
        managers = []

    context = {
        'equipment_count': equipment_count,
        'user_count': user_count,
        'pending_requests_count': pending_requests_count,
        'managers': managers,          # <‑- ключ, который используется в шаблоне
    }
    return render(request, 'equipment/admin_dashboard.html', context)


@login_required
def manager_dashboard(request):
    user = request.user

    # Добавляем список заявок, чтобы отдать его в шаблон
    pending_requests = Request.objects.filter(status='P')
    approved_requests = Request.objects.filter(status='A')

    pending_count = pending_requests.count()
    approved_count = approved_requests.count()

    return render(request,
                  'equipment/manager_dashboard.html',
                  {
                      'user': user,
                      'pending_count': pending_count,
                      'approved_count': approved_count,
                      'pending_requests': pending_requests,
                  })


@login_required
def my_requests(request):
    """
    Страница «Мои одобренные запросы».
    Показываем только те заявки, которые были приняты и принадлежат текущему пользователю.
    """
    approved = Request.objects.filter(
        assigned_to=request.user,
        status='approved',
    ).select_related('equipment', 'assigned_by')
    return render(request, 'equipment/my_requests.html', {'requests': approved})


@login_required
@user_passes_test(lambda u: u.groups.filter(name='employee').exists())
def employee_dashboard(request):
    return render(request, 'equipment/employee_dashboard.html')


@login_required
@user_passes_test(lambda u: u.groups.filter(name='manager').exists())
def request_detail(request, pk):
    """Показать детальную информацию о заявке."""
    req = get_object_or_404(Request, pk=pk)

    return render(request,
                  'equipment/request_detail.html',
                  {'req': req})


# ---------- Обычные пользователи ----------
@login_required
def equip_list(request):
    """Список оборудования"""
    equipments = Equipment.objects.all()
    return render(request, 'equipment/equip_list.html', {'equipments': equipments})


@login_required
def equip_detail(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    # Форма заявки
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.user = request.user
            req.status = Request.Status.PENDING
            req.save()
            return redirect('EquipSense:equip_detail', pk=pk)
    else:
        form = RequestForm(initial={'equipment': equipment})
    # История заявок пользователя к этому оборудованию
    user_requests = Request.objects.filter(user=request.user,
                                           equipment=equipment).order_by('-created_at')
    return render(request, 'equipment/equip_detail.html',
                  {'equipment': equipment,
                   'form': form,
                   'user_requests': user_requests})


@login_required
def cancel_request(request, pk):
    """Отменить свою заявку (если она ещё в ожидании)"""
    req = get_object_or_404(Request, pk=pk, user=request.user)
    if req.status == Request.Status.PENDING:
        req.delete()
    return redirect('EquipSense:equip_detail', pk=req.equipment.pk)


# ---------- Заведующий складом ----------
@login_required
@permission_required('equipment.add_equipment', raise_exception=True)
def equipment_create(request):
    """
    Создание нового оборудования.
    Менеджер видит форму; после успешной отправки – переходит на список.
    """
    if request.method == 'POST':
        form = EquipmentCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('EquipSense:equip_list')   # <- перенаправляем
    else:
        form = EquipmentCreateForm()

    context = {'form': form}
    return render(request, 'equipment/equipment_form.html', context)


@login_required
@permission_required('equipment.change_equipment')
def equip_create(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('EquipSense:equip_list')
    else:
        form = EquipmentForm()
    return render(request, 'equipment/equip_form.html', {'form': form})


@login_required
@permission_required('equipment.change_equipment')
def equip_update(request, pk):
    equip = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=equip)
        if form.is_valid():
            form.save()
            return redirect('EquipSense:equip_detail', pk=pk)
    else:
        form = EquipmentForm(instance=equip)
    return render(request, 'equipment/equip_form.html', {'form': form})


@login_required
@permission_required('equipment.delete_equipment')
def equip_delete(request, pk):
    equip = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        equip.delete()
        return redirect('EquipSense:equip_list')
    return render(request, 'equipment/equip_confirm_delete.html', {'object': equip})


@login_required
@permission_required('equipment.change_request')
def request_review(request):
    """Список заявок в ожидании"""
    pending = Request.objects.filter(status=Request.Status.PENDING).order_by('-created_at')
    if request.method == 'POST':
        # Приём/отказ через POST: {'action': 'approve', 'id': 12}
        action = request.POST.get('action')
        req_id = request.POST.get('id')
        req = get_object_or_404(Request, pk=req_id)
        if action == 'approve' and req.status == Request.Status.PENDING:
            req.status = Request.Status.APPROVED
            req.save()
        elif action == 'reject' and req.status == Request.Status.PENDING:
            req.status = Request.Status.REJECTED
            req.save()
        return redirect('request_review')
    return render(request, 'equipment/request_review.html', {'requests': pending})


# ---------- Администратор ----------
@login_required
@permission_required('auth.add_user')
def create_manager(request):
    """
    Создать нового заведующего (пользователя + группу).
    """
    if request.method == "POST":
        form = ManagerCreationForm(request.POST)
        if form.is_valid():
            user = form.save()          # сохраняем пользователя
            manager_group, _ = Group.objects.get_or_create(name='manager')
            user.groups.add(manager_group)  # добавляем в группу
            return redirect("EquipSense:user_list")   # или куда хотите перейти
    else:
        form = ManagerCreationForm()

    return render(request,
                  "equipment/admin_create_manager.html",
                  {"form": form})


@login_required
@permission_required("auth.change_user", raise_exception=True)
def edit_user(request, user_id):
    """Редактирование пользователя."""
    user_obj = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        form = EditUserForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            # можно добавить сообщение в Django messages
            return redirect("EquipSense:user_list")
    else:
        form = EditUserForm(instance=user_obj)

    context = {"form": form, "user_obj": user_obj}
    return render(request, "equipment/user_edit.html", context)


@login_required
@permission_required("auth.delete_user", raise_exception=True)
def delete_user(request, user_id):
    """Удаление пользователя."""
    user_obj = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        user_obj.delete()
        return redirect("EquipSense:user_list")

    # Если GET – показать страницу подтверждения
    context = {"user_obj": user_obj}
    return render(request, "equipment/user_confirm_delete.html", context)
