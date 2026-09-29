import json
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator

from .models import Bus, Route, Stop, Student, TransportRegistration, BusPass, RouteAllocation
from .forms import (
    StudentRegistrationForm, StudentProfileForm,
    BusForm, RouteForm, StopForm,
    BusPassApplicationForm, RouteAllocationForm, PassReviewForm
)

# Helper Decorators
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please login as Admin to access this page.")
            return redirect('user_login')
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Access denied. Admin privileges required.")
            return redirect('student_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please login to access your student portal.")
            return redirect('user_login')
        if not hasattr(request.user, 'student_profile'):
            if request.user.is_staff or request.user.is_superuser:
                return redirect('admin_dashboard')
            messages.error(request, "No student profile associated with this account.")
            return redirect('landing_page')
        return view_func(request, *args, **kwargs)
    return wrapper


# ----------------------------------------------------
# PUBLIC / AUTH VIEWS
# ----------------------------------------------------

def landing_page(request):
    routes = Route.objects.filter(status='Active').select_related('bus').prefetch_related('stops')[:6]
    total_students = Student.objects.count()
    total_buses = Bus.objects.filter(status='Active').count()
    total_routes = Route.objects.filter(status='Active').count()
    total_stops = Stop.objects.count()

    context = {
        'routes': routes,
        'total_students': total_students,
        'total_buses': total_buses,
        'total_routes': total_routes,
        'total_stops': total_stops,
    }
    return render(request, 'transport/landing.html', context)


def student_register(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            full_name = form.cleaned_data['full_name']

            # Create User
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=full_name.split()[0],
                last_name=" ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else ""
            )

            # Create Student Profile
            student = form.save(commit=False)
            student.user = user
            student.save()

            messages.success(request, "Registration successful. Please login with your credentials.")
            return redirect('user_login')
        else:
            messages.error(request, "Registration failed. Please check the errors below.")
    else:
        form = StudentRegistrationForm()

    return render(request, 'transport/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('student_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            if user.is_staff or user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('student_dashboard')
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    return render(request, 'transport/login.html')


def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('landing_page')


# ----------------------------------------------------
# STUDENT VIEWS
# ----------------------------------------------------

@student_required
def student_dashboard(request):
    student = request.user.student_profile
    allocation = getattr(student, 'route_allocation', None)
    latest_pass = student.bus_passes.order_by('-created_at', '-id').first()
    recent_passes = student.bus_passes.order_by('-created_at')[:3]

    upcoming_pickup = None
    if allocation and allocation.stop:
        upcoming_pickup = {
            'stop': allocation.stop.stop_name,
            'time': allocation.stop.pickup_time,
            'bus': allocation.bus.bus_number,
            'driver': allocation.bus.driver_name,
            'driver_phone': allocation.bus.driver_phone,
        }

    context = {
        'student': student,
        'allocation': allocation,
        'latest_pass': latest_pass,
        'recent_passes': recent_passes,
        'upcoming_pickup': upcoming_pickup,
    }
    return render(request, 'transport/student/dashboard.html', context)


@student_required
def student_routes_list(request):
    query = request.GET.get('q', '').strip()
    routes = Route.objects.filter(status='Active').select_related('bus').prefetch_related('stops')

    if query:
        routes = routes.filter(
            Q(route_name__icontains=query) |
            Q(route_code__icontains=query) |
            Q(start_point__icontains=query) |
            Q(end_point__icontains=query)
        )

    context = {
        'routes': routes,
        'query': query,
    }
    return render(request, 'transport/student/routes_list.html', context)


@student_required
def student_route_detail(request, route_id):
    route = get_object_or_404(Route.objects.select_related('bus').prefetch_related('stops'), id=route_id)
    stops = route.stops.all().order_by('stop_order')

    context = {
        'route': route,
        'stops': stops,
    }
    return render(request, 'transport/student/route_detail.html', context)


@student_required
def apply_bus_pass(request):
    student = request.user.student_profile

    # Check existing pending or active pass
    existing_pending = BusPass.objects.filter(student=student, status='Pending').first()
    if existing_pending:
        messages.info(request, f"You already have a pending pass application ({existing_pending.pass_number}).")
        return redirect('my_bus_pass')

    if request.method == 'POST':
        form = BusPassApplicationForm(request.POST)
        if form.is_valid():
            pass_obj = form.save(commit=False)
            pass_obj.student = student

            # Generate unique pass number
            import random
            random_num = random.randint(1000, 9999)
            pass_obj.pass_number = f"PASS-{date.today().year}-{student.id:04d}-{random_num}"
            pass_obj.status = 'Pending'
            pass_obj.payment_status = 'Pending'
            pass_obj.save()

            messages.success(request, "Bus pass application submitted successfully. Please wait for admin approval.")
            return redirect('my_bus_pass')
        else:
            messages.error(request, "Failed to submit application. Please check form errors.")
    else:
        # Default dates
        initial_data = {
            'valid_from': date.today(),
            'valid_until': date.today() + timedelta(days=180)
        }
        form = BusPassApplicationForm(initial=initial_data)

    routes = Route.objects.filter(status='Active').select_related('bus')
    stops = Stop.objects.all().select_related('route')

    context = {
        'form': form,
        'routes': routes,
        'stops': stops,
    }
    return render(request, 'transport/student/apply_pass.html', context)


@student_required
def my_bus_pass(request):
    student = request.user.student_profile
    passes = student.bus_passes.select_related('route', 'stop', 'route__bus').order_by('-created_at')
    latest_pass = passes.first()

    context = {
        'student': student,
        'passes': passes,
        'latest_pass': latest_pass,
    }
    return render(request, 'transport/student/my_pass.html', context)


@student_required
def my_allocated_route(request):
    student = request.user.student_profile
    allocation = getattr(student, 'route_allocation', None)

    stops = []
    if allocation:
        stops = Stop.objects.filter(route=allocation.route).order_by('stop_order')

    context = {
        'student': student,
        'allocation': allocation,
        'stops': stops,
    }
    return render(request, 'transport/student/my_route.html', context)


@student_required
def student_profile(request):
    student = request.user.student_profile

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('student_profile')
        else:
            messages.error(request, "Could not update profile. Check validation errors.")
    else:
        form = StudentProfileForm(instance=student)

    context = {
        'student': student,
        'form': form,
    }
    return render(request, 'transport/student/profile.html', context)


# ----------------------------------------------------
# ADMIN VIEWS
# ----------------------------------------------------

@admin_required
def admin_dashboard(request):
    total_students = Student.objects.count()
    total_buses = Bus.objects.count()
    total_routes = Route.objects.count()
    total_stops = Stop.objects.count()

    pending_passes = BusPass.objects.filter(status='Pending').count()
    approved_passes = BusPass.objects.filter(status='Approved').count()
    active_allocations = RouteAllocation.objects.filter(status='Active').count()

    # Available seats total
    total_bus_capacity = Bus.objects.aggregate(total=Sum('capacity'))['total'] or 0
    available_seats = max(0, total_bus_capacity - active_allocations)

    # Chart Data 1: Students by Route
    route_stats = Route.objects.annotate(
        alloc_count=Count('routeallocation', filter=Q(routeallocation__status='Active'))
    ).values('route_code', 'route_name', 'alloc_count')

    chart_route_labels = [f"{r['route_code']}" for r in route_stats]
    chart_route_data = [r['alloc_count'] for r in route_stats]

    # Chart Data 2: Bus Capacity vs Allocated
    buses = Bus.objects.all()
    chart_bus_labels = [b.bus_number for b in buses]
    chart_bus_capacity = [b.capacity for b in buses]
    chart_bus_allocated = [b.allocated_count for b in buses]

    # Chart Data 3: Pass Status Breakdown
    pass_counts = BusPass.objects.values('status').annotate(total=Count('id'))
    status_map = {item['status']: item['total'] for item in pass_counts}
    chart_pass_labels = ['Pending', 'Approved', 'Rejected', 'Expired']
    chart_pass_data = [status_map.get(lbl, 0) for lbl in chart_pass_labels]

    # Chart Data 4: Department-wise Students
    dept_counts = Student.objects.values('department').annotate(total=Count('id')).order_by('-total')
    chart_dept_labels = [d['department'] for d in dept_counts]
    chart_dept_data = [d['total'] for d in dept_counts]

    context = {
        'total_students': total_students,
        'total_buses': total_buses,
        'total_routes': total_routes,
        'total_stops': total_stops,
        'pending_passes': pending_passes,
        'approved_passes': approved_passes,
        'active_allocations': active_allocations,
        'available_seats': available_seats,
        'total_bus_capacity': total_bus_capacity,
        'recent_passes': BusPass.objects.select_related('student', 'route').order_by('-created_at')[:5],
        'buses': buses[:5],

        # JSON serialized chart data for JS
        'chart_route_labels': json.dumps(chart_route_labels),
        'chart_route_data': json.dumps(chart_route_data),
        'chart_bus_labels': json.dumps(chart_bus_labels),
        'chart_bus_capacity': json.dumps(chart_bus_capacity),
        'chart_bus_allocated': json.dumps(chart_bus_allocated),
        'chart_pass_labels': json.dumps(chart_pass_labels),
        'chart_pass_data': json.dumps(chart_pass_data),
        'chart_dept_labels': json.dumps(chart_dept_labels),
        'chart_dept_data': json.dumps(chart_dept_data),
    }
    return render(request, 'transport/admin/dashboard.html', context)


@admin_required
def admin_student_list(request):
    search_query = request.GET.get('search', '').strip()
    department_filter = request.GET.get('department', '').strip()
    year_filter = request.GET.get('year', '').strip()
    route_filter = request.GET.get('route', '').strip()
    pass_status_filter = request.GET.get('pass_status', '').strip()

    students = Student.objects.select_related('user', 'route_allocation', 'route_allocation__route', 'route_allocation__bus').all()

    if search_query:
        students = students.filter(
            Q(student_id__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    if department_filter:
        students = students.filter(department=department_filter)

    if year_filter:
        students = students.filter(year=year_filter)

    if route_filter:
        students = students.filter(route_allocation__route_id=route_filter)

    if pass_status_filter:
        students = students.filter(bus_passes__status=pass_status_filter).distinct()

    paginator = Paginator(students.order_by('student_id'), 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    departments = Student.DEPARTMENT_CHOICES
    years = Student.YEAR_CHOICES
    routes = Route.objects.all()

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'department_filter': department_filter,
        'year_filter': year_filter,
        'route_filter': route_filter,
        'pass_status_filter': pass_status_filter,
        'departments': departments,
        'years': years,
        'routes': routes,
        'total_count': students.count(),
    }
    return render(request, 'transport/admin/students.html', context)


@admin_required
def admin_student_detail(request, student_id):
    student = get_object_or_404(Student.objects.select_related('user'), id=student_id)
    passes = student.bus_passes.select_related('route', 'stop').order_by('-created_at')
    allocation = getattr(student, 'route_allocation', None)

    context = {
        'student': student,
        'passes': passes,
        'allocation': allocation,
    }
    return render(request, 'transport/admin/student_detail.html', context)


# Bus CRUD
@admin_required
def admin_bus_list(request):
    buses = Bus.objects.prefetch_related('routes', 'routeallocation_set').all()
    context = {'buses': buses}
    return render(request, 'transport/admin/buses.html', context)


@admin_required
def admin_bus_create(request):
    if request.method == 'POST':
        form = BusForm(request.POST)
        if form.is_valid():
            bus = form.save()
            messages.success(request, f"Bus {bus.bus_number} added successfully.")
            return redirect('admin_bus_list')
        else:
            messages.error(request, "Form validation failed.")
    else:
        form = BusForm()

    return render(request, 'transport/admin/bus_form.html', {'form': form, 'title': 'Add New Bus'})


@admin_required
def admin_bus_update(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)
    if request.method == 'POST':
        form = BusForm(request.POST, instance=bus)
        if form.is_valid():
            form.save()
            messages.success(request, f"Bus {bus.bus_number} updated successfully.")
            return redirect('admin_bus_list')
        else:
            messages.error(request, "Form validation failed.")
    else:
        form = BusForm(instance=bus)

    return render(request, 'transport/admin/bus_form.html', {'form': form, 'bus': bus, 'title': f'Edit Bus {bus.bus_number}'})


@admin_required
def admin_bus_delete(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)
    if bus.routes.exists() or bus.routeallocation_set.filter(status='Active').exists():
        messages.error(request, f"Cannot delete Bus {bus.bus_number} as it has active routes or student allocations assigned to it.")
        return redirect('admin_bus_list')

    if request.method == 'POST':
        num = bus.bus_number
        bus.delete()
        messages.success(request, f"Bus {num} deleted successfully.")
        return redirect('admin_bus_list')

    return render(request, 'transport/admin/confirm_delete.html', {'object': bus, 'type': 'Bus', 'cancel_url': 'admin_bus_list'})


# Route CRUD
@admin_required
def admin_route_list(request):
    routes = Route.objects.select_related('bus').prefetch_related('stops', 'routeallocation_set').all()
    context = {'routes': routes}
    return render(request, 'transport/admin/routes.html', context)


@admin_required
def admin_route_create(request):
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save()
            messages.success(request, f"Route {route.route_code} created successfully.")
            return redirect('admin_route_list')
        else:
            messages.error(request, "Form validation failed.")
    else:
        form = RouteForm()

    return render(request, 'transport/admin/route_form.html', {'form': form, 'title': 'Add New Route'})


@admin_required
def admin_route_update(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    if request.method == 'POST':
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            messages.success(request, f"Route {route.route_code} updated successfully.")
            return redirect('admin_route_list')
        else:
            messages.error(request, "Form validation failed.")
    else:
        form = RouteForm(instance=route)

    return render(request, 'transport/admin/route_form.html', {'form': form, 'route': route, 'title': f'Edit Route {route.route_code}'})


@admin_required
def admin_route_delete(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    if route.routeallocation_set.filter(status='Active').exists():
        messages.error(request, f"Cannot delete Route {route.route_code} while students are allocated to it.")
        return redirect('admin_route_list')

    if request.method == 'POST':
        code = route.route_code
        route.delete()
        messages.success(request, f"Route {code} deleted successfully.")
        return redirect('admin_route_list')

    return render(request, 'transport/admin/confirm_delete.html', {'object': route, 'type': 'Route', 'cancel_url': 'admin_route_list'})


# Stop CRUD
@admin_required
def admin_stop_list(request):
    route_filter = request.GET.get('route', '')
    stops = Stop.objects.select_related('route').all()

    if route_filter:
        stops = stops.filter(route_id=route_filter)

    routes = Route.objects.all()
    context = {
        'stops': stops,
        'routes': routes,
        'selected_route': route_filter
    }
    return render(request, 'transport/admin/stops.html', context)


@admin_required
def admin_stop_create(request):
    if request.method == 'POST':
        form = StopForm(request.POST)
        if form.is_valid():
            stop = form.save()
            messages.success(request, f"Stop '{stop.stop_name}' added to Route {stop.route.route_code}.")
            return redirect('admin_stop_list')
        else:
            messages.error(request, "Form validation failed.")
    else:
        form = StopForm()

    return render(request, 'transport/admin/stop_form.html', {'form': form, 'title': 'Add New Bus Stop'})


@admin_required
def admin_stop_update(request, stop_id):
    stop = get_object_or_404(Stop, id=stop_id)
    if request.method == 'POST':
        form = StopForm(request.POST, instance=stop)
        if form.is_valid():
            form.save()
            messages.success(request, f"Stop '{stop.stop_name}' updated successfully.")
            return redirect('admin_stop_list')
        else:
            messages.error(request, "Form validation failed.")
    else:
        form = StopForm(instance=stop)

    return render(request, 'transport/admin/stop_form.html', {'form': form, 'stop': stop, 'title': f'Edit Stop: {stop.stop_name}'})


@admin_required
def admin_stop_delete(request, stop_id):
    stop = get_object_or_404(Stop, id=stop_id)
    if request.method == 'POST':
        name = stop.stop_name
        stop.delete()
        messages.success(request, f"Stop '{name}' deleted successfully.")
        return redirect('admin_stop_list')

    return render(request, 'transport/admin/confirm_delete.html', {'object': stop, 'type': 'Stop', 'cancel_url': 'admin_stop_list'})


# Bus Pass Applications Review
@admin_required
def admin_pass_applications(request):
    status_filter = request.GET.get('status', 'Pending')
    search_query = request.GET.get('search', '').strip()

    passes = BusPass.objects.select_related('student', 'route', 'stop', 'route__bus').all()

    if status_filter and status_filter != 'All':
        passes = passes.filter(status=status_filter)

    if search_query:
        passes = passes.filter(
            Q(pass_number__icontains=search_query) |
            Q(student__student_id__icontains=search_query) |
            Q(student__full_name__icontains=search_query)
        )

    context = {
        'passes': passes,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'transport/admin/pass_applications.html', context)


@admin_required
def admin_pass_action(request, pass_id):
    bus_pass = get_object_or_404(BusPass.objects.select_related('student', 'route', 'stop', 'route__bus'), id=pass_id)

    if request.method == 'POST':
        form = PassReviewForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            payment_status = form.cleaned_data['payment_status']
            remarks = form.cleaned_data['remarks']

            if action == 'Approve':
                # Check bus capacity
                bus = bus_pass.route.bus
                if not bus:
                    messages.error(request, f"Cannot approve application: Route {bus_pass.route.route_code} has no bus assigned.")
                    return redirect('admin_pass_applications')

                if bus.is_full:
                    # check if already allocated
                    existing_alloc = RouteAllocation.objects.filter(student=bus_pass.student, status='Active').first()
                    if not existing_alloc or existing_alloc.bus != bus:
                        messages.error(request, f"Allocation failed: Bus capacity is full for {bus.bus_number} ({bus.allocated_count}/{bus.capacity}).")
                        return redirect('admin_pass_applications')

                # Update BusPass
                bus_pass.status = 'Approved'
                bus_pass.payment_status = payment_status
                bus_pass.remarks = remarks
                bus_pass.save()

                # Create or Update Route Allocation
                alloc, created = RouteAllocation.objects.get_or_create(
                    student=bus_pass.student,
                    defaults={
                        'route': bus_pass.route,
                        'bus': bus,
                        'stop': bus_pass.stop,
                        'status': 'Active'
                    }
                )
                if not created:
                    alloc.route = bus_pass.route
                    alloc.bus = bus
                    alloc.stop = bus_pass.stop
                    alloc.status = 'Active'
                    alloc.save()

                messages.success(request, f"Pass {bus_pass.pass_number} approved and student allocated to Bus {bus.bus_number}.")

            elif action == 'Reject':
                bus_pass.status = 'Rejected'
                bus_pass.payment_status = payment_status
                bus_pass.remarks = remarks
                bus_pass.save()

                # Inactivate allocation if any
                RouteAllocation.objects.filter(student=bus_pass.student).update(status='Inactive')

                messages.info(request, f"Pass {bus_pass.pass_number} rejected.")

            return redirect('admin_pass_applications')
        else:
            messages.error(request, "Review form validation failed.")
    else:
        form = PassReviewForm(initial={'action': 'Approve', 'payment_status': bus_pass.payment_status, 'remarks': bus_pass.remarks})

    context = {
        'bus_pass': bus_pass,
        'form': form,
    }
    return render(request, 'transport/admin/pass_review.html', context)


# Route Allocation Management
@admin_required
def admin_route_allocation(request):
    search_query = request.GET.get('search', '').strip()
    route_filter = request.GET.get('route', '').strip()

    allocations = RouteAllocation.objects.select_related('student', 'route', 'bus', 'stop').all()

    if search_query:
        allocations = allocations.filter(
            Q(student__student_id__icontains=search_query) |
            Q(student__full_name__icontains=search_query) |
            Q(bus__bus_number__icontains=search_query)
        )

    if route_filter:
        allocations = allocations.filter(route_id=route_filter)

    if request.method == 'POST':
        form = RouteAllocationForm(request.POST)
        if form.is_valid():
            alloc = form.save(commit=False)
            alloc.status = 'Active'
            alloc.save()
            messages.success(request, f"Student {alloc.student.full_name} successfully allocated to Route {alloc.route.route_code}.")
            return redirect('admin_route_allocation')
        else:
            messages.error(request, "Allocation failed. Check validation errors below.")
    else:
        form = RouteAllocationForm()

    routes = Route.objects.all()
    unallocated_students = Student.objects.filter(route_allocation__isnull=True)

    context = {
        'allocations': allocations,
        'form': form,
        'routes': routes,
        'unallocated_students': unallocated_students,
        'search_query': search_query,
        'selected_route': route_filter,
    }
    return render(request, 'transport/admin/route_allocation.html', context)


@admin_required
def admin_allocation_delete(request, alloc_id):
    alloc = get_object_or_404(RouteAllocation, id=alloc_id)
    if request.method == 'POST':
        student_name = alloc.student.full_name
        alloc.delete()
        messages.success(request, f"Allocation for student {student_name} removed.")
        return redirect('admin_route_allocation')

    return render(request, 'transport/admin/confirm_delete.html', {'object': alloc, 'type': 'Route Allocation', 'cancel_url': 'admin_route_allocation'})


# Bus Capacity Monitoring
@admin_required
def admin_capacity_monitoring(request):
    buses = Bus.objects.prefetch_related('routes', 'routeallocation_set').all()
    bus_data = []

    for bus in buses:
        allocated = bus.allocated_count
        available = bus.available_seats
        percentage = bus.occupancy_percentage

        badge_class = "bg-success"
        if percentage >= 100:
            badge_class = "bg-danger"
        elif percentage >= 80:
            badge_class = "bg-warning text-dark"

        bus_data.append({
            'bus': bus,
            'allocated': allocated,
            'available': available,
            'percentage': percentage,
            'badge_class': badge_class,
            'routes': bus.routes.all()
        })

    context = {
        'bus_data': bus_data,
        'total_capacity': sum(b.capacity for b in buses),
        'total_allocated': sum(b.allocated_count for b in buses),
    }
    return render(request, 'transport/admin/capacity_monitoring.html', context)


# Admin Reports
@admin_required
def admin_reports(request):
    # Route statistics
    routes = Route.objects.annotate(
        allocated_students=Count('routeallocation', filter=Q(routeallocation__status='Active'))
    ).select_related('bus')

    # Department statistics
    department_stats = Student.objects.values('department').annotate(
        total_students=Count('id'),
        allocated=Count('route_allocation', filter=Q(route_allocation__status='Active'))
    ).order_by('-total_students')

    # Pass status breakdown
    pass_stats = BusPass.objects.values('status').annotate(count=Count('id'))

    context = {
        'routes': routes,
        'department_stats': department_stats,
        'pass_stats': pass_stats,
        'total_students': Student.objects.count(),
        'total_passes': BusPass.objects.count(),
        'total_allocations': RouteAllocation.objects.filter(status='Active').count(),
    }
    return render(request, 'transport/admin/reports.html', context)


# ----------------------------------------------------
# API ENDPOINT FOR DYNAMIC ROUTE -> STOP SELECTION
# ----------------------------------------------------

def api_route_stops(request, route_id):
    stops = Stop.objects.filter(route_id=route_id).order_by('stop_order')
    data = [
        {
            'id': stop.id,
            'stop_name': stop.stop_name,
            'location': stop.location,
            'pickup_time': stop.pickup_time.strftime('%I:%M %p') if stop.pickup_time else '',
            'drop_time': stop.drop_time.strftime('%I:%M %p') if stop.drop_time else '',
        }
        for stop in stops
    ]
    return JsonResponse({'stops': data})


# ----------------------------------------------------
# ERROR HANDLERS
# ----------------------------------------------------

def custom_404_view(request, exception=None):
    return render(request, 'transport/errors/404.html', status=404)

def custom_403_view(request, exception=None):
    return render(request, 'transport/errors/403.html', status=403)

def custom_500_view(request):
    return render(request, 'transport/errors/500.html', status=500)