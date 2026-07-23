from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

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


CMS_ADMIN_GROUP = 'CMS Admins'
CMS_SUPERVISOR_GROUP = 'CMS Supervisors'
CMS_DESIGNER_GROUP = 'CMS Fashion Designers'
CMS_GROUPS = [CMS_ADMIN_GROUP, CMS_SUPERVISOR_GROUP, CMS_DESIGNER_GROUP]
CMS_ADMIN_MODELS = [
    BespokeRequest,
    BespokeRequestStatusHistory,
    BespokeSilhouette,
    FabricSwatch,
    Garment,
    NewsletterSubscription,
    SiteConfiguration,
    Testimonial,
]


def _all_permissions_for_models(models):
    permissions = []
    for model in models:
        content_type = ContentType.objects.get_for_model(model)
        permissions.extend(Permission.objects.filter(content_type=content_type))
    return permissions


def get_group(name):
    return Group.objects.get_or_create(name=name)[0]


def ensure_cms_groups():
    admin_group = get_group(CMS_ADMIN_GROUP)
    supervisor_group = get_group(CMS_SUPERVISOR_GROUP)
    designer_group = get_group(CMS_DESIGNER_GROUP)

    bespoke_content_type = ContentType.objects.get_for_model(BespokeRequest)
    site_content_type = ContentType.objects.get_for_model(SiteConfiguration)

    bespoke_permissions = {
        'view_bespokerequest_redacted': 'Can view redacted bespoke requests',
        'view_bespokerequest_full': 'Can view full bespoke requests including PII',
        'change_bespokerequest_progress': 'Can update bespoke request progress',
        'change_bespokerequest_internal_notes': 'Can edit admin/internal notes',
        'send_bespokerequest_completion_email': 'Can send bespoke request completion emails',
        'cancel_bespokerequest': 'Can cancel bespoke requests',
        'assign_bespokerequest': 'Can assign bespoke requests to designers',
    }
    site_permissions = {
        'manage_cms_users': 'Can manage CMS users',
        'manage_site_configuration': 'Can manage site configuration',
        'manage_cms_content': 'Can manage CMS content',
        'delete_cms_content': 'Can delete CMS content',
        'access_django_admin': 'Can access Django admin',
    }

    bespoke_perms = {
        codename: Permission.objects.get_or_create(
            codename=codename,
            content_type=bespoke_content_type,
            defaults={'name': name},
        )[0]
        for codename, name in bespoke_permissions.items()
    }
    site_perms = {
        codename: Permission.objects.get_or_create(
            codename=codename,
            content_type=site_content_type,
            defaults={'name': name},
        )[0]
        for codename, name in site_permissions.items()
    }

    admin_group.permissions.set([
        *_all_permissions_for_models(CMS_ADMIN_MODELS),
        *bespoke_perms.values(),
        *site_perms.values(),
    ])
    supervisor_group.permissions.set([
        bespoke_perms['change_bespokerequest_progress'],
        bespoke_perms['change_bespokerequest_internal_notes'],
        bespoke_perms['send_bespokerequest_completion_email'],
        bespoke_perms['cancel_bespokerequest'],
        bespoke_perms['assign_bespokerequest'],
        site_perms['manage_cms_content'],
    ])
    designer_group.permissions.set([
        bespoke_perms['view_bespokerequest_redacted'],
        bespoke_perms['change_bespokerequest_progress'],
    ])

    return {
        'admin': admin_group,
        'supervisor': supervisor_group,
        'designer': designer_group,
    }


def _user_has_group(user, group_name):
    if not user or not user.is_authenticated or not user.is_active:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name=group_name).exists()


def is_cms_admin(user):
    return _user_has_group(user, CMS_ADMIN_GROUP)


def is_cms_supervisor(user):
    return _user_has_group(user, CMS_SUPERVISOR_GROUP)


def is_cms_designer(user):
    return _user_has_group(user, CMS_DESIGNER_GROUP)


def is_cms_user(user):
    return is_cms_admin(user) or is_cms_supervisor(user) or is_cms_designer(user)


def role_slug(user):
    if is_cms_admin(user):
        return 'admin'
    if is_cms_supervisor(user):
        return 'supervisor'
    if is_cms_designer(user):
        return 'designer'
    return 'staff'


def role_label(user):
    return {
        'admin': 'CMS Admin',
        'supervisor': 'Supervisor',
        'designer': 'Fashion Designer',
    }.get(role_slug(user), 'Staff')


def role_summary(user):
    return {
        'admin': 'Owner-level CMS access',
        'supervisor': 'Operational oversight',
        'designer': 'Assigned atelier work',
    }.get(role_slug(user), 'Limited staff access')


def can_view_full_client_pii(user):
    return is_cms_admin(user) or user.has_perm('cms.view_bespokerequest_full')


def can_manage_cms_users(user):
    return is_cms_admin(user) or user.has_perm('cms.manage_cms_users')


def can_manage_site_configuration(user):
    return is_cms_admin(user) or user.has_perm('cms.manage_site_configuration')


def can_manage_cms_content(user):
    return is_cms_admin(user) or is_cms_supervisor(user) or user.has_perm('cms.manage_cms_content')


def can_delete_cms_content(user):
    return is_cms_admin(user) or user.has_perm('cms.delete_cms_content')


def can_update_request_progress(user):
    return is_cms_admin(user) or is_cms_supervisor(user) or is_cms_designer(user) or user.has_perm('cms.change_bespokerequest_progress')


def can_edit_internal_notes(user):
    return is_cms_admin(user) or is_cms_supervisor(user) or user.has_perm('cms.change_bespokerequest_internal_notes')


def can_send_completion_email(user):
    return is_cms_admin(user) or is_cms_supervisor(user) or user.has_perm('cms.send_bespokerequest_completion_email')


def can_cancel_request(user):
    return is_cms_admin(user) or is_cms_supervisor(user) or user.has_perm('cms.cancel_bespokerequest')


def can_assign_request(user):
    return is_cms_admin(user) or is_cms_supervisor(user) or user.has_perm('cms.assign_bespokerequest')


def can_access_django_admin(user):
    return bool(user and user.is_authenticated and (user.is_superuser or user.has_perm('cms.access_django_admin')))


def _designer_queryset():
    return BespokeRequest.objects.defer('email', 'phone', 'agreed_no_returns', 'agreed_offline_payment', 'admin_notes')


def visible_bespoke_requests(user):
    if is_cms_admin(user) or is_cms_supervisor(user) or can_view_full_client_pii(user):
        return BespokeRequest.objects.all()
    if is_cms_designer(user) or user.has_perm('cms.view_bespokerequest_redacted'):
        return _designer_queryset().filter(assigned_to=user)
    return BespokeRequest.objects.none()


def can_view_request(user, request):
    if is_cms_admin(user) or is_cms_supervisor(user) or can_view_full_client_pii(user):
        return True
    if is_cms_designer(user) or user.has_perm('cms.view_bespokerequest_redacted'):
        return bool(request.assigned_to_id == user.pk)
    return False


def allowed_statuses_for_user(user):
    if is_cms_admin(user) or is_cms_supervisor(user):
        return [code for code, _label in BespokeRequest.STATUS_CHOICES]
    return ['new', 'in_progress', 'ready_for_review']


def is_valid_status_transition(user, old_status, new_status):
    if old_status == new_status:
        return True
    if is_cms_admin(user) or is_cms_supervisor(user):
        return new_status in dict(BespokeRequest.STATUS_CHOICES)
    if is_cms_designer(user):
        allowed = {
            ('new', 'in_progress'),
            ('new', 'ready_for_review'),
            ('in_progress', 'ready_for_review'),
        }
        return (old_status, new_status) in allowed
    return False


def cms_context(user):
    return {
        'cms_role': role_slug(user),
        'cms_role_label': role_label(user),
        'cms_role_summary': role_summary(user),
        'cms_is_admin': is_cms_admin(user),
        'cms_is_supervisor': is_cms_supervisor(user),
        'cms_is_designer': is_cms_designer(user),
        'cms_can_view_full_client_pii': can_view_full_client_pii(user),
        'cms_can_manage_cms_users': can_manage_cms_users(user),
        'cms_can_manage_site_configuration': can_manage_site_configuration(user),
        'cms_can_manage_cms_content': can_manage_cms_content(user),
        'cms_can_delete_cms_content': can_delete_cms_content(user),
        'cms_can_update_request_progress': can_update_request_progress(user),
        'cms_can_edit_internal_notes': can_edit_internal_notes(user),
        'cms_can_send_completion_email': can_send_completion_email(user),
        'cms_can_cancel_request': can_cancel_request(user),
        'cms_can_assign_requests': can_assign_request(user),
        'cms_can_access_django_admin': can_access_django_admin(user),
    }


def sync_superuser_cms_admin(user):
    if user and user.is_superuser:
        admin_group = get_group(CMS_ADMIN_GROUP)
        user.groups.add(admin_group)
