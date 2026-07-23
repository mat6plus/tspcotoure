# ROM Couture — Backend / Mini-CMS Implementation Spec

> **Purpose:** Django-powered admin backend for ROM Couture's static frontend.
> Enables the business owner to manage gallery images, view custom order submissions,
> update order status, and trigger email notifications — all without touching HTML.
>
> **Read this document fully before writing any code.** Every detail needed to
> build the complete backend is captured below. Follow the order specified.

---

## 1. Project Overview

### Directory Layout

```
rom_couture_main/
├── rom_couture_final/          # Static frontend — 7 HTML pages + JS + CSS
│   ├── index.html
│   ├── about.html
│   ├── gallery.html
│   ├── how-it-works.html
│   ├── custom-order.html
│   ├── 404.html
│   ├── shared.js
│   ├── security.js
│   └── styles.css
├── backend/                    # NEW — Django project root
│   ├── manage.py               # Django management script
│   ├── requirements.txt        # Python dependencies
│   ├── config/                 # Django project settings
│   │   ├── __init__.py
│   │   ├── settings.py         # Project settings (see §4)
│   │   ├── urls.py             # Root URL config
│   │   └── wsgi.py             # WSGI entry point
│   ├── cms/                    # The mini-CMS app (single app)
│   │   ├── __init__.py
│   │   ├── models.py           # §5 — Data models
│   │   ├── admin.py            # §6 — Admin configuration
│   │   ├── api.py              # §7 — API views (NO DRF)
│   │   ├── signals.py          # §9 — Email notification signals
│   │   ├── urls.py             # §8 — App URL routing
│   │   └── templates/          # Optional admin override templates
│   │       └── admin/
│   │           └── cms/
│   │               └── bespokerequest/
│   │                   └── change_list.html   # Custom admin list (see §6b)
│   └── media/                  # Uploaded images (garments, references)
│       └── garments/
│       └── references/
```

### Technology Choices

| Choice | Reason |
|--------|--------|
| **Django 5.x** | User preference, built-in admin, ORM, auth, email |
| **SQLite** | Zero config, sufficient for < 10k orders |
| **JsonResponse (no DRF)** | Only 5 simple endpoints, DRF is overkill |
| **Whitenoise** | Serves static files + frontend HTML from same Django process |
| **SendGrid / Mailgun SMTP** | Email delivery for notifications |
| **No Celery / No Redis** | Email sent synchronously (acceptable at this scale) |

---

## 2. Implementation Order

Build in this exact sequence — each step depends on the previous:

```
 1. Create Django project + app scaffold
 2. Write requirements.txt
 3. Write config/settings.py
 4. Write cms/models.py
 5. Run makemigrations + migrate
 6. Write cms/admin.py
 7. Write cms/signals.py (connect in apps.py)
 8. Write cms/api.py
 9. Write cms/urls.py
10. Write config/urls.py (root)
11. Create superuser
12. Test admin panel at /admin/
13. Create media directories
14. Modify custom-order.html to POST to API
15. Modify gallery.html to fetch from API
16. Test end-to-end
```

---

## 3. Dependencies (`requirements.txt`)

```txt
Django>=5.0,<5.1
django-cors-headers>=4.0
Pillow>=10.0
python-decouple>=3.8
whitenoise>=6.0
gunicorn>=21.0
```

Only `django-cors-headers` is extra (for development when frontend and backend run on different ports). Pillow handles image uploads. Whitenoise serves static/media in production. `python-decouple` for environment variables (email credentials, secret key).

---

## 4. Django Settings (`config/settings.py`)

### 4a. Basic Configuration

```python
import os
from decouple import config
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # /backend/

SECRET_KEY = config('DJANGO_SECRET_KEY', default='change-this-in-production')

DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')
```

### 4b. Installed Apps

```python
INSTALLED_APPS = [
    # Django built-in
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'corsheaders',
    # Local
    'cms',
]
```

### 4c. Middleware

```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',          # MUST be first
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',     # MUST be after security
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### 4d. CORS (Development)

For development, allow the frontend dev server:

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8001',      # Static frontend server
    'http://127.0.0.1:8001',
]

CORS_ALLOW_CREDENTIALS = True
```

For production, replace with the actual domain:

```python
# CORS_ALLOWED_ORIGINS = ['https://romcouture.com']
```

### 4e. Database

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 4f. Static & Media Files

```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 4g. Frontend Static Files

To serve the existing static frontend from the same Django server (production convenience):

```python
# Optional — serve the static site from Django
# Copy rom_couture_final/ contents into backend/staticfrontend/
# Or configure nginx to serve it. During development, use separate servers.
```

Keep frontend and backend on separate servers during development:
- Frontend: `python3 -m http.server 8001`
- Backend:  `python3 manage.py runserver 8000`

For production, use Whitenoise to serve the frontend HTML from Django, or use a reverse proxy (Caddy/Nginx) to serve static files and proxy `/api/` and `/admin/` to Django.

### 4h. Email Configuration

```python
# Email (use environment variables in production)
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.sendgrid.net')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='apikey')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='bespoke@romcouture.com')

# Admin notification recipients
ADMINS = [
    ('Owner', config('ADMIN_EMAIL', default='owner@romcouture.com')),
]
```

For development, default to console backend (emails print to terminal):

```bash
# .env file
DJANGO_SECRET_KEY=dev-secret-key-change-in-production
DJANGO_DEBUG=True
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### 4i. Internationalization

```python
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
```

### 4j. Default Primary Key

```python
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

---

## 5. Data Models (`cms/models.py`)

### 5a. Garment Model

Represents a single gallery piece — an image with metadata that appears on the gallery page.

```python
from django.db import models
from django.utils.text import slugify

class Garment(models.Model):
    CATEGORY_CHOICES = [
        ('traditional', 'Traditional Attire'),
        ('shirts', 'Shirts'),
        ('caps', 'Caps'),
        ('sets', 'Sets'),
    ]

    title = models.CharField(max_length=200, verbose_name='Garment Title')
    slug = models.SlugField(max_length=200, unique=True, blank=True,
                            help_text='Auto-generated from title if left blank')
    description = models.TextField(blank=True,
                                   help_text='Short description for alt text and captions')
    image = models.ImageField(upload_to='garments/',
                              help_text='Upload high-resolution image (JPEG/PNG/WebP)')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='traditional')
    is_featured = models.BooleanField(default=False,
                                      help_text='Show in homepage social grid')
    is_published = models.BooleanField(default=True,
                                       help_text='Unpublish to hide from gallery')
    sort_order = models.PositiveIntegerField(default=0,
                                             help_text='Lower numbers appear first')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', '-created_at']
        verbose_name = 'Garment'
        verbose_name_plural = 'Garments'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
```

### 5b. BespokeRequest Model

Captures every custom order form submission from the custom-order.html page.

```python
class BespokeRequest(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # Contact
    name = models.CharField(max_length=200, verbose_name='Full Name')
    email = models.EmailField(verbose_name='Email Address')
    phone = models.CharField(max_length=50, verbose_name='Phone Number')

    # Garment selection (from step 2 radio buttons)
    garment_type = models.CharField(max_length=200, blank=True,
                                    verbose_name='Selected Garment')

    # Measurements (step 3) — NULL if not provided
    chest = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    waist = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    shoulder = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    sleeve = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    neck = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    length = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)

    # Fit & sizing references
    standard_size = models.CharField(max_length=50, blank=True,
                                     verbose_name='Standard Clothing Size')
    height = models.CharField(max_length=50, blank=True,
                              verbose_name='Body Height')

    # Style & fabric (steps 2 & 4)
    fabrics = models.TextField(blank=True,
                               verbose_name='Selected Fabrics',
                               help_text='Comma-separated fabric names')
    color_notes = models.TextField(blank=True, verbose_name='Color Preferences')
    inspiration_notes = models.TextField(blank=True, verbose_name='Inspiration & Design Thoughts')
    fit_notes = models.TextField(blank=True, verbose_name='Fit Preferences')

    # File upload (reference drawings)
    reference_file = models.FileField(upload_to='references/', blank=True, null=True,
                                      verbose_name='Reference Drawing/Sketch')

    # Pinterest link (step 1)
    pinterest_link = models.URLField(blank=True, verbose_name='Pinterest Board Link')

    # Status & admin
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True,
                                   verbose_name='Admin Notes',
                                   help_text='Internal notes visible only in admin')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Agreements (stored as boolean)
    agreed_no_returns = models.BooleanField(default=False,
                                            verbose_name='Agreed to No-Returns Policy')
    agreed_offline_payment = models.BooleanField(default=False,
                                                  verbose_name='Agreed to Offline Payment')
    agreed_consultation = models.BooleanField(default=False,
                                              verbose_name='Agreed to Consultation Follow-up')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Bespoke Request'
        verbose_name_plural = 'Bespoke Requests'

    def __str__(self):
        return f'{self.name} — {self.garment_type or "Custom Design"} ({self.get_status_display()})'
```

### 5c. Testimonial Model (Optional)

```python
class Testimonial(models.Model):
    author_name = models.CharField(max_length=200, verbose_name='Author Name')
    author_location = models.CharField(max_length=100, blank=True,
                                       verbose_name='Location (e.g. New York)')
    text = models.TextField(verbose_name='Testimonial Text')
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', '-created_at']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'

    def __str__(self):
        return f'{self.author_name} — {self.text[:50]}...'
```

---

## 6. Admin Configuration (`cms/admin.py`)

### 6a. Garment Admin

```python
from django.contrib import admin
from .models import Garment, BespokeRequest, Testimonial

@admin.register(Garment)
class GarmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'sort_order', 'is_featured', 'is_published', 'created_at']
    list_filter = ['category', 'is_featured', 'is_published']
    search_fields = ['title', 'description']
    list_editable = ['sort_order', 'is_featured', 'is_published']
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = [
        ('Basic Info', {
            'fields': ['title', 'slug', 'description', 'category']
        }),
        ('Media', {
            'fields': ['image']
        }),
        ('Visibility & Order', {
            'fields': ['is_featured', 'is_published', 'sort_order']
        }),
    ]
```

### 6b. BespokeRequest Admin

This is the most important admin view — the owner will spend most of their time here.

```python
@admin.register(BespokeRequest)
class BespokeRequestAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'garment_type', 'status', 'created_at', 'email_link'
    ]
    list_filter = ['status', 'created_at', 'garment_type']
    search_fields = ['name', 'email', 'phone', 'garment_type']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        ('Contact Information', {
            'fields': ['name', 'email', 'phone']
        }),
        ('Garment & Style', {
            'fields': ['garment_type', 'fabrics', 'color_notes',
                       'inspiration_notes', 'fit_notes']
        }),
        ('Measurements', {
            'fields': ['chest', 'waist', 'shoulder', 'sleeve', 'neck', 'length',
                       'standard_size', 'height'],
            'classes': ['collapse'],   # Collapsed by default
        }),
        ('References', {
            'fields': ['pinterest_link', 'reference_file'],
            'classes': ['collapse'],
        }),
        ('Agreements', {
            'fields': ['agreed_no_returns', 'agreed_offline_payment', 'agreed_consultation'],
        }),
        ('Status & Admin', {
            'fields': ['status', 'admin_notes', 'created_at', 'updated_at'],
        }),
    ]

    actions = ['mark_as_in_progress', 'mark_as_completed', 'send_test_email']

    def email_link(self, obj):
        return f'<a href="mailto:{obj.email}">{obj.email}</a>'
    email_link.allow_tags = True
    email_link.short_description = 'Email'

    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} request(s) marked as In Progress.')
    mark_as_in_progress.short_description = 'Mark selected as In Progress'

    def mark_as_completed(self, request, queryset):
        for obj in queryset:
            obj.status = 'completed'
            obj.save(update_fields=['status'])
            # Send notification email (see §9)
        self.message_user(request, f'{queryset.count()} request(s) marked as Completed. '
                                    'Emails will be sent.')
    mark_as_completed.short_description = 'Mark selected as Completed (sends email)'
```

**Custom list template** — Add a summary header at the top of the change list.

Create `cms/templates/admin/cms/bespokerequest/change_list.html`:

```html
{% extends "admin/change_list.html" %}
{% load i18n admin_urls %}

{% block content_title %}
    <h1>Bespoke Requests</h1>
    <div style="margin-bottom: 16px; padding: 12px 16px; background: #f8f9fa; border-radius: 4px; border-left: 4px solid #914325;">
        <strong>Summary:</strong>
        {% with status_counts as counts %}
            New: {{ counts.new|default:0 }} |
            In Progress: {{ counts.in_progress|default:0 }} |
            Completed: {{ counts.completed|default:0 }} |
            Cancelled: {{ counts.cancelled|default:0 }}
        {% endwith %}
    </div>
{% endblock %}

{% block result_list %}
    {{ block.super }}
{% endblock %}
```

Add the status_counts context by overriding `changelist_view`:

```python
class BespokeRequestAdmin(admin.ModelAdmin):
    # ... (existing config above)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['status_counts'] = {
            s: BespokeRequest.objects.filter(status=s).count()
            for s, _ in BespokeRequest.STATUS_CHOICES
        }
        return super().changelist_view(request, extra_context=extra_context)
```

### 6c. Testimonial Admin

```python
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'author_location', 'is_published', 'sort_order']
    list_filter = ['is_published']
    list_editable = ['is_published', 'sort_order']
    search_fields = ['author_name', 'text']
```

### 6d. Connecting Signals

Create `cms/apps.py` to register signals:

```python
# cms/apps.py
from django.apps import AppConfig

class CmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cms'

    def ready(self):
        import cms.signals  # noqa
```

Update `cms/__init__.py`:

```python
default_app_config = 'cms.apps.CmsConfig'
```

---

## 7. Email & Signals (`cms/signals.py`)

### 7a. New Order → Notify Admin

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import mail_admins
from django.template.loader import render_to_string
from .models import BespokeRequest

@receiver(post_save, sender=BespokeRequest)
def notify_admin_new_request(sender, instance, created, **kwargs):
    """
    When a new BespokeRequest is created (from the public API), send an email
    to the site admin(s) with the order summary.
    """
    if not created:
        return

    subject = f'New Bespoke Request: {instance.name} — {instance.garment_type or "Custom"}'

    message = render_to_string('cms/emails/new_request_admin.txt', {
        'request': instance,
        'admin_url': 'http://localhost:8000/admin/cms/bespokerequest/{}/change/'.format(instance.pk),
    })

    mail_admins(subject, message)
```

### 7b. Admin Action → Notify Customer (on completion)

This is triggered from the admin action `mark_as_completed`. In `admin.py`, modify the action:

```python
from django.core.mail import send_mail
from django.template.loader import render_to_string

def mark_as_completed(self, request, queryset):
    for obj in queryset:
        old_status = obj.status
        obj.status = 'completed'
        obj.save(update_fields=['status'])

        # Only send email if transitioning FROM a non-completed status
        if old_status != 'completed':
            self._send_completion_email(obj)

    self.message_user(request, f'{queryset.count()} request(s) marked as Completed.')

def _send_completion_email(self, obj):
    subject = f'Your ROM Couture Bespoke Order is Ready'
    message = render_to_string('cms/emails/order_completed_customer.txt', {
        'request': obj,
    })
    send_mail(
        subject,
        message,
        None,  # uses DEFAULT_FROM_EMAIL
        [obj.email],
        fail_silently=True,
    )
```

### 7c. Email Templates

Create `cms/templates/cms/emails/` directory.

**`new_request_admin.txt`:**

```
New Bespoke Request
══════════════════════════════════════

From: {{ request.name }}
Email: {{ request.email }}
Phone: {{ request.phone }}

Garment: {{ request.garment_type|default:"Custom Design" }}
Fabrics: {{ request.fabrics|default:"Not specified" }}
Status: {{ request.get_status_display }}

View in Admin:
{{ admin_url }}
```

**`order_completed_customer.txt`:**

```
ROM Couture — Your Bespoke Order is Ready
══════════════════════════════════════════

Dear {{ request.name }},

Your custom garment is ready! Our atelier team has completed work on your order.

Garment: {{ request.garment_type|default:"Custom Design" }}

Your next steps:
1. We will contact you at {{ request.phone }} to arrange delivery or pickup.
2. Your garment will arrive in our signature keepsake box.
3. If any final adjustments are needed, we will arrange a fitting session.

Thank you for choosing ROM Couture.

— The ROM Couture Atelier Team
New York · London · Lagos
```

---

## 8. API Views (`cms/api.py`)

No Django REST Framework. Use `django.http.JsonResponse` with `@csrf_exempt` and `@require_http_methods`.

### 8a. API Utility

```python
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
```

### 8b. Garment List (Public)

**URL:** `GET /api/garments/`

Returns all published garments. Used by `gallery.html` to render the gallery grid.

```python
@require_http_methods(['GET'])
def garment_list(request):
    garments = Garment.objects.filter(is_published=True)
    data = []
    for g in garments:
        data.append({
            'id': g.id,
            'title': g.title,
            'slug': g.slug,
            'description': g.description,
            'image_url': g.image.url if g.image else '',
            'category': g.category,
            'is_featured': g.is_featured,
        })
    return JsonResponse({'garments': data})
```

### 8c. Testimonial List (Public)

**URL:** `GET /api/testimonials/`

```python
@require_http_methods(['GET'])
def testimonial_list(request):
    testimonials = Testimonial.objects.filter(is_published=True)
    data = []
    for t in testimonials:
        data.append({
            'id': t.id,
            'author_name': t.author_name,
            'author_location': t.author_location,
            'text': t.text,
        })
    return JsonResponse({'testimonials': data})
```

### 8d. Create Bespoke Request (Public)

**URL:** `POST /api/bespoke-requests/`

This is called by `custom-order.html` when the user submits the form.
The form data is sent as `application/json` in the request body.

```python
@csrf_exempt
@require_http_methods(['POST'])
def create_bespoke_request(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # Validate required fields
    required = ['name', 'email', 'phone']
    for field in required:
        if not data.get(field):
            return JsonResponse({'error': f'{field} is required'}, status=400)

    # Validate email format
    if '@' not in data.get('email', ''):
        return JsonResponse({'error': 'Invalid email address'}, status=400)

    # Create the request
    bespoke = BespokeRequest.objects.create(
        name=data.get('name', ''),
        email=data.get('email', ''),
        phone=data.get('phone', ''),

        # Optional fields — map from frontend form field names to model fields
        garment_type=data.get('garment_type', ''),
        fabrics=data.get('fabrics', ''),
        color_notes=data.get('color_notes', ''),
        inspiration_notes=data.get('inspiration_notes', ''),
        fit_notes=data.get('fit_notes', ''),

        # Measurements
        chest=_safe_decimal(data.get('chest')),
        waist=_safe_decimal(data.get('waist')),
        shoulder=_safe_decimal(data.get('shoulder')),
        sleeve=_safe_decimal(data.get('sleeve')),
        neck=_safe_decimal(data.get('neck')),
        length=_safe_decimal(data.get('length')),

        standard_size=data.get('standard_size', ''),
        height=data.get('height', ''),
        pinterest_link=data.get('pinterest_link', ''),

        # Agreements
        agreed_no_returns=data.get('agreed_no_returns', False),
        agreed_offline_payment=data.get('agreed_offline_payment', False),
        agreed_consultation=data.get('agreed_consultation', False),
    )

    return JsonResponse({
        'success': True,
        'id': bespoke.pk,
        'message': 'Your bespoke request has been received. Our team will contact you within 24 hours.',
    }, status=201)


def _safe_decimal(value):
    """Convert a value to Decimal or None if empty/invalid."""
    if not value:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
```

### 8e. Image Upload for Bespoke Requests

For file uploads (reference drawings), the frontend should first upload the file
via a separate endpoint, then include the returned URL in the main request.

**URL:** `POST /api/upload/`

```python
@csrf_exempt
@require_http_methods(['POST'])
def upload_file(request):
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    uploaded = request.FILES['file']

    # Validate file type
    allowed_types = ['image/png', 'image/jpeg', 'image/webp', 'image/jpg', 'application/pdf']
    if uploaded.content_type not in allowed_types:
        return JsonResponse({'error': 'Invalid file type. PNG, JPG, WebP, and PDF allowed.'}, status=400)

    # Validate file size (10MB max)
    if uploaded.size > 10 * 1024 * 1024:
        return JsonResponse({'error': 'File too large. Maximum 10MB.'}, status=400)

    filename = default_storage.save(f'references/{uploaded.name}', uploaded)
    url = default_storage.url(filename)

    return JsonResponse({
        'success': True,
        'url': url,
        'filename': filename,
    })
```

### 8f. Health Check (Optional)

**URL:** `GET /api/health/`

```python
@require_http_methods(['GET'])
def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'ROM Couture CMS'})
```

---

## 9. URL Routing

### 9a. App URLs (`cms/urls.py`)

```python
from django.urls import path
from . import api

urlpatterns = [
    path('garments/', api.garment_list, name='api-garment-list'),
    path('testimonials/', api.testimonial_list, name='api-testimonial-list'),
    path('bespoke-requests/', api.create_bespoke_request, name='api-create-bespoke-request'),
    path('upload/', api.upload_file, name='api-upload-file'),
    path('health/', api.health_check, name='api-health'),
]
```

### 9b. Root URLs (`config/urls.py`)

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('cms.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 10. Frontend Integration

### 10a. Gallery Page (`rom_couture_final/gallery.html`)

**What changes:** Replace the hardcoded gallery cards with dynamic fetch.

**Approach:**

1. Keep the HTML structure for the container (`#gallery-grid`)
2. Remove all hardcoded `<a>` cards inside it (except keep the filter buttons)
3. On page load, fetch from `http://localhost:8000/api/garments/` and render cards

**JS to add** (inside the existing `<script>` block, before the reveal observer):

```javascript
// Fetch garments from backend API
(function () {
    var grid = document.getElementById('gallery-grid');
    if (!grid) return;

    var apiUrl = 'http://localhost:8000/api/garments/';

    // In production, use relative URL:
    // var apiUrl = '/api/garments/';

    fetch(apiUrl)
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (!data.garments || data.garments.length === 0) return;

            // Clear existing placeholder cards (if any)
            // grid.innerHTML = '';

            data.garments.forEach(function (g, i) {
                var delay = (i * 0.1).toFixed(1) + 's';
                var card = document.createElement('a');
                card.href = 'custom-order.html?garment=' + encodeURIComponent(g.title);
                card.className = 'masonry-item reveal group block overflow-hidden bg-white atelier-shadow hover-lift';
                card.style.transitionDelay = delay;
                card.setAttribute('data-category', g.category);

                // Build the card HTML
                // IMPORTANT: Use SecurityUtils.safeRender for any user-provided text
                card.innerHTML =
                    '<div class="relative overflow-hidden aspect-[3/4]">' +
                        '<img alt="' + (SecurityUtils ? SecurityUtils.sanitizeInput(g.description || g.title) : g.title) + '" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" src="' + g.image_url + '" loading="lazy"/>' +
                        '<div class="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 flex items-end p-4">' +
                            '<span class="bg-white/90 text-primary px-3 py-1.5 font-label-caps text-[10px] rounded-sm flex items-center gap-1.5 shadow-sm">' +
                                '<span class="material-symbols-outlined text-[12px]">verified</span> Made-to-Measure' +
                            '</span>' +
                        '</div>' +
                    '</div>' +
                    '<div class="p-5 flex justify-between items-center">' +
                        '<h3 class="font-headline-sm text-headline-sm text-on-surface">' + (SecurityUtils ? SecurityUtils.sanitizeInput(g.title) : g.title) + '</h3>' +
                        '<span class="material-symbols-outlined text-primary group-hover:translate-x-1 transition-transform text-lg">arrow_forward</span>' +
                    '</div>';

                grid.appendChild(card);
            });

            // Re-initialize IntersectionObserver for new cards
            // (The existing observer at the bottom of the page handles this if it runs AFTER this fetch)
            // If fetch completes after observer runs, manually observe new cards:
            if (window.revealObserver) {
                grid.querySelectorAll('.reveal').forEach(function (el) {
                    window.revealObserver.observe(el);
                });
            }
        })
        .catch(function (err) {
            console.warn('Could not load garments from CMS:', err);
            // Keep hardcoded fallback cards if fetch fails
        });
})();
```

**Important:** The IntersectionObserver at the bottom of gallery.html needs to be stored in a variable so it can be reused:

```javascript
// Change from:
// (function () { var els = ...; var obs = ...
// To:
window.revealObserver = null;
(function () {
    var els = document.querySelectorAll('.reveal, ...');
    if ('IntersectionObserver' in window) {
        var obs = new IntersectionObserver(function (entries, observer) {
            // ... same code ...
        }, { ... });
        window.revealObserver = obs;
        els.forEach(function (el) { obs.observe(el); });
    }
})();
```

Also add the container's `id="gallery-grid"` with a data attribute to indicate it should be populated from the API:

```html
<div class="masonry-grid gap-6" id="gallery-grid" data-source="api"></div>
```

When `data-source="api"` is present, the JS clears any hardcoded children before rendering API results.

### 10b. Custom Order Page (`rom_couture_final/custom-order.html`)

**What changes:** On successful form submission, POST data to Django API instead of showing local success state.

**Approach:**

Replace the form submission handler's final `setTimeout` block (lines ~909-923) with an API call:

```javascript
// In the existing form submit handler (around line 884-923),
// replace the setTimeout success simulation with:

if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="material-symbols-outlined text-[18px]" style="animation:spin 1s linear infinite">sync</span>&nbsp;Submitting\u2026';
}

// Collect form data
var formData = {
    name: document.getElementById('client-name')?.value || '',
    email: document.getElementById('client-email')?.value || '',
    phone: document.getElementById('client-phone')?.value || '',
    garment_type: document.querySelector('input[name="garment"]:checked')?.value || '',
    fabrics: document.getElementById('selected-fabrics-hidden')?.value || '',
    color_notes: document.getElementById('color-notes')?.value || '',
    inspiration_notes: document.getElementById('inspiration-notes')?.value || '',
    fit_notes: document.getElementById('fit-notes')?.value || '',
    chest: document.getElementById('size-chest')?.value || '',
    waist: document.getElementById('size-waist')?.value || '',
    shoulder: document.getElementById('size-shoulder')?.value || '',
    sleeve: document.getElementById('size-sleeve')?.value || '',
    neck: document.getElementById('size-neck')?.value || '',
    length: document.getElementById('size-length')?.value || '',
    standard_size: document.getElementById('usual-clothing-size')?.value || '',
    height: document.getElementById('client-height')?.value || '',
    pinterest_link: document.getElementById('pinterest-link')?.value || '',
    agreed_no_returns: document.getElementById('agree-no-returns')?.checked || false,
    agreed_offline_payment: document.getElementById('agree-offline-payment')?.checked || false,
    agreed_consultation: document.getElementById('agree-consultation')?.checked || false,
};

var apiUrl = 'http://localhost:8000/api/bespoke-requests/';
// In production: var apiUrl = '/api/bespoke-requests/';

fetch(apiUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData),
})
.then(function (r) { return r.json(); })
.then(function (data) {
    if (data.success) {
        // Show success state (same as before)
        document.querySelectorAll('.step-content').forEach(function (el) { el.classList.remove('active'); });
        if (formNavControls) formNavControls.classList.add('hidden');
        var aside = document.querySelector('aside');
        if (aside) aside.classList.add('hidden');
        var col = document.querySelector('.lg\\:col-span-9');
        if (col) { col.classList.remove('lg:col-span-9'); col.classList.add('lg:col-span-12'); }
        sessionStorage.removeItem('rc_wizard_step');
        if (successState) {
            successState.classList.remove('hidden');
            successState.style.animation = 'stepFadeIn 0.5s ease forwards';
        }
        smoothScrollToForm();
    } else {
        // Show error
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Submit Couture Request <span class="material-symbols-outlined text-[18px]">verified</span>';
        }
        var errMsg = data.error || 'An error occurred. Please try again.';
        alert(errMsg);  // Or show inline
    }
})
.catch(function () {
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Submit Couture Request <span class="material-symbols-outlined text-[18px]">verified</span>';
    }
    alert('Could not connect to server. Please try again later.');
});
```

Make sure these changes are made to the existing submit handler:

1. **Remove** the `lastFormSubmit` throttle (or keep it — 5s debounce is fine)
2. **Replace** the `setTimeout(function () { ... show success ... }, 1800)` block with the `fetch` call above
3. **Keep** the validation logic (line 890-904) that checks agreements
4. **Keep** the `generateBespokeSummary()` call from updateWizardUI

### 10c. Homepage Testimonials (`rom_couture_final/index.html`)

**Optional:** Fetch testimonials from API for dynamic updates.

Add a fetch block before the existing testimonial carousel code (around line 315):

```javascript
(function () {
    var apiUrl = 'http://localhost:8000/api/testimonials/';
    // In production: var apiUrl = '/api/testimonials/';

    fetch(apiUrl)
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (!data.testimonials || data.testimonials.length === 0) return;
            var slides = document.querySelectorAll('.testimonial-slide');
            if (slides.length !== data.testimonials.length) return; // HTML structure must match

            data.testimonials.forEach(function (t, i) {
                var slide = slides[i];
                if (!slide) return;
                var p = slide.querySelector('p');
                var span = slide.querySelector('span.font-label-caps');
                if (p) {
                    p.textContent = '"' + (SecurityUtils ? SecurityUtils.sanitizeInput(t.text) : t.text) + '"';
                }
                if (span) {
                    span.textContent = '— ' + (SecurityUtils ? SecurityUtils.sanitizeInput(t.author_name) : t.author_name) + (t.author_location ? ', ' + t.author_location : '');
                }
            });
        })
        .catch(function () { /* Keep hardcoded testimonials */ });
})();
```

Add this BEFORE the existing carousel initialization code (the `show(0); start();` block).

### 10d. CORS Note

During development:
- Frontend runs on `http://localhost:8001`
- Backend runs on `http://localhost:8000`
- Fetch calls use full URL: `http://localhost:8000/api/...`
- CORS must be configured (see §4d)

In production:
- Both served from same domain via nginx/Caddy/Whitenoise
- Fetch calls use relative URLs: `/api/...`
- No CORS needed

---

## 11. Running the Backend

### 11a. Setup Commands

```bash
# From the backend/ directory

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations cms
python manage.py migrate

# Create superuser (follow prompts)
python manage.py createsuperuser

# Run development server (on port 8000)
python manage.py runserver 8000
```

### 11b. Production Notes

For production deployment, switch from console email to SMTP:

```bash
# .env file (production)
DJANGO_SECRET_KEY=your-production-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=romcouture.com,www.romcouture.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.your-sendgrid-api-key
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=bespoke@romcouture.com
ADMIN_EMAIL=owner@romcouture.com
```

Run with Gunicorn:

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2
```

### 11c. Media Directory

Create the media directories before first upload:

```bash
mkdir -p media/garments media/references
```

Add a `.gitkeep` to each so they're tracked:

```bash
touch media/garments/.gitkeep media/references/.gitkeep
```

Add `media/` to `.gitignore` if you don't want uploaded files in version control:

```
# .gitignore
*.pyc
__pycache__/
db.sqlite3
venv/
media/garments/
media/references/
.env
```

---

## 12. Testing Checklist

After building, verify each of these:

### Admin Panel
- [ ] `GET /admin/` loads login page
- [ ] Login with superuser credentials works
- [ ] Garment list shows all fields, filtering works by category
- [ ] Upload a new garment image (JPEG/PNG/WebP)
- [ ] Bespoke Request list shows all submissions with filters
- [ ] Click into a Bespoke Request detail — all fields display
- [ ] Change status dropdown works
- [ ] "Mark as Completed" action works from list
- [ ] Testimonial CRUD works

### API Endpoints
- [ ] `GET /api/garments/` returns JSON with published garments
- [ ] `GET /api/testimonials/` returns JSON with published testimonials
- [ ] `POST /api/bespoke-requests/` with valid JSON returns 201
- [ ] `POST /api/bespoke-requests/` with missing fields returns 400
- [ ] `GET /api/health/` returns `{"status": "ok"}`
- [ ] `POST /api/upload/` with a valid image returns success

### Email
- [ ] Creating a BespokeRequest via API prints email to console (dev)
- [ ] "Mark as Completed" action prints customer email to console (dev)

### Frontend Integration
- [ ] Gallery page loads cards from API (check network tab)
- [ ] Gallery falls back gracefully if API is unavailable
- [ ] Custom order form POSTs to API on submit
- [ ] Success state shows after API submission
- [ ] Form validation still works before API call

### Static Frontend (unchanged)
- [ ] All 7 HTML pages load without errors
- [ ] Mobile drawer opens/closes
- [ ] Gallery filter tabs work
- [ ] Form wizard navigation works
- [ ] Testimonial carousel auto-rotates

---

## 13. Frontend Changes Summary

| File | Change | Complexity |
|------|--------|------------|
| `rom_couture_final/gallery.html` | Fetch garments from API, render dynamically | Medium |
| `rom_couture_final/custom-order.html` | POST form to API instead of local success | Medium |
| `rom_couture_final/index.html` | Optional: fetch testimonials from API | Low |
| `rom_couture_final/shared.js` | No changes needed | None |
| `rom_couture_final/security.js` | No changes needed | None |
| `rom_couture_final/styles.css` | No changes needed | None |
| `rom_couture_final/*.html` (other pages) | No changes needed | None |

---

## 14. File Reference

Every file to create in the `backend/` directory:

```
backend/
├── .env                          # Environment variables (gitignored)
├── .gitignore                    # Python + media + db
├── requirements.txt              # See §3
├── manage.py                     # Django's manage.py
├── config/
│   ├── __init__.py
│   ├── settings.py               # See §4
│   ├── urls.py                   # See §9b
│   └── wsgi.py                   # Django default
├── cms/
│   ├── __init__.py
│   ├── apps.py                   # See §6d
│   ├── models.py                 # See §5
│   ├── admin.py                  # See §6
│   ├── api.py                    # See §8
│   ├── signals.py                # See §7a
│   ├── urls.py                   # See §9a
│   └── templates/
│       ├── admin/cms/bespokerequest/
│       │   └── change_list.html  # See §6b
│       └── cms/emails/
│           ├── new_request_admin.txt        # See §7c
│           └── order_completed_customer.txt  # See §7c
└── media/
    ├── .gitkeep
    ├── garments/
    │   └── .gitkeep
    └── references/
        └── .gitkeep
```

---

## 15. Visual Identity for Admin

The admin interface should be visually distinct from the customer-facing site.
**Do not apply the frontend design system to the admin.** Use Django admin's
built-in styling. Minimal customization:

1. **Login page** — Add the ROM Couture logo (small SVG/text above login form)
2. **Site header** — Change from "Django Administration" to "ROM Couture CMS"
3. **Index title** — Change from "Site administration" to "ROM Couture — Atelier Dashboard"

This is done via settings:

```python
# config/settings.py
ADMIN_SITE_HEADER = 'ROM Couture CMS'
ADMIN_SITE_TITLE = 'ROM Couture — Atelier Dashboard'
ADMIN_INDEX_TITLE = 'Atelier Dashboard'
```

No custom CSS, no restyling. The admin should look like Django admin — functional and purposeful.

---

## 16. Security Notes

1. **CSRF:** The public API endpoints (`POST /api/bespoke-requests/`, `POST /api/upload/`) use `@csrf_exempt` because they're called from static HTML pages that can't get a CSRF token. This is acceptable because:
   - These endpoints only accept data (no auth, no session needed)
   - Rate limiting is handled by the 5s throttle in the frontend
   - In production, add rate limiting via nginx or Django middleware

2. **File upload validation:** The upload endpoint validates file type and size. Always check content type and file extension.

3. **Admin access:** The `/admin/` path requires authentication. Use a strong password for the superuser. Consider adding HTTPS in production.

4. **XSS:** All user-submitted data that renders in API responses is sanitized by `SecurityUtils.safeRender` in the frontend. The admin panel uses Django's auto-escaping.

---

## 17. Quick Start (for new agent)

> If starting in a fresh conversation, execute this exact sequence:

```bash
# 1. Navigate to project
cd /rom_couture_main

# 2. Read this spec fully
cat backend/IMPLEMENTATION_SPEC.md

# 3. Create the Django project files following §14 layout
#    Start with requirements.txt, then config/settings.py, then models...

# 4. After creating all files:
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations cms
python manage.py migrate
python manage.py createsuperuser

# 5. Start backend
python manage.py runserver 8000

# 6. In another terminal, start frontend (for testing)
cd ../rom_couture_final
python3 -m http.server 8001

# 7. Verify at http://localhost:8000/admin/ and http://localhost:8001/
```
