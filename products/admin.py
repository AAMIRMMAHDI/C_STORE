from django.contrib import admin
from .models import Product, ProductImage, Color, Size, ProductSpecification, Review, ShippingPolicy

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ColorInline(admin.TabularInline):
    model = Color
    extra = 1

class SizeInline(admin.TabularInline):
    model = Size
    extra = 1

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1

class ShippingPolicyInline(admin.TabularInline):
    model = ShippingPolicy
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'discount_price', 'stock_status', 'category', 'brand', 'is_new', 'views_count', 'sales_count']
    list_filter = ['category', 'brand', 'stock_status', 'is_new']
    search_fields = ['name', 'product_code', 'tags']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ColorInline, SizeInline, ProductSpecificationInline, ShippingPolicyInline]
    list_editable = ['stock_status', 'is_new']
    fields = ['name', 'slug', 'description', 'price', 'discount_price', 'stock_status', 'category', 'brand', 'product_code', 'tags', 'is_new', 'views_count', 'sales_count']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__name', 'user__username']