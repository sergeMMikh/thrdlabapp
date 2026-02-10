from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from datetime import date
from .models import Furnace, BookingOfFurnace, Equipment, BookingOfEquipment
from .forms import FurnaceBookingForm, EquipmentBookingForm


def home_view(request):
    template = 'main/furnaces.html'

    context = {}

    furnaces = Furnace.objects.all().order_by('location', 'name')

    print(f'type(furnaces): {type(furnaces)}, len(furnaces): {len(furnaces)}')

    context = {'furnaces': furnaces}

    context = {
        'title': 'Furnaces',
        'furnaces': furnaces,
    }

    print(f"context: {context}")

    return render(request, template, context)


def equipment_list_view(request):
    template = 'main/equipments.html'

    equipments = Equipment.objects.all().order_by('location', 'name')

    context = {
        'title': 'Equipment',
        'equipments': equipments,
    }

    return render(request, template, context)


def equipment_booking_view(request):
    template = 'equipment_booking_form.html'

    if request.method == 'POST':
        form = EquipmentBookingForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                with transaction.atomic():
                    BookingOfEquipment.objects.create(
                        date=data['date'],
                        equipment=data['equipment'],
                        person=data['person'],
                        comments=data.get('comments') or None,
                    )
            except IntegrityError:
                form.add_error(None, 'This equipment is already booked for that date.')
            else:
                return redirect(f"{reverse('equipment')}?equipment={data['equipment'].name}")
    else:
        form = EquipmentBookingForm()

    context = {
        'title': 'Equipment booking',
        'form': form,
    }

    return render(request, template, context)


def furnace_booking_view(request):
    template = 'furnace_booking_form.html'

    if request.method == 'POST':
        form = FurnaceBookingForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                with transaction.atomic():
                    BookingOfFurnace.objects.create(
                        date=data['date'],
                        furnace=data['furnace'],
                        person=data['person'],
                        comments=data.get('comments') or None,
                    )
            except IntegrityError:
                form.add_error(None, 'This furnace is already booked for that date.')
            else:
                return redirect(f"{reverse('furnace')}?furnace={data['furnace'].name}")
    else:
        form = FurnaceBookingForm()

    context = {
        'title': 'Furnace booking',
        'form': form,
    }

    return render(request, template, context)


def furnace_book_list(request):
    template = 'furnace_booking_list.html'

    furnace_name = request.GET.get('furnace', 'Forno')
    furnace = Furnace.objects.filter(
        name=furnace_name)

    booking = BookingOfFurnace.objects.order_by('date').filter(
        furnace__name=furnace_name).reverse()

    book_list = []

    for book in booking:

        comments = str(book.comments)

        if comments == 'None':
            comments = ' '

        tmp_dict = {'date': book.date,
                    'user': book.person,
                    'comment': comments}

        book_list.append(tmp_dict)

    context = {'furnace': furnace[0],
               'date_today': date.today(),
               'booking_list': book_list}

    return render(request, template, context)


def equipment_book_list(request):
    template = 'equipment_booking_list.html'

    equipment_name = request.GET.get('equipment', 'Equipment')
    equipment = Equipment.objects.filter(
        name=equipment_name)

    booking = BookingOfEquipment.objects.order_by('date').filter(
        equipment__name=equipment_name).reverse()

    book_list = []

    for book in booking:

        comments = str(book.comments)

        if comments == 'None':
            comments = ' '

        tmp_dict = {'date': book.date,
                    'user': book.person,
                    'comment': comments}

        book_list.append(tmp_dict)

    context = {'equipment': equipment[0],
               'date_today': date.today(),
               'booking_list': book_list}

    return render(request, template, context)
