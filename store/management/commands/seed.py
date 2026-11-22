import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from store.models import Category, Product

CATEGORIES = [
    {
        "slug": "audio",
        "name": "صوتی و هدفون",
        "description": "هدفون، ایرباد و اسپیکر برای شنیدن بی‌نقص",
        "icon": "headphones",
        "order": 1,
    },
    {
        "slug": "wearables",
        "name": "ساعت و پوشیدنی",
        "description": "ساعت هوشمند و دستبند سلامتی",
        "icon": "watch",
        "order": 2,
    },
    {
        "slug": "home",
        "name": "خانه و آشپزخانه",
        "description": "لوازم کاربردی با طراحی مینیمال",
        "icon": "home",
        "order": 3,
    },
    {
        "slug": "accessories",
        "name": "اکسسوری و دیجیتال",
        "description": "کیبورد، کیف و لوازم روزمره",
        "icon": "bag",
        "order": 4,
    },
]

PRODUCTS = [
    {
        "category": "audio",
        "slug": "vitrin-pro-headphones",
        "name": "هدفون بی‌سیم ویترین پرو",
        "brand": "ویترین",
        "price": 2890000,
        "old_price": 3450000,
        "stock": 14,
        "rating": "4.8",
        "image": "img/products/headphones.svg",
        "is_featured": True,
        "is_new": True,
        "description": (
            "هدفون ویترین پرو با حذف فعال نویز و درایورهای ۴۰ میلی‌متری، تجربه‌ای "
            "شفاف و عمیق از موسیقی می‌سازد. طراحی سبک و بالشتک‌های نرم آن، استفاده "
            "طولانی‌مدت را راحت می‌کند و باتری ۳۵ ساعته همراه همیشگی شماست."
        ),
        "specs": "نوع اتصال: بلوتوث ۵.۳\nمدت زمان باتری: تا ۳۵ ساعت\nحذف نویز: فعال (ANC)\nوزن: ۲۵۰ گرم\nضمانت: ۱۸ ماه",
    },
    {
        "category": "audio",
        "slug": "studio-max-earbuds",
        "name": "ایرباد استودیو مکس",
        "brand": "استودیو",
        "price": 1750000,
        "old_price": 2100000,
        "stock": 22,
        "rating": "4.6",
        "image": "img/products/earbuds.svg",
        "is_featured": True,
        "is_new": False,
        "description": (
            "ایرباد استودیو مکس با کیس شارژ جمع‌وجمع و اتصال پایدار، همراه ایده‌آل "
            "برای مسیر روزانه است. میکروفون دوگانه تماس‌ها را شفاف نگه می‌دارد و "
            "حالت شفافیت اجازه می‌دهد صداهای محیط را هم بشنوید."
        ),
        "specs": "نوع اتصال: بلوتوث ۵.۲\nمدت زمان باتری: ۶ ساعت + ۱۸ ساعت با کیس\nمقاومت: IPX4\nشارژ سریع: ۱۰ دقیقه = ۲ ساعت پخش",
    },
    {
        "category": "audio",
        "slug": "portable-bluetooth-speaker",
        "name": "اسپیکر بلوتوث پرتابل",
        "brand": "ساندویو",
        "price": 1290000,
        "old_price": None,
        "stock": 9,
        "rating": "4.4",
        "image": "img/products/speaker.svg",
        "is_featured": True,
        "is_new": False,
        "description": (
            "اسپیکر پرتابل ساندویو با بدنه مقاوم در برابر پاشش آب و بند حمل، برای "
            "پیک‌نیک و سفر ساخته شده است. خروجی ۲۰ وات و امکان اتصال دو اسپیکر، "
            "صدایی پرحجم در فضای باز می‌سازد."
        ),
        "specs": "توان خروجی: ۲۰ وات\nمقاومت: IPX7\nباتری: تا ۱۲ ساعت\nقابلیت: اتصال استریو دو اسپیکر",
    },
    {
        "category": "wearables",
        "slug": "nova-smartwatch",
        "name": "ساعت هوشمند نوا",
        "brand": "نوا",
        "price": 3650000,
        "old_price": 4200000,
        "stock": 7,
        "rating": "4.7",
        "image": "img/products/smartwatch.svg",
        "is_featured": True,
        "is_new": True,
        "description": (
            "ساعت هوشمند نوا با نمایشگر AMOLED و پایش شبانه‌روزی ضربان قلب، خواب و "
            "اکسیژن خون، سلامت شما را جدی می‌گیرد. بیش از ۱۰۰ حالت ورزشی و باتری "
            "۱۰ روزه، آن را به همراهی مطمئن تبدیل می‌کند."
        ),
        "specs": "نمایشگر: AMOLED ۱.۴۳ اینچ\nباتری: تا ۱۰ روز\nحالت‌های ورزشی: ۱۰۰+\nمقاومت: 5ATM\nسازگاری: اندروید و iOS",
    },
    {
        "category": "wearables",
        "slug": "fitline-health-band",
        "name": "دستبند سلامتی فیت‌لاین",
        "brand": "فیت‌لاین",
        "price": 890000,
        "old_price": None,
        "stock": 31,
        "rating": "4.3",
        "image": "img/products/fitness-band.svg",
        "is_featured": False,
        "is_new": False,
        "description": (
            "دستبند فیت‌لاین با وزن سبک و بند سیلیکونی نرم، شمارش قدم‌ها، کالری و "
            "کیفیت خواب را ساده و دقیق انجام می‌دهد. اعلان تماس و پیام هم روی مچ "
            "دست شماست."
        ),
        "specs": "نمایشگر: رنگی ۱.۱ اینچ\nباتری: تا ۱۴ روز\nمقاومت: IP68\nوزن: ۲۴ گرم",
    },
    {
        "category": "home",
        "slug": "minimal-desk-lamp",
        "name": "چراغ مطالعه مینیمال",
        "brand": "نورا",
        "price": 640000,
        "old_price": 790000,
        "stock": 18,
        "rating": "4.5",
        "image": "img/products/lamp.svg",
        "is_featured": True,
        "is_new": False,
        "description": (
            "چراغ مطالعه نورا با بازوی قابل تنظیم و نور گرم بدون چشمک، فضای کار را "
            "دلنشین می‌کند. سه سطح روشنایی و پایه کم‌جا، مناسب میزهای کوچک است."
        ),
        "specs": "منبع نور: LED\nدمای رنگ: ۳۰۰۰ کلوین\nسطوح روشنایی: ۳ حالت\nتوان: ۸ وات",
    },
    {
        "category": "home",
        "slug": "ceramic-mug",
        "name": "ماگ سرامیکی دست‌ساز",
        "brand": "خاک",
        "price": 245000,
        "old_price": None,
        "stock": 60,
        "rating": "4.2",
        "image": "img/products/mug.svg",
        "is_featured": False,
        "is_new": False,
        "description": (
            "ماگ سرامیکی خاک با لعاب مات و لبه گرد، برای قهوه صبحگاهی ساخته شده "
            "است. هر قطعه به‌صورت دست‌ساز تولید می‌شود و ممکن است تفاوت‌های کوچکی "
            "داشته باشد."
        ),
        "specs": "جنس: سرامیک\nحجم: ۳۵۰ میلی‌لیتر\nقابل استفاده در مایکروویو: بله\nشست‌وشو: دستی توصیه می‌شود",
    },
    {
        "category": "accessories",
        "slug": "urban-backpack",
        "name": "کوله پشتی شهری",
        "brand": "راه",
        "price": 980000,
        "old_price": 1150000,
        "stock": 12,
        "rating": "4.6",
        "image": "img/products/backpack.svg",
        "is_featured": True,
        "is_new": False,
        "description": (
            "کوله پشتی راه با پارچه ضدآب و جیب اختصاصی لپ‌تاپ ۱۵ اینچ، همراه "
            "روزهای کاری و سفرهای کوتاه است. طراحی ساده و ارگونومیک آن فشار را "
            "روی شانه‌ها کم می‌کند."
        ),
        "specs": "ظرفیت: ۲۲ لیتر\nجیب لپ‌تاپ: تا ۱۵ اینچ\nجنس: پلی‌استر ضدآب\nوزن: ۷۸۰ گرم",
    },
    {
        "category": "accessories",
        "slug": "wireless-mechanical-keyboard",
        "name": "کیبورد مکانیکال بی‌سیم",
        "brand": "کی‌استروک",
        "price": 2150000,
        "old_price": None,
        "stock": 6,
        "rating": "4.8",
        "image": "img/products/keyboard.svg",
        "is_featured": True,
        "is_new": True,
        "description": (
            "کیبورد مکانیکال کی‌استروک با سوییچ‌های قهوه‌ای و ساختار آلومینیومی، "
            "تایپ را لذت‌بخش می‌کند. اتصال سه‌گانه بلوتوث، دانگل و کابل، آن را برای "
            "میز کار و تبلت مناسب می‌سازد."
        ),
        "specs": "چیدمان: ۷۵ درصد\nسوییچ: قهوه‌ای (تاکتیل)\nاتصال: بلوتوث / 2.4GHz / USB-C\nباتری: ۴۰۰۰ میلی‌آمپر",
    },
    {
        "category": "accessories",
        "slug": "ergonomic-mouse",
        "name": "ماوس ارگونومیک",
        "brand": "کی‌استروک",
        "price": 760000,
        "old_price": None,
        "stock": 25,
        "rating": "4.4",
        "image": "img/products/mouse.svg",
        "is_featured": False,
        "is_new": False,
        "description": (
            "ماوس ارگونومیک با زاویه طبیعی مچ و سنسور دقیق ۴۰۰۰ DPI، خستگی دست را "
            "در ساعت‌های طولانی کار کاهش می‌دهد. اتصال بی‌سیم پایدار و سکوت کلیک‌ها "
            "از مزایای آن است."
        ),
        "specs": "سنسور: ۴۰۰۰ DPI\nاتصال: 2.4GHz بی‌سیم\nباتری: تا ۱۲ ماه\nتعداد کلید: ۶",
    },
    {
        "category": "accessories",
        "slug": "classic-sunglasses",
        "name": "عینک آفتابی کلاسیک",
        "brand": "آفتاب",
        "price": 520000,
        "old_price": 680000,
        "stock": 16,
        "rating": "4.1",
        "image": "img/products/sunglasses.svg",
        "is_featured": False,
        "is_new": False,
        "description": (
            "عینک آفتابی آفتاب با فریم سبک استیل و لنز UV400، ترکیبی از کلاسیک و "
            "کاربردی است. کیف محافظ و دستمال میکروفایبر همراه آن ارائه می‌شود."
        ),
        "specs": "جنس فریم: استیل\nلنز: UV400\nعرض عدسی: ۵۲ میلی‌متر\nهمراه: کیف و دستمال",
    },
    {
        "category": "accessories",
        "slug": "leather-wallet",
        "name": "کیف پول چرمی",
        "brand": "چرم‌خانه",
        "price": 430000,
        "old_price": None,
        "stock": 40,
        "rating": "4.5",
        "image": "img/products/wallet.svg",
        "is_featured": True,
        "is_new": False,
        "description": (
            "کیف پول چرم‌خانه از چرم طبیعی با دوخت دستی ساخته شده و با گذر زمان "
            "زیباتر می‌شود. جیب‌های متعدد، کارت‌ها و اسکناس‌ها را مرتب نگه می‌دارد."
        ),
        "specs": "جنس: چرم طبیعی\nجیب کارت: ۸ عدد\nابعاد: ۱۱ × ۹ سانتی‌متر\nساخت: دست‌ساز",
    },
]


class Command(BaseCommand):
    help = "Create or refresh the Persian demo catalog (idempotent)."

    def handle(self, *args, **options):
        categories = {}
        for data in CATEGORIES:
            category, _ = Category.objects.update_or_create(slug=data["slug"], defaults=data)
            categories[data["slug"]] = category

        created = updated = 0
        for data in PRODUCTS:
            payload = dict(data)
            payload["category"] = categories[payload.pop("category")]
            _, was_created = Product.objects.update_or_create(
                slug=payload["slug"], defaults=payload
            )
            created += int(was_created)
            updated += int(not was_created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo catalog ready: {len(categories)} categories, "
                f"{created} products created, {updated} refreshed."
            )
        )

        password = os.getenv("DEMO_ADMIN_PASSWORD", "")
        if password:
            user_model = get_user_model()
            username = os.getenv("DEMO_ADMIN_USERNAME", "admin")
            if user_model.objects.filter(username=username).exists():
                self.stdout.write(f"Demo admin already exists: {username}")
            else:
                user_model.objects.create_superuser(
                    username=username,
                    email=os.getenv("DEMO_ADMIN_EMAIL", "admin@example.com"),
                    password=password,
                )
                self.stdout.write(self.style.SUCCESS(f"Demo admin created: {username}"))
