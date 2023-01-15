from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    Менеджер пользователей
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Создаём и сохраняем пользователя
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        print('_create_user', user.password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        print('create_user')
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        print('create_superuser')
        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Кастомная модель пользователя
    """
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(blank=True, max_length=12)
    USERNAME_FIELD = 'email'
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"
        ordering = ('email',)
