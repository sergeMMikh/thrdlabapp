# Generated by Django 4.0.4 on 2024-03-08 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='articles',
            options={'verbose_name': 'News', 'verbose_name_plural': 'News'},
        ),
        migrations.AlterField(
            model_name='articles',
            name='anons',
            field=models.CharField(default='Anons', max_length=100, verbose_name='Anons'),
        ),
    ]
