# 🚀 استقرار ویترین روی سرور

فارسی · [English](DEPLOY.md)

دو مسیر پشتیبانی می‌شود: **VPS با Docker Compose** (کنترل کامل و ارزان‌ترین) یا
**سرویس PaaS** که خودش Dockerfile را build می‌کند.

---

## روش اول — VPS با Docker و nginx (پیشنهادی)

فرض: اوبونتو ۲۲.۰۴ یا ۲۴.۰۴ و دامنه‌ای که رکورد `A` آن به IP سرور اشاره می‌کند.

### ۱. نصب داکر

```bash
sudo apt update && sudo apt install -y ca-certificates curl git
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER" && newgrp docker
```

### ۲. کلون و تنظیمات

```bash
sudo mkdir -p /srv/vitrin && sudo chown "$USER":"$USER" /srv/vitrin
git clone https://github.com/ms-sec-dev/vitrin-shop.git /srv/vitrin
cd /srv/vitrin
cp .env.example .env
```

فایل `.env` را ویرایش کنید:

```dotenv
DEBUG=0
SECRET_KEY=<خروجی: python3 -c "import secrets;print(secrets.token_urlsafe(50))">
ALLOWED_HOSTS=shop.example.com
CSRF_TRUSTED_ORIGINS=https://shop.example.com
DEMO_ADMIN_PASSWORD=<یک رمز قوی>
```

اجرا:

```bash
docker compose up -d --build
curl -fsS http://127.0.0.1:8000/health/ && echo OK
```

### ۳. پروکسی معکوس nginx

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

### ۴. HTTPS با Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d shop.example.com
```

Certbot بلوک nginx را برای TLS بازنویسی می‌کند و تایمر تمدید خودکار نصب می‌کند.

### ۵. فایروال

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

پورت `8000` فقط از طریق پروکسی در دسترس است؛ آن را مستقیم روی اینترنت باز نکنید.

---

## روش دوم — PaaS (Render / Railway / Fly.io)

پروژه Dockerfile آمادهٔ پروداکشن دارد، پس تقریباً همه‌جا بدون تغییر کار می‌کند:

1. یک **Web Service** جدید از ریپوی `ms-sec-dev/vitrin-shop` بسازید.
2. Runtime: **Docker** و پورت: `8000`.
3. متغیرهای محیطی:

```dotenv
DEBUG=0
SECRET_KEY=<رشتهٔ تصادفی ۵۰+ کاراکتری>
ALLOWED_HOSTS=<دامنهٔ اپ>
CSRF_TRUSTED_ORIGINS=https://<دامنهٔ اپ>
DEMO_ADMIN_PASSWORD=<رمز قوی>
```

4. یک دیسک پایدار روی `/app/data` وصل کنید تا SQLite بین دیپلوی‌ها باقی بماند.
5. دیپلوی کنید و `https://<دامنهٔ اپ>/health/` را باز کنید.

> بدون دیسک پایدار، کاتالوگ در هر دیپلوی دوباره seed می‌شود و سفارش‌ها از بین می‌روند.

---

## به‌روزرسانی نسخهٔ در حال اجرا

```bash
cd /srv/vitrin
git pull
docker compose up -d --build
docker compose ps
docker compose logs --tail=50
```

مایگریشن‌ها به‌صورت خودکار در `entrypoint.sh` پیش از اجرای gunicorn انجام می‌شوند.

---

## بکاپ

دیتابیس داخل volume با نام `vitrin_data` است:

```bash
docker compose exec web python -c "import shutil; shutil.copy('/app/data/db.sqlite3','/app/data/backup.sqlite3')"
docker compose cp web:/app/data/backup.sqlite3 ./backup-$(date +%F).sqlite3
```

برای بازگردانی، فایل را به `/app/data/db.sqlite3` برگردانید و کانتینر را ری‌استارت کنید.

---

## چک‌لیست پروداکشن

- [ ] `DEBUG=0` و `SECRET_KEY` قوی
- [ ] `ALLOWED_HOSTS` و `CSRF_TRUSTED_ORIGINS` روی دامنهٔ واقعی
- [ ] تغییر رمز ادمین نمونه (یا `SEED_DEMO_DATA=0`)
- [ ] فعال بودن HTTPS و ریدایرکت HTTP
- [ ] بکاپ زمان‌بندی‌شدهٔ دیتابیس
- [ ] برای ترافیک واقعی: مهاجرت از SQLite به PostgreSQL
