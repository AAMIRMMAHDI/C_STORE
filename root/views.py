from django.shortcuts import render, redirect
from django.contrib import messages
from products.models import Product

def index(request):
    featured_products = Product.objects.filter(is_new=True)[:3]  # ۳ محصول جدید
    if not featured_products:
        featured_products = Product.objects.filter(discount_price__isnull=False)[:3]  # یا محصولات تخفیف‌دار
    return render(request, 'root/index.html', {'featured_products': featured_products})

from django.shortcuts import render, redirect
from .forms import ContactForm
from django.contrib import messages

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'پیام شما با موفقیت ارسال شد!')
            return redirect('root:contact')
    else:
        form = ContactForm()
    return render(request, 'root/contact.html', {'form': form})



from django.shortcuts import render
from .models import AboutSection

def about_view(request):
    sections = AboutSection.objects.filter(is_active=True).order_by('order')
    return render(request, 'root/about.html', {'sections': sections})