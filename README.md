# pikLearn

> یک پلتفرم یادگیری و آموزش مدرن

**pikLearn** یک سایت آموزشی کامل است که با **Django** ساخته شده و امکان مدیریت دوره‌ها، بلاگ، داشبورد کاربر، نظرات و سیستم ثبت‌نام را فراهم می‌کند.

🔗 **دمو زنده:** [http://piklearn.ir:8081](http://piklearn.ir:8081)

---

## ✨ ویژگی‌ها

- رابط کاربری مدرن با طراحی Glassmorphism
- سیستم احراز هویت (ثبت‌نام و ورود)
- داشبورد اختصاصی کاربر (دوره‌های من، لیست علاقه‌مندی، سفارش‌ها، پروفایل)
- سیستم مدیریت دوره‌ها با امتیاز، تعداد دانشجو و قیمت
- بلاگ با دسته‌بندی، تگ و قابلیت پاسخ به نظرات
- پشتیبانی از اعداد فارسی و تاریخ جلالی
- سیستم اعلان‌ها (Notifications)
- پنل مدیریت قدرتمند
- طراحی واکنش‌پذیر (Responsive)

---

## 🛠 تکنولوژی‌ها

- **Backend:** Django
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Database:** SQLite (قابل تغییر به PostgreSQL)
- **سایر:** Django Template Tags, Custom Filters

---

## 📋 نیازمندی‌ها

- Python 3.10+
- pip
- Git

---

## 🚀 نصب و راه‌اندازی

### ۱. کلون کردن پروژه

```bash
git clone https://github.com/Piklearn/pikLearn.git
cd pikLearn
```

### ۲. ساخت محیط مجازی

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### ۳. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### ۴. اعمال مایگریشن‌ها

```bash
python config/manage.py migrate
```

### ۵. بارگذاری داده‌های اولیه (اختیاری)

```bash
python config/manage.py load_test_data
```

### ۶. ساخت کاربر ادمین

```bash
python config/manage.py createsuperuser
```

### ۷. اجرای پروژه

```bash
python config/manage.py runserver
```

سپس به آدرس زیر بروید:

```
http://127.0.0.1:8000
```

---

## 📁 ساختار پروژه

```
pikLearn/
├── config/                  # تنظیمات اصلی پروژه
│   ├── settings/            # تنظیمات Django
│   ├── courses/             # اپلیکیشن دوره‌ها
│   ├── blog/                # اپلیکیشن بلاگ
│   ├── accounts/            # مدیریت کاربران
│   ├── templates/           # قالب‌های HTML
│   └── static/              # فایل‌های CSS و JS
├── docs/
│   └── screenshots/         # اسکرین‌شات‌های پروژه
├── requirements.txt
└── README.md
```

---

## 📸 اسکرین‌شات‌ها
## 📸 اسکرین‌شات‌ها

### صفحه اصلی
![صفحه اصلی](https://raw.githubusercontent.com/piklearn/pikLearn/main/docs/screenshots/home.png)

### لیست دوره‌ها
![لیست دوره‌ها](https://raw.githubusercontent.com/piklearn/pikLearn/main/docs/screenshots/courses.png)

### جزئیات دوره
![جزئیات دوره](https://raw.githubusercontent.com/piklearn/pikLearn/main/docs/screenshots/course_detail.png)

### داشبورد کاربر
![داشبورد](https://raw.githubusercontent.com/piklearn/pikLearn/main/docs/screenshots/dashboard.png)

### لیست مقالات
![لیست مقالات](https://raw.githubusercontent.com/piklearn/pikLearn/main/docs/screenshots/blogs.png)

### جزئیات مقاله
![جزئیات مقاله](https://raw.githubusercontent.com/piklearn/pikLearn/main/docs/screenshots/blog_detail.png)
---

## 🤝 مشارکت

1. پروژه را Fork کنید
2. یک Branch جدید بسازید (`git checkout -b feature/amazing-feature`)
3. تغییرات را Commit کنید (`git commit -m 'Add amazing feature'`)
4. به Branch خود Push کنید (`git push origin feature/amazing-feature`)
5. یک Pull Request باز کنید

---

## 📄 لایسنس

این پروژه تحت لایسنس **MIT** منتشر شده است.

---

## 📬 تماس

- **ایمیل:** pkyanpwr@gmail.com
- **GitHub:** [github.com/Piklearn](https://github.com/Piklearn)
- **دمو:** [piklearn.ir:8081](http://piklearn.ir:8081)

---

ساخته شده با ❤️ توسط **pky**
