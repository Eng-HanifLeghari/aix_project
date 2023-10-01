import os
from django.contrib.gis.geos import Polygon
from apps.reconnaissance.models import ImageServerData, FootprintsGeometry, ReconnaissanceAIResults, \
    ReconnaissanceAIServices
from apps.reconnaissance.serializers import CreateImageServerDataSerializer, \
    CreateFootprintsGeometrySerializer, GetFootprintsGeometrySerializer, GetReconnaissanceAIServicesSerializer, \
    GetReconnaissanceAIResultsSerializer
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from customutils.request_handlers import RequestHandler
from customutils.kafka_utils import Kafka


class ReconnaissanceController:

    @classmethod
    def image_server_data(cls, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            serializer = CreateImageServerDataSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                aix_response.update(
                    {
                        "statusMessage": "Query Runs Successfully!",
                        "errorStatus": False,
                        "data": [],
                        "statusCode": status.HTTP_200_OK,
                    }
                )
            else:
                aix_response.update(
                    {
                        "statusMessage": str(serializer.errors),
                        "errorStatus": True,
                        "data": [],
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                    }
                )
        except Exception as e:
            aix_response.update(
                {
                    "statusMessage": "Images are not found, error is {}".format(str(e)),
                    "errorStatus": True,
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            )
        finally:
            return aix_response

    @classmethod
    def image_server_data_filter(cls, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            location = RequestHandler.get_request_data(request, "location")
            data_source = RequestHandler.get_request_data(request, "data_source")
            queryset = FootprintsGeometry.image_server_list(location, data_source)
            paginator = PageNumberPagination()
            paginator.page_size = 10
            result_page = paginator.paginate_queryset(queryset, request)
            serializer_data = GetFootprintsGeometrySerializer(result_page, many=True)
            data = paginator.get_paginated_response(serializer_data.data)
            aix_response.update(
                {
                    "statusMessage": "Query Runs Successfully!",
                    "errorStatus": False,
                    "data": data.data,
                    "statusCode": status.HTTP_200_OK,
                }
            )
        except Exception as e:
            aix_response.update(
                {
                    "statusMessage": "Images are not found, error is {}".format(str(e)),
                    "errorStatus": True,
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            )
        finally:
            return aix_response

    @classmethod
    def foot_print_geometry(cls, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            serializer = CreateFootprintsGeometrySerializer(data=request.data)
            if serializer.is_valid():
                image = serializer.validated_data["image"]
                geometry = serializer.validated_data["geometry"]
                obj = FootprintsGeometry(image=image, geometry=geometry)
                obj.save()
                aix_response.update(
                    {
                        "statusMessage": "Geo Fence Created!",
                        "errorStatus": False,
                        "data": [],
                        "statusCode": status.HTTP_200_OK,
                    }
                )
            else:
                aix_response.update(
                    {
                        "statusMessage": str(serializer.errors),
                        "errorStatus": True,
                        "data": [],
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                    }
                )
        except Exception as e:
            aix_response.update(
                {
                    "statusMessage": "Images are not found, error is {}".format(str(e)),
                    "errorStatus": True,
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            )
        finally:
            return aix_response

    @classmethod
    def filter_foot_print_geometry(cls, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            coordinates = RequestHandler.get_request_data(request, "coordinates")
            data_source = RequestHandler.get_request_data(request, "data_source")
            polygon = Polygon(coordinates)
            queryset = FootprintsGeometry.objects.filter(geometry__intersects=polygon, image__data_source=data_source)
            serializer = GetFootprintsGeometrySerializer(queryset, many=True)
            aix_response.update(
                    {
                        "statusMessage": "Filtered Images!",
                        "errorStatus": False,
                        "data": serializer.data,
                        "statusCode": status.HTTP_200_OK,
                    }
                )
        except Exception as e:
            aix_response.update(
                {
                    "statusMessage": "Images are not found, error is {}".format(str(e)),
                    "errorStatus": True,
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            )
        finally:
            return aix_response

    @classmethod
    def reconnaissance_ai_analyser(cls, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            ids = RequestHandler.get_request_data(request, "ids")
            for obj in ids:
                image = ImageServerData.objects.filter(id=obj.get("image_id")).first()
                service = ReconnaissanceAIServices.objects.filter(service_key=obj.get("service_id")).first()
                if image:
                    reconnaissance_ai_obj = ReconnaissanceAIResults(image=image, reconnaissance_ai_service=service)
                    reconnaissance_ai_obj.save()
                    if reconnaissance_ai_obj:
                        kafka_payload = {
                            "kafka_uuid": str(reconnaissance_ai_obj.kafka_uuid),
                            "base_url": f"{os.getenv('image_server_ip')}/{reconnaissance_ai_obj.image.file_path_local}",
                            "file_name": reconnaissance_ai_obj.image.filename,
                            "reconnaissance_ai_service": reconnaissance_ai_obj.reconnaissance_ai_service.service_key
                        }
                        kafka_con = Kafka()
                        kafka_con.kafka_producer(
                            topic=os.getenv("KAFKA_SMART_RECONNAISSANCE_IMAGE"),
                            values=kafka_payload,
                        )
            aix_response.update(
                    {
                        "statusMessage": "Processing Started!",
                        "errorStatus": False,
                        "data": [],
                        "statusCode": status.HTTP_200_OK,
                    }
                )
        except Exception as e:
            aix_response.update(
                {
                    "statusMessage": "Processing does not started because, error is {}".format(str(e)),
                    "errorStatus": True,
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            )
        finally:
            return aix_response

    @classmethod
    def auto_complete_image_search(cls, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            location = RequestHandler.get_request_data(request, "location")
            data_source = RequestHandler.get_request_data(request, "data_source")
            queryset = list(set(ImageServerData.objects.filter(area_name__icontains=location, data_source=data_source).values_list("area_name")))
            auto_list = [name for query in queryset for name in query]
            aix_response.update(
                {
                    "statusMessage": "Query Runs Successfully!",
                    "errorStatus": False,
                    "data": auto_list,
                    "statusCode": status.HTTP_200_OK,
                }
            )
        except Exception as e:
            aix_response.update(
                {
                    "statusMessage": "Images are not found, error is {}".format(str(e)),
                    "errorStatus": True,
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            )
        finally:
            return aix_response

    @classmethod
    def get_reconnaissance_ai_services(cls, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            queryset = ReconnaissanceAIServices.objects.all()
            serializer = GetReconnaissanceAIServicesSerializer(queryset, many=True)
            aix_response.update(
                {
                    "statusMessage": "Query Runs Successfully!",
                    "errorStatus": False,
                    "data": serializer.data,
                    "statusCode": status.HTTP_200_OK,
                }
            )
        except Exception as e:
            aix_response.update(
                {
                    "statusMessage": "Reconnaissance AI services are not found, error is {}".format(str(e)),
                    "errorStatus": True,
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            )
        finally:
            return aix_response

    @classmethod
    def get_reconnaissance_ai_results(cls, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            queryset = ReconnaissanceAIResults.objects.select_related("image").filter(is_processing=True)
            paginator = PageNumberPagination()
            paginator.page_size = 10
            result_page = paginator.paginate_queryset(queryset, request)
            serializer = GetReconnaissanceAIResultsSerializer(result_page, many=True)
            data = paginator.get_paginated_response(serializer.data)
            aix_response.update(
                {
                    "statusMessage": "Query Runs Successfully!",
                    "errorStatus": False,
                    "data": data.data,
                    "statusCode": status.HTTP_200_OK,
                }
            )
        except Exception as e:
            aix_response.update(
                {
                    "statusMessage": "Reconnaissance AI Results are not found, error is {}".format(str(e)),
                    "errorStatus": True,
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            )
        finally:
            return aix_response

    @classmethod
    def get_reconnaissance_ai_unprocessed_results(cls, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            queryset = ReconnaissanceAIResults.objects.select_related("image").filter(is_processing=False).order_by("-created_at")[:10]
            data = [
                        {
                            "image_name": obj.image.filename,
                            "date": obj.created_at.strftime(os.getenv("CUSTOM_TIME_FORMAT")),
                            "ai_service": obj.reconnaissance_ai_service.service_name,
                            "status": obj.status
                        } for obj in queryset]
            # serializer = GetReconnaissanceAIResultsSerializer(queryset, many=True)
            aix_response.update(
                {
                    "statusMessage": "Query Runs Successfully!",
                    "errorStatus": False,
                    "data": data,
                    "statusCode": status.HTTP_200_OK,
                }
            )
        except Exception as e:
            aix_response.update(
                {
                    "statusMessage": "Reconnaissance AI Results are not found, error is {}".format(str(e)),
                    "errorStatus": True,
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            )
        finally:
            return aix_response
