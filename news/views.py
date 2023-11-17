from django.shortcuts import render
from .models import Articles


def news_home(request):
    news = Articles.objects.order_by('-date')[:5]
    content = {
        'title': 'News',
        'news': news,
    }
    return render(request, 'news/news_home.html', content)

def create_news(request):
    news = Articles.objects.order_by('-date')[:5]
    content = {
        'title': 'New news craetion.',
        'news': news,
    }
    return render(request, 'news/create_news.html', content)
