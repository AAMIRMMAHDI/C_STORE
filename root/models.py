from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام کامل")
    email = models.EmailField(verbose_name="ایمیل")
    phone = models.CharField(max_length=15, verbose_name="شماره تماس")
    subject = models.CharField(max_length=200, verbose_name="موضوع")
    message = models.TextField(verbose_name="پیام")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")

    class Meta:
        verbose_name = "پیام تماس"
        verbose_name_plural = "پیام‌های تماس"

    def __str__(self):
        return f"{self.name} - {self.subject}"
    



from django.db import models
from django.utils.translation import gettext_lazy as _

class AboutSection(models.Model):
    title = models.CharField(_("عنوان"), max_length=200)
    image = models.ImageField(_("تصویر"), upload_to='about/')
    content = models.TextField(_("محتوا"))
    order = models.PositiveIntegerField(_("ترتیب نمایش"), default=0)
    is_active = models.BooleanField(_("فعال"), default=True)

    class Meta:
        verbose_name = _("بخش درباره ما")
        verbose_name_plural = _("بخش‌های درباره ما")
        ordering = ['order']

    def __str__(self):
        return self.title