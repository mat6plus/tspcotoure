from django.contrib import admin
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html

from .admin_site import cms_admin_site
from .models import (
    BespokeRequest,
    BespokeRequestStatusHistory,
    BespokeSilhouette,
    FabricSwatch,
    Garment,
    NewsletterSubscription,
    SiteConfiguration,
    Testimonial,
)
from .rbac import can_send_completion_email


class GarmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'sort_order', 'is_featured', 'is_published', 'created_at']
    list_filter = ['category', 'is_featured', 'is_published']
    search_fields = ['title', 'description']
    list_editable = ['sort_order', 'is_featured', 'is_published']
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = [
        ('Basic Info', {'fields': ['title', 'slug', 'description', 'category']}),
        ('Media', {'fields': ['image']}),
        ('Visibility & Order', {'fields': ['is_featured', 'is_published', 'sort_order']}),
    ]


cms_admin_site.register(Garment, GarmentAdmin)


class BespokeRequestStatusHistoryInline(admin.TabularInline):
    model = BespokeRequestStatusHistory
    extra = 0
    fields = ['old_status', 'new_status', 'changed_by', 'source', 'note', 'created_at']
    readonly_fields = fields
    can_delete = False


class BespokeRequestAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'garment_type', 'assigned_to', 'status', 'created_at', 'email_link'
    ]
    list_filter = ['status', 'created_at', 'garment_type']
    search_fields = ['name', 'email', 'phone', 'garment_type']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        ('Contact Information', {'fields': ['name', 'email', 'phone']}),
        ('Garment & Style', {
            'fields': ['garment_type', 'fabrics', 'color_notes', 'inspiration_notes', 'fit_notes']
        }),
        ('Measurements', {
            'fields': ['chest', 'waist', 'shoulder', 'sleeve', 'neck', 'length', 'standard_size', 'height'],
            'classes': ['collapse'],
        }),
        ('References', {
            'fields': ['pinterest_link', 'reference_file'],
            'classes': ['collapse'],
        }),
        ('Agreements', {
            'fields': ['agreed_no_returns', 'agreed_offline_payment', 'agreed_consultation'],
        }),
        ('Status & Admin', {
            'fields': ['status', 'assigned_to', 'admin_notes', 'work_notes', 'created_at', 'updated_at'],
        }),
    ]
    inlines = [BespokeRequestStatusHistoryInline]
    actions = ['mark_as_in_progress', 'mark_as_completed']

    def email_link(self, obj):
        return format_html('<a href="mailto:{}">{}</a>', obj.email, obj.email)
    email_link.short_description = 'Email'

    def mark_as_in_progress(self, request, queryset):
        updated = 0
        for obj in queryset:
            old_status = obj.status
            obj.status = 'in_progress'
            obj.save(update_fields=['status'])
            updated += 1
            BespokeRequestStatusHistory.objects.create(
                request=obj,
                old_status=old_status,
                new_status='in_progress',
                changed_by=request.user,
                source='django_admin',
            )
        self.message_user(request, f'{updated} request(s) marked as In Progress.')
    mark_as_in_progress.short_description = 'Mark selected as In Progress'

    def mark_as_completed(self, request, queryset):
        if not can_send_completion_email(request.user):
            self.message_user(request, 'You do not have permission to mark requests as completed.', level='error')
            return
        for obj in queryset:
            old_status = obj.status
            obj.status = 'completed'
            obj.save(update_fields=['status'])

            if old_status != 'completed':
                self._send_completion_email(obj)
                BespokeRequestStatusHistory.objects.create(
                    request=obj,
                    old_status=old_status,
                    new_status='completed',
                    changed_by=request.user,
                    note='Marked completed from Django admin with completion email.',
                    source='django_admin',
                )

        self.message_user(request, f'{queryset.count()} request(s) marked as Completed.')
    mark_as_completed.short_description = 'Mark selected as Completed (sends email)'

    def _send_completion_email(self, obj):
        subject = 'Your TSP Couture Bespoke Order is Ready'
        message = render_to_string('cms/emails/order_completed_customer.txt', {'request': obj})
        send_mail(subject, message, None, [obj.email], fail_silently=True)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['status_counts'] = {
            s: BespokeRequest.objects.filter(status=s).count()
            for s, _ in BespokeRequest.STATUS_CHOICES
        }
        return super().changelist_view(request, extra_context=extra_context)


class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'author_location', 'is_published', 'sort_order']
    list_filter = ['is_published']
    list_editable = ['is_published', 'sort_order']
    search_fields = ['author_name', 'text']


class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['email', 'created_at']
    search_fields = ['email']
    date_hierarchy = 'created_at'


class BespokeSilhouetteAdmin(admin.ModelAdmin):
    list_display = ['name', 'label', 'is_custom_vision', 'is_published', 'sort_order']
    list_editable = ['is_published', 'sort_order']
    list_filter = ['is_published', 'is_custom_vision']
    search_fields = ['name', 'label']
    fieldsets = [
        ('Silhouette Details', {'fields': ['name', 'label', 'image']}),
        ('Display Options', {'fields': ['is_custom_vision', 'is_published', 'sort_order']}),
    ]
    help_text = (
        'These silhouettes appear as selectable cards in Step 2 of the Custom Order form. '
        'Upload a photo and set a name + label. Mark one as “Custom Vision” to render an icon-only card.'
    )


class FabricSwatchAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_hex', 'is_published', 'sort_order', 'colour_preview']
    list_editable = ['is_published', 'sort_order']
    list_filter = ['is_published']
    search_fields = ['name']
    fieldsets = [
        ('Fabric Details', {'fields': ['name', 'color_hex', 'texture_css', 'image']}),
        ('Display Options', {'fields': ['is_published', 'sort_order']}),
    ]

    def colour_preview(self, obj):
        return format_html(
            '<span style="display:inline-block;width:24px;height:24px;border-radius:4px;'
            'background:{};border:1px solid #ccc;"></span>',
            obj.color_hex,
        )
    colour_preview.short_description = 'Colour'


class BespokeRequestStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['request', 'old_status', 'new_status', 'changed_by', 'source', 'created_at']
    list_filter = ['new_status', 'source', 'created_at']
    search_fields = ['request__name', 'changed_by__username', 'note']
    readonly_fields = ['created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'contact_email', 'whatsapp_number', 'updated_at']
    fieldsets = [
        ('Contact Information', {
            'fields': ['contact_email', 'whatsapp_number'],
            'description': 'Primary contact details shown in the footer and used for customer notifications.',
        }),
        ('Social Media Links', {
            'fields': ['instagram_url', 'facebook_url', 'twitter_url', 'pinterest_url'],
        }),
        ('Homepage Hero Content', {
            'fields': ['hero_tagline', 'hero_subtext'],
            'classes': ['collapse'],
            'description': 'Served by the /api/site-config/ endpoint. Leave blank to keep the default HTML copy.',
        }),
        ('Footer', {
            'fields': ['footer_address', 'footer_copyright'],
            'classes': ['collapse'],
        }),
        ('Miscellaneous', {'fields': ['delivery_lead_time']}),
    ]

    def has_add_permission(self, request):
        return not SiteConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteConfiguration.get_solo()
        return redirect(reverse('cms_admin:cms_siteconfiguration_change', args=[obj.pk]))


cms_admin_site.register(BespokeRequest, BespokeRequestAdmin)
cms_admin_site.register(Testimonial, TestimonialAdmin)
cms_admin_site.register(NewsletterSubscription, NewsletterSubscriptionAdmin)
cms_admin_site.register(BespokeSilhouette, BespokeSilhouetteAdmin)
cms_admin_site.register(FabricSwatch, FabricSwatchAdmin)
cms_admin_site.register(BespokeRequestStatusHistory, BespokeRequestStatusHistoryAdmin)
cms_admin_site.register(SiteConfiguration, SiteConfigurationAdmin)
