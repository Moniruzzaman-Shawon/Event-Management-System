# 🗓️ Event Management System

A web-based Event Management System built with **Django**, allowing users to create, manage, and view events easily. Ideal for university, organizational, or public event coordination.

---

## 🚀 Features

### ✅ 1. Data Models
- `Event`: name, description, date, time, location, and linked category.
- `Participant`: name, email, and ManyToMany relation with Event.
- `Category`: name and description.

### ✅ 2. Full CRUD Functionality
- Add, view, edit, and delete Events, Participants, and Categories.
- Proper form validation to prevent invalid submissions.

### ✅ 3. Optimized Database Queries
- Uses `select_related` to efficiently fetch event categories.
- Uses `prefetch_related` to optimize participant loading.
- Includes aggregate query: total participants across all events.
- Filter events by category and date range.

### ✅ 4. Modern UI with Tailwind CSS
- **Responsive design** for all screens (mobile, tablet, desktop).
- **Events listing** with category and participant counts.
- **Detailed event view** with associated participant list.
- **Forms** for adding/updating events, participants, and categories.
- **Navigation bar** for seamless navigation.
- **Consistent styling** using Tailwind utility classes.

### ✅ 5. Organizer Dashboard
- Stats Grid:
  - Total participants
  - Total events
  - Upcoming events
  - Past events
- Today's Events section
- Interactive stats that dynamically filter event listings

### ✅ 6. Search Functionality
- Search events by **name** or **location** using case-insensitive queries (`icontains`).


---

## 🛠️ Tech Stack

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS (Tailwind optional), Django Templates
- **Database**: PostgreSQL
- **Tools**: Django Admin, Git, Render (Deployment)

---

## 🔧 Setup Instructions

```bash
git clone https://github.com/your-username/event-management-system.git
cd event-management-system
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

````

## 🧩 PostgreSQL Setup (Local)

```
psql
CREATE DATABASE eventdb;
CREATE USER eventuser WITH PASSWORD 'yourpassword';
ALTER ROLE eventuser SET client_encoding TO 'utf8';
ALTER ROLE eventuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE eventuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE eventdb TO eventuser;

```

### Update settings.py:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'eventdb',
        'USER': 'eventuser',
        'PASSWORD': 'yourpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

```

### Run migrations:
```
python manage.py migrate

```

### 🌐 Live Demo

🚀 Check out the live deployed version of the project:  
🔗 [https://event-management-system-n5em.onrender.com/](https://event-management-system-n5em.onrender.com/)

> Hosted on **Render** for demonstration purposes. Feel free to explore event listings, pages, and features.


