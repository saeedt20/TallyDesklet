"""Explicit per-window language and numerals; never changes the system locale."""
FA = {
    "Today / This week": "مصرف امروز و هفته", "System": "سیستم", "Live": "زنده", "CPU": "پردازنده", "Memory": "حافظهٔ رم",
    "System disk": "دیسک سیستم", "Network": "شبکه", "Download": "دریافت", "Upload": "ارسال",
    "Today": "امروز", "This week": "این هفته", "60 s": "60 ثانیه",
    "Ready": "آماده", "Offline": "آفلاین", "Unavailable": "در دسترس نیست",
    "Warming up": "در حال آماده‌سازی", "Waiting for the first system sample": "در انتظار نخستین آمار سیستم",
    "Settings": "تنظیمات", "TallyDesklet Settings": "تنظیمات تالی‌دسکلت",
    "Appearance": "ظاهر", "Display & language": "نمایش و زبان", "Monitoring": "پایش",
    "Desktop & startup": "میزکار و راه‌اندازی", "Alerts": "هشدارها", "About": "درباره",
    "Ember": "اخگر", "Mint": "نعنا", "Ocean": "اقیانوس", "Lilac": "یاسی",
    "Paper": "کاغذ", "Silver": "نقره‌ای", "Charcoal & warm orange": "زغالی و نارنجی گرم",
    "Quiet mint green": "سبز نعنایی آرام", "Deep blue & cyan": "سرمه‌ای و فیروزه‌ای",
    "Soft violet": "بنفش ملایم", "Warm white & amber": "سفید گرم و کهربایی",
    "Cool gray & blue": "خاکستری روشن و آبی", "Theme": "تم",
    "Background opacity": "شفافیت پس‌زمینه", "Widget scale": "اندازهٔ ویجت",
    "Custom accent color": "رنگ تأکیدی سفارشی", "Accent color": "رنگ تأکیدی",
    "Restore theme colors": "بازگرداندن رنگ‌های تم", "Reduce motion": "کاهش جلوه‌های حرکتی",
    "Compact layout": "چیدمان فشرده", "Language": "زبان", "Numerals": "نوع ارقام",
    "Automatic": "خودکار", "Latin": "لاتین", "Persian": "فارسی", "Units": "واحدها",
    "Decimal · GB, MB/s": "ده‌دهی · GB, MB/s", "Binary · GiB, MiB/s": "دودویی · GiB, MiB/s",
    "Visible sections": "بخش‌های قابل نمایش", "Refresh interval": "فاصلهٔ به‌روزرسانی",
    "Network interface": "کارت شبکه", "Automatic · routed interface": "خودکار · رابط مسیر فعال",
    "Disk path": "مسیر دیسک", "Choose folder": "انتخاب پوشه", "Choose": "انتخاب",
    "Week starts on": "شروع هفته", "Saturday": "شنبه", "Sunday": "یکشنبه", "Monday": "دوشنبه",
    "Lock position": "قفل موقعیت", "Always on top": "همیشه روی پنجره‌ها",
    "Show on all workspaces": "نمایش در همهٔ میزکارها", "Start at login": "شروع هنگام ورود",
    "Reset position": "بازگرداندن موقعیت", "Quit": "خروج", "GitHub repository": "مخزن GitHub",
    "Report an issue": "گزارش مشکل", "Credits & licenses": "سازندگان و مجوزها",
    "Enable notifications": "فعال‌کردن اعلان‌ها", "Memory warning": "هشدار مصرف رم",
    "Disk warning": "هشدار ظرفیت دیسک", "Memory threshold": "آستانهٔ رم",
    "Disk threshold": "آستانهٔ دیسک", "_Close": "_بستن", "_Apply": "_اعمال تغییرات",
    "Cancel": "لغو", "Discard changes": "صرف‌نظر از تغییرات", "Keep editing": "ادامهٔ ویرایش",
    "Unsaved changes": "تغییرات ذخیره‌نشده", "Preferences applied.": "تنظیمات ذخیره شد.",
    "Preview only · press Apply to save": "پیش‌نمایش · برای ذخیره، اعمال تغییرات را بزنید",
    "Display changes preview immediately. Close restores your saved preferences.":
        "تغییرات ظاهر فوراً پیش‌نمایش می‌شوند. بستن پنجره، تنظیمات ذخیره‌شده را برمی‌گرداند.",
    "A smaller card with the same readings.": "کارت کوچک‌تر با همان اطلاعات.",
    "Keep at least one section visible.": "حداقل یک بخش باید قابل نمایش باشد.",
    "Disk: capacity of the filesystem containing this path, not read/write speed.":
        "دیسک: ظرفیت فایل‌سیستمِ این مسیر، نه سرعت خواندن و نوشتن.",
    "Usage combines download + upload observed while TallyDesklet runs. Closed-app traffic is excluded.":
        "مصرف، مجموع دریافت و ارسال هنگام اجرای تالی‌دسکلت است. ترافیک زمان بسته‌بودن برنامه حساب نمی‌شود.",
    "Daily reset: local midnight. The selected weekday defines the calendar week.":
        "مصرف روزانه نیمه‌شب محلی بازنشانی می‌شود. روز انتخاب‌شده، آغاز هفته است.",
    "Install the .deb to enable a stable login startup command.": "برای راه‌اندازی خودکار، بستهٔ deb را نصب کنید.",
    "Notifications are optional and require TallyDesklet to be running.": "اعلان اختیاری است و برنامه باید در حال اجرا باشد.",
    "Warn after 60 seconds above the threshold. At most once per metric in 10 minutes.":
        "پس از ۶۰ ثانیه عبور از آستانه هشدار می‌دهد؛ حداکثر یک بار برای هر معیار در ۱۰ دقیقه.",
    "All measurements and preferences stay on your computer.": "آمار و تنظیمات روی دستگاه شما نگهداری می‌شوند.",
    "Created by saeedt20 · MIT license": "ساختهٔ saeedt20 · مجوز MIT",
    "Vazirmatn by the Vazirmatn Project Authors · SIL Open Font License 1.1":
        "وزیرمتن، اثر سازندگان پروژهٔ Vazirmatn · مجوز SIL OFL 1.1",
    "Choose an existing absolute path. Its containing filesystem will be measured.":
        "یک مسیر کامل و موجود انتخاب کنید؛ فایل‌سیستم آن پایش می‌شود.",
    "Could not save preferences": "ذخیرهٔ تنظیمات انجام نشد", "Filesystem containing": "فایل‌سیستمِ مسیر",
    "Interface": "رابط", "Available": "در دسترس", "Usage tracking started": "آغاز پایش مصرف",
    "Preferences could not be saved": "تنظیمات ذخیره نشد", "Notifications unavailable": "اعلان در دسترس نیست",
    "High memory usage": "مصرف بالای رم", "Disk is getting full": "دیسک در حال پرشدن است",
}


def language(config):
    return config.get("display", {}).get("language", "en")


def rtl(config):
    return language(config) == "fa"


def tr(config, text):
    if not rtl(config):
        return text
    if text in FA:
        return FA[text]
    if '_' in text and text.replace('_','') in FA:
        return '_' + FA[text.replace('_','')]
    if text.endswith(' seconds'):
        return numerals(config,text.removesuffix(' seconds'))+' ثانیه'
    return text


def numerals(config, value):
    mode = config.get("display", {}).get("digits", "auto")
    persian = mode == "persian" or (mode == "auto" and rtl(config))
    value = str(value)
    if persian:
        return value.translate(str.maketrans("0123456789.%", "۰۱۲۳۴۵۶۷۸۹٫٪"))
    return value.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٫٪", "0123456789.%"))
