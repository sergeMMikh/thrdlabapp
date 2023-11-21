from django.shortcuts import render, redirect
from .models import Articles
from .forms import ArticlesForm


def news_home(request):
    news = Articles.objects.order_by('-date')[:5]
    content = {
        'title': 'News',
        'news': news,
    }
    return render(request, 'news/news_home.html', content)


def create_news(request):
    error = ''
    if request.method == 'POST':
        form = ArticlesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('news_home')
        else:
            error = 'The form is not correct'

    form = ArticlesForm()
    content = {
        'title': 'New news craetion.',
        'form': form,
        'error': error,
    }
    return render(request, 'news/create_news.html', content)
