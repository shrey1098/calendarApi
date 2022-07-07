from django.urls import path, include
from . import views

app_name = "api"
urlpatterns = [
    path('index/', views.index, name='index'),
    path('docs/', views.docs, name='docs'),
    path('about', views.about, name='about'),
    path('init/', views.GoogleCalendarInitView, name='register'),
    path('redirect/', views.GoogleCalendarRedirectView, name='oauth2callback'),
    
]