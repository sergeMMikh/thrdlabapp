from django.db import migrations, models
import django.db.models.deletion


LABORATORY_NAMES = {
    '3.2.10': 'Electrochemistry Lab.',
    '3.2.13': 'Thermal Materials Treatment',
}


def forwards_func(apps, schema_editor):
    laboratory_model = apps.get_model('furnace_booking', 'Laboratory')
    furnace_model = apps.get_model('furnace_booking', 'Furnace')
    equipment_model = apps.get_model('furnace_booking', 'Equipment')

    locations = set(
        furnace_model.objects.exclude(location__isnull=True)
        .exclude(location__exact='')
        .values_list(
            'location',
            flat=True,
        )
    )
    locations.update(
        equipment_model.objects.exclude(location__isnull=True)
        .exclude(location__exact='')
        .values_list(
            'location',
            flat=True,
        )
    )

    laboratories = {}
    for number in locations:
        laboratory, _ = laboratory_model.objects.update_or_create(
            number=number,
            defaults={'name': LABORATORY_NAMES.get(number, f'Laboratory {number}')},
        )
        laboratories[number] = laboratory

    for furnace in furnace_model.objects.all():
        furnace.laboratory = laboratories[furnace.location]
        furnace.save(update_fields=['laboratory'])

    for equipment in equipment_model.objects.all():
        equipment.laboratory = laboratories[equipment.location]
        equipment.save(update_fields=['laboratory'])


def backwards_func(apps, schema_editor):
    furnace_model = apps.get_model('furnace_booking', 'Furnace')
    equipment_model = apps.get_model('furnace_booking', 'Equipment')

    for furnace in furnace_model.objects.select_related('laboratory').all():
        furnace.location = furnace.laboratory.number
        furnace.save(update_fields=['location'])

    for equipment in equipment_model.objects.select_related('laboratory').all():
        equipment.location = equipment.laboratory.number
        equipment.save(update_fields=['location'])


class Migration(migrations.Migration):

    dependencies = [
        ('furnace_booking', '0005_person_fk'),
    ]

    operations = [
        migrations.CreateModel(
            name='Laboratory',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID',
                )),
                ('number', models.CharField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'ordering': ['number'],
            },
        ),
        migrations.AddField(
            model_name='equipment',
            name='laboratory',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='equipments',
                to='furnace_booking.laboratory',
                verbose_name='laboratory',
            ),
        ),
        migrations.AddField(
            model_name='furnace',
            name='laboratory',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='furnaces',
                to='furnace_booking.laboratory',
                verbose_name='laboratory',
            ),
        ),
        migrations.RunPython(forwards_func, backwards_func),
        migrations.RemoveField(
            model_name='equipment',
            name='location',
        ),
        migrations.RemoveField(
            model_name='furnace',
            name='location',
        ),
        migrations.AlterField(
            model_name='equipment',
            name='laboratory',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='equipments',
                to='furnace_booking.laboratory',
                verbose_name='laboratory',
            ),
        ),
        migrations.AlterField(
            model_name='furnace',
            name='laboratory',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='furnaces',
                to='furnace_booking.laboratory',
                verbose_name='laboratory',
            ),
        ),
    ]
