from django.db import models
from django.contrib.auth.models import User
from products.models import Product, Color, Size
from django.utils import timezone
import uuid

class Cart(models.Model):
    user = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE, 
        verbose_name="کاربر"
    )
    session_id = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        verbose_name="شناسه جلسه"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="تاریخ ایجاد"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="تاریخ به‌روزرسانی"
    )

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"

    def __str__(self):
        return f"سبد خرید {self.id} - {'کاربر: ' + str(self.user) if self.user else 'جلسه: ' + self.session_id}"

    def merge_carts(self, other_cart):
        """ادغام سبدهای خرید برای کاربرانی که لاگین می‌کنند"""
        for item in other_cart.cartitem_set.all():
            cart_item, created = self.cartitem_set.get_or_create(
                cart=self,
                product=item.product,
                color=item.color,
                size=item.size,
                defaults={'quantity': item.quantity}
            )
            if not created:
                cart_item.quantity += item.quantity
                cart_item.save()
        other_cart.delete()

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE, 
        related_name='cartitem_set', 
        verbose_name="سبد خرید"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        verbose_name="محصول"
    )
    color = models.ForeignKey(
        Color, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        verbose_name="رنگ"
    )
    size = models.ForeignKey(
        Size, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        verbose_name="سایز"
    )
    quantity = models.PositiveIntegerField(
        default=1, 
        verbose_name="تعداد"
    )

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"
        unique_together = ('cart', 'product', 'color', 'size')

    def __str__(self):
        return f"{self.product.name} - تعداد: {self.quantity}"

    def get_total_price(self):
        """محاسبه قیمت کل آیتم با احتساب تخفیف"""
        price = self.product.discount_price if self.product.discount_price is not None else self.product.price if self.product.price is not None else 0
        return self.quantity * price

    def get_discount(self):
        """محاسبه تخفیف آیتم"""
        if self.product.discount_price is not None and self.product.price is not None and self.product.discount_price < self.product.price:
            return self.quantity * (self.product.price - self.product.discount_price)
        return 0

class Address(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="کاربر"
    )
    full_name = models.CharField(
        max_length=255, 
        verbose_name="نام کامل"
    )
    phone_number = models.CharField(
        max_length=20, 
        verbose_name="شماره تلفن"
    )
    province = models.CharField(
        max_length=100, 
        verbose_name="استان"
    )
    city = models.CharField(
        max_length=100, 
        verbose_name="شهر"
    )
    address = models.TextField(
        verbose_name="آدرس"
    )
    postal_code = models.CharField(
        max_length=20, 
        verbose_name="کد پستی"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="تاریخ ایجاد"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="تاریخ به‌روزرسانی"
    )
    is_default = models.BooleanField(
        default=False, 
        verbose_name="آدرس پیش‌فرض"
    )

    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس‌ها"

    def __str__(self):
        return f"{self.full_name} - {self.city}"

    def save(self, *args, **kwargs):
        """مطمئن شدن که فقط یک آدرس پیش‌فرض وجود داره"""
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)

class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'در حال پردازش'),
        ('SHIPPED', 'ارسال شده'),
        ('DELIVERED', 'تحویل شده'),
        ('CANCELED', 'لغو شده'),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="کاربر"
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="آدرس"
    )
    order_number = models.CharField(
        max_length=64,
        unique=True,
        blank=True,
        verbose_name="شماره سفارش"
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="مبلغ کل"
    )
    total_discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="تخفیف کل"
    )
    shipping_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="هزینه ارسال"
    )
    final_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="مبلغ نهایی"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="وضعیت"
    )
    shipping_method = models.CharField(
        max_length=50,
        default='پست پیشتاز',
        verbose_name="روش ارسال"
    )
    delivery_time = models.CharField(
        max_length=50,
        default='۳ روز کاری',
        verbose_name="زمان تحویل"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="تاریخ ایجاد"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="تاریخ به‌روزرسانی"
    )
    tracking_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="شماره مرسوله"
    )
    payment_method = models.CharField(
        max_length=50,
        default='آنلاین',
        verbose_name="روش پرداخت"
    )
    payment_transaction_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="کد رهگیری پرداخت"
    )

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارشات"

    def __str__(self):
        return f"سفارش {self.order_number} - {self.user.username}"

    def generate_order_number(self):
        """تولید شماره سفارش منحصربه‌فرد با استفاده از UUID"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S%f')
        uuid_suffix = str(uuid.uuid4()).replace('-', '')[:12]
        order_number = f"ST-{timestamp}-{uuid_suffix}"
        return order_number

    def save(self, *args, **kwargs):
        """تضمین اینکه order_number همیشه یونیک باشه"""
        if not self.order_number:
            self.order_number = self.generate_order_number()
            counter = 1
            while Order.objects.filter(order_number=self.order_number).exclude(id=self.id).exists():
                uuid_suffix = str(uuid.uuid4()).replace('-', '')[:12]
                self.order_number = f"ST-{timezone.now().strftime('%Y%m%d%H%M%S%f')}-{uuid_suffix}"
                counter += 1
                if counter > 10:
                    raise ValueError("نمی‌توان شماره سفارش یونیک تولید کرد.")
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='orderitems',
        verbose_name="سفارش"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="محصول"
    )
    color = models.ForeignKey(
        Color,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="رنگ"
    )
    size = models.ForeignKey(
        Size,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="سایز"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="تعداد"
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="قیمت واحد"
    )
    discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="تخفیف"
    )

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

    def __str__(self):
        return f"{self.product.name} - تعداد: {self.quantity}"

    def get_total_price(self):
        """محاسبه قیمت کل آیتم با احتساب تخفیف"""
        unit_price = self.unit_price if self.unit_price is not None else 0
        discount = self.discount if self.discount is not None else 0
        return self.quantity * (unit_price - discount)

class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="کاربر"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="محصول"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ افزودن"
    )

    class Meta:
        verbose_name = "علاقه‌مندی"
        verbose_name_plural = "علاقه‌مندی‌ها"
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"