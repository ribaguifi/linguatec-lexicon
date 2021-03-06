from django.conf.urls import include, url
from django.urls import path
from rest_framework import routers
from . import views

# Wire up our API using automatic URL routing.
router = routers.DefaultRouter()
router.register(r'lexicons', views.LexiconViewSet)
router.register(r'words', views.WordViewSet)
router.register(r'gramcats', views.GramaticalCategoryViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    path('validator/', views.DataValidatorView.as_view(), name='validator'),
    path('validator-diatopic-variation/', views.DiatopicVariationValidatorView.as_view(), name='validator-variation'),
]
