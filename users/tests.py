from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from furnace_booking.models import BookingOfEquipment, Equipment
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

    def test_view_shows_only_todays_equipment_bookings(self):
        response = self.client.get(reverse('today_equipment_bookings'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Microscope')
        self.assertContains(response, 'Alice Miller')
        self.assertNotContains(response, 'Pump')
        self.assertNotContains(response, 'Bob Stone')
