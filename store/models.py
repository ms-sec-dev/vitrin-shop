import random

from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField("نام", max_length=80)
    slug = models.SlugField("اسلاگ", max_length=80, unique=True, allow_unicode=True)
    description = models.CharField("توضیح کوتاه", max_length=160, blank=True)
    icon = models.CharField("آیکن", max_length=40, blank=True)
    order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"{reverse('store:product_list')}?category={self.slug}"


class Product(models.Model):
    category = models.ForeignKey(
        Category, verbose_name="دسته‌بندی", related_name="products", on_delete=models.PROTECT
    )
    name = models.CharField("نام محصول", max_length=140)
    slug = models.SlugField("اسلاگ", max_length=140, unique=True, allow_unicode=True)
    brand = models.CharField("برند", max_length=80, blank=True)
    description = models.TextField("توضیحات")
    specs = models.TextField(
        "مشخصات", blank=True, help_text="هر مشخصه را در یک خط بنویسید؛ مثال: وزن: ۲۵۰ گرم"
    )
    price = models.PositiveIntegerField("قیمت (تومان)")
    old_price = models.PositiveIntegerField("قیمت قبل از تخفیف (تومان)", null=True, blank=True)
    stock = models.PositiveIntegerField("موجودی", default=0)
    rating = models.DecimalField("امتیاز", max_digits=2, decimal_places=1, default=4.5)
    image = models.CharField(
        "مسیر تصویر",
        max_length=200,
        default="img/products/headphones.svg",
        help_text="مسیر نسبی داخل پوشه static؛ مثال: img/products/headphones.svg",
    )
    is_featured = models.BooleanField("ویژه", default=False)
    is_new = models.BooleanField("جدید", default=False)
    is_active = models.BooleanField("فعال", default=True)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        ordering = ["-created_at", "id"]
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        indexes = [models.Index(fields=["is_active", "category"])]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("store:product_detail", args=[self.slug])

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return round((self.old_price - self.price) * 100 / self.old_price)
        return 0

    @property
    def spec_list(self):
        return [line.strip() for line in self.specs.splitlines() if line.strip()]

    @property
    def in_stock(self):
        return self.stock > 0


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار پرداخت"),
        ("paid", "پرداخت شده"),
        ("shipped", "ارسال شده"),
        ("canceled", "لغو شده"),
    ]

    code = models.CharField("کد سفارش", max_length=12, unique=True, blank=True)
    full_name = models.CharField("نام و نام خانوادگی", max_length=120)
    phone = models.CharField("شماره موبایل", max_length=11)
    email = models.EmailField("ایمیل", blank=True)
    city = models.CharField("شهر", max_length=80)
    address = models.TextField("نشانی")
    postal_code = models.CharField("کد پستی", max_length=10, blank=True)
    note = models.TextField("یادداشت", blank=True)
    shipping_price = models.PositiveIntegerField("هزینه ارسال", default=0)
    total_price = models.PositiveIntegerField("مبلغ کل", default=0)
    status = models.CharField("وضعیت", max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"

    def __str__(self):
        return f"{self.code} — {self.full_name}"

    def save(self, *args, **kwargs):
        if not self.code:
            alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
            while True:
                code = "VT-" + "".join(random.choices(alphabet, k=6))
                if not Order.objects.filter(code=code).exists():
                    self.code = code
                    break
        super().save(*args, **kwargs)

    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, verbose_name="سفارش", related_name="items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        verbose_name="محصول",
        related_name="order_items",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    product_name = models.CharField("نام محصول", max_length=140)
    price = models.PositiveIntegerField("قیمت واحد")
    quantity = models.PositiveIntegerField("تعداد", default=1)

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity
