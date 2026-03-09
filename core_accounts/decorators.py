from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

def is_main_admin(user):
    if user.is_authenticated and user.role == 'main_admin':
        return True
    raise PermissionDenied

def is_co_admin_or_higher(user):
    if user.is_authenticated and user.role in ['main_admin', 'co_admin']:
        return True
    raise PermissionDenied

def main_admin_required(function=None, login_url='/admin/login/'):
    """
    Decorator for views that checks that the user is logged in and is a main_admin,
    raising PermissionDenied if not.
    """
    actual_decorator = user_passes_test(
        is_main_admin,
        login_url=login_url
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def co_admin_or_higher_required(function=None, login_url='/admin/login/'):
    """
    Decorator for views that checks that the user is logged in and is a co_admin or main_admin,
    raising PermissionDenied if not.
    """
    actual_decorator = user_passes_test(
        is_co_admin_or_higher,
        login_url=login_url
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
