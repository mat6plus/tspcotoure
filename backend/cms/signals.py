from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import mail_admins
from django.template.loader import render_to_string
from .models import BespokeRequest


@receiver(post_save, sender=BespokeRequest)
def notify_admin_new_request(sender, instance, created, **kwargs):
    if not created:
        return

    subject = f'New Bespoke Request: {instance.name} — {instance.garment_type or "Custom"}'

    message = render_to_string('cms/emails/new_request_admin.txt', {
        'request': instance,
        'admin_url': 'http://localhost:8000/admin/cms/bespokerequest/{}/change/'.format(instance.pk),
    })

    mail_admins(subject, message)
