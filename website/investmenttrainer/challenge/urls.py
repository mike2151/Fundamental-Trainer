from django.urls import include, path

from . import views

urlpatterns = [
    path('/<int:pk>/', views.ChallengeView.as_view()),
    path('/next_challenge', views.NextChallengeView.as_view())
]
