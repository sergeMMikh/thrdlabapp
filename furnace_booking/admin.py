from django.contrib import admin

from furnace_booking.models import (
    Furnace,
    BookingOfFurnace,
    Equipment,
    BookingOfEquipment,
)


class BookingOfFurnaceInLine(admin.TabularInline):
    model = BookingOfFurnace
    extra = 3


class BookingOfEquipmentInLine(admin.TabularInline):
    model = BookingOfEquipment
    extra = 3


@admin.register(Furnace)
class FurnaceAdmin(admin.ModelAdmin):
    list_display = 'name', 'location', 'max_temperature', \
                   'min_temperature', 'is_clean', 'serviceable'
    fields = ['location',
              'name',
              'max_temperature',
              'min_temperature',
              'is_clean',
              'serviceable']
    inlines = [BookingOfFurnaceInLine]
    list_filter = ('location',)


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    fields = ('location', 'name')
    inlines = [BookingOfEquipmentInLine]
    list_filter = ('location',)


@admin.register(BookingOfFurnace)
class BookingOfFurnaceAdmin(admin.ModelAdmin):
    list_display = 'date', 'furnace', 'person', 'comments'
    list_filter = ('furnace',)


@admin.register(BookingOfEquipment)
class BookingOfEquipmentAdmin(admin.ModelAdmin):
    list_display = 'date', 'equipment', 'person', 'comments'
    list_filter = ('equipment',)
