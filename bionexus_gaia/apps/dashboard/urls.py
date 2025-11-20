from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_overview, name='dashboard_overview'),
]