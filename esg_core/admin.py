from django.contrib import admin
from .models import Tenant, Facility, IngestionRun, RawRecord, ActivityRecord, AuditLog

admin.site.register(Tenant)
admin.site.register(Facility)
admin.site.register(IngestionRun)
admin.site.register(RawRecord)
admin.site.register(ActivityRecord)
admin.site.register(AuditLog)