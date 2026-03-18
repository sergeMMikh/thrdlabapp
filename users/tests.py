from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from furnace_booking.models import BookingOfEquipment, BookingOfFurnace, Equipment, Furnace
from users.models import Person


class TodayEquipmentBookingsViewTests(TestCase):
    def setUp(self):
        self.person_today = Person.objects.create(
            first_name='Alice',
            surname='Miller',
            email='alice@example.com',
            telephone_number='+351111111111',
        )
        self.person_tomorrow = Person.objects.create(
            first_name='Bob',
            surname='Stone',
        )
        self.equipment = Equipment.objects.create(
            name='Microscope',
            location='Lab 1',
        )
        self.furnace = Furnace.objects.create(
            name='Tube Furnace',
            location='Lab 3',
            serviceable=True,
            max_temperature=1200,
            min_temperature=100,
            is_clean=True,
        )
        self.today = timezone.localdate()

        BookingOfEquipment.objects.create(
            date=self.today,
            equipment=self.equipment,
            person=self.person_today,
            comments='Urgent sample',
        )
        BookingOfEquipment.objects.create(
            date=self.today + timedelta(days=1),
            equipment=Equipment.objects.create(name='Pump', location='Lab 2'),
            person=self.person_tomorrow,
        )
        BookingOfFurnace.objects.create(
            date=self.today,
            furnace=self.furnace,
            person=self.person_today,
        )
        BookingOfFurnace.objects.create(
            date=self.today + timedelta(days=1),
            furnace=Furnace.objects.create(
                name='Box Furnace',
                location='Lab 4',
                serviceable=True,
                max_temperature=1000,
                min_temperature=50,
                is_clean=False,
            ),
            person=self.person_tomorrow,
        )

    def test_view_shows_only_todays_bookings_for_equipment_and_furnaces(self):
        response = self.client.get(reverse('today_equipment_bookings'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Microscope')
        self.assertContains(response, 'Tube Furnace')
        self.assertContains(response, 'Equipment')
        self.assertContains(response, 'Furnace')
        self.assertContains(response, 'Alice Miller')
        self.assertNotContains(response, 'Pump')
        self.assertNotContains(response, 'Box Furnace')
        self.assertNotContains(response, 'Bob Stone')
