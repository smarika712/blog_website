from django.urls import path
from django.views.generic import RedirectView
from .import views

urlpatterns = [
    path('', views.home, name='home'),
    path('blog', RedirectView.as_view(url='/')),
    path('blog/add/', views.blog_add, name='blog_add'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('blog/<slug:slug>/edit/', views.blog_edit, name='blog_edit'),
    path('blog/<slug:slug>/delete/', views.blog_delete, name='blog_delete'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('refresh/', views.refresh_view, name='refresh'),
]