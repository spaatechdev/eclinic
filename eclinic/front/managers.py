from django.contrib.auth.models import UserManager as BaseUserManager
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now


class UserManager(BaseUserManager): # Here
   
    def _create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError("The given phone must be set")
        phone = self.normalize_email(phone)
        extra_fields['username'] = phone # username should be as phone
        user = self.model(phone=phone, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone=None, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        extra_fields["pswd_token"] = password
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone=None, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields["pswd_token"] = password
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone, password, **extra_fields)