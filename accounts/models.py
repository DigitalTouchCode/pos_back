import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from utils.models.base import TimeStampedModel
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class Tenant(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=100, unique=True)
    currency = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)

    email_host = models.CharField(max_length=255, blank=True, null=True)
    email_port = models.PositiveIntegerField(blank=True, null=True)
    email_use_tls = models.BooleanField(default=True)
    email_use_ssl = models.BooleanField(default=False)
    email_host_user = models.EmailField(blank=True, null=True)
    email_host_password = models.CharField(max_length=255, blank=True, null=True)
    email_from = models.EmailField(blank=True, null=True)
    email_from_name = models.CharField(max_length=100, blank=True, null=True)

    def get_email_connection(self):
        from django.core.mail import get_connection

        return get_connection(
            host=self.email_host,
            port=self.email_port,
            use_tls=self.email_use_tls,
            use_ssl=self.email_use_ssl,
            username=self.email_host_user,
            password=self.email_host_password,
        )

    def __str__(self):
        return self.name


class Branch(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)


class User(AbstractUser, TimeStampedModel):
    ROLE_CHOICES = (
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("staff", "Staff"),
        ("sales", "Sales"),
        ("purchase", "Purchase"),
        ("accountant", "Accountant"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, null=True, related_name="users"
    )
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True)
    username = None
    email = models.EmailField("email address", unique=True)
    password = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False, null=True)
    role = models.CharField(choices=ROLE_CHOICES, max_length=100, default="owner")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        unique_together = ("email", "tenant")

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name


class Invitation(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=User.ROLE_CHOICES)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at
