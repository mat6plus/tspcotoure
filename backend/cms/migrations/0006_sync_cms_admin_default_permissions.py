from django.conf import settings
from django.db import migrations


def _permissions_for_model(apps, model_name):
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    model = apps.get_model('cms', model_name)
    content_type = ContentType.objects.get_for_model(model)
    return list(Permission.objects.filter(content_type=content_type))


def sync_cms_admin_default_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    admin_group, _ = Group.objects.get_or_create(name='CMS Admins')
    permissions = []
    for model_name in [
        'BespokeRequest',
        'BespokeRequestStatusHistory',
        'BespokeSilhouette',
        'FabricSwatch',
        'Garment',
        'NewsletterSubscription',
        'SiteConfiguration',
        'Testimonial',
    ]:
        permissions.extend(_permissions_for_model(apps, model_name))

    existing_ids = set(admin_group.permissions.values_list('id', flat=True))
    for permission in permissions:
        if permission.id not in existing_ids:
            admin_group.permissions.add(permission)


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0005_alter_bespokerequest_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(sync_cms_admin_default_permissions, migrations.RunPython.noop),
    ]
