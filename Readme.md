# Realtime Bidding App - Local Setup Guide

This guide helps developers run the **Realtime Bidding App** locally using Docker Compose.

---

## Prerequisites

Make sure your machine has the following installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Git

---

## 1. Clone the repository
```bash
git clone <REPO_URL>
cd realtime-bidding
```

---

## 2. Environment Variables

Create a `.env` file at the root of the project (optional, default values are used if not present):

```env
POSTGRES_DB=realtime
POSTGRES_USER=realtime
POSTGRES_PASSWORD=realtime
DB_HOST=db
REDIS_HOST=redis
```

---

## 3. Docker Compose Services

The project includes:

- **db** - PostgreSQL database
- **redis** - Redis server
- **web1, web2, web3** - Django/Daphne application instances
- **nginx** - Reverse proxy and load balancer

---

## 4. Running the App Locally

Start the application using Docker Compose:

```bash
docker-compose up --build
```

This command will:

1. Build Docker images
2. Start Postgres and Redis and wait until they are healthy
3. Start 3 Django/Daphne web containers
4. Start nginx as reverse proxy and load balancer

---

### Ports

- **Nginx**: accessible on `http://localhost:8000` (or the port you configured in `docker-compose.yml`)  
- **Redis**: `6379`  
- **PostgreSQL**: `5432`  

> ⚠️ If port `8000` is already used on your machine, change nginx port in `docker-compose.yml`:
```yaml
ports:
  - "8080:80"
```

---

## 5. Accessing Django Containers

Each web container exposes a port internally:

- `web1` → 8001  
- `web2` → 8002  
- `web3` → 8003  

These ports are used by nginx upstream for load balancing. You usually **don’t access them directly**.

---

## 6. Running Commands Inside Web Container

To run Django management commands:

```bash
docker-compose exec web1 python manage.py <command>
```

For example:

```bash
docker-compose exec web1 python manage.py migrate
docker-compose exec web1 python manage.py createsuperuser
```

---

## 7. Logs

To follow logs of all services:

```bash
docker-compose logs -f
```

To see logs for a specific service:

```bash
docker-compose logs -f web1
docker-compose logs -f nginx
```

---

## 8. Stopping the App

```bash
docker-compose down
```

This will stop and remove all containers but preserve database data (thanks to Docker volumes).

---

## 9. Notes for Developers

- The app uses **Daphne + Django Channels** for real-time bidding.  
- Nginx handles WebSocket connections and load balancing between web containers.  
- The entrypoint script ensures **Postgres and Redis are ready** before starting the web container.  
- Static files are collected automatically at container start.

---

## Optional: Network Diagram

A simple diagram of the network flow:

```
+----------------+       +----------------+       +----------------+
|     Web1       |       |     Web2       |       |     Web3       |
|  Daphne 8001   |       |  Daphne 8002   |       |  Daphne 8003   |
+----------------+       +----------------+       +----------------+
        \                     |                     /
         \                    |                    /
          +---------------------------------------+
          |                 Nginx                  |
          |  Reverse Proxy + Load Balancer 80      |
          +---------------------------------------+
                       |           |
                       |           |
              +----------------+ +----------------+
              |     Redis      | |    PostgreSQL  |
              |     6379       | |     5432       |
              +----------------+ +----------------+
```

