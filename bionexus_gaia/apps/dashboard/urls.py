from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_overview, name='dashboard_overview'),
    path('overview/', views.dashboard_overview, name='dashboard_overview_detail'),
]