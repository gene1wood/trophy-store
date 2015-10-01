from django.contrib import admin
from django_browserid.admin import site as browserid_admin
from .models import CertDestinations, Certificate

browserid_admin.register(CertDestinations)
browserid_admin.register(Certificate)