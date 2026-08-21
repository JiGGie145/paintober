from django.urls import path

from .views import JobCreateView, JobDetailView, JobDownloadView, JobListView, JobRenameView

urlpatterns = [
    path("", JobListView.as_view(), name="job-list"),
    path("create/", JobCreateView.as_view(), name="job-create"),
    path("<uuid:job_id>/", JobDetailView.as_view(), name="job-detail"),
    path("<uuid:job_id>/rename/", JobRenameView.as_view(), name="job-rename"),
    path("<uuid:job_id>/download/<str:file_key>/", JobDownloadView.as_view(), name="job-download"),
]
