# Containerized app (Stage 2)

## Run (Compose)

From this folder:

```sh
docker compose up --build
```

Open:

- <http://localhost:8000/>
- <http://localhost:8000/healthz>

Stop:

```sh
docker compose down
```

Reset everything including the Redis volume:

```sh
docker compose down -v
```

## What this demonstrates

- Images + layers: Dockerfile builds an image for the API.
- Non-root container user (safer default).
- Healthcheck (container reports healthy/unhealthy).
- Compose networking: API talks to `redis` by service name.
- Compose volumes: Redis data persists via a named volume.

## Useful inspection commands

```sh
docker image ls
docker history stage2-app:local 2>/dev/null || true
docker compose ps
docker compose logs -f app
docker compose exec app id
docker volume ls
docker volume inspect app_redis_data
```

## Evidence commands

```sh
❯ docker compose ps
NAME          IMAGE              COMMAND                  SERVICE   CREATED         STATUS                    PORTS
app-app-1     stage2-app:local   "uv run uvicorn app.…"   app       2 minutes ago   Up 41 seconds (healthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
app-redis-1   redis:7-alpine     "docker-entrypoint.s…"   redis     2 minutes ago   Up 46 seconds (healthy)   6379/tcp
❯ docker compose exec app id

uid=1000(appuser) gid=1000(appuser) groups=1000(appuser),100(users)
❯ curl -s localhost:8000/healthz

{"status":"ok"}%
docker volume ls | grep redis_data

local     app_redis_data
```

---

## Stage 2 checklist

- [x] Dockerfile builds image
- [x] Compose runs app + redis
- [x] Healthchecks work and gate startup
- [x] Networking by service name (`redis`)
- [x] Volume exists and removable via `down -v`
- [x] Run instructions + evidence commands in README
