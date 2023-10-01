from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from customutils.request_handlers import RequestHandler


class NotificationController:

    @classmethod
    def get_notification_list(cls, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)

        try:
            priority = request.query_params.get("priority")
            queryset = Notification.notification_list(priority)
            paginator = PageNumberPagination()
            paginator.page_size = 10
            result_page = paginator.paginate_queryset(queryset, request)
            serializer_data = NotificationSerializer(result_page, many=True)
            data = paginator.get_paginated_response(serializer_data.data)
            aix_response = {
                    "statusMessage": "Notification list",
                    "errorStatus": False,
                    "data": data.data,
                    "statusCode": status.HTTP_200_OK,
                }
        except Exception as e:
            aix_response = {
                    "statusMessage": "Notifications are not found, error is {}".format(str(e)),
                    "errorStatus": True,
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }

        finally:
            return aix_response

    @classmethod
    def update_notification_read_status(cls, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)

        try:
            alert_id_list = RequestHandler.get_request_data(request=request , key= "notification_ids")
            Notification.objects.filter(alert_id__in=alert_id_list).update(is_read=True)
            aix_response = {
                    "statusMessage": "Notification updated list",
                    "errorStatus": False,
                    "data": [],
                    "statusCode": status.HTTP_200_OK,
                }
        except Exception as e:
            aix_response = {
                    "statusMessage": "Exception in updating read status, with exception message: {}".format(str(e)),
                    "errorStatus": True,
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
        finally:
            return aix_response
