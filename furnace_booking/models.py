from django.db import models

from users.models import User, Person


class BaseEquipment(models.Model):
    # equipment name in laboratory specifications
    name = models.CharField(max_length=100)

    # location in laboratory
    location = models.CharField(max_length=100,
                                verbose_name='location')

    # ip = models.CharField(max_length=20, null=True, blank=True)
    # port = models.CharField(max_length=6, null=True, blank=True)

    # the current equipment user
    user = models.ManyToManyField(Person,
                                  related_name='%(class)s_users',
                                  blank=True)

    class Meta:
        abstract = True


class Furnace(BaseEquipment):
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

    def __str__(self):
        return self.name


class Equipment(BaseEquipment):
    def __str__(self):
        return self.name


class BookingOfFurnace(models.Model):
    date = models.DateField()
    furnace = models.ForeignKey(
        Furnace,
        on_delete=models.CASCADE,
        related_name='furnace',
    )

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='furnace_bookings',
    )

    comments = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(name='unique_booking_d_f',
                                               fields=['date',
                                                       'furnace'])]


class BookingOfEquipment(models.Model):
    date = models.DateField()
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='equipment',
    )

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='equipment_bookings',
    )

    comments = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(name='unique_booking_d_e',
                                               fields=['date',
                                                       'equipment'])]
