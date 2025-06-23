

## Tech Stack

- **Django & Django REST Framework**: Backend API framework
- **GeoDjango & PostGIS**: Geospatial data handling
- **Mosquitto**: MQTT broker for real-time communication
- **PostgreSQL**: Database with PostGIS extension
- **Docker & Docker Compose**: Containerization and orchestration
- **JWT Authentication**: Secure API access

---

## Getting Started

### Prerequisites

- Docker

---

### Setup Instructions

1. **Clone the Repository**

```bash
git clone https://github.com/HebaDwairi/sager-backend-task.git
cd sager-backend-task
```

2. **Create a `.env` File**

In the root directory:

```env
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=drones_db
DJANGO_SECRET_KEY=your_secret_key_here
DEBUG=True
```

3. **Start the Project**

```bash
docker compose up --build -d
```
4.  **Apply Database Migrations**


```bash
docker compose exec web python manage.py migrate
```


5. **Create a Superuser (for Admin Access)**

```bash
docker compose exec web python manage.py createsuperuser
```

---

## Simulating Drone Data

To simulate drone telemetry via MQTT:

```bash
docker compose exec web python simulate_drone_data.py --count 3 --delay 2
```

- `--count`: number of drones to simulate
- `--delay`: seconds between telemetry messages per drone

---

## Accessing the Application

Once the Docker containers are running, you can access the various parts of the application:

* **Django Web Application:** [http://localhost:8000/](http://localhost:8000/)
* **API Root:** [http://localhost:8000/api/](http://localhost:8000/api/)
* **Swagger UI :** [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)
* **Django Admin Panel:** [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## API Documentation

The API includes the following endpoints:

- `GET /api/drones/`: List all drones (`?serial=...` or `?partial_serial=...`)
- `GET /api/drones/online/`: Drones active in the past 60 seconds
- `GET /api/drones/dangerous/`: List of dangerous drones
- `GET /api/drones/within-5km/?latitude=...&longitude=...`: Nearby drones
- `GET /api/drones/{serial}/flight-path/`: GeoJSON flight path

---

## API Auth

The API uses JWT authentication.

1. **Obtain a Token**

```http
POST /api/token/
{
  "username": "your_username",
  "password": "your_password"
}
```

2. **Use the Access Token**

Include it in the `Authorization` header:

```http
Authorization: Bearer <access_token>
```


## Running Tests


```bash
docker compose exec web python manage.py test
```