from django.db import models

from users.models import User


class Furnace(models.Model):
    # furnace name in laboratory specifications
    furnace_name = models.CharField(max_length=100)

    # location in laboratory
    location = models.CharField(max_length=100,
                                verbose_name='location')

    # technical furnace conditions: is it working (Tru) or broken (False)
    serviceable = models.BooleanField(verbose_name='available to use')

    # the maximum operating temperature
    max_temperature = models.PositiveIntegerField(
        verbose_name='max. temperature')

    # the minimum operating temperature
    min_temperature = models.PositiveIntegerField(
        verbose_name='min. temperature')

    # is furnace using for clean materials:
    # free from acids, alkaline, transition or volatilizing elements
    is_clean = models.BooleanField(verbose_name='for clean materials')

    # ip = models.CharField(max_length=20, null=True, blank=True)
    # port = models.CharField(max_length=6, null=True, blank=True)

    # the current furnace user
    user = models.ManyToManyField(User,
                                  related_name='furnaces',
                                  through='BookingOfFurnace')

    def __str__(self):
        return self.furnace_name


class BookingOfFurnace(models.Model):
    date = models.DateField()
    furnace = models.ForeignKey(
        Furnace,
        on_delete=models.CASCADE,
        related_name='furnace',
    )

    person = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user',
    )

    comments = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(name='unique_booking_d_f',
                                               fields=['date',
                                                       'furnace'])]
