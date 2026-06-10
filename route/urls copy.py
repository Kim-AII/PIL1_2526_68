from django.urls import path
from . import views

urlpatterns = [
    path('api/inscription/', views.api_inscription, name='api_inscription'),
    path('api/connexion/', views.api_connexion, name='api_connexion'),
    path('api/utilisateurs/', views.api_utilisateurs, name='api_utilisateurs'),
]