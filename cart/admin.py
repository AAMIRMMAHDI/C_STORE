from django.contrib import admin
from .models import Cart, CartItem, Address, Order, OrderItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_id', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'session_id']
    date_hierarchy = 'created_at'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'color', 'size', 'quantity', 'get_total_price']
    list_filter = ['cart', 'color', 'size']
    search_fields = ['product__name']
    list_select_related = ['cart', 'product', 'color', 'size']

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = 'قیمت کل'

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'phone_number', 'city', 'province', 'postal_code', 'is_default', 'created_at']
    list_filter = ['city', 'province', 'is_default', 'created_at']
    search_fields = ['user__username', 'full_name', 'address', 'postal_code']
    list_editable = ['is_default']
    date_hierarchy = 'created_at'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'color', 'size', 'quantity', 'unit_price', 'discount', 'get_total_price']
    readonly_fields = ['get_total_price']
    can_delete = True
    show_change_link = True

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = 'قیمت کل'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at', 'updated_at']
    search_fields = ['order_number', 'user__username']
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('order_number', 'user', 'status', 'payment_method', 'tracking_number')
        }),
        ('اطلاعات آدرس', {
            'fields': ('address', 'get_full_address'),
        }),
        ('اطلاعات مالی', {
            'fields': ('total_price', 'total_discount', 'shipping_cost', 'final_price'),
        }),
        ('محصولات', {
            'fields': ('get_products', 'get_items_count'),
        }),
        ('زمان‌بندی', {
            'fields': ('shipping_method', 'delivery_time', 'created_at', 'updated_at'),
        }),
        ('پرداخت', {
            'fields': ('payment_transaction_id',),
        }),
    )

    readonly_fields = ['get_products', 'get_items_count', 'get_full_address', 'created_at', 'updated_at']

    def get_products(self, obj):
        """نمایش نام محصولات در سفارش"""
        return ", ".join([item.product.name for item in obj.orderitems.all()])[:100]
    get_products.short_description = 'محصولات'

    def get_items_count(self, obj):
        """نمایش تعداد آیتم‌های سفارش"""
        return obj.orderitems.count()
    get_items_count.short_description = 'تعداد آیتم‌ها'

    def get_full_address(self, obj):
        """نمایش آدرس کامل"""
        if obj.address:
            return f"{obj.address.full_name}, {obj.address.address}, {obj.address.city}, {obj.address.province}"
        return "-"
    get_full_address.short_description = 'آدرس'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'color', 'size', 'quantity', 'unit_price', 'discount', 'get_total_price']
    list_filter = ['order', 'color', 'size']
    search_fields = ['product__name', 'order__order_number']
    list_select_related = ['order', 'product', 'color', 'size']

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = 'قیمت کل'