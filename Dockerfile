# استخدام صورة بايثون خفيفة ورسمية
FROM python:3.10-slim

# ضبط متغيرات البيئة لمنع بايثون من تخزين الملفات المؤقتة وطباعة المخرجات فوراً
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# تحديد مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ ملف المكتبات أولاً للاستفادة من الكاش
COPY requirements.txt .

# تثبيت المكتبات الخارجية
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع إلى داخل الحاوية
COPY . .

# الأمر الافتراضي لتشغيل السكربت (يمكنك تغيير main.py إلى اسم ملفك الرئيسي)
CMD ["python", "main.py"]
