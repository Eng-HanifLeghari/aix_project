import ast
import json
import logging
import os
import sys
from multiprocessing import Process

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.apps import AppConfig

from apps.data_source.enums.type import DataTypeChoices
from customutils.channels_util import ChannelsCommonConsumer
from customutils.kafka_utils import Kafka


class DataSourceConfig(AppConfig):
    app_logger = logging.getLogger()
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.data_source"
    run_already = False

    def ready(self):
        if "runserver" in sys.argv:
            pass
        else:
            return
        con = ChannelsCommonConsumer()
        kaf = Kafka()

        def mulhim_image_response():
            """
            Consumer for handling processed mage response
            :return:
            """
            print("In Kafka Image response function")
            try:
                consumer = kaf.kafka_consumer(
                    topic=os.getenv("KAFKA_IMAGE_TOPIC"), group_id=None
                )
                for msg in consumer:
                    data = msg.value.decode("UTF-8")
                    if data:
                        from apps.data_source.controllers import FileResponseController

                        data = json.loads(data)
                        (
                            update_status,
                            exception_message,
                        ) = FileResponseController.update_processed_url(data=data)
                        if update_status:
                            satellite_image = data.get("reconnaissance", False)
                            if satellite_image:

                                (
                                    data_object,
                                    status,
                                ) = FileResponseController.save_datasource_response_satellite(
                                    data=data
                                )

                            else:

                                (
                                    data_object,
                                    status,
                                ) = FileResponseController.save_datasource_response(
                                    data=data
                                )
                            if status:

                                data = (
                                    FileResponseController.create_response_for_channels(
                                        data=data, datasource_object=data_object
                                    )
                                )

                                if data:

                                    if (
                                        data_object.data_source.type
                                        == DataTypeChoices.SATELLITE
                                    ):

                                        if data_object.data_source.recon_detection:
                                            con.send_data(
                                                data=data, room_group_name="AIXRDI"
                                            )

                                        elif data_object.data_source.recon_fixed:

                                            con.send_data(
                                                data=data, room_group_name="AIXRFI"
                                            )
                                    elif (
                                        data_object.data_source.type
                                        == DataTypeChoices.IMAGE
                                    ):

                                        con.send_data(
                                            data=data, room_group_name="AIXIMAGE"
                                        )
                        else:

                            print(
                                "Image response update processed_url failed",
                                exception_message,
                            )

            except Exception as e:
                print(str(e), "execption in chanelss")

        def mulhim_video_response():
            try:
                print("In kafka video response function")
                consumer = kaf.kafka_consumer(
                    topic=os.getenv("KAFKA_VIDEO_TOPIC"), group_id=None
                )
                for msg in consumer:
                    data = msg.value.decode("UTF-8")
                    if data:
                        from apps.data_source.controllers import FileResponseController

                        data = json.loads(data)
                        (
                            update_status,
                            exception_message,
                        ) = FileResponseController.update_processed_url(data=data)
                        if update_status:
                            (
                                data_object,
                                status,
                            ) = FileResponseController.save_datasource_response_video(
                                meta_data=data
                            )
                            if status:
                                data = (
                                    FileResponseController.create_response_for_channels(
                                        data=data, datasource_object=data_object
                                    )
                                )
                                con.send_data(data=data, room_group_name="AIXVIDEO")
            except Exception as e:
                print(e)
                pass

        p1 = Process(target=mulhim_image_response, args=())
        p1.start()
        p2 = Process(target=mulhim_video_response, args=())
        p2.start()
