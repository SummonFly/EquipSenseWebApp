# equipment/middleware.py
from django.shortcuts import redirect


class RoleRedirectMiddleware:
    """
    После успешного login перенаправляет пользователя в нужный раздел.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.path == '/accounts/login/' and request.user.is_authenticated:
            if request.user.is_superuser or request.user.groups.filter(name='administrator').exists():
                return redirect('EquipSense:admin_dashboard')
            elif request.user.groups.filter(name='manager').exists():
                return redirect('EquipSense:manager_dashboard')
            else:
                return redirect('EquipSense:employee_dashboard')

        return response
