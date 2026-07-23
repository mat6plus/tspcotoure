from django.conf import settings
from django.core.exceptions import ValidationError
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


class BespokeRequest(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('ready_for_review', 'Ready for Review'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=200, verbose_name='Full Name')
    email = models.EmailField(verbose_name='Email Address')
    phone = models.CharField(max_length=50, verbose_name='Phone Number')
    garment_type = models.CharField(max_length=200, blank=True,
                                    verbose_name='Selected Garment')
    chest = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    waist = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    shoulder = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    sleeve = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    neck = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    length = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    standard_size = models.CharField(max_length=50, blank=True,
                                     verbose_name='Standard Clothing Size')
    height = models.CharField(max_length=50, blank=True,
                              verbose_name='Body Height')
    fabrics = models.TextField(blank=True,
                               verbose_name='Selected Fabrics',
                               help_text='Comma-separated fabric names')
    color_notes = models.TextField(blank=True, verbose_name='Color Preferences')
    inspiration_notes = models.TextField(blank=True, verbose_name='Inspiration & Design Thoughts')
    fit_notes = models.TextField(blank=True, verbose_name='Fit Preferences')
    reference_file = models.FileField(upload_to='references/', blank=True, null=True,
                                      verbose_name='Reference Drawing/Sketch')
    pinterest_link = models.URLField(blank=True, verbose_name='Pinterest Board Link')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(
        blank=True,
        verbose_name='Admin Notes',
        help_text='Sensitive internal notes visible only to Admins and Supervisors.'
    )
    work_notes = models.TextField(
        blank=True,
        verbose_name='Work / Progress Notes',
        help_text='Shared atelier progress notes visible to Admins, Supervisors, and Fashion Designers.'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_bespoke_requests',
        verbose_name='Assigned Designer'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
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
        permissions = [
            ('view_bespokerequest_redacted', 'Can view redacted bespoke requests'),
            ('view_bespokerequest_full', 'Can view full bespoke requests including PII'),
            ('change_bespokerequest_progress', 'Can update bespoke request progress'),
            ('change_bespokerequest_internal_notes', 'Can edit admin/internal notes'),
            ('send_bespokerequest_completion_email', 'Can send bespoke request completion emails'),
            ('cancel_bespokerequest', 'Can cancel bespoke requests'),
            ('assign_bespokerequest', 'Can assign bespoke requests to designers'),
        ]

    def __str__(self):
        return f'{self.name} — {self.garment_type or "Custom Design"} ({self.get_status_display()})'


class BespokeRequestStatusHistory(models.Model):
    request = models.ForeignKey(
        BespokeRequest,
        on_delete=models.CASCADE,
        related_name='status_history',
    )
    old_status = models.CharField(max_length=30, blank=True)
    new_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='bespoke_status_history',
    )
    note = models.TextField(blank=True)
    source = models.CharField(
        max_length=50,
        default='cms_admin',
        choices=[
            ('cms_admin', 'CMS Admin'),
            ('django_admin', 'Django Admin'),
            ('api', 'API'),
            ('system', 'System'),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Bespoke Request Status History'
        verbose_name_plural = 'Bespoke Request Status Histories'

    def __str__(self):
        changed_by = self.changed_by.get_username() if self.changed_by else 'System'
        return f'{self.request_id}: {self.old_status or "—"} → {self.new_status} by {changed_by}'


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


class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email Address')
    is_active = models.BooleanField(default=True, verbose_name='Active Subscription')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Newsletter Subscription'
        verbose_name_plural = 'Newsletter Subscriptions'

    def __str__(self):
        return self.email


class BespokeSilhouette(models.Model):
    """A garment silhouette option shown in custom-order Step 2."""
    name = models.CharField(
        max_length=200,
        verbose_name='Silhouette Name',
        help_text='e.g. Royal Indigo Agbada'
    )
    label = models.CharField(
        max_length=100,
        verbose_name='Display Label',
        help_text='Short label shown under the card, e.g. Royal Agbada'
    )
    image = models.ImageField(
        upload_to='silhouettes/',
        blank=True,
        null=True,
        verbose_name='Silhouette Image',
        help_text='Upload garment silhouette photo (JPEG/PNG/WebP)'
    )
    is_custom_vision = models.BooleanField(
        default=False,
        verbose_name='Custom Vision Card',
        help_text='If checked, renders as the open-ended "Custom Vision" card with an icon instead of a photo'
    )
    is_published = models.BooleanField(default=True, help_text='Unpublish to hide from the order form')
    sort_order = models.PositiveIntegerField(default=0, help_text='Lower numbers appear first')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Bespoke Silhouette'
        verbose_name_plural = 'Bespoke Silhouettes'

    def __str__(self):
        return self.name


class FabricSwatch(models.Model):
    """A fabric option shown in custom-order Step 4."""
    name = models.CharField(
        max_length=200,
        verbose_name='Fabric Name',
        help_text='e.g. Heavy Linen'
    )
    color_hex = models.CharField(
        max_length=7,
        default='#e0d6c8',
        verbose_name='Swatch Background Colour',
        help_text='CSS hex colour used as the swatch preview background, e.g. #e0d6c8'
    )
    texture_css = models.TextField(
        blank=True,
        verbose_name='Texture Overlay CSS',
        help_text='Optional inline CSS for a decorative overlay div on the swatch (background-image, opacity, etc.)'
    )
    image = models.ImageField(
        upload_to='swatches/',
        blank=True,
        null=True,
        verbose_name='Swatch Image',
        help_text='Optional photo of the fabric; overrides the colour swatch if provided'
    )
    is_published = models.BooleanField(default=True, help_text='Unpublish to hide from the order form')
    sort_order = models.PositiveIntegerField(default=0, help_text='Lower numbers appear first')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Fabric Swatch'
        verbose_name_plural = 'Fabric Swatches'

    def __str__(self):
        return self.name


class SiteConfiguration(models.Model):
    """Singleton model for site-wide settings editable from Django Admin."""
    # Contact
    contact_email = models.EmailField(
        default='hello@romcouture.com',
        verbose_name='Primary Contact Email'
    )
    whatsapp_number = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='WhatsApp Number',
        help_text='International format, e.g. +2348012345678'
    )
    # Social
    instagram_url = models.URLField(blank=True, verbose_name='Instagram URL')
    facebook_url = models.URLField(blank=True, verbose_name='Facebook URL')
    twitter_url = models.URLField(blank=True, verbose_name='Twitter / X URL')
    pinterest_url = models.URLField(blank=True, verbose_name='Pinterest URL')
    # Hero / Branding copy
    hero_tagline = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Hero Tagline',
        help_text='Short headline shown on the homepage hero'
    )
    hero_subtext = models.TextField(
        blank=True,
        verbose_name='Hero Subtext',
        help_text='Supporting paragraph beneath the hero tagline'
    )
    # Footer
    footer_address = models.CharField(max_length=300, blank=True, verbose_name='Studio Address')
    footer_copyright = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Footer Copyright Text',
        help_text='Overrides default copyright. Leave blank to use default.'
    )
    # Misc
    delivery_lead_time = models.CharField(
        max_length=100,
        default='4–6 weeks',
        verbose_name='Delivery Lead Time'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Configuration'
        verbose_name_plural = 'Site Configuration'
        permissions = [
            ('manage_cms_users', 'Can manage CMS users'),
            ('manage_site_configuration', 'Can manage site configuration'),
            ('manage_cms_content', 'Can manage CMS content'),
            ('delete_cms_content', 'Can delete CMS content'),
            ('access_django_admin', 'Can access Django admin'),
        ]

    def __str__(self):
        return 'TSP Couture — Site Configuration'

    def clean(self):
        if not self.pk and SiteConfiguration.objects.exists():
            raise ValidationError(
                'Only one Site Configuration record is allowed. Edit the existing one.'
            )

    @classmethod
    def get_solo(cls):
        """Return the singleton instance, creating it with defaults if absent."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
