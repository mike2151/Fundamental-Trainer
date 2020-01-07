from django.urls import include, path

from . import views

urlpatterns = [
    path('<int:pk>/', views.ChallengeView.as_view()),
    path('<str:challenge_type>/next_challenge/', views.NextChallengeView.as_view()),
    path('out/', views.OutOfChallengesView.as_view())
]
