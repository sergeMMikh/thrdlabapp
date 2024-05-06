from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='furnaces'),
    path('furnace', views.furnace_book_list, name='furnace'),
]
