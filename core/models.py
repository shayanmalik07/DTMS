# core/models.py
from __future__ import annotations

from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# ==========================================
# 1. COMPANY & SUBSCRIPTION MULTI-TENANCY
# ==========================================

class Company(models.Model):
    class PlanTier(models.TextChoices):
        STARTER = 'starter', 'Starter (£2.50/staff)'
        PROFESSIONAL = 'professional', 'Professional (£5.00/staff)'
        ENTERPRISE = 'enterprise', 'Enterprise (£8.00-10.00/staff)'
        COMPANY_SMALL = 'company_small', 'Small Company (£99/mo)'
        COMPANY_MEDIUM = 'company_medium', 'Medium Company (£299/mo)'
        COMPANY_LARGE = 'company_large', 'Large Company (£499-699/mo)'

    name = models.CharField(max_length=255)
    plan = models.CharField(max_length=50, choices=PlanTier.choices, default=PlanTier.PROFESSIONAL)
    is_trial = models.BooleanField(default=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    max_staff_limit = models.PositiveIntegerField(default=10)  # 30-day trial cap
    is_whitelabel_enabled = models.BooleanField(default=False)
    setup_fee_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ==========================================
# 2. USER MODEL (Custom AbstractUser)
# ==========================================

class UserManager(BaseUserManager['User']):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.SUPER_ADMIN)
        extra_fields.setdefault('status', User.Status.ACTIVE)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    class Role(models.TextChoices):
        SUPER_ADMIN = 'super_admin', 'Super Admin'
        SUPERVISOR = 'supervisor', 'Supervisor'
        OFFICER = 'officer', 'Officer / Staff'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Approval'
        ACTIVE = 'active', 'Active'
        REJECTED = 'rejected', 'Rejected'
        SUSPENDED = 'suspended', 'Suspended'

    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.OFFICER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_officers')
    phone = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    objects: UserManager = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} ({self.role})"


# ==========================================
# 3. DOCUMENT COMPLIANCE & EXPIRY
# ==========================================

class Document(models.Model):
    class DocType(models.TextChoices):
        SIA_LICENCE = 'sia_licence', 'SIA Licence'
        PROOF_OF_ADDRESS = 'proof_of_address', 'Proof of Address'
        PASSPORT_ID = 'passport_id', 'Passport / ID'
        RIGHT_TO_WORK = 'right_to_work', 'Right to Work'
        OTHER = 'other', 'Other Certification'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Review'
        VERIFIED = 'verified', 'Verified / Approved'
        EXPIRED = 'expired', 'Expired'
        REJECTED = 'rejected', 'Rejected'

    officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=50, choices=DocType.choices)
    title = models.CharField(max_length=255)
    file_url = models.URLField(max_length=500)
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Digital Signature & Timestamps
    digital_signature = models.TextField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def is_expiring_soon(self, days=30):
        if self.expiry_date:
            return (self.expiry_date - timezone.now().date()).days <= days
        return False

    def __str__(self):
        return f"{self.officer.email} - {self.title} ({self.status})"


# ==========================================
# 4. SHIFTS, GEO-FENCING & LOGS
# ==========================================

class Shift(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_shifts')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    latitude = models.FloatField()
    longitude = models.FloatField()
    radius_meters = models.FloatField(default=5.0, help_text="Geofence radius in meters")

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ShiftApplication(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'

    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='applications')
    officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shift_applications')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    policy_signed = models.BooleanField(default=True)
    signature_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('shift', 'officer')


class ShiftLog(models.Model):
    class Type(models.TextChoices):
        CHECKIN = 'checkin', 'Check-In'
        CHECKOUT = 'checkout', 'Check-Out'

    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='logs')
    officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shift_logs')
    type = models.CharField(max_length=10, choices=Type.choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    latitude = models.FloatField()
    longitude = models.FloatField()
    within_boundary = models.BooleanField(default=False)


# ==========================================
# 5. LIVE LOCATION TRACKING
# ==========================================

class LiveLocation(models.Model):
    officer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='live_location')
    latitude = models.FloatField()
    longitude = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)


# ==========================================
# 6. INVOICING MODULE
# ==========================================

class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SUBMITTED = 'submitted', 'Submitted'
        PAID = 'paid', 'Paid'
        REJECTED = 'rejected', 'Rejected'

    invoice_number = models.CharField(max_length=50, unique=True)
    officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True)
    
    hours_worked = models.DecimalField(max_digits=6, decimal_places=2)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.officer.name}"


# ==========================================
# 7. COMMUNICATIONS, INCIDENTS & REPORTS
# ==========================================

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='received_messages')
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='company_messages')
    message = models.TextField()
    is_broadcast = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


class Incident(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='incidents')
    officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_incidents')
    description = models.TextField()
    photo_urls = models.JSONField(default=list, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class Report(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='reports')
    officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_reports')
    summary = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)