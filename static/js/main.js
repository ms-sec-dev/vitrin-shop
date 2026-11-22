/* ============================================================
   Vitrin — vanilla JavaScript
   Cart (AJAX), steppers, mobile menu, toasts, reveal animations
   ============================================================ */

"use strict";

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

function csrfToken() {
  return $('meta[name="csrf-token"]')?.content || "";
}

function faDigits(value) {
  return String(value).replace(/\d/g, (digit) => "۰۱۲۳۴۵۶۷۸۹"[digit]);
}

async function post(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken(),
      "X-Requested-With": "XMLHttpRequest",
      Accept: "application/json",
    },
    body,
    credentials: "same-origin",
  });
  let data;
  try {
    data = await response.json();
  } catch {
    data = { ok: false, message: "پاسخ نامعتبر از سرور دریافت شد." };
  }
  if (!response.ok && data.ok !== false) {
    data.ok = false;
  }
  return data;
}

function showToast(message, ok = true) {
  const stack = $("[data-toast-stack]");
  if (!stack) return;
  const toast = document.createElement("div");
  toast.className = "toast" + (ok ? "" : " toast--error");
  toast.textContent = message;
  stack.appendChild(toast);
  window.setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(8px)";
    toast.style.transition = "opacity .2s ease, transform .2s ease";
    window.setTimeout(() => toast.remove(), 220);
  }, 2800);
}

function updateCartCount(count) {
  $$("[data-cart-count]").forEach((element) => {
    element.textContent = faDigits(count);
  });
}

function updateSummary(data) {
  const total = $("[data-cart-total]");
  if (total) total.textContent = `${data.total_fa} تومان`;
  const shipping = $("[data-cart-shipping]");
  if (shipping) {
    shipping.textContent = data.shipping ? `${data.shipping_fa} تومان` : "رایگان";
  }
  const payable = $("[data-cart-payable]");
  if (payable) payable.textContent = `${data.payable_fa} تومان`;
}

/* ---------- Add to cart ---------- */

document.addEventListener("submit", async (event) => {
  const form = event.target.closest("form[data-add-to-cart]");
  if (!form) return;
  event.preventDefault();

  const button = form.querySelector('button[type="submit"]');
  if (button) button.disabled = true;

  try {
    const data = await post(form.action, new FormData(form));
    if (!data.ok) {
      showToast(data.message || "خطایی رخ داد.", false);
      return;
    }
    updateCartCount(data.count);
    showToast(data.message || "محصول به سبد خرید اضافه شد.");
    const quantity = form.querySelector("[data-stepper-input]");
    if (quantity) quantity.value = 1;
  } catch {
    showToast("خطا در برقراری ارتباط با سرور.", false);
  } finally {
    if (button) button.disabled = false;
  }
});

/* ---------- Quantity steppers ---------- */

document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-stepper] button[data-step]");
  if (!button) return;

  const stepper = button.closest("[data-stepper]");
  const input = stepper.querySelector("[data-stepper-input]");
  if (!input) return;

  const step = Number.parseInt(button.dataset.step, 10) || 0;
  const min = Number.parseInt(input.min || "1", 10);
  const max = Number.parseInt(input.max || "9999", 10);
  const next = (Number.parseInt(input.value, 10) || min) + step;
  input.value = Math.min(Math.max(next, min), max);
  input.dispatchEvent(new Event("change", { bubbles: true }));
});

/* ---------- Cart page ---------- */

document.addEventListener("submit", async (event) => {
  const form = event.target.closest("form[data-cart-qty-form]");
  if (!form) return;
  event.preventDefault();

  const row = form.closest("[data-cart-row]");
  const data = await post(form.action, new FormData(form)).catch(() => null);
  if (!data) {
    showToast("خطا در برقراری ارتباط با سرور.", false);
    return;
  }
  if (!data.ok) {
    showToast(data.message || "خطایی رخ داد.", false);
    return;
  }

  updateCartCount(data.count);
  if (data.count === 0) {
    window.location.reload();
    return;
  }
  if (row && data.row_quantity === 0) {
    row.remove();
  } else if (row) {
    const subtotal = row.querySelector("[data-row-subtotal]");
    if (subtotal) subtotal.innerHTML = `${data.row_subtotal_fa} <small>تومان</small>`;
    const quantity = row.querySelector("[data-cart-quantity]");
    if (quantity) quantity.value = data.row_quantity;
  }
  updateSummary(data);
  showToast("سبد خرید به‌روزرسانی شد.");
});

document.addEventListener("submit", async (event) => {
  const form = event.target.closest("form[data-cart-remove]");
  if (!form) return;
  event.preventDefault();

  const row = form.closest("[data-cart-row]");
  const data = await post(form.action, new FormData(form)).catch(() => null);
  if (!data) {
    showToast("خطا در برقراری ارتباط با سرور.", false);
    return;
  }
  if (!data.ok) {
    showToast(data.message || "خطایی رخ داد.", false);
    return;
  }

  updateCartCount(data.count);
  if (data.count === 0) {
    window.location.reload();
    return;
  }
  if (row) row.remove();
  updateSummary(data);
  showToast("محصول از سبد خرید حذف شد.");
});

/* ---------- Mobile menu ---------- */

const menuToggle = $("[data-menu-toggle]");
const mainNav = $("[data-nav]");

if (menuToggle && mainNav) {
  menuToggle.addEventListener("click", () => {
    const isOpen = mainNav.classList.toggle("is-open");
    menuToggle.setAttribute("aria-expanded", String(isOpen));
  });

  document.addEventListener("click", (event) => {
    if (!mainNav.classList.contains("is-open")) return;
    if (mainNav.contains(event.target) || menuToggle.contains(event.target)) return;
    mainNav.classList.remove("is-open");
    menuToggle.setAttribute("aria-expanded", "false");
  });
}

/* ---------- Auto-submit selects ---------- */

$$("[data-auto-submit]").forEach((select) => {
  select.addEventListener("change", () => select.form?.submit());
});

/* ---------- Flash messages ---------- */

$$("[data-flash-close]").forEach((button) => {
  button.addEventListener("click", () => button.closest(".flash")?.remove());
});

/* ---------- Checkout validation ---------- */

const checkoutForm = $("[data-checkout-form]");
if (checkoutForm) {
  checkoutForm.addEventListener("submit", (event) => {
    const phone = checkoutForm.querySelector("#id_phone");
    if (phone && !/^09\d{9}$/.test(phone.value.trim())) {
      event.preventDefault();
      showToast("شماره موبایل باید ۱۱ رقم و با ۰۹ شروع شود.", false);
      phone.focus();
    }
  });
}

/* ---------- Reveal on scroll ---------- */

const revealElements = $$(".reveal");
if ("IntersectionObserver" in window && revealElements.length) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.12 }
  );
  revealElements.forEach((element) => observer.observe(element));
} else {
  revealElements.forEach((element) => element.classList.add("is-visible"));
}
