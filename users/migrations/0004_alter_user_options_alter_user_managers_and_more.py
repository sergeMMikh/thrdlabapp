# Generated by Django 4.0.4 on 2024-03-18 17:39

import django.contrib.auth.validators
from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_managers_remove_user_telephone_number_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('email',), 'verbose_name': 'User', 'verbose_name_plural': 'List of users'},
        ),
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', users.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='email_is_verified',
            field=models.BooleanField(default=False, help_text='Designates whether this user email is verified.', verbose_name='verified'),
        ),
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(default='unlnown', error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer.\n             Letters, digits and @/./+/-/_ only.', max_length=150, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username'),
        ),
    ]