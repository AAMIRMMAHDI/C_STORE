from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg
from .models import Product, Review, Color, Size


def product_list(request):
    products = Product.objects.all()
    # فیلترها
    category = request.GET.get('category')
    color = request.GET.get('color')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    size = request.GET.get('size')
    brand = request.GET.get('brand')
    sort = request.GET.get('sort')

    if category and category != 'all':
        products = products.filter(category=category)
    if color:
        products = products.filter(colors__hex_code=color)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if size:
        products = products.filter(sizes__name=size, sizes__available=True)
    if brand and brand != 'all':
        products = products.filter(brand=brand)
    if sort == 'most_viewed':
        products = products.order_by('-views_count')
    elif sort == 'best_selling':
        products = products.order_by('-sales_count')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'cheapest':
        products = products.order_by('price')
    elif sort == 'most_expensive':
        products = products.order_by('-price')

    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'categories': Product.objects.values('category').distinct(),
        'colors': Color.objects.values('hex_code', 'name').distinct(),
        'sizes': Size.objects.filter(available=True).values('name').distinct(),
        'brands': Product.objects.values('brand').distinct(),
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product.views_count += 1
    product.save()

    # محاسبه میانگین امتیاز با گرد کردن به یک رقم اعشار
    avg_rating = product.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    avg_rating = round(avg_rating, 1)

    # محصولات مرتبط
    related_products = Product.objects.filter(category=product.category).exclude(slug=slug)[:4]

    context = {
        'product': product,
        'related_products': related_products,
        'avg_rating': avg_rating,
        # متغیرهای colors و sizes حذف شده‌اند زیرا مستقیماً در قالب استفاده می‌شوند
    }
    return render(request, 'products/product_detail.html', context)


@login_required
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        if rating and comment:
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    messages.error(request, 'امتیاز باید بین ۱ تا ۵ باشد.')
                else:
                    # بررسی اینکه کاربر قبلاً نظری برای این محصول ثبت نکرده باشد
                    if Review.objects.filter(product=product, user=request.user).exists():
                        messages.error(request, 'شما قبلاً برای این محصول نظر ثبت کرده‌اید.')
                    else:
                        Review.objects.create(
                            product=product,
                            user=request.user,
                            rating=rating,
                            comment=comment
                        )
                        messages.success(request, 'نظر شما با موفقیت ثبت شد.')
            except ValueError:
                messages.error(request, 'امتیاز نامعتبر است.')
        else:
            messages.error(request, 'لطفاً امتیاز و نظر خود را وارد کنید.')
    return redirect(product.get_absolute_url())