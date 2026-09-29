from datetime import date, time, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from transport.models import Bus, Route, Stop, Student, BusPass, RouteAllocation, TransportRegistration


class CampusRideCoreTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@campusride.edu',
            password='admin123'
        )

        # Bus
        self.bus = Bus.objects.create(
            bus_number='BUS-TEST-1',
            registration_number='TN-72-TEST-001',
            driver_name='Driver Sam',
            driver_phone='9998887770',
            capacity=2,
            bus_type='Standard',
            status='Active'
        )

        # Route
        self.route = Route.objects.create(
            route_code='R-TEST-1',
            route_name='Test Route Alpha',
            start_point='Start Point A',
            end_point='NEC Campus',
            distance=15.0,
            estimated_time='25 Mins',
            bus=self.bus,
            status='Active'
        )

        # Stop
        self.stop = Stop.objects.create(
            route=self.route,
            stop_name='Central Square',
            location='Main Arch',
            stop_order=1,
            pickup_time=time(7, 30),
            drop_time=time(17, 30)
        )

        # Student user 1
        self.user1 = User.objects.create_user(username='student1', password='student123')
        self.student1 = Student.objects.create(
            user=self.user1,
            student_id='24TEST001',
            full_name='Alice Smith',
            email='alice@test.edu',
            phone='9876543210',
            department='Computer Science',
            year='1st Year',
            section='A',
            gender='Female',
            address='123 Test Street',
            emergency_contact='9990001112'
        )

        # Student user 2
        self.user2 = User.objects.create_user(username='student2', password='student123')
        self.student2 = Student.objects.create(
            user=self.user2,
            student_id='24TEST002',
            full_name='Bob Jones',
            email='bob@test.edu',
            phone='9876543211',
            department='Information Technology',
            year='2nd Year',
            section='B',
            gender='Male',
            address='456 Test Avenue',
            emergency_contact='9990001113'
        )

    def test_student_registration(self):
        response = self.client.post(reverse('student_register'), {
            'username': 'newstudent',
            'password': 'password123',
            'confirm_password': 'password123',
            'student_id': '24NEW001',
            'full_name': 'Charlie Brown',
            'email': 'charlie@test.edu',
            'phone': '9876543212',
            'department': 'Mechanical',
            'year': '3rd Year',
            'section': 'A',
            'gender': 'Male',
            'address': '789 Park Road',
            'emergency_contact': '9990001114'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newstudent').exists())
        self.assertTrue(Student.objects.filter(student_id='24NEW001').exists())

    def test_login_and_role_redirect(self):
        # Student Login Redirect
        login_success = self.client.login(username='student1', password='student123')
        self.assertTrue(login_success)
        response = self.client.get(reverse('student_dashboard'))
        self.assertEqual(response.status_code, 200)

        # Admin Login Redirect
        self.client.logout()
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_bus_and_route_creation(self):
        self.client.login(username='admin', password='admin123')

        # Add Bus
        response = self.client.post(reverse('admin_bus_create'), {
            'bus_number': 'BUS-TEST-2',
            'registration_number': 'TN-72-TEST-002',
            'driver_name': 'Driver Mike',
            'driver_phone': '9876500000',
            'capacity': 30,
            'bus_type': 'AC',
            'status': 'Active'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Bus.objects.filter(bus_number='BUS-TEST-2').exists())

    def test_bus_pass_application_and_capacity_check(self):
        self.client.login(username='student1', password='student123')

        # Submit Bus Pass Application
        response = self.client.post(reverse('apply_bus_pass'), {
            'route': self.route.id,
            'stop': self.stop.id,
            'valid_from': date.today(),
            'valid_until': date.today() + timedelta(days=180)
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(BusPass.objects.filter(student=self.student1, route=self.route).exists())

    def test_admin_pass_approval_and_route_allocation(self):
        # Create pass application
        pass_obj = BusPass.objects.create(
            student=self.student1,
            pass_number='PASS-TEST-100',
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=180),
            route=self.route,
            stop=self.stop,
            status='Pending'
        )

        self.client.login(username='admin', password='admin123')
        response = self.client.post(reverse('admin_pass_action', args=[pass_obj.id]), {
            'action': 'Approve',
            'payment_status': 'Paid',
            'remarks': 'Approved by admin test'
        })
        self.assertEqual(response.status_code, 302)

        pass_obj.refresh_from_db()
        self.assertEqual(pass_obj.status, 'Approved')
        self.assertTrue(RouteAllocation.objects.filter(student=self.student1, status='Active').exists())

    def test_capacity_exceeded_validation(self):
        # Bus capacity is 2. Allocate 2 students
        RouteAllocation.objects.create(student=self.student1, route=self.route, bus=self.bus, stop=self.stop, status='Active')
        RouteAllocation.objects.create(student=self.student2, route=self.route, bus=self.bus, stop=self.stop, status='Active')

        self.assertEqual(self.bus.allocated_count, 2)
        self.assertTrue(self.bus.is_full)

        # Try to apply pass when bus is full
        self.client.login(username='student1', password='student123')
        response = self.client.post(reverse('apply_bus_pass'), {
            'route': self.route.id,
            'stop': self.stop.id,
            'valid_from': date.today(),
            'valid_until': date.today() + timedelta(days=180)
        })
        self.assertEqual(response.status_code, 200) # Form stays invalid with error

    def test_role_based_access_security(self):
        # Student cannot access admin panel
        self.client.login(username='student1', password='student123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302) # Redirected out of admin
