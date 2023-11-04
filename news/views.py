from django.shortcuts import render
from .models import Articles


def news_home(request):
    news = Articles.objects.order_by('-date')[:5]
    content = {
        'title': 'News',
        'news': news,
    }
    return render(request, 'news/news_home.html', content)
