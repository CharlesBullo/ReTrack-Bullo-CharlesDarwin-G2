# ReTrack (core): Register, Login/Logout, Dashboards, Profile

Django (templates only) + PostgreSQL/Supabase. Roles: **Admin** and **Member**.

## Setup (Windows Command Prompt)
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env          (then edit .env with your Supabase values)
python manage.py makemigrations accounts
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8080
```
Open http://127.0.0.1:8080/. Superusers are Admins automatically; new registrations are Members.
To promote a user: /admin/ > Users > the user > Profile > Role.

## Where things are
| Requirement | Location |
|---|---|
| Registration validation | `accounts/forms.py` (`RegistrationForm`) |
| Login / logout | `accounts/views.py` (`CustomLoginView`, `logout_view`) |
| Protected pages + role check | `accounts/decorators.py` (`role_required`) |
| Role dashboards | `accounts/views.py` (`admin_dashboard`, `member_dashboard`) |
| Profile view/edit (own only) | `accounts/views.py` (`profile_view`, `profile_edit`) |
