from django.shortcuts import render


# from django.http import HttpResponse


def index(request):
    return render(request, 'main/index.html', {'title': 'Home'})


def about(request):
    return render(request, 'main/about.html', {'title': 'About'})

def contacts(request):
    return render(request, 'main/contacts.html', {'title': 'Contacts'})

def furnaces(request):
    return render(request, 'main/furnaces.html', {'title': 'Furnaces'})
