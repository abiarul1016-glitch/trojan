from django.urls import path

from . import views

app_name = "trojan"

urlpatterns = [
    path("", views.index, name="index"),
    path("course/<int:pk>/", views.CourseView.as_view(), name="course"),
    path("teacher/<int:pk>/", views.TeacherView.as_view(), name="teacher"),
    path("directory", views.directory, name="directory"),
]
