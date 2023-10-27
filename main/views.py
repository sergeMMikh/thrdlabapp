from django.shortcuts import render


# from django.http import HttpResponse


def index(request):
    content = {
        'title': 'Home'
    }
    return render(request, 'main/index.html', content)


def about(request):
    content = {
        'title': 'About'
    }
    return render(request, 'main/about.html', content)

def contacts(request):
    content = {
        'title': 'Contacts'
    }
    return render(request, 'main/contacts.html', content)

def furnaces(request):
    content = {
        'title': 'Furnaces'
    }
    return render(request, 'main/furnaces.html', content)
