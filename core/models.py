from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email field is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', User.Role.SUPER_ADMIN)
        extra_fields.setdefault('status', User.Status.ACTIVE)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        SUPER_ADMIN = 'super_admin', 'Super Admin'
        SUPERVISOR = 'supervisor', 'Supervisor'
        OFFICER = 'officer', 'Officer'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        REJECTED = 'rejected', 'Rejected'

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.OFFICER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Foreign key pointing to supervisor (for officers)
    supervisor = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='officers'
    )
    
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects: UserManager = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f"{self.name} ({self.role})"


class Document(models.Model):
    officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=100)
    file_url = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Shift(models.Model):
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_shifts')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    location_name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    radius_meters = models.FloatField(default=100.0)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)


class ShiftApplication(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'

    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='applications')
    officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shift_applications')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    applied_at = models.DateTimeField(auto_now_add=True)


class ShiftLog(models.Model):
    class Type(models.TextChoices):
        CHECKIN = 'checkin', 'Check-In'
        CHECKOUT = 'checkout', 'Check-Out'

    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='logs')
    officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shift_logs')
    type = models.CharField(max_length=20, choices=Type.choices)
    latitude = models.FloatField()
    longitude = models.FloatField()
    within_boundary = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class LiveLocation(models.Model):
    officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='live_locations')
    latitude = models.FloatField()
    longitude = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)


class Incident(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='incidents')
    officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incidents')
    description = models.TextField()
    photo_urls = models.JSONField(default=list)  # MySQL JSON Field
    created_at = models.DateTimeField(auto_now_add=True)


class Report(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='reports')
    officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='received_messages')
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_messages')
    message = models.TextField()
    is_broadcast = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    body = models.TextField()
    type = models.CharField(max_length=50)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)