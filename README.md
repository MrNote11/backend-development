# HiYield

A Django-based API project with Swagger documentation.

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
.\venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## Project Structure

```
hiyield/
├── apps/                    # Application modules
│   ├── core/               # Core functionality
│   └── api/                # API endpoints
├── config/                 # Project configuration
├── static/                 # Static files
├── media/                  # User-uploaded files
├── templates/              # HTML templates
└── manage.py              # Django management script
``` 