from django.urls import path
from Api.views import apiOverview,TaskListCreateView,TaskRetrieveUpdateDeleteView, ImportCsvFileView, ExportCsvFileView

urlpatterns = [
    path('',apiOverview,name='api-overview'),
    path('task',TaskListCreateView.as_view(), name='list-create'),
    path('task/<int:pk>',TaskRetrieveUpdateDeleteView.as_view(), name='read-update-delete'),
    path('csvimp',ImportCsvFileView.as_view(), name='csv-upload'),
    path('csvexp',ExportCsvFileView.as_view(), name='csv-download'),
]
   
