from django.shortcuts import render

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

    context = {
        'title': 'Person',
        'person': person,
        'side_bar_image': 'main/img/side_bar_person.png',
    }

    return render(request, template, context)
