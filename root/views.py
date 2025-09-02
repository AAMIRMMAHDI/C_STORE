from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Story, ContactMessage, AboutSection
from .forms import StoryForm, ContactForm
from products.models import Product
from django.http import JsonResponse

def staff_required(user):
    return user.is_staff

def index(request):
    stories = Story.objects.filter(is_active=True)
    featured_products = Product.objects.filter(is_featured=True)[:6]
    if not featured_products:
        featured_products = Product.objects.filter(is_new=True)[:6] 
        if not featured_products:
            featured_products = Product.objects.filter(discount_price__isnull=False)[:6] 
    context = {
        'stories': stories,
        'featured_products': featured_products,
    }
    return render(request, 'root/index.html', context)

def get_stories(request):
    stories = Story.objects.filter(is_active=True).values('id', 'title', 'file', 'caption')
    return JsonResponse(list(stories), safe=False)

@login_required
def dashboard_upload_story(request):
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.user = request.user
            story.save()
            messages.success(request, 'استوری با موفقیت آپلود شد!')
            return redirect('root:dashboard')
    else:
        form = StoryForm()
    return render(request, 'account/upload.html', {'form': form})

def get_story_data(request, story_id):
    try:
        story = Story.objects.get(id=story_id, is_active=True)
        data = {
            'id': story.id,
            'type': 'video' if story.file.name.lower().endswith(('.mp4', '.mov', '.avi')) else 'image',
            'src': story.file.url,
            'thumbnail': story.file.url,
            'title': story.title,
            'caption': story.caption,
            'product_url': story.product.get_absolute_url() if story.product else ''
        }
        return JsonResponse(data)
    except Story.DoesNotExist:
        return JsonResponse({'error': 'استوری یافت نشد'}, status=404)

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

def about_view(request):
    sections = AboutSection.objects.filter(is_active=True).order_by('order')
    return render(request, 'root/about.html', {'sections': sections})

@user_passes_test(staff_required)
@login_required
def dashboard(request):
    return render(request, "admin/root/dashboard.html")

@user_passes_test(staff_required)
@login_required
def contact_list(request):
    messages = ContactMessage.objects.all().order_by("-created_at")
    return render(request, "admin/root/contact_list.html", {"messages": messages})

@user_passes_test(staff_required)
@login_required
def contact_detail(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    return render(request, "admin/root/contact_detail.html", {"msg": msg})

@user_passes_test(staff_required)
@login_required
def about_list(request):
    sections = AboutSection.objects.all().order_by("order")
    return render(request, "admin/root/about_list.html", {"sections": sections})

@user_passes_test(staff_required)
@login_required
def about_edit(request, pk):
    section = get_object_or_404(AboutSection, pk=pk)
    if request.method == "POST":
        section.title = request.POST.get("title")
        section.content = request.POST.get("content")
        section.is_active = bool(request.POST.get("is_active"))
        section.save()
        messages.success(request, 'بخش درباره ما با موفقیت به‌روزرسانی شد!')
        return redirect("root:about_list")
    return render(request, "admin/root/about_edit.html", {"section": section})




