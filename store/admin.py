from django.contrib import admin

from .models import Category, Order, OrderItem, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "old_price",
        "stock",
        "rating",
        "is_featured",
        "is_new",
        "is_active",
    )
    list_filter = ("category", "is_active", "is_featured", "is_new")
    list_editable = ("price", "stock", "is_featured", "is_new", "is_active")
    search_fields = ("name", "brand", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_select_related = ("category",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "price", "quantity")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("code", "full_name", "phone", "city", "total_price", "status", "created_at")
    list_filter = ("status", "created_at", "city")
    search_fields = ("code", "full_name", "phone", "email")
    readonly_fields = ("code", "created_at", "shipping_price", "total_price")
    inlines = [OrderItemInline]
    date_hierarchy = "created_at"
