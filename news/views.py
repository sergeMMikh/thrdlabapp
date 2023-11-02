from django.shortcuts import render


def news_home(request):
    content = {
        'title': 'News',
    }
    return render(request, 'news/news_home.html', content)
