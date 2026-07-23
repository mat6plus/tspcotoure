from django.urls import path
from . import views_admin

app_name = 'cms-admin'

urlpatterns = [
    path('login/', views_admin.login_view, name='login'),
    path('logout/', views_admin.logout_view, name='logout'),
    path('', views_admin.dashboard, name='dashboard'),

    path('bespoke-requests/', views_admin.bespoke_request_list, name='bespoke_list'),
    path('bespoke-requests/<int:pk>/', views_admin.bespoke_request_detail, name='bespoke_detail'),

    path('garments/', views_admin.garment_list, name='garment_list'),
    path('garments/create/', views_admin.garment_create, name='garment_create'),
    path('garments/<int:pk>/edit/', views_admin.garment_edit, name='garment_edit'),
    path('garments/<int:pk>/delete/', views_admin.garment_delete, name='garment_delete'),

    path('testimonials/', views_admin.testimonial_list, name='testimonial_list'),
    path('testimonials/create/', views_admin.testimonial_create, name='testimonial_create'),
    path('testimonials/<int:pk>/edit/', views_admin.testimonial_edit, name='testimonial_edit'),
    path('testimonials/<int:pk>/delete/', views_admin.testimonial_delete, name='testimonial_delete'),

    # Bespoke Silhouettes
    path('silhouettes/', views_admin.silhouette_list, name='silhouette_list'),
    path('silhouettes/create/', views_admin.silhouette_create, name='silhouette_create'),
    path('silhouettes/<int:pk>/edit/', views_admin.silhouette_edit, name='silhouette_edit'),
    path('silhouettes/<int:pk>/delete/', views_admin.silhouette_delete, name='silhouette_delete'),

    # Fabric Swatches
    path('fabric-swatches/', views_admin.swatch_list, name='swatch_list'),
    path('fabric-swatches/create/', views_admin.swatch_create, name='swatch_create'),
    path('fabric-swatches/<int:pk>/edit/', views_admin.swatch_edit, name='swatch_edit'),
    path('fabric-swatches/<int:pk>/delete/', views_admin.swatch_delete, name='swatch_delete'),

    # Site Configuration
    path('site-configuration/', views_admin.site_configuration, name='site_configuration'),

    # Team & Access
    path('team/', views_admin.team_list, name='team_list'),
    path('team/create/', views_admin.team_create, name='team_create'),
    path('team/<int:pk>/edit/', views_admin.team_edit, name='team_edit'),
    path('team/<int:pk>/toggle-active/', views_admin.team_toggle_active, name='team_toggle_active'),
    path('team/<int:pk>/password/', views_admin.team_password, name='team_password'),
]
