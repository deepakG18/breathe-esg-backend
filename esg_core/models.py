from django.db import models

class Tenant(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Facility(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    sap_plant_code = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.sap_plant_code})"

class IngestionRun(models.Model):
    SOURCE_CHOICES = [
        ('SAP', 'SAP ERP'),
        ('UTILITY', 'Utility Portal'),
        ('TRAVEL', 'Corporate Travel'),
    ]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='PENDING')

class RawRecord(models.Model):
    ingestion_run = models.ForeignKey(IngestionRun, on_delete=models.CASCADE)
    raw_data = models.JSONField() 
    created_at = models.DateTimeField(auto_now_add=True)

class ActivityRecord(models.Model):
    SCOPE_CHOICES = [(1, 'Scope 1'), (2, 'Scope 2'), (3, 'Scope 3')]
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('FLAGGED', 'Anomaly Flagged'),
        ('APPROVED', 'Approved'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, null=True, blank=True, on_delete=models.SET_NULL)
    raw_record = models.OneToOneField(RawRecord, on_delete=models.CASCADE)
    
    activity_type = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=19, decimal_places=4)
    unit = models.CharField(max_length=20)
    period_start = models.DateField()
    period_end = models.DateField()
    scope = models.IntegerField(choices=SCOPE_CHOICES)
    metadata = models.JSONField(null=True, blank=True) 
    
    review_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not is_new:
            old_instance = ActivityRecord.objects.get(pk=self.pk)
            if old_instance.review_status != self.review_status:
                AuditLog.objects.create(
                    activity_record=self,
                    action="STATUS_CHANGED",
                    old_value={"status": old_instance.review_status},
                    new_value={"status": self.review_status}
                )
        super().save(*args, **kwargs)

class AuditLog(models.Model):
    activity_record = models.ForeignKey(ActivityRecord, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)