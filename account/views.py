from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, RegisterForm, ProfileForm, CustomPasswordChangeForm
from cart.models import Cart, CartItem, Order, Favorite
from django.contrib.auth.models import User
from products.models import Product
from django.http import HttpResponseRedirect

def login_view(request):
    if request.user.is_authenticated:
        return redirect('account:profile')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        # ادغام سبد خرید مهمان با کاربر
        session_cart, _ = Cart.objects.get_or_create(
            user=None,
            session_id=request.session.session_key or request.session.create()
        )
        user_cart, _ = Cart.objects.get_or_create(user=user)
        for item in session_cart.cartitem_set.all():
            user_item, created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=item.product,
                color=item.color,
                size=item.size,
                defaults={'quantity': item.quantity}
            )
            if not created:
                user_item.quantity += item.quantity
                user_item.save()
        session_cart.delete()
        messages.success(request, 'با موفقیت وارد شدید.')
        return redirect('account:profile')
    return render(request, 'account/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('account:profile')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        # ادغام سبد خرید مهمان با کاربر
        session_cart, _ = Cart.objects.get_or_create(
            user=None,
            session_id=request.session.session_key or request.session.create()
        )
        user_cart, _ = Cart.objects.get_or_create(user=user)
        for item in session_cart.cartitem_set.all():
            user_item, created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=item.product,
                color=item.color,
                size=item.size,
                defaults={'quantity': item.quantity}
            )
            if not created:
                user_item.quantity += item.quantity
                user_item.save()
        session_cart.delete()
        messages.success(request, 'ثبت‌نام با موفقیت انجام شد.')
        return redirect('account:profile')
    return render(request, 'account/register.html', {'form': form})

@login_required
def profile_view(request):
    addresses = request.user.address_set.all()
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'اطلاعات پروفایل به‌روزرسانی شد.')
            return redirect('account:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'account/profile.html', {'form': form, 'addresses': addresses})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'کلمه عبور با موفقیت تغییر کرد.')
            return redirect('account:profile')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'account/change_password.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'با موفقیت خارج شدید.')
    return redirect('products:product_list')

@login_required
def dashboard(request):
    orders = Order.objects.filter(user=request.user, order_number__isnull=False).order_by('-created_at')[:3]
    favorites_count = Favorite.objects.filter(user=request.user).count()
    comments_count = 0  # بعداً مدل نظرات رو اضافه کن
    credit = 250000  # بعداً از مدل کیف‌پول بگیر
    context = {
        'user': request.user,
        'orders': orders,
        'favorites_count': favorites_count,
        'comments_count': comments_count,
        'credit': credit,
    }
    return render(request, 'account/dashboard.html', context)

@login_required
def favorites(request):
    favorites = Favorite.objects.filter(user=request.user).order_by('-created_at')
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        product = get_object_or_404(Product, id=product_id)
        if action == 'add':
            Favorite.objects.get_or_create(user=request.user, product=product)
            messages.success(request, f'{product.name} به لیست علاقه‌مندی‌ها اضافه شد.')
        elif action == 'remove':
            Favorite.objects.filter(user=request.user, product=product).delete()
            messages.success(request, f'{product.name} از لیست علاقه‌مندی‌ها حذف شد.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'account:favorites'))
    return render(request, 'account/favorites.html', {'favorites': favorites})