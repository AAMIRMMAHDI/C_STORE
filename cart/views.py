from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from .models import Cart, CartItem, Address, Order, OrderItem
from products.models import Product, Color, Size
from django.utils import timezone
from django.http import HttpResponse
import pdfkit
from django.template.loader import render_to_string

def get_or_merge_cart(request):
    """گرفتن یا ادغام سبد خرید برای کاربر یا جلسه"""
    if request.user.is_authenticated:
        carts = Cart.objects.filter(user=request.user)
        if carts.count() > 1:
            latest_cart = carts.latest('created_at')
            for cart in carts.exclude(id=latest_cart.id):
                latest_cart.merge_carts(cart)
            cart = latest_cart
        else:
            cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.session_key or request.session.create()
        carts = Cart.objects.filter(session_id=session_id)
        if carts.count() > 1:
            latest_cart = carts.latest('created_at')
            for cart in carts.exclude(id=latest_cart.id):
                latest_cart.merge_carts(cart)
            cart = latest_cart
        else:
            cart, _ = Cart.objects.get_or_create(session_id=session_id)
    return cart

def cart_detail(request):
    cart = get_or_merge_cart(request)
    cart_items = cart.cartitem_set.all()
    total_price = sum(item.get_total_price() for item in cart_items)
    total_discount = sum(item.get_discount() for item in cart_items)
    final_price = total_price - total_discount
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_discount': total_discount,
        'final_price': final_price,
    }
    return render(request, 'cart/cart.html', context)

def add_to_cart(request, slug):
    if request.method == 'POST':
        product = get_object_or_404(Product, slug=slug)
        if not product.stock_status:
            messages.error(request, 'محصول ناموجود است.')
            return redirect(product.get_absolute_url())
        
        color_hex = request.POST.get('color')
        size_name = request.POST.get('size')
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                messages.error(request, 'تعداد باید حداقل ۱ باشد.')
                return redirect(product.get_absolute_url())
        except ValueError:
            messages.error(request, 'تعداد نامعتبر است.')
            return redirect(product.get_absolute_url())

        color = Color.objects.filter(hex_code=color_hex, product=product).first() if color_hex else None
        size = Size.objects.filter(name=size_name, product=product, available=True).first() if size_name else None

        if not color and product.colors.exists():
            messages.error(request, 'لطفاً رنگ محصول را انتخاب کنید.')
            return redirect(product.get_absolute_url())
        if not size and product.sizes.exists():
            messages.error(request, 'لطفاً سایز محصول را انتخاب کنید.')
            return redirect(product.get_absolute_url())

        cart = get_or_merge_cart(request)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            color=color,
            size=size,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        product.sales_count += quantity
        product.save()
        messages.success(request, f'{product.name} به سبد خرید اضافه شد.')
        return redirect('cart:cart_detail')
    return redirect('products:product_list')

@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id)
        try:
            quantity = int(request.POST.get('quantity', 1))
            product = cart_item.product
            if quantity < 1:
                product.sales_count -= cart_item.quantity
                product.save()
                cart_item.delete()
                messages.success(request, 'محصول از سبد خرید حذف شد.')
            else:
                product.sales_count += (quantity - cart_item.quantity)
                product.save()
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, 'تعداد محصول به‌روزرسانی شد.')
        except ValueError:
            messages.error(request, 'تعداد نامعتبر است.')
        return redirect('cart:cart_detail')
    return redirect('cart:cart_detail')

@login_required
def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    product = cart_item.product
    product.sales_count -= cart_item.quantity
    product.save()
    cart_item.delete()
    messages.success(request, 'محصول از سبد خرید حذف شد.')
    return redirect('cart:cart_detail')

@login_required
def address(request):
    addresses = Address.objects.filter(user=request.user)
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        province = request.POST.get('province')
        city = request.POST.get('city')
        address_text = request.POST.get('address')
        postal_code = request.POST.get('postal_code')
        is_default = request.POST.get('is_default', False) == 'on'
        if all([full_name, phone_number, province, city, address_text, postal_code]):
            Address.objects.create(
                user=request.user,
                full_name=full_name,
                phone_number=phone_number,
                province=province,
                city=city,
                address=address_text,
                postal_code=postal_code,
                is_default=is_default
            )
            messages.success(request, 'آدرس جدید ثبت شد.')
            return redirect('cart:payment')
        else:
            messages.error(request, 'لطفاً همه فیلدها را پر کنید.')
    context = {'addresses': addresses}
    return render(request, 'cart/address.html', context)

@login_required
def payment(request):
    cart = get_or_merge_cart(request)
    cart_items = cart.cartitem_set.all()
    if not cart_items:
        messages.error(request, 'سبد خرید شما خالی است. لطفاً محصولی اضافه کنید.')
        return redirect('cart:cart_detail')

    total_price = sum(item.get_total_price() for item in cart_items)
    total_discount = sum(item.get_discount() for item in cart_items)
    final_price = total_price - total_discount
    address = Address.objects.filter(user=request.user, is_default=True).first() or Address.objects.filter(user=request.user).last()
    if not address:
        messages.error(request, 'لطفاً ابتدا یک آدرس ثبت کنید.')
        return redirect('cart:address')

    if request.method == 'POST':
        try:
            order = Order.objects.create(
                user=request.user,
                address=address,
                total_price=total_price,
                total_discount=total_discount,
                final_price=final_price,
                shipping_cost=0,
                status='PENDING',
                payment_method='آنلاین',
                payment_transaction_id=f"TRX-{timezone.now().strftime('%Y%m%d%H%M%S%f')}"
            )
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    color=item.color,
                    size=item.size,
                    quantity=item.quantity,
                    unit_price=item.product.discount_price or item.product.price,
                    discount=item.get_discount() / item.quantity if item.quantity else 0
                )
                item.product.sales_count += item.quantity
                item.product.save()
            cart.delete()
            messages.success(request, 'سفارش شما با موفقیت ثبت شد.')
            return redirect('cart:orders')
        except Exception as e:
            messages.error(request, f'خطا در ثبت سفارش: {str(e)}')
            return redirect('cart:payment')

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_discount': total_discount,
        'final_price': final_price,
        'address': address,
    }
    return render(request, 'cart/payment.html', context)

@login_required
def orders(request):
    status = request.GET.get('status', '')
    orders = Order.objects.filter(
        user=request.user,
        order_number__isnull=False,
        order_number__gt=''  # فیلتر کردن order_number غیرخالی
    ).order_by('-created_at')
    if status in ['PENDING', 'SHIPPED', 'DELIVERED', 'CANCELED']:
        orders = orders.filter(status=status)
    
    context = {
        'orders': orders,
        'current_status': status,
    }
    return render(request, 'cart/orders.html', context)

@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    context = {
        'order': order,
        'order_items': order.orderitems.all(),
    }
    return render(request, 'cart/order-detail.html', context)

@login_required
def cancel_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    if order.status in ['PENDING', 'SHIPPED']:
        order.status = 'CANCELED'
        order.save()
        messages.success(request, 'سفارش با موفقیت لغو شد.')
    else:
        messages.error(request, 'این سفارش قابل لغو نیست.')
    return redirect('cart:orders')

@login_required
def reorder(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    cart = get_or_merge_cart(request)
    for item in order.orderitems.all():
        if item.product.stock_status:
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=item.product,
                color=item.color,
                size=item.size,
                defaults={'quantity': item.quantity}
            )
            if not created:
                cart_item.quantity += item.quantity
                cart_item.save()
            item.product.sales_count += item.quantity
            item.product.save()
    messages.success(request, 'محصولات سفارش به سبد خرید اضافه شدند.')
    return redirect('cart:cart_detail')

@login_required
def track_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    context = {
        'order': order,
        'tracking_info': {
            'status': order.get_status_display(),
            'tracking_number': order.tracking_number,
            'last_updated': order.updated_at,
        }
    }
    return render(request, 'cart/track_order.html', context)

@login_required
def download_invoice(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    html = render_to_string('cart/invoice.html', {'order': order, 'order_items': order.orderitems.all()})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_number}.pdf"'
    pdfkit.from_string(html, response)
    return response