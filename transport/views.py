from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count

from .models import Route, Bus, Stop, RouteStop, Student, BusPass
from .forms import StudentRegistrationForm, BusPassApplicationForm


def route_stop_list(request):
    route_stops = RouteStop.objects.all()

    return render(request, "transport/route_stop_list.html", {
        "route_stops": route_stops
    })


def route_stop_create(request):

    if request.method == "POST":
        RouteStop.objects.create(
            route_id=request.POST["route"],
            stop_id=request.POST["stop"],
            stop_order=request.POST["stop_order"]
        )

        return redirect("route_stop_list")

    routes = Route.objects.all()
    stops = Stop.objects.all()

    return render(request, "transport/route_stop_form.html", {
        "routes": routes,
        "stops": stops
    })

def stop_list(request):
    stops = Stop.objects.all()

    return render(request, "transport/stop_list.html", {
        "stops": stops
    })


def stop_create(request):

    if request.method == "POST":
        Stop.objects.create(
            stop_name=request.POST["stop_name"],
            location=request.POST["location"]
        )

        return redirect("stop_list")

    return render(request, "transport/stop_form.html")


def stop_update(request, id):

    stop = get_object_or_404(Stop, id=id)

    if request.method == "POST":
        stop.stop_name = request.POST["stop_name"]
        stop.location = request.POST["location"]

        stop.save()

        return redirect("stop_list")

    return render(request, "transport/stop_form.html", {
        "stop": stop
    })


def stop_delete(request, id):

    stop = get_object_or_404(Stop, id=id)
    stop.delete()

    return redirect("stop_list")

def bus_list(request):
    buses = Bus.objects.all()

    return render(request, "transport/bus_list.html", {
        "buses": buses
    })


def bus_create(request):

    if request.method == "POST":
        Bus.objects.create(
            bus_number=request.POST["bus_number"],
            registration_number=request.POST["registration_number"],
            capacity=request.POST["capacity"],
            route_id=request.POST["route"]
        )

        return redirect("bus_list")

    routes = Route.objects.all()

    return render(request, "transport/bus_form.html", {
        "routes": routes
    })


def bus_update(request, id):

    bus = get_object_or_404(Bus, id=id)

    if request.method == "POST":
        bus.bus_number = request.POST["bus_number"]
        bus.registration_number = request.POST["registration_number"]
        bus.capacity = request.POST["capacity"]
        bus.route_id = request.POST["route"]

        bus.save()

        return redirect("bus_list")

    routes = Route.objects.all()

    return render(request, "transport/bus_form.html", {
        "bus": bus,
        "routes": routes
    })


def bus_delete(request, id):

    bus = get_object_or_404(Bus, id=id)
    bus.delete()

    return redirect("bus_list")

def dashboard(request):
    routes = Route.objects.count()

    return render(request, "transport/dashboard.html", {
        "routes": routes
    })


def route_list(request):
    routes = Route.objects.all()

    return render(request, "transport/route_list.html", {
        "routes": routes
    })


def route_create(request):

    if request.method == "POST":
        Route.objects.create(
            route_number=request.POST["route_number"],
            route_name=request.POST["route_name"],
            start_point=request.POST["start_point"],
            end_point=request.POST["end_point"]
        )

        return redirect("route_list")

    return render(request, "transport/route_form.html")


def route_update(request, id):

    route = get_object_or_404(Route, id=id)

    if request.method == "POST":
        route.route_number = request.POST["route_number"]
        route.route_name = request.POST["route_name"]
        route.start_point = request.POST["start_point"]
        route.end_point = request.POST["end_point"]

        route.save()

        return redirect("route_list")

    return render(request, "transport/route_form.html", {
        "route": route
    })


def route_delete(request, id):

    route = get_object_or_404(Route, id=id)
    route.delete()

    return redirect("route_list")
    
def student_register(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
            )

            student = form.save(commit=False)
            student.user = user
            student.save()

            messages.success(request, "Registration successful!")
            return redirect("student_login")

    else:
        form = StudentRegistrationForm()

    return render(request, "transport/student_register.html", {"form": form})

def student_login(request):
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            try:
                Student.objects.get(user=user)

                login(request, user)

                return redirect("student_dashboard")

            except Student.DoesNotExist:
                messages.error(
                    request,
                    "This account is not registered as a student."
                )

        else:
            messages.error(
                request,
                "Invalid username or password."
            )

    return render(
        request,
        "transport/student_login.html"
    )

def student_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("student_login")

    student = get_object_or_404(
        Student,
        user=request.user
    )

    try:
        bus_pass = BusPass.objects.get(student=student)
    except BusPass.DoesNotExist:
        bus_pass = None

    return render(
        request,
        "transport/student_dashboard.html",
        {
            "student": student,
            "bus_pass": bus_pass,
        }
    )

def apply_bus_pass(request):
    if not request.user.is_authenticated:
        return redirect("student_login")

    student = get_object_or_404(
        Student,
        user=request.user
    )

    # Check if student already has a bus pass
    if BusPass.objects.filter(student=student).exists():
        messages.warning(
            request,
            "You have already applied for a bus pass."
        )
        return redirect("student_dashboard")

    if request.method == "POST":

        form = BusPassApplicationForm(request.POST)

        if form.is_valid():

            bus_pass = form.save(commit=False)

            bus_pass.student = student
            bus_pass.status = "Pending"

            bus_pass.save()

            messages.success(
                request,
                "Bus pass application submitted successfully!"
            )

            return redirect("student_dashboard")

    else:
        form = BusPassApplicationForm()

    return render(
        request,
        "transport/bus_pass_apply.html",
        {
            "form": form
        }
    )

def student_logout(request):
    logout(request)
    return redirect("student_login")

def admin_required(user):
    return user.is_authenticated and user.is_staff

@login_required(login_url="student_login")
@user_passes_test(admin_required)
def route_allocation(request):

    routes = Route.objects.all().order_by("route_number")

    students = Student.objects.select_related(
        "user",
        "route"
    ).all().order_by("student_id")

    search = request.GET.get("search", "").strip()
    route_id = request.GET.get("route", "")

    # -----------------------------
    # SEARCH STUDENTS
    # -----------------------------
    if search:
        students = students.filter(
            student_id__icontains=search
        ) | students.filter(
            user__first_name__icontains=search
        ) | students.filter(
            user__last_name__icontains=search
        )

    # -----------------------------
    # FILTER BY ROUTE
    # -----------------------------
    if route_id:
        students = students.filter(route_id=route_id)

    # -----------------------------
    # ROUTE ALLOCATION
    # -----------------------------
    if request.method == "POST":

        student_id = request.POST.get("student_id")
        selected_route_id = request.POST.get("route_id")

        student = get_object_or_404(
            Student,
            id=student_id
        )

        # Remove route allocation
        if not selected_route_id:

            student.route = None
            student.save()

            messages.success(
                request,
                f"{student.student_id} route allocation removed."
            )

            return redirect("route_allocation")

        # Get selected route
        route = get_object_or_404(
            Route,
            id=selected_route_id
        )

        # -----------------------------
        # CHECK BUS
        # -----------------------------
        bus = Bus.objects.filter(
            route=route
        ).first()

        if not bus:

            messages.error(
                request,
                f"No bus is assigned to {route.route_number}."
            )

            return redirect("route_allocation")

        # -----------------------------
        # CHECK BUS PASS
        # -----------------------------
        try:

            bus_pass = BusPass.objects.get(
                student=student
            )

            if bus_pass.status != "Approved":

                messages.error(
                    request,
                    f"{student.student_id} does not have an approved bus pass."
                )

                return redirect("route_allocation")

        except BusPass.DoesNotExist:

            messages.error(
                request,
                f"{student.student_id} has not applied for a bus pass."
            )

            return redirect("route_allocation")

        # -----------------------------
        # CHECK IF ALREADY ON SAME ROUTE
        # -----------------------------
        if student.route_id == route.id:

            messages.info(
                request,
                f"{student.student_id} is already allocated to {route.route_number}."
            )

            return redirect("route_allocation")

        # -----------------------------
        # CHECK BUS CAPACITY
        # -----------------------------
        current_passengers = Student.objects.filter(
            route=route
        ).count()

        if current_passengers >= bus.capacity:

            messages.error(
                request,
                f"Bus {bus.bus_number} is full. "
                f"Capacity: {bus.capacity}."
            )

            return redirect("route_allocation")

        # -----------------------------
        # ALLOCATE STUDENT
        # -----------------------------
        student.route = route
        student.save()

        available_seats = bus.capacity - (
            current_passengers + 1
        )

        messages.success(
            request,
            f"{student.student_id} allocated to "
            f"{route.route_number}. "
            f"{available_seats} seat(s) remaining."
        )

        return redirect("route_allocation")

    return render(
        request,
        "transport/route_allocation.html",
        {
            "students": students,
            "routes": routes,
            "search": search,
            "selected_route": route_id,
        }
    )

@login_required(login_url="student_login")
@user_passes_test(admin_required)
def transport_dashboard(request):

    routes = Route.objects.all().order_by("route_number")

    buses = Bus.objects.select_related(
        "route"
    ).all()

    students = Student.objects.select_related(
        "route"
    ).all()

    # --------------------------------
    # BASIC STATISTICS
    # --------------------------------

    total_routes = routes.count()

    total_buses = buses.count()

    total_students = students.count()

    allocated_students = students.filter(
        route__isnull=False
    ).count()

    unallocated_students = students.filter(
        route__isnull=True
    ).count()

    # --------------------------------
    # TOTAL BUS CAPACITY
    # --------------------------------

    total_capacity = sum(
        bus.capacity for bus in buses
    )

    available_seats = max(
        total_capacity - allocated_students,
        0
    )

    # --------------------------------
    # ROUTE-WISE AGGREGATION
    # --------------------------------

    route_passenger_counts = Student.objects.values(
        "route"
    ).annotate(
        passenger_count=Count("id")
    )

    passenger_map = {
        item["route"]: item["passenger_count"]
        for item in route_passenger_counts
    }

    # --------------------------------
    # ROUTE DATA
    # --------------------------------

    route_data = []

    for route in routes:

        bus = buses.filter(
            route=route
        ).first()

        passenger_count = passenger_map.get(
            route.id,
            0
        )

        if bus:

            capacity = bus.capacity

            available = max(
                capacity - passenger_count,
                0
            )

            if passenger_count >= capacity:
                status = "FULL"

            elif passenger_count >= capacity * 0.8:
                status = "NEAR FULL"

            else:
                status = "AVAILABLE"

        else:

            capacity = 0
            available = 0
            status = "NO BUS"

        route_data.append(
            {
                "route": route,
                "bus": bus,
                "passengers": passenger_count,
                "capacity": capacity,
                "available": available,
                "status": status,
            }
        )

    return render(
        request,
        "transport/transport_dashboard.html",
        {
            "total_routes": total_routes,
            "total_buses": total_buses,
            "total_students": total_students,
            "allocated_students": allocated_students,
            "unallocated_students": unallocated_students,
            "total_capacity": total_capacity,
            "available_seats": available_seats,
            "route_data": route_data,
        }
    )