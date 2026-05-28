import csv
from datetime import datetime
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from .models import Tenant, Facility, IngestionRun, RawRecord, ActivityRecord
from .serializers import ActivityRecordSerializer

class SAPUploadView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        tenant_id = request.data.get('tenant_id')

        if not file or not file.name.endswith('.csv'):
            return Response({"error": "Please upload a valid CSV file."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            return Response({"error": "Invalid Tenant ID"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Create Ingestion Run
        run = IngestionRun.objects.create(
            tenant=tenant,
            source_type='SAP',
            status='PROCESSING'
        )

        # Decode and read CSV
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        
        success_count = 0

        for row in reader:
            # 2. Save Raw Record (The Immutable Source of Truth)
            raw_record = RawRecord.objects.create(
                ingestion_run=run,
                raw_data=row
            )

            # 3. Extract SAP Data (Mapping standard export columns)
            plant_code = row.get('Plant', '')
            raw_qty = row.get('Quantity', '0')
            unit = row.get('Unit', 'L')
            
            # Find Facility by SAP Plant Code
            facility = Facility.objects.filter(tenant=tenant, sap_plant_code=plant_code).first()
            
            # Anomaly Rule: If plant code doesn't exist, flag the record
            review_status = 'PENDING'
            if not facility:
                review_status = 'FLAGGED'

            # Date parsing (Assuming DD.MM.YYYY from standard SAP)
            try:
                posting_date = datetime.strptime(row.get('Posting Date', ''), '%d.%m.%Y').date()
            except ValueError:
                posting_date = datetime.now().date() 

            # 4. Create Normalized Activity Record
            ActivityRecord.objects.create(
                tenant=tenant,
                facility=facility,
                raw_record=raw_record,
                activity_type='FUEL_DIESEL', 
                quantity=Decimal(raw_qty) if raw_qty else Decimal('0.0'),
                unit=unit,
                period_start=posting_date,
                period_end=posting_date,
                scope=1,
                review_status=review_status,
                metadata={"sap_material_doc": row.get('Material Document', '')}
            )
            success_count += 1

        run.status = 'PROCESSED'
        run.save()

        return Response({
            "message": "SAP data ingested and normalized successfully.",
            "ingestion_run_id": run.id,
            "rows_processed": success_count
        }, status=status.HTTP_201_CREATED)
    
# DHYAN DEIN: Ye nayi class ekdum left se shuru honi chahiye (No indentation)
class DashboardView(ListAPIView):
    # In dono lines me 4 spaces ka gap hona zaroori hai
    queryset = ActivityRecord.objects.all().order_by('-id')
    serializer_class = ActivityRecordSerializer

# Ye code views.py ke sabse end me aayega
class UtilityUploadView(APIView):
    def post(self, request):
        payload = request.data
        tenant_id = payload.get('tenant_id')

        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            return Response({"error": "Invalid Tenant ID"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Create Ingestion Run for Utility
        run = IngestionRun.objects.create(
            tenant=tenant,
            source_type='UTILITY_API',
            status='PROCESSING'
        )
        
        success_count = 0
        records = payload.get('data', [])

        for row in records:
            # 2. Save Raw Record
            raw_record = RawRecord.objects.create(
                ingestion_run=run,
                raw_data=row
            )

            # 3. Extract Data
            facility_code = row.get('facility_code', '')
            facility = Facility.objects.filter(tenant=tenant, sap_plant_code=facility_code).first()
            
            review_status = 'PENDING'
            if not facility:
                review_status = 'FLAGGED'

            try:
                start_date = datetime.strptime(row.get('start_date', ''), '%Y-%m-%d').date()
                end_date = datetime.strptime(row.get('end_date', ''), '%Y-%m-%d').date()
            except ValueError:
                start_date = datetime.now().date()
                end_date = datetime.now().date()

            # 4. Create Normalized Record (Electricity - Scope 2)
            ActivityRecord.objects.create(
                tenant=tenant,
                facility=facility,
                raw_record=raw_record,
                activity_type='ELECTRICITY_GRID',
                quantity=Decimal(str(row.get('consumption_kwh', 0))),
                unit='kWh',
                period_start=start_date,
                period_end=end_date,
                scope=2,  # Electricity grid falls under Scope 2
                review_status=review_status,
                metadata={"bill_id": row.get('bill_id', '')}
            )
            success_count += 1

        run.status = 'PROCESSED'
        run.save()

        return Response({
            "message": "Utility JSON data ingested successfully.",
            "ingestion_run_id": run.id,
            "rows_processed": success_count
        }, status=status.HTTP_201_CREATED)    
    
    # Ye code views.py ke sabse end me aayega
class TravelUploadView(APIView):
    def post(self, request):
        payload = request.data
        tenant_id = payload.get('tenant_id')

        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            return Response({"error": "Invalid Tenant ID"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Create Ingestion Run for Travel (Concur/Navan Simulation)
        run = IngestionRun.objects.create(
            tenant=tenant,
            source_type='CONCUR_API',
            status='PROCESSING'
        )
        
        success_count = 0
        records = payload.get('trips', [])
        
        # Corporate travel usually maps to the HQ or default facility
        default_facility = Facility.objects.filter(tenant=tenant).first()

        for row in records:
            # 2. Save Raw Record
            raw_record = RawRecord.objects.create(
                ingestion_run=run,
                raw_data=row
            )

            # 3. Extract Data & Anomaly Detection
            trip_type = row.get('trip_type', 'FLIGHT')
            distance = row.get('distance_km', 0)
            
            # Anomaly Rule: If it's a flight but distance is 0 or missing, flag it for analyst review
            review_status = 'PENDING'
            if trip_type == 'FLIGHT' and (not distance or float(distance) <= 0):
                review_status = 'FLAGGED'

            try:
                travel_date = datetime.strptime(row.get('travel_date', ''), '%Y-%m-%d').date()
            except ValueError:
                travel_date = datetime.now().date()

            # 4. Create Normalized Record (Business Travel - Scope 3)
            ActivityRecord.objects.create(
                tenant=tenant,
                facility=default_facility,
                raw_record=raw_record,
                activity_type='BUSINESS_TRAVEL',
                quantity=Decimal(str(distance)) if distance else Decimal('0.0'),
                unit='km',
                period_start=travel_date,
                period_end=travel_date,
                scope=3,  # Business Travel falls under Scope 3
                review_status=review_status,
                metadata={
                    "trip_id": row.get('trip_id', ''),
                    "origin": row.get('origin', ''),
                    "destination": row.get('destination', ''),
                    "traveler": row.get('traveler_name', '')
                }
            )
            success_count += 1

        run.status = 'PROCESSED'
        run.save()

        return Response({
            "message": "Corporate travel data ingested successfully.",
            "ingestion_run_id": run.id,
            "rows_processed": success_count
        }, status=status.HTTP_201_CREATED)

# views.py ke aakhiri me add kijiye
class ActivityApproveView(APIView):
    def patch(self, request, pk):
        try:
            record = ActivityRecord.objects.get(pk=pk)
        except ActivityRecord.DoesNotExist:
            return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)

        record.review_status = 'APPROVED'
        record.save()
        return Response({
            "message": "Record approved successfully", 
            "status": "APPROVED"
        }, status=status.HTTP_200_OK)    

class ActivityFixView(APIView):
    def patch(self, request, pk):
        try:
            record = ActivityRecord.objects.get(pk=pk)
        except ActivityRecord.DoesNotExist:
            return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)

        new_quantity = request.data.get('quantity')
        
        if new_quantity is not None:
            try:
                record.quantity = Decimal(str(new_quantity))
                # Fix hone ke baad wapas PENDING stage me daal rahe hain
                record.review_status = 'PENDING' 
                record.save()
                return Response({
                    "message": "Record fixed successfully", 
                    "status": "PENDING",
                    "quantity": new_quantity
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": "Invalid number format"}, status=status.HTTP_400_BAD_REQUEST)
                
        return Response({"error": "No quantity provided"}, status=status.HTTP_400_BAD_REQUEST)
    
class SetupDataView(APIView):
    def get(self, request):
        # Ye code automatically ek Tenant aur Facility bana dega
        tenant, created_t = Tenant.objects.get_or_create(id=1, defaults={'name': 'Acme Corp Live'})
        facility, created_f = Facility.objects.get_or_create(
            tenant=tenant,
            sap_plant_code='PLANT-1001',
            defaults={'name': 'Bhopal Plant Live'}
        )
        
        return Response({
            "message": "Database ready! Aap testing shuru kar sakte hain.",
            "tenant_id": tenant.id,
            "facility_sap_code": facility.sap_plant_code
        }, status=status.HTTP_200_OK)