from django.test import TestCase
from django.urls import reverse
from django.core.management import call_command

from .models import Category, Order, Product
from .utils import format_money, gregorian_to_jalali


class StoreFrontTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="صوتی", slug="audio", description="هدفون و اسپیکر", icon="headphones"
        )
        cls.product = Product.objects.create(
            category=cls.category,
            name="هدفون تست",
            slug="test-headphones",
            brand="ویترین",
            description="یک هدفون برای تست",
            specs="وزن: ۲۵۰ گرم\nباتری: ۳۰ ساعت",
            price=1_000_000,
            old_price=1_250_000,
            stock=10,
            rating="4.7",
            image="img/products/headphones.svg",
            is_featured=True,
            is_new=True,
        )
        cls.other = Product.objects.create(
            category=cls.category,
            name="اسپیکر تست",
            slug="test-speaker",
            brand="ساند",
            description="یک اسپیکر برای تست",
            price=500_000,
            stock=3,
            rating="4.1",
            image="img/products/speaker.svg",
        )

    def test_home_page(self):
        response = self.client.get(reverse("store:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "هدفون تست")
        self.assertContains(response, "محصولات ویژه")

    def test_product_list_search_and_filter(self):
        response = self.client.get(reverse("store:product_list"), {"q": "اسپیکر"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "اسپیکر تست")
        self.assertNotContains(response, "هدفون تست")

        response = self.client.get(reverse("store:product_list"), {"category": "audio"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "هدفون تست")

    def test_product_detail(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "هدفون تست")
        self.assertContains(response, "وزن: ۲۵۰ گرم")

    def test_about_and_health(self):
        self.assertEqual(self.client.get(reverse("store:about")).status_code, 200)
        response = self.client.get(reverse("store:health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_add_to_cart_ajax(self):
        response = self.client.post(
            reverse("store:cart_add"),
            {"product_id": self.product.pk, "quantity": 2},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["count"], 2)
        self.assertEqual(payload["total"], 2_000_000)

    def test_cart_update_and_remove(self):
        self.client.post(
            reverse("store:cart_add"),
            {"product_id": self.product.pk, "quantity": 1},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        response = self.client.post(
            reverse("store:cart_update"),
            {"product_id": self.product.pk, "quantity": 3},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.json()["count"], 3)
        self.assertEqual(response.json()["row_quantity"], 3)

        response = self.client.post(
            reverse("store:cart_remove"),
            {"product_id": self.product.pk},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.json()["count"], 0)

    def test_checkout_creates_order_and_clears_cart(self):
        self.client.post(
            reverse("store:cart_add"),
            {"product_id": self.product.pk, "quantity": 2},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        response = self.client.post(
            reverse("store:checkout"),
            {
                "full_name": "سارا محمدی",
                "phone": "09121234567",
                "email": "sara@example.com",
                "city": "تهران",
                "address": "خیابان نمونه، پلاک ۱۲",
                "postal_code": "1234567890",
                "note": "",
            },
        )
        self.assertRedirects(response, reverse("store:order_success"))
        order = Order.objects.get()
        self.assertEqual(order.total_price, 2_000_000 + 49_000)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().quantity, 2)
        self.assertTrue(order.code.startswith("VT-"))

        response = self.client.get(reverse("store:order_success"))
        self.assertContains(response, order.code)
        self.assertEqual(self.client.get(reverse("store:cart_detail")).context["cart_count"], 0)

    def test_checkout_rejects_invalid_phone(self):
        self.client.post(
            reverse("store:cart_add"),
            {"product_id": self.product.pk, "quantity": 1},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        response = self.client.post(
            reverse("store:checkout"),
            {
                "full_name": "سارا محمدی",
                "phone": "12345",
                "city": "تهران",
                "address": "خیابان نمونه",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "شماره موبایل باید ۱۱ رقم")
        self.assertEqual(Order.objects.count(), 0)


class UtilityTests(TestCase):
    def test_persian_money_format(self):
        self.assertEqual(format_money(1_234_000), "۱٬۲۳۴٬۰۰۰")
        self.assertEqual(format_money(0), "۰")

    def test_jalali_conversion(self):
        self.assertEqual(gregorian_to_jalali(2024, 3, 20), (1403, 1, 1))
        self.assertEqual(gregorian_to_jalali(2026, 11, 22), (1405, 9, 1))


class SeedCommandTests(TestCase):
    def test_seed_is_idempotent(self):
        call_command("seed", verbosity=0)
        call_command("seed", verbosity=0)
        self.assertEqual(Category.objects.count(), 4)
        self.assertEqual(Product.objects.count(), 12)
