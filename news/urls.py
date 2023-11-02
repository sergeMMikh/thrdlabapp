from django.urls import path
from . import views

urlpatterns = [
    path('', views.news_home, name='news_home'),
    # path('about', views.about, name='about'),
    # path('contacts', views.contacts, name='contacts'),
    # path('furnaces', views.furnaces, name='furnaces'),
]
