import json
import os
import sys
from datetime import datetime

from django.apps import AppConfig
from customutils.channels_util import ChannelsCommonConsumer
from customutils.helpers import reconnaissance_ai_processed
from customutils.kafka_utils import Kafka
from multiprocessing import Process


class ReconnaissanceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reconnaissance"

    def ready(self):
        if "runserver" in sys.argv:
            pass
        else:
            return
        con = ChannelsCommonConsumer()
        kaf = Kafka()

        def reconnaissance_ai_result():
            try:
                consumer = kaf.kafka_consumer(
                    topic=os.getenv("KAFKA_PROCESSED_SMART_RECONNAISSANCE_IMAGE"), group_id=None
                )
                for msg in consumer:
                    data = msg.value.decode("UTF-8")
                    if data:
                        from apps.reconnaissance.models import ReconnaissanceAIResults
                        data = json.loads(data)
                        geo_data = {
                            "geo_data": data.get("geo_data", None),
                            "label": data.get("label", None),
                            "object_count": data.get("object_count", None)
                        }
                        reconnaissance_result = ReconnaissanceAIResults.objects.get(kafka_uuid=data.get("kafka_uuid"))
                        if geo_data:
                            reconnaissance_result.status = "completed"
                            reconnaissance_result.is_processing = True
                            reconnaissance_result.complete_ai_date = data.get("date_time", None)
                            reconnaissance_result.geojson_data = geo_data
                            reconnaissance_result.save()
                            if reconnaissance_result:
                                data["filename"] = reconnaissance_result.image.filename
                                data["file_path_local"] = reconnaissance_result.image.file_path_local
                                data["wms_url"] = reconnaissance_result.image.wms_url
                                data["area_name"] = reconnaissance_result.image.area_name
                                data["date_of_acquisition"] = str(reconnaissance_result.image.date_of_acquisition)
                                data["resolution"] = reconnaissance_result.image.resolution
                                data["data_source"] = reconnaissance_result.image.data_source
                                data["base_folder"] = reconnaissance_result.image.base_folder
                                data["layer_name"] = reconnaissance_result.image.layer_name
                                con.send_data(data=data, room_group_name="RECONNAISSANCEAIRESULT")
                            reconnaissance_ai_processed(con)
                        else:
                            reconnaissance_result.status = "failed"
                            reconnaissance_result.save()
                            reconnaissance_ai_processed(con)
            except Exception as e:
                print("Exception in cam detections. Exception message :", str(e))

        p1 = Process(target=reconnaissance_ai_result, args=())
        p1.start()

