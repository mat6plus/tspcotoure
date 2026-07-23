from django.urls import path
from . import api

urlpatterns = [
    path('garments/', api.garment_list, name='api-garment-list'),
    path('testimonials/', api.testimonial_list, name='api-testimonial-list'),
    path('bespoke-requests/', api.create_bespoke_request, name='api-create-bespoke-request'),
    path('upload/', api.upload_file, name='api-upload-file'),
    path('newsletter/subscribe/', api.subscribe_newsletter, name='api-subscribe-newsletter'),
    path('health/', api.health_check, name='api-health'),
    # CMS-driven content
    path('silhouettes/', api.silhouette_list, name='api-silhouette-list'),
    path('fabric-swatches/', api.fabric_swatch_list, name='api-fabric-swatch-list'),
    path('site-config/', api.site_config, name='api-site-config'),
]
