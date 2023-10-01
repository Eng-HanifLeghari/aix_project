from rest_framework import serializers
from apps.reconnaissance.models import ImageServerData, FootprintsGeometry, ReconnaissanceAIServices, \
    ReconnaissanceAIResults
from rest_framework_gis.serializers import GeoFeatureModelSerializer


class CreateFootprintsGeometrySerializer(GeoFeatureModelSerializer):

    class Meta:
        model = FootprintsGeometry
        geo_field = "geometry"
        fields = ["id", "geometry", "image", "created_at", "updated_at"]


class CreateImageServerDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImageServerData
        fields = ('id', 'filename', 'file_path_local', 'wms_url', 'area_name', 'date_of_acquisition',
                  'resolution', 'data_source', 'base_folder', 'layer_name', 'image_uuid')


class GetFootprintsGeometrySerializer(GeoFeatureModelSerializer):
    image = CreateImageServerDataSerializer()

    class Meta:
        model = FootprintsGeometry
        geo_field = "geometry"
        fields = ["id", "geometry", "image"]


class GetReconnaissanceAIServicesSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReconnaissanceAIServices
        fields = "__all__"


class ResultImageServerDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImageServerData
        fields = ["id", "wms_url", "layer_name"]


class GetReconnaissanceAIResultsSerializer(serializers.ModelSerializer):
    image = ResultImageServerDataSerializer()

    class Meta:
        model = ReconnaissanceAIResults
        fields = ["id", "kafka_uuid", "status", "complete_ai_date", "image", "reconnaissance_ai_service",
                  "is_processing", "geojson_data", "created_at"]
