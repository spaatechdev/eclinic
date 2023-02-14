from .models import User
from django.db.models import Q


class AuthBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = False
    supports_inactive_user = False

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, username, password):
        try:
            user = User.objects.filter(
                Q(username=username) | Q(email=username) | Q(phone=username)
            ).first()
        except:
            user = None
        return user if user is not None and user.check_password(password) else None
