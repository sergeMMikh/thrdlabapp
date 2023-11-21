from django.db import models


class Articles(models.Model):
    title = models.CharField(verbose_name='Title', max_length=100, default='News')
    date = models.DateField(verbose_name='Data')
    anons = models.CharField(verbose_name='Anons', max_length=100, default='Anons')
    full_text = models.TextField(verbose_name='Article contetn')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'News'
        verbose_name_plural = 'News'
