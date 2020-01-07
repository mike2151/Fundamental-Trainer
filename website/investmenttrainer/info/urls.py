from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.HomePageView.as_view()),
    path('terms_conditions/', views.TermsConditionsView.as_view()),
    path('about/', views.AboutView.as_view()),
    path('no-auth/', views.NoAuthView.as_view()),
]
