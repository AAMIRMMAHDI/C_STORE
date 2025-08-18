from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }




from django import forms
from .models import Story
from products.models import Product

class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['title', 'caption', 'file', 'product']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان استوری'}),
            'caption': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'توضیحات استوری', 'rows': 4}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*,video/*'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.all()
        self.fields['product'].empty_label = "انتخاب محصول (اختیاری)"