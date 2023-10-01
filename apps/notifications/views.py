from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from apps.notifications.controllers import NotificationController


class NotificationView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def get(self, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            aix_response = NotificationController.get_notification_list(request)
        except Exception as e:
            aix_response = {
                    "statusMessage": "Notifications are not found, error is {}".format(str(e)),
                    "errorStatus": False,
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
        finally:
            return Response(aix_response)


class UpdateNotificationStatus(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def patch(self, request):
        """
        Update notification read status
        :param request:
        :return:
        """
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)

        try:
            aix_response = NotificationController.update_notification_read_status(request)
        except Exception as e:
            aix_response = {
                    "statusMessage": "Exception in update notification, exception message {}".format(str(e)),
                    "errorStatus": False,
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
        finally:
            return Response(aix_response)
