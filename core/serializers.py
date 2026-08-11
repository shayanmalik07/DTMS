from rest_framework import serializers
from .models import User, Shift, ShiftApplication, Incident, Report, Message


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
			'created_at',
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
			'location_name',
			'latitude',
			'longitude',
			'radius_meters',
			'start_time',
			'end_time',
			'created_at',
		]


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
			'applied_at',
		]


class IncidentSerializer(serializers.ModelSerializer):
	officer = serializers.PrimaryKeyRelatedField(read_only=True)
	shift = serializers.PrimaryKeyRelatedField(queryset=Shift.objects.all())

	class Meta:
		model = Incident
		fields = [
			'id',
			'shift',
			'officer',
			'description',
			'photo_urls',
			'created_at',
		]


class ReportSerializer(serializers.ModelSerializer):
	officer = serializers.PrimaryKeyRelatedField(read_only=True)
	shift = serializers.PrimaryKeyRelatedField(queryset=Shift.objects.all())

	class Meta:
		model = Report
		fields = [
			'id',
			'shift',
			'officer',
			'description',
			'created_at',
		]


class MessageSerializer(serializers.ModelSerializer):
	sender = serializers.PrimaryKeyRelatedField(read_only=True)
	receiver = serializers.PrimaryKeyRelatedField(read_only=True)
	supervisor = serializers.PrimaryKeyRelatedField(read_only=True)

	class Meta:
		model = Message
		fields = [
			'id',
			'sender',
			'receiver',
			'supervisor',
			'message',
			'is_broadcast',
			'created_at',
		]



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class RegisterOfficerSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    name = serializers.CharField()
    phone = serializers.CharField()