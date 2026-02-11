from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='furnaces'),
    path('furnace-booking/', views.furnace_booking_view, name='furnace_booking'),
    path('furnace-booking/delete/', views.delete_furnace_booking_view, name='delete_furnace_booking'),
    path('equipments/', views.equipment_list_view, name='equipments'),
    path('equipment-booking/', views.equipment_booking_view, name='equipment_booking'),
    path('equipment-booking/delete/', views.delete_equipment_booking_view, name='delete_equipment_booking'),
    path('furnace', views.furnace_book_list, name='furnace'),
    path('equipment', views.equipment_book_list, name='equipment'),
]
