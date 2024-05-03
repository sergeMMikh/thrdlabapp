from django.shortcuts import render
from datetime import date
from .models import Furnace, BookingOfFurnace


def home_view(request):
    template = 'main/furnaces.html'

    context = {}

    furnaces = Furnace.objects.all().order_by('location', 'furnace_name')

    print(f'type(furnaces): {type(furnaces)}, len(furnaces): {len(furnaces)}')

    context = {'furnaces': furnaces}

    context = {
        'title': 'Furnaces',
        'furnaces': furnaces,
    }

    print(f"context: {context}")

    return render(request, template, context)


def furnace_book_list(request):
    template = '../templates/furnace_booking_list.html'

    furnace_name = request.GET.get('furnace', 'Forno')
    furnace = Furnace.objects.filter(
        furnace_name=furnace_name)

    booking = BookingOfFurnace.objects.order_by('date').filter(
        furnace__furnace_name=furnace_name).reverse()

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
