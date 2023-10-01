from django.urls import re_path
from apps.camera.views import (
    CameraOperationsView,
    CameraList,
    DeleteCamera,
    StartStream,
    CameraUri,
    CamDetailView,
    UpdateCamStatus,
    CamEventsFilterView,
    SearchCameraView,
    CamAlertsFilterView,
    TestConnectionAddingCamera, UpdateCamDetail, CamEventAggregateView,
    TestConnectionAddingCamera, UpdateCamDetail, DeleteCameraMultiple, CamThreatAlertView, CamForceAlertView,
    CamAssetCountView, CamForceCountView, camLegendsCountView, camImageAlertView, CameraListWithLimit,
    CamAssetCountView, CamForceCountView, camLegendsCountView, camImageAlertView, SinglePageGraphView, ImageAlertPath,
)

urlpatterns = [
    # User management
    re_path(r"^add-camera/", CameraOperationsView.as_view(), name="add-camera-view"),
    re_path(r"^all-cameras/", CameraList.as_view(), name="all-camera-view"),
    re_path(r"^cameras-limit/", CameraListWithLimit.as_view(), name="all-camera-view-limit"),
    re_path(r"^cam-detail/", CamDetailView.as_view(), name="camera-detail-view"),
    re_path(
        r"^cam-status/", UpdateCamStatus.as_view(), name="camera-change-status-view"
    ),
    re_path(r"^delete-camera/", DeleteCamera.as_view(), name="delete-camera-view"),
    re_path(r"^multiple-delete-camera/", DeleteCameraMultiple.as_view(), name="delete-camera-multiple-view"),
    re_path("update-camera/", UpdateCamDetail.as_view(), name="update-camera-view"),
    re_path(r"^camera-uri/", CameraUri.as_view(), name="live-cam-feed-view"),
    re_path(r"^start-stream/", StartStream.as_view(), name="start_stream_view"),
    re_path(r"^cam-events-filtration/", CamEventsFilterView.as_view(), name="cam_events_filtration"),
    re_path(r"^test-camera-connection/", TestConnectionAddingCamera.as_view(), name="test_camera_connection"),
    re_path(r"^search-camera/", SearchCameraView.as_view(), name="search_camera"),
    re_path(r"^cam-alerts-filtration/", CamAlertsFilterView.as_view(), name="cam_alerts_filtration"),
    re_path(r"^cam-event-aggregation/", CamEventAggregateView.as_view(), name="came_event_aggregation"),
    re_path(r'^cam_threat_alert_aggregation/', CamThreatAlertView.as_view(), name="cam_threat_alert_aggregation"),
    re_path(r'^cam_force_alert_aggregation/', CamForceAlertView.as_view(), name="cam_force_alert_aggregation"),
    re_path(r'^cam_asset_count_aggregation/', CamAssetCountView.as_view(), name="cam_asset_count_aggregation"),
    re_path(r'^cam_force_count_aggregation/', CamForceCountView.as_view(), name="cam_force_count_aggregation"),
    re_path(r'^cam_legend_count_aggregation/', camLegendsCountView.as_view(), name="cam_legend_count_aggregation"),
    re_path(r'^cam_image_alert_aggregation/', camImageAlertView.as_view(), name="cam_image_alert_aggregation"),
    re_path(r'^image-alert-path/', ImageAlertPath.as_view(), name="image_path_alert"),
    re_path(r'^cam_single_page_graph_aggregation/', SinglePageGraphView.as_view(), name="cam_image_alert_aggregation"),
]
