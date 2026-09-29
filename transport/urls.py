from django.urls import path
from . import views

urlpatterns = [
    # Public & Auth
    path('', views.landing_page, name='landing_page'),
    path('register/', views.student_register, name='student_register'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),

    # Student Portal
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/routes/', views.student_routes_list, name='student_routes_list'),
    path('student/routes/<int:route_id>/', views.student_route_detail, name='student_route_detail'),
    path('student/apply-pass/', views.apply_bus_pass, name='apply_bus_pass'),
    path('student/my-pass/', views.my_bus_pass, name='my_bus_pass'),
    path('student/my-route/', views.my_allocated_route, name='my_allocated_route'),
    path('student/profile/', views.student_profile, name='student_profile'),

    # Admin Portal
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/students/', views.admin_student_list, name='admin_student_list'),
    path('admin-panel/students/<int:student_id>/', views.admin_student_detail, name='admin_student_detail'),

    # Bus Management
    path('admin-panel/buses/', views.admin_bus_list, name='admin_bus_list'),
    path('admin-panel/buses/add/', views.admin_bus_create, name='admin_bus_create'),
    path('admin-panel/buses/edit/<int:bus_id>/', views.admin_bus_update, name='admin_bus_update'),
    path('admin-panel/buses/delete/<int:bus_id>/', views.admin_bus_delete, name='admin_bus_delete'),

    # Route Management
    path('admin-panel/routes/', views.admin_route_list, name='admin_route_list'),
    path('admin-panel/routes/add/', views.admin_route_create, name='admin_route_create'),
    path('admin-panel/routes/edit/<int:route_id>/', views.admin_route_update, name='admin_route_update'),
    path('admin-panel/routes/delete/<int:route_id>/', views.admin_route_delete, name='admin_route_delete'),

    # Stop Management
    path('admin-panel/stops/', views.admin_stop_list, name='admin_stop_list'),
    path('admin-panel/stops/add/', views.admin_stop_create, name='admin_stop_create'),
    path('admin-panel/stops/edit/<int:stop_id>/', views.admin_stop_update, name='admin_stop_update'),
    path('admin-panel/stops/delete/<int:stop_id>/', views.admin_stop_delete, name='admin_stop_delete'),

    # Pass Applications
    path('admin-panel/pass-applications/', views.admin_pass_applications, name='admin_pass_applications'),
    path('admin-panel/pass-applications/<int:pass_id>/action/', views.admin_pass_action, name='admin_pass_action'),

    # Route Allocation
    path('admin-panel/allocations/', views.admin_route_allocation, name='admin_route_allocation'),
    path('admin-panel/allocations/delete/<int:alloc_id>/', views.admin_allocation_delete, name='admin_allocation_delete'),

    # Capacity & Reports
    path('admin-panel/capacity/', views.admin_capacity_monitoring, name='admin_capacity_monitoring'),
    path('admin-panel/reports/', views.admin_reports, name='admin_reports'),

    # API endpoints
    path('api/route-stops/<int:route_id>/', views.api_route_stops, name='api_route_stops'),
]