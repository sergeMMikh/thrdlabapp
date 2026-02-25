from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from datetime import date, timedelta
from urllib.parse import urlencode
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
        'side_bar_image': 'main/img/side_bar_img.png',
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
            action = request.POST.get('action', 'book')
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
                if action == 'book_and_next':
                    query = urlencode({
                        'person': data['person'].pk,
                        'equipment': data['equipment'].pk,
                        'date': (data['date'] + timedelta(days=1)).isoformat(),
                        'comments': data.get('comments') or '',
                    })
                    return redirect(f"{reverse('equipment_booking')}?{query}")
                equipment_query = urlencode({'equipment': data['equipment'].name})
                return redirect(f"{reverse('equipment')}?{equipment_query}")
    else:
        initial = {}
        person_id = request.GET.get('person')
        equipment_id = request.GET.get('equipment')
        if person_id:
            initial['person'] = person_id
        if equipment_id:
            initial['equipment'] = equipment_id
        if request.GET.get('date'):
            initial['date'] = request.GET['date']
        if 'comments' in request.GET:
            initial['comments'] = request.GET.get('comments', '')
        form = EquipmentBookingForm(initial=initial or None)

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
            action = request.POST.get('action', 'book')
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
                if action == 'book_and_next':
                    query = urlencode({
                        'person': data['person'].pk,
                        'furnace': data['furnace'].pk,
                        'date': (data['date'] + timedelta(days=1)).isoformat(),
                        'comments': data.get('comments') or '',
                    })
                    return redirect(f"{reverse('furnace_booking')}?{query}")
                furnace_query = urlencode({'furnace': data['furnace'].name})
                return redirect(f"{reverse('furnace')}?{furnace_query}")
    else:
        initial = {}
        person_id = request.GET.get('person')
        furnace_id = request.GET.get('furnace')
        if person_id:
            initial['person'] = person_id
        if furnace_id:
            initial['furnace'] = furnace_id
        if request.GET.get('date'):
            initial['date'] = request.GET['date']
        if 'comments' in request.GET:
            initial['comments'] = request.GET.get('comments', '')
        form = FurnaceBookingForm(initial=initial or None)

    context = {
        'title': 'Furnace booking',
        'form': form,
        'side_bar_image': 'main/img/side_bar_img.png',
    }

    return render(request, template, context)


def furnace_book_list(request):
    template = 'furnace_booking_list.html'

    furnace_name = request.GET.get('furnace', 'Forno')
    furnace = Furnace.objects.filter(name=furnace_name).first()
    if furnace is None:
        return redirect(reverse('furnaces'))

    booking = BookingOfFurnace.objects.order_by('date').filter(
        furnace__name=furnace_name).reverse()

    book_list = []

    for book in booking:

        comments = str(book.comments)

        if comments == 'None':
            comments = ' '

        tmp_dict = {'id': book.id,
                    'date': book.date,
                    'user': book.person,
                    'comment': comments}

        book_list.append(tmp_dict)

    context = {'furnace': furnace,
               'date_today': date.today(),
               'booking_list': book_list,
               'side_bar_image': 'main/img/side_bar_img.png'}

    return render(request, template, context)


def equipment_book_list(request):
    template = 'equipment_booking_list.html'

    equipment_name = request.GET.get('equipment', 'Equipment')
    equipment = Equipment.objects.filter(name=equipment_name).first()
    if equipment is None:
        return redirect(reverse('equipments'))

    booking = BookingOfEquipment.objects.order_by('date').filter(
        equipment__name=equipment_name).reverse()

    book_list = []

    for book in booking:

        comments = str(book.comments)

        if comments == 'None':
            comments = ' '

        tmp_dict = {'id': book.id,
                    'date': book.date,
                    'user': book.person,
                    'comment': comments}

        book_list.append(tmp_dict)

    context = {'equipment': equipment,
               'date_today': date.today(),
               'booking_list': book_list}

    return render(request, template, context)


def delete_furnace_booking_view(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        furnace_name = request.POST.get('furnace_name')
        next_url = request.POST.get('next')
        if booking_id:
            booking = BookingOfFurnace.objects.filter(id=booking_id).first()
            if booking and booking.date >= date.today():
                booking.delete()
        if next_url:
            return redirect(next_url)
        if furnace_name:
            furnace_query = urlencode({'furnace': furnace_name})
            return redirect(f"{reverse('furnace')}?{furnace_query}")
    return redirect(reverse('furnaces'))


def delete_equipment_booking_view(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        equipment_name = request.POST.get('equipment_name')
        next_url = request.POST.get('next')
        if booking_id:
            booking = BookingOfEquipment.objects.filter(id=booking_id).first()
            if booking and booking.date >= date.today():
                booking.delete()
        if next_url:
            return redirect(next_url)
        if equipment_name:
            return redirect(
                f"{reverse('equipment')}?{urlencode({'equipment': equipment_name})}",
            )
    return redirect(reverse('equipments'))
