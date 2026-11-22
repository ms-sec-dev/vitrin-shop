# 🚀 Deploying Vitrin

[فارسی](DEPLOY.fa.md) · English

Two supported paths: a **VPS with Docker Compose** (full control, cheapest) or a
**PaaS** that builds the Dockerfile for you.

---

## Option A — VPS with Docker + nginx (recommended)

Assumes Ubuntu 22.04/24.04 and a domain whose `A` record points to the server IP.

### 1. Install Docker

```bash
sudo apt update && sudo apt install -y ca-certificates curl git
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER" && newgrp docker
```

### 2. Clone and configure

```bash
sudo mkdir -p /srv/vitrin && sudo chown "$USER":"$USER" /srv/vitrin
git clone https://github.com/ms-sec-dev/vitrin-shop.git /srv/vitrin
cd /srv/vitrin
cp .env.example .env
```

Edit `.env`:

```dotenv
DEBUG=0
SECRET_KEY=<paste output of: python3 -c "import secrets;print(secrets.token_urlsafe(50))">
ALLOWED_HOSTS=shop.example.com
CSRF_TRUSTED_ORIGINS=https://shop.example.com
DEMO_ADMIN_PASSWORD=<a strong password>
```

Start it:

```bash
docker compose up -d --build
curl -fsS http://127.0.0.1:8000/health/ && echo OK
```

### 3. nginx reverse proxy

```bash
sudo apt install -y nginx
sudo tee /etc/nginx/sites-available/vitrin >/dev/null <<'CONF'
server {
    listen 80;
    server_name shop.example.com;

    client_max_body_size 10m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
CONF
sudo ln -sf /etc/nginx/sites-available/vitrin /etc/nginx/sites-enabled/vitrin
sudo nginx -t && sudo systemctl reload nginx
```

### 4. HTTPS with Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d shop.example.com
```

Certbot rewrites the nginx block for TLS and installs a renewal timer.

### 5. Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

Port `8000` stays bound to localhost-only traffic through the proxy; do not expose it publicly.

---

## Option B — PaaS (Render / Railway / Fly.io)

The repo already contains a production `Dockerfile`, so most platforms work with zero changes:

1. Create a new **Web Service** from `ms-sec-dev/vitrin-shop`.
2. Runtime: **Docker**. Exposed port: `8000`.
3. Environment variables:

```dotenv
DEBUG=0
SECRET_KEY=<random 50+ chars>
ALLOWED_HOSTS=<your-app-domain>
CSRF_TRUSTED_ORIGINS=https://<your-app-domain>
DEMO_ADMIN_PASSWORD=<strong password>
```

4. Add a persistent disk mounted at `/app/data` so SQLite survives redeploys.
5. Deploy, then open `https://<your-app-domain>/health/`.

> Without a persistent disk, the catalog re-seeds on every deploy and orders are lost.

---

## Updating a running deployment

```bash
cd /srv/vitrin
git pull
docker compose up -d --build
docker compose ps
docker compose logs --tail=50
```

Migrations run automatically in `entrypoint.sh` before gunicorn starts.

---

## Backups

The database lives in the `vitrin_data` volume:

```bash
docker compose exec web python -c "import shutil; shutil.copy('/app/data/db.sqlite3','/app/data/backup.sqlite3')"
docker compose cp web:/app/data/backup.sqlite3 ./backup-$(date +%F).sqlite3
```

Restore by copying the file back to `/app/data/db.sqlite3` and restarting the container.

---

## Production checklist

- [ ] `DEBUG=0` and a strong `SECRET_KEY`
- [ ] `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` set to the real domain
- [ ] Demo admin password changed (or `SEED_DEMO_DATA=0`)
- [ ] HTTPS enabled and HTTP redirected
- [ ] Database backups scheduled
- [ ] For real traffic: migrate from SQLite to PostgreSQL

