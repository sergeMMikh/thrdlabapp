from django.shortcuts import render


def home_view(request):
    template = '../templates/base.html'
    context = {}

    return render(request, template, context)
