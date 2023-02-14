from django.db import models
from django.contrib.auth.models import AbstractUser, Permission
from .managers import UserManager


class UserType(models.Model):
    name = models.CharField(max_length=20)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'user_type'
        verbose_name_plural = 'user_type'


class Role(models.Model):
    name = models.CharField(max_length=20)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'role'
        verbose_name_plural = 'role'


class User(AbstractUser):
    phone = models.CharField(
        verbose_name='phone number',
        max_length=15,
        unique=True,
        error_messages={
            'unique': 'A user with that phone number already exists.'},
        help_text='Required. 15 characters or fewer',
    )
    email = models.EmailField(
        verbose_name='email address',
        max_length=150,
        unique=True,
        error_messages={'unique': 'A user with that email already exists.'},
        help_text='Required. 150 characters or fewer. Letters, digits and @/./_ only.',
    )
    name = models.CharField(max_length=200, blank=True, null=True)
    pswd_token = models.CharField(max_length=255, blank=True, null=True)
    role = models.ForeignKey(
        Role, related_name='userRole', on_delete=models.CASCADE, blank=True, null=True)
    user_type = models.ForeignKey(
        UserType, related_name='userType', on_delete=models.CASCADE, blank=True, null=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name', 'email']

    manager = UserManager()

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_superuser

    class Meta:
        managed = True
        db_table = 'user'
        verbose_name_plural = 'user'


class RolePermission(models.Model):
    role = models.ForeignKey(Role, related_name='RolePermission',
                             on_delete=models.CASCADE, blank=True, null=True)
    permission = models.ForeignKey(
        Permission, related_name='PermissionRole', on_delete=models.CASCADE, blank=True, null=True)
    permitted = models.SmallIntegerField(default=0)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)

    def __str__(self):
        return self.role.name + "=>" + self.permission.codename

    class Meta:
        managed = True
        db_table = 'role_permissions'
        verbose_name_plural = 'role_permissions'


class Country(models.Model):
    sortname = models.CharField(max_length=3)
    name = models.CharField(max_length=150)
    phonecode = models.CharField(max_length=5, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'country'
        verbose_name_plural = 'country'


class State(models.Model):
    name = models.CharField(max_length=30)
    country = models.ForeignKey(
        Country, related_name='CountryState', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'state'
        verbose_name_plural = 'state'


class City(models.Model):
    name = models.CharField(max_length=30)
    state = models.ForeignKey(
        State, related_name='StateCity', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'city'
        verbose_name_plural = 'city'


class UserDetail(models.Model):
    user = models.ForeignKey(User, related_name='UserDetail',
                             on_delete=models.CASCADE, null=True, blank=True)
    field = models.CharField(max_length=255)
    value = models.TextField(blank=True, null=True)
    deleted = models.BooleanField(default=0)

    class Meta:
        managed = True
        db_table = 'user_detail'
        verbose_name_plural = "user_detail"
