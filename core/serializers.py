from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Company, User, Shift, ShiftApplication, Incident, Report, Message, Invoice, Document


class UserSerializer(serializers.ModelSerializer):
    supervisor = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'name',
            'phone',
            'role',
            'status',
            'supervisor',
            'is_staff',
            'date_joined',
        ]


class ShiftSerializer(serializers.ModelSerializer):
    supervisor = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Shift
        fields = [
            'id',
            'supervisor',
            'title',
            'description',
            'latitude',        # <--- Target location for 5m radius
            'longitude',       # <--- Target location for 5m radius
            'radius_meters',   # <--- Default 5.0m
            'start_time',
            'end_time',
            'created_at',
        ]
        read_only_fields = ['id', 'supervisor', 'created_at']
        extra_kwargs = {
            'radius_meters': {
                'default': 5.0,
                'help_text': 'Geofence radius in meters (default: 5.0)'
            },
            'latitude': {
                'help_text': 'Shift location latitude coordinate'
            },
            'longitude': {
                'help_text': 'Shift location longitude coordinate'
            }
        }


class ShiftApplicationSerializer(serializers.ModelSerializer):
    shift = serializers.PrimaryKeyRelatedField(queryset=Shift.objects.all())
    officer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ShiftApplication
        fields = [
            'id',
            'shift',
            'officer',
            'status',
            'policy_signed',
            'signature_timestamp',
        ]


class IncidentSerializer(serializers.ModelSerializer):
    officer = serializers.PrimaryKeyRelatedField(read_only=True)
    shift = serializers.PrimaryKeyRelatedField(queryset=Shift.objects.all())

    class Meta:
        model = Incident
        fields = ['id', 'shift', 'officer', 'description', 'photo_urls', 'timestamp']
        read_only_fields = ['officer', 'timestamp']


class ReportSerializer(serializers.ModelSerializer):
    officer = serializers.PrimaryKeyRelatedField(read_only=True)
    shift = serializers.PrimaryKeyRelatedField(queryset=Shift.objects.all())

    class Meta:
        model = Report
        fields = ['id', 'shift', 'officer', 'summary', 'timestamp']
        read_only_fields = ['officer', 'timestamp']


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    receiver = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    supervisor = serializers.PrimaryKeyRelatedField(read_only=True, required=False)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'supervisor', 'message', 'is_broadcast', 'timestamp']
        read_only_fields = ['sender', 'timestamp']


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class RegisterOfficerSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    name = serializers.CharField()
    phone = serializers.CharField()


class DocumentSerializer(serializers.ModelSerializer):
    is_expiring_soon = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id',
            'officer',
            'doc_type',
            'title',
            'file_url',
            'expiry_date',
            'status',
            'digital_signature',
            'signed_at',
            'uploaded_at',
            'is_expiring_soon',
        ]
        read_only_fields = ['officer', 'status', 'signed_at', 'uploaded_at']

    @extend_schema_field(serializers.BooleanField)
    def get_is_expiring_soon(self, obj):
        return obj.is_expiring_soon()


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            'id',
            'invoice_number',
            'officer',
            'company',
            'shift',
            'hours_worked',
            'hourly_rate',
            'total_amount',
            'status',
            'generated_at',
        ]
        read_only_fields = ['invoice_number', 'officer', 'total_amount', 'generated_at']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'plan',
            'is_trial',
            'trial_ends_at',
            'max_staff_limit',
            'is_whitelabel_enabled',
            'setup_fee_paid',
            'created_at',
        ]