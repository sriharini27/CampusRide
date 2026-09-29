from datetime import date, time, timedelta
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from transport.models import Bus, Route, Stop, Student, TransportRegistration, BusPass, RouteAllocation


class Command(BaseCommand):
    help = 'Seeds database with realistic CampusRide college transport demo data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Clearing existing sample data...'))

        # Remove existing allocations, passes, registrations, students, stops, routes, buses
        RouteAllocation.objects.all().delete()
        BusPass.objects.all().delete()
        TransportRegistration.objects.all().delete()
        Student.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Stop.objects.all().delete()
        Route.objects.all().delete()
        Bus.objects.all().delete()


        # Create Superuser Admin
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser('admin', 'admin@campusride.edu', 'admin123')
            admin_user.first_name = 'Transport'
            admin_user.last_name = 'Admin'
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Admin created: admin / admin123'))
        else:
            admin_user = User.objects.get(username='admin')
            admin_user.set_password('admin123')
            admin_user.save()

        # 1. Create Buses
        bus_data = [
            {'bus_number': 'BUS-101', 'registration_number': 'TN-72-AB-1001', 'driver_name': 'Ramesh Kumar', 'driver_phone': '9842100001', 'capacity': 50, 'bus_type': 'Standard', 'status': 'Active'},
            {'bus_number': 'BUS-102', 'registration_number': 'TN-72-AB-1002', 'driver_name': 'Suresh Pitchai', 'driver_phone': '9842100002', 'capacity': 45, 'bus_type': 'AC', 'status': 'Active'},
            {'bus_number': 'BUS-103', 'registration_number': 'TN-72-AB-1003', 'driver_name': 'Murugan S', 'driver_phone': '9842100003', 'capacity': 55, 'bus_type': 'Express', 'status': 'Active'},
            {'bus_number': 'BUS-104', 'registration_number': 'TN-72-AB-1004', 'driver_name': 'Manikandan R', 'driver_phone': '9842100004', 'capacity': 40, 'bus_type': 'Standard', 'status': 'Active'},
            {'bus_number': 'BUS-105', 'registration_number': 'TN-72-AB-1005', 'driver_name': 'Selvam V', 'driver_phone': '9842100005', 'capacity': 50, 'bus_type': 'AC', 'status': 'Active'},
        ]

        buses = []
        for bd in bus_data:
            bus = Bus.objects.create(**bd)
            buses.append(bus)
        self.stdout.write(self.style.SUCCESS(f'Created {len(buses)} buses.'))

        # 2. Create Routes
        routes_info = [
            {
                'route_code': 'R101',
                'route_name': 'Kovilpatti → National Engineering College',
                'start_point': 'Kovilpatti New Bus Stand',
                'end_point': 'National Engineering College Campus',
                'distance': 22.5,
                'estimated_time': '35 Mins',
                'bus': buses[0],
                'status': 'Active',
                'stops': [
                    ('Kovilpatti New Bus Stand', 'Main Entrance', 1, time(7, 15), time(17, 45)),
                    ('Inam Maniyachi', 'Highway Junction', 2, time(7, 25), time(17, 35)),
                    ('Pandavarmangalam', 'Arch Gate', 3, time(7, 35), time(17, 25)),
                    ('Kallugumalai Road', 'Cross Cut', 4, time(7, 42), time(17, 18)),
                    ('NEC Campus Gate', 'Main Admin Block', 5, time(7, 50), time(17, 10)),
                ]
            },
            {
                'route_code': 'R102',
                'route_name': 'Tirunelveli → National Engineering College',
                'start_point': 'Tirunelveli New Bus Stand',
                'end_point': 'National Engineering College Campus',
                'distance': 55.0,
                'estimated_time': '65 Mins',
                'bus': buses[1],
                'status': 'Active',
                'stops': [
                    ('Vannarpettai', 'Junction Arch', 1, time(6, 45), time(18, 15)),
                    ('Palayamkottai Bus Stand', 'Market Corner', 2, time(6, 55), time(18, 5)),
                    ('Thachanallur', 'Bypass Toll', 3, time(7, 10), time(17, 50)),
                    ('Gangaikondan', 'SIPCOT Gate', 4, time(7, 25), time(17, 35)),
                    ('Kayathar Toll', 'Toll Plaza', 5, time(7, 40), time(17, 20)),
                    ('NEC Campus Gate', 'Main Admin Block', 6, time(7, 55), time(17, 10)),
                ]
            },
            {
                'route_code': 'R103',
                'route_name': 'Sankarankovil → National Engineering College',
                'start_point': 'Sankarankovil Temple Stop',
                'end_point': 'National Engineering College Campus',
                'distance': 48.0,
                'estimated_time': '55 Mins',
                'bus': buses[2],
                'status': 'Active',
                'stops': [
                    ('Sankarankovil Temple', 'Car Street', 1, time(6, 50), time(18, 10)),
                    ('Thiruvengadam', 'Bus Stop', 2, time(7, 10), time(17, 50)),
                    ('Kalugumalai', 'Bus Stand', 3, time(7, 25), time(17, 35)),
                    ('Nalattinputhur', 'Bypass Stop', 4, time(7, 40), time(17, 20)),
                    ('NEC Campus Gate', 'Main Admin Block', 5, time(7, 50), time(17, 10)),
                ]
            },
            {
                'route_code': 'R104',
                'route_name': 'Kadambur → National Engineering College',
                'start_point': 'Kadambur Railway Station',
                'end_point': 'National Engineering College Campus',
                'distance': 18.0,
                'estimated_time': '25 Mins',
                'bus': buses[3],
                'status': 'Active',
                'stops': [
                    ('Kadambur Station', 'Main Road', 1, time(7, 25), time(17, 35)),
                    ('Kapasikadu', 'Bazaar Street', 2, time(7, 35), time(17, 25)),
                    ('Kattur', 'Junction', 3, time(7, 42), time(17, 18)),
                    ('NEC Campus Gate', 'Main Admin Block', 4, time(7, 50), time(17, 10)),
                ]
            },
            {
                'route_code': 'R105',
                'route_name': 'Kayathar → National Engineering College',
                'start_point': 'Kayathar Veerapandiya Kattabomman Statue',
                'end_point': 'National Engineering College Campus',
                'distance': 30.0,
                'estimated_time': '40 Mins',
                'bus': buses[4],
                'status': 'Active',
                'stops': [
                    ('Kayathar Kattabomman Statue', 'Main Square', 1, time(7, 10), time(17, 50)),
                    ('Aralikottai', 'Bus Stop', 2, time(7, 22), time(17, 38)),
                    ('Nalattinputhur Cross', 'Highway Stop', 3, time(7, 35), time(17, 25)),
                    ('NEC Campus Gate', 'Main Admin Block', 4, time(7, 50), time(17, 10)),
                ]
            }
        ]

        created_routes = []
        created_stops = []
        for rinfo in routes_info:
            stops_data = rinfo.pop('stops')
            route = Route.objects.create(**rinfo)
            created_routes.append(route)

            for sname, sloc, sorder, ptime, dtime in stops_data:
                stop = Stop.objects.create(
                    route=route,
                    stop_name=sname,
                    location=sloc,
                    stop_order=sorder,
                    pickup_time=ptime,
                    drop_time=dtime
                )
                created_stops.append(stop)

        self.stdout.write(self.style.SUCCESS(f'Created {len(created_routes)} routes and {len(created_stops)} stops.'))

        # 3. Create 25 Students & User Accounts
        departments = ['Computer Science', 'Information Technology', 'Electronics', 'Electrical', 'Mechanical', 'Civil', 'Artificial Intelligence']
        years = ['1st Year', '2nd Year', '3rd Year', '4th Year']
        sections = ['A', 'B', 'C']

        student_names = [
            ("Harini Sri", "Female", "Computer Science"),
            ("Arun Karthik", "Male", "Information Technology"),
            ("Divya Lakshmi", "Female", "Electronics"),
            ("Bala Murugan", "Male", "Electrical"),
            ("Kavitha R", "Female", "Computer Science"),
            ("Praveen Kumar", "Male", "Mechanical"),
            ("Subhashini S", "Female", "Artificial Intelligence"),
            ("Vigneshwaran M", "Male", "Civil"),
            ("Anitha V", "Female", "Information Technology"),
            ("Deepak Raja", "Male", "Electronics"),
            ("Gowtham S", "Male", "Computer Science"),
            ("Janani M", "Female", "Artificial Intelligence"),
            ("Karthikeyan P", "Male", "Electrical"),
            ("Lavanya K", "Female", "Computer Science"),
            ("Manojkumar T", "Male", "Mechanical"),
            ("Nivetha R", "Female", "Information Technology"),
            ("Pavithra S", "Female", "Electronics"),
            ("Rajesh Kannan", "Male", "Computer Science"),
            ("Sangeetha M", "Female", "Civil"),
            ("Tamilselvan K", "Male", "Electrical"),
            ("Uma Maheshwari", "Female", "Artificial Intelligence"),
            ("Venkatesh R", "Male", "Mechanical"),
            ("Yamuna S", "Female", "Computer Science"),
            ("Yogeshwaran B", "Male", "Information Technology"),
            ("Surya Prakash", "Male", "Electronics"),
        ]

        students = []
        for idx, (name, gender, dept) in enumerate(student_names, start=1):
            username = f"student{idx}"
            email = f"student{idx}@nec.edu.in"
            student_id = f"24{dept[:3].upper()}{idx:03d}"
            phone = f"9876543{idx:03d}"

            user = User.objects.create_user(
                username=username,
                email=email,
                password='student123',
                first_name=name.split()[0],
                last_name=name.split()[1] if len(name.split()) > 1 else ""
            )

            student = Student.objects.create(
                user=user,
                student_id=student_id,
                full_name=name,
                email=email,
                phone=phone,
                department=dept,
                year=years[idx % len(years)],
                section=sections[idx % len(sections)],
                gender=gender,
                address=f"No. {idx * 12}, College Road, Kovilpatti",
                emergency_contact=f"9443100{idx:03d}"
            )
            students.append(student)

        self.stdout.write(self.style.SUCCESS(f'Created {len(students)} student accounts.'))

        # 4. Create Applications, Passes, and Allocations
        valid_from = date.today()
        valid_until = date.today() + timedelta(days=180)

        for idx, student in enumerate(students):
            target_route = created_routes[idx % len(created_routes)]
            route_stops = list(target_route.stops.all())
            target_stop = route_stops[idx % len(route_stops)]

            # Create Transport Registration
            reg_status = 'Approved' if idx < 20 else ('Pending' if idx < 23 else 'Rejected')
            TransportRegistration.objects.create(
                student=student,
                preferred_route=target_route,
                preferred_stop=target_stop,
                status=reg_status
            )

            # Create BusPass
            pass_status = 'Approved' if idx < 18 else ('Pending' if idx < 22 else 'Rejected')
            pass_num = f"PASS-2026-{idx+1001:04d}"

            bus_pass = BusPass.objects.create(
                student=student,
                pass_number=pass_num,
                valid_from=valid_from,
                valid_until=valid_until,
                route=target_route,
                stop=target_stop,
                status=pass_status,
                payment_status='Paid' if pass_status == 'Approved' else 'Pending',
                remarks='Verified & Fee Processed' if pass_status == 'Approved' else 'Awaiting fee receipt verification'
            )

            # Create Route Allocation for Approved passes
            if pass_status == 'Approved' and target_route.bus:
                RouteAllocation.objects.create(
                    student=student,
                    route=target_route,
                    bus=target_route.bus,
                    stop=target_stop,
                    status='Active'
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded complete demo dataset!'))
        self.stdout.write(self.style.SUCCESS('================================================='))
        self.stdout.write(self.style.SUCCESS('DEMO CREDENTIALS:'))
        self.stdout.write(self.style.SUCCESS('Admin Login:   Username: admin     | Password: admin123'))
        self.stdout.write(self.style.SUCCESS('Student Login: Username: student1  | Password: student123'))
        self.stdout.write(self.style.SUCCESS('               Username: student2  | Password: student123'))
        self.stdout.write(self.style.SUCCESS('================================================='))
