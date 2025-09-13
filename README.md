
# IT Help Desk Ticketing System

A Django-based ticketing system for managing IT support requests. Users can log in, create, track, and resolve IT tickets.

## Features
- User authentication (login, logout, signup).
- Create, read, update, and delete (CRUD) tickets.
- Each ticket is linked to the user who created it.
- Ticket statuses: Open, In Progress, Resolved, Closed.
- Authorization: only the ticket creator can edit or delete their tickets.
- Responsive design with Bootstrap.


## Tech Stack
- Python 3
- Django
- SQLite (development) / PostgreSQL (production)

## Project Structure

```
IT-Helpdesk-Ticketing-System/
│   manage.py
│   README.md
│
├── helpdesk/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── __pycache__/
│       ├── __init__.cpython-313.pyc
│       └── settings.cpython-313.pyc
│
├── tickets/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   └── migrations/
│       └── __init__.py
```


