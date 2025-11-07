from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

class SettingsBackend(BaseBackend):
    """
    Authenticate against credentials defined in settings.ALLOWED_CREDENTIALS.
    Each entry is a dict: {'username': 'name', 'password': 'plain-text'}.
    If the username matches, a local User object is created (if needed) so
    Django can attach a session and permissions as normal.
    """
    def authenticate(self, request, username=None, password=None):
        creds = getattr(settings, 'ALLOWED_CREDENTIALS', [])
        for c in creds:
            if c.get('username') == username and c.get('password') == password:
                UserModel = get_user_model()
                try:
                    user = UserModel.objects.get(username=username)
                except UserModel.DoesNotExist:
                    user = UserModel(username=username)
                    user.set_unusable_password()
                    user.is_staff = False
                    user.is_superuser = False
                    user.save()
                return user
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None