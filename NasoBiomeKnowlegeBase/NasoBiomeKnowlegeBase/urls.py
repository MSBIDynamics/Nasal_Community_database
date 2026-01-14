"""
URL configuration for NasoBiomeKnowlegeBase project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path,include
from .admin_site import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('NasoBiome.urls')),
]


