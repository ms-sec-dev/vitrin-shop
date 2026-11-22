from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .cart import Cart, shipping_cost
from .forms import CheckoutForm
from .models import Category, Order, OrderItem, Product
from .utils import format_money

SORT_OPTIONS = {
    "newest": ("جدیدترین", "-created_at"),
    "cheapest": ("ارزان‌ترین", "price"),
    "expensive": ("گران‌ترین", "-price"),
    "popular": ("محبوب‌ترین", "-rating"),
}


def _cart_payload(cart):
    return {
        "ok": True,
        "count": len(cart),
        "count_fa": format_money(len(cart)),
        "total": cart.total,
        "total_fa": format_money(cart.total),
        "shipping": cart.shipping,
        "shipping_fa": format_money(cart.shipping),
        "payable": cart.payable,
        "payable_fa": format_money(cart.payable),
        "is_empty": len(cart) == 0,
    }


def _wants_json(request):
    return (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or "application/json" in request.headers.get("accept", "")
    )


def home(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    context = {
        "categories": Category.objects.all(),
        "featured_products": products.filter(is_featured=True)[:8],
        "new_products": products.filter(is_new=True)[:4],
        "best_rated": products.order_by("-rating")[:4],
        "product_count": products.count(),
    }
    return render(request, "store/home.html", context)


def product_list(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    sort = request.GET.get("sort", "newest")
    if sort not in SORT_OPTIONS:
        sort = "newest"

    active_category = None
    if category_slug:
        active_category = Category.objects.filter(slug=category_slug).first()
        if active_category:
            products = products.filter(category=active_category)

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(brand__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )

    products = products.order_by(SORT_OPTIONS[sort][1])
    paginator = Paginator(products, 9)
    page = paginator.get_page(request.GET.get("page"))

    querystring = request.GET.copy()
    querystring.pop("page", None)

    context = {
        "page_obj": page,
        "products": page.object_list,
        "categories": Category.objects.all(),
        "active_category": active_category,
        "query": query,
        "sort": sort,
        "sort_options": SORT_OPTIONS,
        "total_results": paginator.count,
        "querystring": querystring.urlencode(),
    }
    return render(request, "store/product_list.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category"), slug=slug, is_active=True
    )
    related = (
        Product.objects.filter(is_active=True, category=product.category)
        .exclude(pk=product.pk)
        .select_related("category")[:4]
    )
    return render(
        request, "store/product_detail.html", {"product": product, "related_products": related}
    )


@require_POST
def cart_add(request):
    product = get_object_or_404(Product, pk=request.POST.get("product_id"), is_active=True)
    if not product.in_stock:
        message = "این محصول فعلاً موجود نیست."
        if _wants_json(request):
            return JsonResponse({"ok": False, "message": message}, status=400)
        messages.error(request, message)
        return redirect(product)

    try:
        quantity = max(1, int(request.POST.get("quantity", 1)))
    except (TypeError, ValueError):
        quantity = 1

    cart = Cart(request)
    cart.add(product, quantity=quantity)
    message = f"«{product.name}» به سبد خرید اضافه شد."

    if _wants_json(request):
        payload = _cart_payload(cart)
        payload["message"] = message
        return JsonResponse(payload)

    messages.success(request, message)
    next_url = request.POST.get("next") or ""
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(next_url)
    return redirect("store:cart_detail")


@require_POST
def cart_update(request):
    product = get_object_or_404(Product, pk=request.POST.get("product_id"))
    cart = Cart(request)
    try:
        quantity = int(request.POST.get("quantity", 0))
    except (TypeError, ValueError):
        quantity = 0

    if quantity <= 0:
        cart.remove(product.pk)
    else:
        cart.add(product, quantity=min(quantity, product.stock), override=True)

    if _wants_json(request):
        payload = _cart_payload(cart)
        row = next((item for item in cart if item["product"].pk == product.pk), None)
        payload["row_subtotal_fa"] = format_money(row["subtotal"]) if row else "۰"
        payload["row_quantity"] = row["quantity"] if row else 0
        return JsonResponse(payload)
    return redirect("store:cart_detail")


@require_POST
def cart_remove(request):
    cart = Cart(request)
    product_id = request.POST.get("product_id")
    if product_id:
        cart.remove(product_id)
    if _wants_json(request):
        return JsonResponse(_cart_payload(cart))
    messages.info(request, "محصول از سبد خرید حذف شد.")
    return redirect("store:cart_detail")


def cart_detail(request):
    cart = Cart(request)
    return render(request, "store/cart.html", {"cart": cart})


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.info(request, "سبد خرید شما خالی است؛ ابتدا محصولی انتخاب کنید.")
        return redirect("store:product_list")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            shipping = shipping_cost(cart.total)
            order = Order(**form.cleaned_data)
            order.shipping_price = shipping
            order.total_price = cart.total + shipping
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    product_name=item["product"].name,
                    price=item["product"].price,
                    quantity=item["quantity"],
                )
            cart.clear()
            request.session["last_order_code"] = order.code
            return redirect("store:order_success")
    else:
        form = CheckoutForm()

    return render(request, "store/checkout.html", {"cart": cart, "form": form})


def order_success(request):
    code = request.session.get("last_order_code")
    order = Order.objects.prefetch_related("items").filter(code=code).first() if code else None
    if not order:
        return redirect("store:home")
    return render(request, "store/order_success.html", {"order": order})


def about(request):
    return render(request, "store/about.html")


def health(request):
    return JsonResponse({"status": "ok", "service": "vitrin-shop"})
