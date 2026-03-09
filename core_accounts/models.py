from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CoreUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'main_admin')

        return self.create_user(email, password, **extra_fields)

class CoreUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('main_admin', 'Main Admin'),     
        ('co_admin', 'Co-Admin'),         
        ('core_member', 'Core Member'),   
    )

    email = models.EmailField(unique=True) 
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='core_member')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) 

    objects = CoreUserManager()

    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"