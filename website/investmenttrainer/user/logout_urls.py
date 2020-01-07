from django.urls import include, path, re_path
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', LogoutView.as_view())
]
