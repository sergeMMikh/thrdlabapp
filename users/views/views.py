import datetime as dt

from django.shortcuts import render

from furnace_booking.models import BookingOfEquipment, BookingOfFurnace
from ..models import Person


def home_view(request):
    template = '../templates/base.html'
    context = {}

    return render(request, template, context)


def people_list_view(request):
    template = 'users/people.html'
    people = list(Person.objects.all().order_by('first_name', 'surname'))
    people_rows = [people[i:i + 2] for i in range(0, len(people), 2)]

    context = {
        'title': 'People',
        'people_rows': people_rows,
        'side_bar_image': 'main/img/side_bar_person.png',
    }

    return render(request, template, context)


def person_detail_view(request, person_id):
    template = 'users/person_detail.html'
    person = Person.objects.get(id=person_id)
    today = dt.date.today()

    furnace_bookings = BookingOfFurnace.objects.select_related(
        'furnace',
    ).filter(
        person=person,
        date__gte=today,
    )
    equipment_bookings = BookingOfEquipment.objects.select_related(
        'equipment',
    ).filter(
        person=person,
        date__gte=today,
    )

    bookings = [
        {
            'id': booking.id,
            'date': booking.date,
            'kind': 'Furnace',
            'kind_key': 'furnace',
            'name': booking.furnace.name,
            'comments': booking.comments or '',
        }
        for booking in furnace_bookings
    ] + [
        {
            'id': booking.id,
            'date': booking.date,
            'kind': 'Equipment',
            'kind_key': 'equipment',
            'name': booking.equipment.name,
            'comments': booking.comments or '',
        }
        for booking in equipment_bookings
    ]
    bookings.sort(key=lambda booking: (booking['date'], booking['kind'], booking['name']))

    context = {
        'title': 'Person',
        'person': person,
        'side_bar_image': 'main/img/side_bar_person.png',
        'date_today': today,
        'bookings': bookings,
    }

    return render(request, template, context)
