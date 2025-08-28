# equipment/context_processors.py

def user_role(request):
    if not request.user.is_authenticated:
        return {}

    # Пример с группами
    groups = request.user.groups.values_list('name', flat=True)

    if 'administrator' in groups or request.user.is_superuser:
        role = 'admin'
    elif 'manager' in groups:
        role = 'manager'
    else:
        role = 'employee'

    return {'role': role}
