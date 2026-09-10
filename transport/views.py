from django.shortcuts import render, redirect, get_object_or_404
from .models import Route,Bus
from .models import Stop
from .models import RouteStop,Student,BusPass
from .forms import StudentForm, BusPassForm


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
    buses = Bus.objects.count()
    students = Student.objects.count()
    buspasses = BusPass.objects.count()
    approved_passes = BusPass.objects.filter(
        status="Approved"
    ).count()

    return render(request, "transport/dashboard.html", {
        "routes": routes,
        "buses": buses,
        "students": students,
        "buspasses": buspasses,
        "approved_passes": approved_passes
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

# Student Registration
def student_list(request):
    students = Student.objects.all()
    return render(request, "transport/student_list.html", {
        "students": students
    })


def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("student_list")
    else:
        form = StudentForm()

    return render(request, "transport/student_form.html", {
        "form": form
    })


# Bus Pass Management
def buspass_list(request):
    buspasses = BusPass.objects.all()
    return render(request, "transport/buspass_list.html", {
        "buspasses": buspasses
    })


def buspass_create(request):
    if request.method == "POST":
        form = BusPassForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("buspass_list")
    else:
        form = BusPassForm()

    return render(request, "transport/buspass_form.html", {
        "form": form
    })

# Route Allocation + Search + Filter
def route_allocation(request):

    buspasses = BusPass.objects.select_related(
        "student",
        "route"
    ).all()

    search = request.GET.get("search", "")
    route_id = request.GET.get("route", "")

    # Search by student name
    if search:
        buspasses = buspasses.filter(
            student__name__icontains=search
        )

    # Filter by route
    if route_id:
        buspasses = buspasses.filter(
            route_id=route_id
        )

    routes = Route.objects.all()

    return render(request, "transport/route_allocation.html", {
        "buspasses": buspasses,
        "routes": routes,
        "search": search,
        "selected_route": route_id
    })

# Bus Capacity Monitoring
def bus_capacity(request):

    buses = Bus.objects.select_related("route").all()

    bus_data = []

    for bus in buses:

        allocated = BusPass.objects.filter(
            route=bus.route,
            status="Approved"
        ).count()

        available = bus.capacity - allocated

        bus_data.append({
            "bus": bus,
            "allocated": allocated,
            "available": available
        })

    return render(request, "transport/bus_capacity.html", {
        "bus_data": bus_data
    })