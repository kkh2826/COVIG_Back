from django.urls import include, path
from .views import *

urlpatterns = [
    path('covidBasicinfo/', CovidBasicInfo.as_view()),
    path('covidregioninfo/', CovidRegionInfo.as_view())
]