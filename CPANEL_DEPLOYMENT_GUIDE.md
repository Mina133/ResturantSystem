# دليل نشر نظام إدارة المطاعم على cPanel
# Restaurant Management System - cPanel Deployment Guide

## المتطلبات الأساسية / Prerequisites

### 1. متطلبات cPanel
- cPanel hosting with Python support
- Python 3.8+ (Python 3.9+ recommended)
- Passenger WSGI support enabled
- SSH access (recommended)

### 2. متطلبات المشروع
- جميع الملفات المطلوبة للنشر
- قاعدة بيانات SQLite (مضمنة في المشروع)

## خطوات النشر / Deployment Steps

### 1. تحضير الملفات / Prepare Files

#### أ. رفع الملفات إلى cPanel
```
public_html/
├── passenger_wsgi.py          # ملف Passenger WSGI الرئيسي
├── .htaccess                  # ملف إعدادات Apache
├── requirements_production.txt # متطلبات الإنتاج
├── src/                       # مجلد الكود المصدري
│   ├── main.py
│   ├── __init__.py
│   ├── database/
│   ├── models/
│   ├── routes/
│   └── static/
└── README.md
```

#### ب. إعداد الصلاحيات
```bash
# تعيين الصلاحيات المناسبة
chmod 755 passenger_wsgi.py
chmod 644 .htaccess
chmod -R 755 src/
chmod -R 777 src/database/  # للكتابة في قاعدة البيانات
```

### 2. تثبيت المتطلبات / Install Requirements

#### أ. عبر SSH (الأفضل)
```bash
# الانتقال إلى مجلد المشروع
cd ~/public_html

# إنشاء بيئة افتراضية (اختياري)
python3 -m venv venv
source venv/bin/activate

# تثبيت المتطلبات
pip install -r requirements_production.txt
```

#### ب. عبر cPanel File Manager
1. اذهب إلى "Python App" في cPanel
2. أنشئ تطبيق Python جديد
3. اختر Python 3.9+ كإصدار
4. ارفع ملف `requirements_production.txt`
5. اضغط "Install"

### 3. إعداد قاعدة البيانات / Database Setup

#### أ. إنشاء مجلد قاعدة البيانات
```bash
mkdir -p src/database
chmod 777 src/database
```

#### ب. تشغيل التطبيق لأول مرة
- عند تشغيل التطبيق لأول مرة، سيتم إنشاء قاعدة البيانات تلقائياً
- سيتم إدراج البيانات الافتراضية (المستخدمين، الأصناف، إلخ)

### 4. إعداد Passenger WSGI / Passenger WSGI Setup

#### أ. في cPanel Python App
1. اذهب إلى "Python App"
2. اختر التطبيق الذي أنشأته
3. في "Startup File" أدخل: `passenger_wsgi.py`
4. في "Application Root" أدخل: `/home/username/public_html`
5. اضغط "Save"

#### ب. إعداد متغيرات البيئة (اختياري)
```bash
# في cPanel Python App
FLASK_ENV=production
FLASK_DEBUG=False
```

### 5. اختبار النشر / Testing Deployment

#### أ. فتح التطبيق
- اذهب إلى: `https://yourdomain.com`
- يجب أن تظهر صفحة تسجيل الدخول

#### ب. اختبار الحسابات الافتراضية
```
مدير النظام: admin / password
مدير الفرع: manager / 123456
أمين الصندوق: cashier / cashier123
النادل: waiter / waiter123
المشرف العام: supervisor / super123
```

## استكشاف الأخطاء / Troubleshooting

### 1. مشاكل شائعة / Common Issues

#### أ. خطأ 500 Internal Server Error
```bash
# تحقق من ملفات السجل
tail -f ~/logs/error_log
tail -f ~/logs/access_log

# تحقق من صلاحيات الملفات
ls -la passenger_wsgi.py
ls -la src/database/
```

#### ب. خطأ في قاعدة البيانات
```bash
# تحقق من وجود مجلد قاعدة البيانات
ls -la src/database/

# تحقق من الصلاحيات
chmod 777 src/database/
```

#### ج. خطأ في استيراد الوحدات
```bash
# تحقق من مسار Python
which python3

# تحقق من المتطلبات المثبتة
pip list
```

### 2. تحسين الأداء / Performance Optimization

#### أ. إعدادات Apache
```apache
# في .htaccess
# تم إضافة إعدادات الضغط والتخزين المؤقت
```

#### ب. إعدادات قاعدة البيانات
```python
# في main.py
# قاعدة البيانات SQLite محسنة للإنتاج
```

## الأمان / Security

### 1. إعدادات الأمان المطبقة
- منع الوصول للملفات الحساسة
- رؤوس أمان HTTP
- تشفير كلمات المرور
- حماية من XSS و CSRF

### 2. توصيات إضافية
- استخدم HTTPS دائماً
- حدث التطبيق بانتظام
- احتفظ بنسخ احتياطية من قاعدة البيانات
- راقب ملفات السجل

## الصيانة / Maintenance

### 1. النسخ الاحتياطية
```bash
# نسخ احتياطي لقاعدة البيانات
cp src/database/restaurant_arabic_fixed.db backup_$(date +%Y%m%d).db

# نسخ احتياطي كامل
tar -czf backup_$(date +%Y%m%d).tar.gz src/
```

### 2. مراقبة الأداء
- راقب استخدام الذاكرة والمعالج
- تحقق من ملفات السجل بانتظام
- راقب حجم قاعدة البيانات

## الدعم / Support

### 1. معلومات الاتصال
- للمساعدة التقنية، راجع ملف README.md
- للأسئلة العامة، راجع INSTALLATION_GUIDE.md

### 2. التحديثات
- تحقق من التحديثات بانتظام
- اختبر التحديثات في بيئة التطوير أولاً

---

**ملاحظة مهمة:** تأكد من اختبار التطبيق بشكل كامل بعد النشر وقبل الاستخدام في الإنتاج.

**Important Note:** Make sure to thoroughly test the application after deployment before using it in production.
