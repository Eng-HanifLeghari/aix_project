import os
from datetime import datetime, timedelta
from django.contrib.gis.geos import GEOSGeometry


def default_datetime_format():
    current_datetime = datetime.now()
    default_end_time = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
    default_start_time = (current_datetime - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S.%f")
    return default_end_time, default_start_time


def provided_datetime_format(start_time=None, end_time=None):
    try:
        if start_time:
            start_time = datetime.strptime(start_time.split(" GMT")[0], "%a %b %d %Y %H:%M:%S")\
                .strftime("%Y-%m-%d %H:%M:%S.%f")
        if end_time:
            end_time = datetime.strptime(end_time.split(" GMT")[0], "%a %b %d %Y %H:%M:%S")\
                .strftime("%Y-%m-%d %H:%M:%S.%f")
        return start_time, end_time
    except:
        return None, None


def reconnaissance_ai_processed(con):
    try:
        from apps.reconnaissance.models import ReconnaissanceAIResults
        queryset = ReconnaissanceAIResults.objects.select_related("image").order_by(
            "-created_at")[:10]
        data = [
            {
                "image_name": obj.image.filename,
                "date": obj.created_at.strftime(os.getenv("CUSTOM_TIME_FORMAT")),
                "ai_service": obj.reconnaissance_ai_service.service_name,
                "status": obj.status
            } for obj in queryset]
        con.send_data(data=data, room_group_name="RECONNAISSANCEAIPROCESS")
    except Exception as e:
        print("Exception in cam detections. Exception message :", str(e))
