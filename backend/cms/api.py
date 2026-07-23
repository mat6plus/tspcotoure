import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import (
    Garment, BespokeRequest, Testimonial, NewsletterSubscription,
    BespokeSilhouette, FabricSwatch, SiteConfiguration,
)


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
            'image_url': request.build_absolute_uri(g.image.url) if g.image else '',
            'category': g.category,
            'is_featured': g.is_featured,
        })
    return JsonResponse({'garments': data})


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


@csrf_exempt
@require_http_methods(['POST'])
def create_bespoke_request(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    required = ['name', 'email', 'phone']
    for field in required:
        if not data.get(field):
            return JsonResponse({'error': f'{field} is required'}, status=400)

    if '@' not in data.get('email', ''):
        return JsonResponse({'error': 'Invalid email address'}, status=400)

    bespoke = BespokeRequest.objects.create(
        name=data.get('name', ''),
        email=data.get('email', ''),
        phone=data.get('phone', ''),
        garment_type=data.get('garment_type', ''),
        fabrics=data.get('fabrics', ''),
        color_notes=data.get('color_notes', ''),
        inspiration_notes=data.get('inspiration_notes', ''),
        fit_notes=data.get('fit_notes', ''),
        chest=_safe_decimal(data.get('chest')),
        waist=_safe_decimal(data.get('waist')),
        shoulder=_safe_decimal(data.get('shoulder')),
        sleeve=_safe_decimal(data.get('sleeve')),
        neck=_safe_decimal(data.get('neck')),
        length=_safe_decimal(data.get('length')),
        standard_size=data.get('standard_size', ''),
        height=data.get('height', ''),
        pinterest_link=data.get('pinterest_link', ''),
        reference_file=data.get('reference_file', ''),
        agreed_no_returns=data.get('agreed_no_returns', False),
        agreed_offline_payment=data.get('agreed_offline_payment', False),
        agreed_consultation=data.get('agreed_consultation', False),
    )

    return JsonResponse({
        'success': True,
        'id': bespoke.pk,
        'message': 'Your bespoke request has been received. Our team will contact you within 24 hours.',
    }, status=201)


@csrf_exempt
@require_http_methods(['POST'])
def upload_file(request):
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    uploaded = request.FILES['file']

    allowed_types = ['image/png', 'image/jpeg', 'image/webp', 'image/jpg', 'application/pdf']
    if uploaded.content_type not in allowed_types:
        return JsonResponse({'error': 'Invalid file type. PNG, JPG, WebP, and PDF allowed.'}, status=400)

    if uploaded.size > 10 * 1024 * 1024:
        return JsonResponse({'error': 'File too large. Maximum 10MB.'}, status=400)

    filename = default_storage.save(f'references/{uploaded.name}', uploaded)
    url = request.build_absolute_uri(default_storage.url(filename))

    return JsonResponse({
        'success': True,
        'url': url,
        'filename': filename,
    })


@require_http_methods(['GET'])
def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'TSP Couture CMS'})


@csrf_exempt
@require_http_methods(['POST'])
def subscribe_newsletter(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    email = data.get('email', '').strip()
    if not email:
        return JsonResponse({'error': 'Email is required'}, status=400)

    if '@' not in email:
        return JsonResponse({'error': 'Invalid email address'}, status=400)

    if NewsletterSubscription.objects.filter(email__iexact=email).exists():
        return JsonResponse({'success': True, 'message': 'You are already subscribed to our newsletter!'})

    NewsletterSubscription.objects.create(email=email)
    return JsonResponse({'success': True, 'message': 'Thank you for subscribing to our newsletter!'})



def _safe_decimal(value):
    if not value:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


# ─── Default seed data (used only when the DB has no records yet) ─────────────

_DEFAULT_SILHOUETTES = [
    {'name': 'Royal Indigo Agbada', 'label': 'Royal Agbada', 'sort_order': 0},
    {'name': 'Linen Archive Shirt', 'label': 'Archive Shirt', 'sort_order': 1},
    {'name': 'Geometric Two-Piece', 'label': 'Two-Piece Set', 'sort_order': 2},
    {'name': 'Formal Blazer',       'label': 'Ankara Blazer', 'sort_order': 3},
    {'name': 'Atelier Cap Series',  'label': 'Artisan Cap',   'sort_order': 4},
    {'name': 'Terracotta Kaftan',   'label': 'Terracotta Kaftan', 'sort_order': 5},
    {'name': 'Other / Custom',      'label': 'Custom Vision', 'sort_order': 6,
     'is_custom_vision': True},
]

_DEFAULT_SWATCHES = [
    {'name': 'Heavy Linen',   'color_hex': '#e0d6c8',
     'texture_css': 'background-image:repeating-linear-gradient(45deg,transparent,transparent 2px,#000 2px,#000 4px);opacity:0.2;mix-blend-mode:multiply;',
     'sort_order': 0},
    {'name': 'Worsted Wool',  'color_hex': '#2c2f33',
     'texture_css': 'background-image:repeating-radial-gradient(circle,#fff 1px,transparent 1px);background-size:4px 4px;opacity:0.1;mix-blend-mode:overlay;',
     'sort_order': 1},
    {'name': 'Crisp Cotton',  'color_hex': '#f4f1ea', 'texture_css': '', 'sort_order': 2},
    {'name': 'Raw Silk',      'color_hex': '#8c3a3a',
     'texture_css': 'background-image:linear-gradient(to top right,transparent,white);opacity:0.2;',
     'sort_order': 3},
]


def _seed_silhouettes():
    """Populate BespokeSilhouette with defaults if the table is empty."""
    if BespokeSilhouette.objects.exists():
        return
    for s in _DEFAULT_SILHOUETTES:
        BespokeSilhouette.objects.create(
            name=s['name'],
            label=s['label'],
            sort_order=s.get('sort_order', 0),
            is_custom_vision=s.get('is_custom_vision', False),
        )


def _seed_swatches():
    """Populate FabricSwatch with defaults if the table is empty."""
    if FabricSwatch.objects.exists():
        return
    for f in _DEFAULT_SWATCHES:
        FabricSwatch.objects.create(
            name=f['name'],
            color_hex=f['color_hex'],
            texture_css=f.get('texture_css', ''),
            sort_order=f.get('sort_order', 0),
        )


# ─── New Endpoints ────────────────────────────────────────────────────────────

@require_http_methods(['GET'])
def silhouette_list(request):
    _seed_silhouettes()
    silhouettes = BespokeSilhouette.objects.filter(is_published=True)
    data = []
    for s in silhouettes:
        data.append({
            'id': s.id,
            'name': s.name,
            'label': s.label,
            'image_url': request.build_absolute_uri(s.image.url) if s.image else '',
            'is_custom_vision': s.is_custom_vision,
        })
    return JsonResponse({'silhouettes': data})


@require_http_methods(['GET'])
def fabric_swatch_list(request):
    _seed_swatches()
    swatches = FabricSwatch.objects.filter(is_published=True)
    data = []
    for f in swatches:
        data.append({
            'id': f.id,
            'name': f.name,
            'color_hex': f.color_hex,
            'texture_css': f.texture_css,
            'image_url': request.build_absolute_uri(f.image.url) if f.image else '',
        })
    return JsonResponse({'swatches': data})


@require_http_methods(['GET'])
def site_config(request):
    cfg = SiteConfiguration.get_solo()
    return JsonResponse({
        'contact_email': cfg.contact_email,
        'whatsapp_number': cfg.whatsapp_number,
        'instagram_url': cfg.instagram_url,
        'facebook_url': cfg.facebook_url,
        'twitter_url': cfg.twitter_url,
        'pinterest_url': cfg.pinterest_url,
        'hero_tagline': cfg.hero_tagline,
        'hero_subtext': cfg.hero_subtext,
        'footer_address': cfg.footer_address,
        'footer_copyright': cfg.footer_copyright,
        'delivery_lead_time': cfg.delivery_lead_time,
    })
