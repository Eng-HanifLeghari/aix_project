from django.urls import path
from apps.reconnaissance.views import ImageServerDataView, FootPrintGeometryView, FilterGeometryView, \
    FilterImageServerDataView, ReconnaissanceAIAnalyser, AutoCompleteImageSearch, ReconnaissanceAIServicesView, \
    ReconnaissanceAIResultsView, ReconnaissanceAIUnprocessedResultsView

urlpatterns = [
    path("image-server-list/", FilterImageServerDataView.as_view(), name="image_server_list"),
    path("image-server-data/", ImageServerDataView.as_view(), name="image_server_data"),
    path("foot-print-geometry/", FootPrintGeometryView.as_view(), name="foot_print_geometry"),
    path("filter-foot-print-geometry/", FilterGeometryView.as_view(), name="filter-foot_print_geometry"),
    path("image-analyzer/", ReconnaissanceAIAnalyser.as_view(), name="images_analyzer"),
    path("autocomplete-image-search/", AutoCompleteImageSearch.as_view(), name="autocomplete_image_search"),
    path("reconnaissance-ai-services-list/", ReconnaissanceAIServicesView.as_view(), name="reconnaissance_ai_services_list"),
    path("reconnaissance-ai-result-list/", ReconnaissanceAIResultsView.as_view(), name="reconnaissance_ai_result_list"),
    path("reconnaissance-ai-unprocessed-results/", ReconnaissanceAIUnprocessedResultsView.as_view(), name="reconnaissance_ai_unprocessed_results"),
]
