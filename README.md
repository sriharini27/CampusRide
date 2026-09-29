# CampusRide – College Transport & Bus Pass Management System

**Tagline:** *"Making College Transportation Simple, Smart and Connected."*

CampusRide is a centralized full-stack Django web application designed for colleges and universities to manage bus fleets, routes, boarding stops, student transport registrations, online bus pass applications, seat capacity enforcement, and analytical dashboards.

---

## 🚀 Key Features

### 👨‍🎓 Student Portal
- **Student Registration & Authentication:** Prevent duplicate student registration using unique Student IDs and Username validation.
- **Interactive Route Explorer:** View active routes, distance, estimated travel time, bus capacities, seat availability, and ordered stop timelines.
- **Online Bus Pass Application:** Apply for semester bus passes with **dynamic AJAX route-to-stop filtering**.
- **Digital Bus Pass & Printing:** Instant access to digital bus passes with approval status badges, payment status, and a **one-click printable bus pass layout** (`window.print()`).
- **Allocated Route Overview:** View assigned bus details, driver contact numbers, and morning/evening pickup times for your boarding stop.
- **Profile Management:** View and update contact and residential details using Django ModelForms.

### 🛡️ Admin Portal
- **Dashboard & Chart.js Analytics:** 8 real-time KPI stat cards (Students, Buses, Routes, Stops, Pending Applications, Approved Passes, Active Allocations, Available Seats) + 4 Chart.js charts.
- **Bus Fleet CRUD:** Full management of buses, registration numbers, seating capacities, driver info, and status (Active, Maintenance, Inactive).
- **Route & Stop Management:** Configure route codes, start/end locations, distance, estimated time, and ordered stops sequence with pickup/drop timings.
- **Student Directory & Search/Filter:** Search students by ID, Name, Phone; filter by Department, Year, Allocated Route, and Bus Pass Status with pagination.
- **Pass Application Approval:** Review applications, verify seating capacity, approve passes, or reject with custom admin remarks.
- **Route Allocation & Capacity Guard:** Allocate students to buses while enforcing strict seating capacity constraints (prevents overbooking).
- **Bus Capacity Monitoring:** Visual breakdown of occupancy percentages and color-coded status indicators (Low, Medium, High, Full).
- **Printable System Reports:** Exportable summary reports for route utilization, department distribution, and application status statistics.

---

## 🛠️ Technology Stack

- **Backend:** Python 3, Django
- **Frontend:** HTML5, CSS3, Bootstrap 5, Bootstrap Icons, JavaScript (Vanilla JS / AJAX)
- **Database:** SQLite3
- **ORM & Security:** Django ORM, Django Authentication, Django Messages, CSRF protection, ModelForms
- **Analytics & Visualization:** Chart.js

---

## 📁 Project Structure

```
CampusRide/
│
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3
│
├── CampusRide/               # Project Configuration
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
└── transport/                # Core Application Module
    ├── migrations/
    ├── templates/
    │   └── transport/
    │       ├── base.html
    │       ├── landing.html
    │       ├── login.html
    │       ├── register.html
    │       ├── includes/
    │       │   ├── navbar.html
    │       │   ├── sidebar.html
    │       │   ├── messages.html
    │       │   └── footer.html
    │       ├── student/
    │       │   ├── dashboard.html
    │       │   ├── routes_list.html
    │       │   ├── route_detail.html
    │       │   ├── apply_pass.html
    │       │   ├── my_pass.html
    │       │   ├── my_route.html
    │       │   └── profile.html
    │       ├── admin/
    │       │   ├── dashboard.html
    │       │   ├── students.html
    │       │   ├── student_detail.html
    │       │   ├── buses.html
    │       │   ├── bus_form.html
    │       │   ├── routes.html
    │       │   ├── route_form.html
    │       │   ├── stops.html
    │       │   ├── stop_form.html
    │       │   ├── pass_applications.html
    │       │   ├── pass_review.html
    │       │   ├── route_allocation.html
    │       │   ├── capacity_monitoring.html
    │       │   ├── reports.html
    │       │   └── confirm_delete.html
    │       └── errors/
    │           ├── 404.html
    │           ├── 403.html
    │           └── 500.html
    ├── static/
    │   └── transport/
    │       ├── css/
    │       │   ├── style.css
    │       │   ├── dashboard.css
    │       │   └── print.css
    │       └── js/
    │           ├── main.js
    │           └── dashboard.js
    ├── management/
    │   └── commands/
    │       └── seed_data.py
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── models.py
    ├── urls.py
    ├── views.py
    └── tests.py
```

---

## 🔑 Demo Credentials

| Role | Username | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Full Admin Control Panel, Applications Review, Route Allocations, Fleet CRUD, Reports |
| **Student 1** | `student1` | `student123` | Student Dashboard, Apply Pass, View Digital Pass, Profile, Route View |
| **Student 2** | `student2` | `student123` | Student Portal Account |

---

## ⚡ Quick Start Guide

### 1. Create and Activate Virtual Environment
```bash
python -m venv venv
```

**Windows:**
```cmd
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Populate Demo Dataset
Seed the database with 5 buses, 5 routes, 24 stops, 25 students, applications, and allocations:
```bash
python manage.py seed_data
```

### 5. Run Development Server
```bash
python manage.py runserver
```
Open your browser and visit: `http://127.0.0.1:8000/`

---

## 🧪 Running Unit Tests

Run the complete Django test suite verifying student registration, login authentication, CRUD operations, capacity enforcement, pass approvals, and access control:
```bash
python manage.py test
```

---

## 👥 Team 12 Module Distribution

- **Member 1:** Route, Bus & Stop Management (CRUD, timetable ordering, bus capacities).
- **Member 2:** Student Registration & Bus Pass Management (Auth, online pass applications, printable passes).
- **Member 3:** Route Allocation, Search, Filtering & Dashboard (Capacity guard, Chart.js analytics, student search & multi-filtering).

---

## 📚 Learning Outcomes

1. Designed relational Django database models for transport systems using `OneToOneField` and `ForeignKey`.
2. Developed dynamic front-end forms with JavaScript AJAX for dependent dropdown filtering (Route ➔ Stops).
3. Utilized Django ORM aggregation (`Count`, `Sum`, `Q`, `select_related`) for real-time dashboard analytics.
4. Enforced role-based access control (RBAC) and security for student vs administrator views.
5. Built responsive UI layout with Bootstrap 5, Chart.js, and CSS `@media print` rules.
