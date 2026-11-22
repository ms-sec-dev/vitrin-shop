import re

from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        label="نام و نام خانوادگی",
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "مثلاً سارا محمدی", "autocomplete": "name"}),
        error_messages={"required": "نام و نام خانوادگی را وارد کنید."},
    )
    phone = forms.CharField(
        label="شماره موبایل",
        max_length=11,
        widget=forms.TextInput(
            attrs={"placeholder": "09121234567", "inputmode": "numeric", "autocomplete": "tel"}
        ),
        error_messages={"required": "شماره موبایل را وارد کنید."},
    )
    email = forms.EmailField(
        label="ایمیل (اختیاری)",
        required=False,
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com", "autocomplete": "email"}),
        error_messages={"invalid": "ایمیل معتبر نیست."},
    )
    city = forms.CharField(
        label="شهر",
        max_length=80,
        widget=forms.TextInput(attrs={"placeholder": "تهران", "autocomplete": "address-level2"}),
        error_messages={"required": "شهر را وارد کنید."},
    )
    address = forms.CharField(
        label="نشانی کامل",
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "خیابان، کوچه، پلاک و واحد",
                "autocomplete": "street-address",
            }
        ),
        error_messages={"required": "نشانی را وارد کنید."},
    )
    postal_code = forms.CharField(
        label="کد پستی (اختیاری)",
        required=False,
        max_length=10,
        widget=forms.TextInput(attrs={"placeholder": "1234567890", "inputmode": "numeric"}),
    )
    note = forms.CharField(
        label="یادداشت سفارش (اختیاری)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "توضیحات اضافه برای ارسال"}),
    )

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not re.fullmatch(r"09\d{9}", phone):
            raise forms.ValidationError("شماره موبایل باید ۱۱ رقم و با ۰۹ شروع شود.")
        return phone

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get("postal_code", "").strip()
        if postal_code and not re.fullmatch(r"\d{10}", postal_code):
            raise forms.ValidationError("کد پستی باید ۱۰ رقم باشد.")
        return postal_code
