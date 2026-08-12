# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 1. Auth
    path('auth/login', views.login_view, name='login'),
    path('auth/register', views.register_officer, name='register-officer'),
    path('supervisors/invite', views.generate_invite_link, name='generate-invite'),

    # 2. Users
    path('users', views.UserListView.as_view(), name='user-list'),
    path('supervisors', views.create_supervisor, name='create-supervisor'),
    path('officers', views.SupervisorOfficerListView.as_view(), name='supervisor-officers'),
    path('officers/<int:officer_id>/decision', views.decide_officer_registration, name='officer-decision'),

    # 3. Shifts
    path('shifts', views.ShiftListCreateView.as_view(), name='shifts-list-create'),
    path('shifts/<int:shift_id>/apply', views.apply_shift, name='shift-apply'),
    path('shifts/applications/<int:application_id>/decision', views.decide_shift_application, name='shift-app-decision'),
    path('shifts/<int:shift_id>/checkin', views.checkin_shift, name='shift-checkin'),
    path('shifts/<int:shift_id>/checkout', views.checkout_shift, name='shift-checkout'),

    # 4. Communication & Reports
    path('messages', views.send_message, name='send-message'),
    path('messages/broadcast', views.broadcast_message, name='broadcast-message'),
    path('incidents', views.IncidentListCreateView.as_view(), name='incidents'),
    path('reports', views.ReportListCreateView.as_view(), name='reports'),

    # 5. Tracking
    path('location/update', views.update_location, name='location-update'),
    path('officers/<int:officer_id>/location', views.get_officer_location, name='officer-location'),

    # 6. Compliance & Document Management
    path('documents', views.DocumentListCreateView.as_view(), name='documents-list-create'),
    path('documents/expiring', views.expiring_documents, name='expiring-documents'),

    # 7. Invoicing Engine
    path('invoices', views.InvoiceListCreateView.as_view(), name='invoices-list-create'),
]