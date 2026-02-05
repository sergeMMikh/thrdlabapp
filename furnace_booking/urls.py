from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='furnaces'),
    path('equipments/', views.equipment_list_view, name='equipments'),
    path('furnace', views.furnace_book_list, name='furnace'),
    path('equipment', views.equipment_book_list, name='equipment'),
]
