from django.db import models
from django.contrib.auth.models import AbstractUser, Permission
from .managers import UserManager
from django.utils.timezone import now
from django.core.validators import RegexValidator
from django.utils.text import gettext_lazy as _


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


class Gender(models.Model):
    name = models.CharField(max_length=15)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'gender'
        verbose_name_plural = 'gender'


class Specialization(models.Model):
    name = models.CharField(max_length=15)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'specialization'
        verbose_name_plural = 'specialization'


class BloodGroup(models.Model):
    name = models.CharField(max_length=15)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'blood_group'
        verbose_name_plural = 'blood_group'


class Language(models.Model):
    name = models.CharField(max_length=15)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'language'
        verbose_name_plural = 'language'


class DoctorDetail(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    profile_pic = models.CharField(max_length=255, blank=True, null=True)
    gender = models.ForeignKey(
        Gender, on_delete=models.CASCADE, blank=True, null=True)
    specialization = models.ForeignKey(
        Specialization, on_delete=models.CASCADE, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    blood_group = models.ForeignKey(
        BloodGroup, on_delete=models.CASCADE, blank=True, null=True)
    address = models.CharField(max_length=50, blank=True, null=True)
    locality = models.CharField(max_length=50, blank=True, null=True)
    pin = models.CharField(max_length=6, validators=[
                           RegexValidator('^[0-9]{6}$', _('Invalid Pin Number'))])
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, blank=True, null=True)
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, blank=True, null=True)
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, blank=True, null=True)
    alternate_number = models.CharField(max_length=15, blank=True, null=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, blank=True, null=True)
    status = models.SmallIntegerField(default=1)
    deleted = models.BooleanField(default=0)

    class Meta:
        managed = True
        db_table = 'doctor_detail'
        verbose_name_plural = "doctor_detail"
