from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="نام محصول")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="اسلاگ")
    description = models.TextField(verbose_name="توضیحات")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="قیمت")
    discount_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, verbose_name="قیمت با تخفیف")
    stock_status = models.BooleanField(default=True, verbose_name="موجودی")
    category = models.CharField(max_length=100, verbose_name="دسته‌بندی")
    brand = models.CharField(max_length=100, verbose_name="برند")
    product_code = models.CharField(max_length=50, verbose_name="کد محصول")
    tags = models.CharField(max_length=200, blank=True, verbose_name="تگ‌ها")
    views_count = models.IntegerField(default=0, verbose_name="تعداد بازدید")
    sales_count = models.IntegerField(default=0, verbose_name="تعداد فروش")
    is_new = models.BooleanField(default=False, verbose_name="جدید")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    def get_discount_percentage(self):
        if self.discount_price and self.price:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, verbose_name="محصول")
    image = models.ImageField(upload_to='products/', verbose_name="تصویر")
    is_main = models.BooleanField(default=False, verbose_name="تصویر اصلی")

    class Meta:
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصول"

    def __str__(self):
        return f"تصویر {self.product.name}"

class Color(models.Model):
    product = models.ForeignKey(Product, related_name='colors', on_delete=models.CASCADE, verbose_name="محصول")
    name = models.CharField(max_length=50, verbose_name="نام رنگ")
    hex_code = models.CharField(max_length=7, verbose_name="کد هگز رنگ")

    class Meta:
        verbose_name = "رنگ"
        verbose_name_plural = "رنگ‌ها"

    def __str__(self):
        return self.name

class Size(models.Model):
    product = models.ForeignKey(Product, related_name='sizes', on_delete=models.CASCADE, verbose_name="محصول")
    name = models.CharField(max_length=10, verbose_name="نام سایز")
    available = models.BooleanField(default=True, verbose_name="موجود")

    class Meta:
        verbose_name = "سایز"
        verbose_name_plural = "سایزها"

    def __str__(self):
        return self.name

class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, related_name='specifications', on_delete=models.CASCADE, verbose_name="محصول")
    title = models.CharField(max_length=100, verbose_name="عنوان")
    value = models.CharField(max_length=200, verbose_name="مقدار")

    class Meta:
        verbose_name = "مشخصه فنی"
        verbose_name_plural = "مشخصات فنی"

    def __str__(self):
        return f"{self.title}: {self.value}"

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE, verbose_name="محصول")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name="امتیاز")
    comment = models.TextField(verbose_name="نظر")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"

    def __str__(self):
        return f"نظر {self.user.username} برای {self.product.name}"

class ShippingPolicy(models.Model):
    product = models.ForeignKey(Product, related_name='shipping_policies', on_delete=models.CASCADE, verbose_name="محصول")
    title = models.CharField(max_length=100, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")

    class Meta:
        verbose_name = "سیاست ارسال"
        verbose_name_plural = "سیاست‌های ارسال"

    def __str__(self):
        return self.title