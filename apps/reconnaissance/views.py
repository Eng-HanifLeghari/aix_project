from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.reconnaissance.controllers import ReconnaissanceController
from rest_framework.pagination import PageNumberPagination


class ImageServerDataView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def post(self, request):
        aix_response = ReconnaissanceController.image_server_data(request=request)
        return Response(aix_response)


class FilterImageServerDataView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def post(self, request):
        aix_response = ReconnaissanceController.image_server_data_filter(request=request)
        return Response(aix_response)


class FootPrintGeometryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        aix_response = ReconnaissanceController.foot_print_geometry(request=request)
        return Response(aix_response)


class FilterGeometryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        aix_response = ReconnaissanceController.filter_foot_print_geometry(request=request)
        return Response(aix_response)


class ReconnaissanceAIAnalyser(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        aix_response = ReconnaissanceController.reconnaissance_ai_analyser(request=request)
        return Response(aix_response)


class AutoCompleteImageSearch(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        aix_response = ReconnaissanceController.auto_complete_image_search(request=request)
        return Response(aix_response)


class ReconnaissanceAIServicesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        aix_response = ReconnaissanceController.get_reconnaissance_ai_services(request=request)
        return Response(aix_response)


class ReconnaissanceAIResultsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        aix_response = ReconnaissanceController.get_reconnaissance_ai_results(request=request)
        return Response(aix_response)


class ReconnaissanceAIUnprocessedResultsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        aix_response = ReconnaissanceController.get_reconnaissance_ai_unprocessed_results(request=request)
        return Response(aix_response)
