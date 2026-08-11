# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 1. Auth
    path('api/auth/login', views.login_view, name='login'),
    path('api/auth/register', views.register_officer, name='register-officer'),
    path('api/supervisors/invite', views.generate_invite_link, name='generate-invite'),

    # 2. Users
    path('api/users', views.UserListView.as_view(), name='user-list'),
    path('api/supervisors', views.create_supervisor, name='create-supervisor'),
    path('api/officers', views.SupervisorOfficerListView.as_view(), name='supervisor-officers'),
    path('api/officers/<int:officer_id>/decision', views.decide_officer_registration, name='officer-decision'),

    # 3. Shifts
    path('api/shifts', views.ShiftListCreateView.as_view(), name='shifts-list-create'),
    path('api/shifts/<int:shift_id>/apply', views.apply_shift, name='shift-apply'),
    path('api/shifts/applications/<int:application_id>/decision', views.decide_shift_application, name='shift-app-decision'),
    path('api/shifts/<int:shift_id>/checkin', views.checkin_shift, name='shift-checkin'),
    path('api/shifts/<int:shift_id>/checkout', views.checkout_shift, name='shift-checkout'),

    # 4. Communication & Reports
    path('api/messages', views.send_message, name='send-message'),
    path('api/messages/broadcast', views.broadcast_message, name='broadcast-message'),
    path('api/incidents', views.IncidentListCreateView.as_view(), name='incidents'),
    path('api/reports', views.ReportListCreateView.as_view(), name='reports'),

    # 5. Tracking
    path('api/location/update', views.update_location, name='location-update'),
    path('api/officers/<int:officer_id>/location', views.get_officer_location, name='officer-location'),
]