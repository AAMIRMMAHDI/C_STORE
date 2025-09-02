
from django.urls import path
from . import views

app_name = 'root'

urlpatterns = [
    path('', views.index, name='index'),
    path('contact/', views.contact_view, name='contact'),
    path('about/', views.about_view, name='about'),
    path('dashboard/upload-story/', views.dashboard_upload_story, name='dashboard_upload_story'),
    path('story/<int:story_id>/', views.get_story_data, name='get_story_data'),
    path('stories/', views.get_stories, name='stories'), 

    path('admin-panel/', views.dashboard, name='dashboard'),
    path('admin-panel/contacts/', views.contact_list, name='contact_list'),
    path('admin-panel/contacts/<int:pk>/', views.contact_detail, name='contact_detail'),
    path('admin-panel/about/', views.about_list, name='about_list'),
    path('admin-panel/about/<int:pk>/edit/', views.about_edit, name='about_edit'),
]