from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

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