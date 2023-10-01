from django.db.models import Q
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from .controllers import FileUpload, FileResponseController
from customutils.request_handlers import RequestHandler
from apps.data_source.serializers import DataSourceListSerializer, AIServiceListSerializer
from .enums.type import DataTypeChoices
from rest_framework.pagination import PageNumberPagination


class FileUploadView(APIView):
    """
    File uploading view.
    """

    authentication_classes = [JWTAuthentication]

    def post(self, request):
        """
        For storing files
        :param request:
        :return:
        """
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            file_list = RequestHandler.get_files(request=request)
            request.data.pop("file")
            aix_response = FileUpload.save_files(request=request, file_list=file_list)
        except Exception as e:
            aix_response = {
                    "statusMessage": "FIle uploading failed with exception {}".format(
                        str(e)
                    ),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class FilesList(generics.ListAPIView):
    """

    API for getting list of required data
    @param : No params
    @returns: returns list
    @raises Exception: Not found exception

    """

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    serializer_class = DataSourceListSerializer
    pagination_class = PageNumberPagination
    model = serializer_class.Meta.model
    queryset = None

    def get_data(self, file_type=None):
        if self.request.user.is_superuser or self.request.user.role.role_key == 1:
            self.queryset = (
                self.model.objects.filter(
                    processed_url__isnull=False,
                    type=file_type,
                    is_processed=True,
                ).values(
                    "file_name",
                    "type",
                    "base_url",
                    "recon_fixed",
                    "user_id",
                    "recon_detection",
                    "processed_url",
                    "id",
                    "user__username",
                    "created_at",
                    "drone_image",
                    "drone_video",
                    "service_type",
                )
            ).order_by("-created_at")
        else:
            self.queryset = (
                self.model.objects.filter(
                    user=self.request.user,
                    processed_url__isnull=False,
                    type=file_type,
                    is_processed=True,
                ).values(
                    "file_name",
                    "type",
                    "base_url",
                    "recon_fixed",
                    "user_id",
                    "recon_detection",
                    "processed_url",
                    "id",
                    "user__username",
                    "created_at",
                    "drone_image",
                    "drone_video",
                    "service_type",
                )
            ).order_by("-created_at")

    def get_queryset(self):
        file_type = self.request.query_params.get("file_type")
        if file_type in [DataTypeChoices.IMAGE.value, DataTypeChoices.SATELLITE.value]:
            self.get_data(file_type=file_type)
        elif file_type == DataTypeChoices.VIDEO:
            self.get_data(file_type=file_type)
        else:
            self.queryset = (
                self.model.objects.filter(
                    Q(user=self.request.user) | Q(user__is_superuser=True),
                    processed_url__isnull=False,
                    is_processed=True,
                    user__is_superuser=True,
                ).values(
                    "file_name",
                    "type",
                    "base_url",
                    "user_id",
                    "recon_fixed",
                    "recon_detection",
                    "processed_url",
                    "id",
                    "drone_image",
                    "drone_video",
                    "service_type",
                )
            ).order_by("-created_at")
        return self.queryset

    def list(self, request, *args, **kwargs):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            queryset = self.filter_queryset(self.get_queryset())
            paginator = PageNumberPagination()
            paginator.page_size = 20
            page = paginator.paginate_queryset(queryset, request)
            serializer = self.get_serializer(page, many=True)
            data = paginator.get_paginated_response(serializer.data)
            if data.data:
                aix_response = {
                    "statusMessage": "Data fetched successfully",
                    "errorStatus": False,
                    "data": data.data,
                    "statusCode": status.HTTP_200_OK,
                }
            else:
                aix_response = {
                    "statusMessage": "No Data",
                    "errorStatus": False,
                    "data": data.data,
                    "statusCode": status.HTTP_200_OK,
                }
        except Exception as err:
            aix_response = {
                "statusMessage": str(err),
                "data": [],
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "errorStatus": True,
            }
        finally:
            return Response(aix_response)


class FileDetailView(APIView):
    """
    File uploading view.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        For fetching detail of file
        :param request:
        :return:
        """
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            id = request.query_params.get("id")
            if id:
                aix_response = FileResponseController.get_file_detail(datasource_id=id)
            else:
                aix_response = {
                        "statusMessage": "Please provide ID",
                        "data": [],
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "errorStatus": True,
                    }
        except Exception as e:
            aix_response = {
                    "statusMessage": "Fetching detail failed with exception {}".format(
                        str(e)
                    ),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class AIServicesList(generics.ListAPIView):
    """

    API for getting list of required data
    @param : No params
    @returns: returns list
    @raises Exception: Not found exception

    """

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    serializer_class = AIServiceListSerializer
    pagination_class = None
    model = serializer_class.Meta.model

    def get_queryset(self):
        ai_service_required = self.request.query_params.get("offline", None)
        if ai_service_required:
            queryset = (self.model.objects.all())
        else:
            queryset = (self.model.objects.filter(service_key="object_detection"))
        return queryset

    def list(self, request, *args, **kwargs):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            res = super(AIServicesList, self).list(request, *args, **kwargs)
            print(res.data)
            if res.data:
                aix_response = {
                        "statusMessage": "Data fetched successfully",
                        "errorStatus": False,
                        "data": res.data,
                        "statusCode": status.HTTP_200_OK,
                    }
            else:
                aix_response = {
                        "statusMessage": "No Data",
                        "errorStatus": False,
                        "data": res.data,
                        "statusCode": status.HTTP_200_OK,
                    }
        except Exception as err:
            aix_response = {
                    "statusMessage": str(err),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            print(aix_response, "-----------------------Services-------------------", request.get_full_path)
            return Response(aix_response)
