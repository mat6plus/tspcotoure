from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from cms.masking import mask_email, mask_phone
from cms.models import BespokeRequest, Garment
from cms.rbac import (
    CMS_ADMIN_GROUP,
    CMS_DESIGNER_GROUP,
    CMS_SUPERVISOR_GROUP,
    ensure_cms_groups,
    get_group,
    visible_bespoke_requests,
)


@override_settings(
    ALLOWED_HOSTS=['testserver'],
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
)
class CMSRBACTests(TestCase):
    def setUp(self):
        settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ['testserver']
        mail.outbox = []
        ensure_cms_groups()
        self.admin = self._create_user('rbac_admin', CMS_ADMIN_GROUP)
        self.supervisor = self._create_user('rbac_supervisor', CMS_SUPERVISOR_GROUP)
        self.designer = self._create_user('rbac_designer', CMS_DESIGNER_GROUP)
        self.other_designer = self._create_user('rbac_other_designer', CMS_DESIGNER_GROUP)
        self.inactive = self._create_user('rbac_inactive', CMS_DESIGNER_GROUP, is_active=False)
        self.assigned_request = self._create_request('RBAC Assigned Client', self.designer)
        self.other_request = self._create_request('RBAC Other Client', self.other_designer)

    def _create_user(self, username, group_name, is_active=True):
        user = get_user_model().objects.create_user(
            username,
            email=f'{username}@example.com',
            password='TempPass1234!',
            is_staff=True,
            is_active=is_active,
        )
        user.groups.add(get_group(group_name))
        return user

    def _create_request(self, name, assigned_to):
        return BespokeRequest.objects.create(
            name=name,
            email=f'{name.lower().replace(" ", ".")}@example.com',
            phone='+15550100000',
            garment_type='Bespoke Agbada',
            fabrics='Linen, Silk',
            color_notes='Terracotta',
            inspiration_notes='Classic tailored silhouette',
            fit_notes='Slim fit',
            assigned_to=assigned_to,
        )

    def _post_with_csrf(self, url, data):
        if 'csrftoken' not in self.client.cookies:
            self.client.get(reverse('cms-admin:dashboard'))
        data = dict(data)
        data['csrfmiddlewaretoken'] = self.client.cookies['csrftoken'].value
        return self.client.post(url, data)

    def _login(self, user):
        response = self.client.post(reverse('cms-admin:login'), {
            'username': user.username,
            'password': 'TempPass1234!',
        })
        self.assertEqual(response.status_code, 302)

    def _masked_email_for_request(self, request):
        return mask_email(request.email)

    def _masked_phone_for_request(self, request):
        return mask_phone(request.phone)

    def test_designer_sees_only_assigned_redacted_requests_and_limited_actions(self):
        inactive_login = self.client.post(reverse('cms-admin:login'), {
            'username': self.inactive.username,
            'password': 'TempPass1234!',
        })
        self.assertEqual(inactive_login.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

        self._login(self.designer)
        self.assertEqual(self.client.get(reverse('cms-admin:dashboard')).status_code, 200)

        list_response = self.client.get(reverse('cms-admin:bespoke_list'))
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, 'RBAC Assigned Client')
        self.assertNotContains(list_response, 'rbac.assigned.client@example.com')
        self.assertNotContains(list_response, '+15550100000')
        self.assertNotContains(list_response, 'RBAC Other Client')

        masked_email = self._masked_email_for_request(self.assigned_request)
        masked_phone = self._masked_phone_for_request(self.assigned_request)
        self.assertNotEqual(masked_email, self.assigned_request.email)
        self.assertNotEqual(masked_phone, self.assigned_request.phone)
        self.assertNotEqual(masked_email, '*' * len(self.assigned_request.email))
        self.assertContains(list_response, masked_email)
        self.assertContains(list_response, masked_phone)

        detail_response = self.client.get(reverse('cms-admin:bespoke_detail', args=[self.assigned_request.pk]))
        self.assertEqual(detail_response.status_code, 200)
        self.assertNotContains(detail_response, 'rbac.assigned.client@example.com')
        self.assertNotContains(detail_response, '+15550100000')
        self.assertContains(detail_response, masked_email)
        self.assertContains(detail_response, masked_phone)
        self.assertContains(detail_response, 'Work / Progress Notes')
        self.assertNotContains(detail_response, 'Admin Notes')

        self.assertEqual(
            self.client.get(reverse('cms-admin:bespoke_detail', args=[self.other_request.pk])).status_code,
            404,
        )
        self.assertEqual(self.client.get(reverse('cms-admin:garment_list')).status_code, 403)

        ready_response = self._post_with_csrf(reverse('cms-admin:bespoke_detail', args=[self.assigned_request.pk]), {
            'status': 'ready_for_review',
            'work_notes': 'Designer moved to review',
        })
        self.assertEqual(ready_response.status_code, 302)
        self.assigned_request.refresh_from_db()
        self.assertEqual(self.assigned_request.status, 'ready_for_review')

        blocked_response = self._post_with_csrf(reverse('cms-admin:bespoke_detail', args=[self.assigned_request.pk]), {
            'status': 'completed',
            'work_notes': 'Designer attempted completion',
        })
        self.assertEqual(blocked_response.status_code, 200)
        self.assertContains(blocked_response, 'Select a valid choice')
        self.assigned_request.refresh_from_db()
        self.assertEqual(self.assigned_request.status, 'ready_for_review')
        self.assertEqual(len(list(visible_bespoke_requests(self.designer))), 1)

    def test_supervisor_sees_full_requests_and_can_complete_without_delete_or_django_admin_access(self):
        self._login(self.supervisor)
        list_response = self.client.get(reverse('cms-admin:bespoke_list'))
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, 'RBAC Assigned Client')
        self.assertNotContains(list_response, 'rbac.assigned.client@example.com')
        self.assertNotContains(list_response, '+15550100000')
        self.assertContains(list_response, self._masked_email_for_request(self.assigned_request))
        self.assertContains(list_response, self._masked_phone_for_request(self.assigned_request))

        detail_response = self.client.get(reverse('cms-admin:bespoke_detail', args=[self.assigned_request.pk]))
        self.assertEqual(detail_response.status_code, 200)
        self.assertNotContains(detail_response, 'rbac.assigned.client@example.com')
        self.assertNotContains(detail_response, '+15550100000')
        self.assertContains(detail_response, 'Admin Notes')
        self.assertContains(detail_response, 'Completion email')
        self.assertContains(detail_response, self._masked_email_for_request(self.assigned_request))
        self.assertContains(detail_response, self._masked_phone_for_request(self.assigned_request))

        complete_response = self._post_with_csrf(reverse('cms-admin:bespoke_detail', args=[self.assigned_request.pk]), {
            'status': 'completed',
            'work_notes': 'Supervisor completed request',
            'send_completion_email': 'on',
        })
        self.assertEqual(complete_response.status_code, 302)
        self.assigned_request.refresh_from_db()
        self.assertEqual(self.assigned_request.status, 'completed')
        self.assertEqual(self.assigned_request.assigned_to_id, self.designer.pk)
        self.assertTrue(any('Your TSP Couture Bespoke Order is Ready' in message.subject for message in mail.outbox))

        garment = Garment.objects.create(title='RBAC Supervisor Garment', category='traditional')
        delete_response = self._post_with_csrf(reverse('cms-admin:garment_delete', args=[garment.pk]), {})
        self.assertIn(delete_response.status_code, (302, 403))
        self.assertTrue(Garment.objects.filter(pk=garment.pk).exists())
        self.assertEqual(self.client.get('/admin/').status_code, 302)

    def test_admin_can_manage_team_site_content_and_django_admin(self):
        self._login(self.admin)
        self.assertEqual(self.client.get(reverse('cms-admin:team_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('cms-admin:site_configuration')).status_code, 200)

        garment = Garment.objects.create(title='RBAC Admin Garment', category='traditional')
        delete_response = self._post_with_csrf(reverse('cms-admin:garment_delete', args=[garment.pk]), {})
        self.assertEqual(delete_response.status_code, 302)
        self.assertFalse(Garment.objects.filter(pk=garment.pk).exists())
        self.assertEqual(self.client.get('/admin/').status_code, 200)
        self.assertEqual(len(list(visible_bespoke_requests(self.admin))), 2)

        list_response = self.client.get(reverse('cms-admin:bespoke_list'))
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, 'rbac.assigned.client@example.com')
        self.assertContains(list_response, '+15550100000')
        self.assertNotContains(list_response, self._masked_email_for_request(self.assigned_request))
        self.assertNotContains(list_response, self._masked_phone_for_request(self.assigned_request))


@override_settings(
    ALLOWED_HOSTS=['testserver'],
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
)
class MaskingUtilityTests(TestCase):
    def test_mask_email_preserves_domain_and_masks_local_part(self):
        result = mask_email('john.doe@example.com')
        local_part = result.split('@')[0]
        self.assertEqual(local_part[0], 'j')
        self.assertEqual(local_part[-1], 'e')
        self.assertEqual(result.split('@')[1], 'example.com')
        self.assertIn('@', result)
        self.assertNotEqual(result, 'john.doe@example.com')
        self.assertNotEqual(result, '*' * len('john.doe@example.com'))

    def test_mask_email_handles_short_local_part(self):
        result = mask_email('ab@example.com')
        self.assertEqual(result, '**@example.com')

    def test_mask_email_handles_invalid_input(self):
        self.assertEqual(mask_email(''), '•••@••••.com')
        self.assertEqual(mask_email('no-at-sign.com'), '•••@••••.com')

    def test_mask_email_is_deterministic_but_content_dependent(self):
        result_a = mask_email('test.user@example.com')
        result_b = mask_email('other.user@example.com')
        self.assertEqual(result_a, mask_email('test.user@example.com'))
        self.assertNotEqual(result_a, result_b)

    def test_mask_phone_masks_approximately_six_digits(self):
        result = mask_phone('+15550100000')
        clean = result.replace('+1 ', '')
        self.assertEqual(len(clean), 11)
        self.assertTrue(result.startswith('+1 15'))
        self.assertTrue(result.endswith('000'))
        self.assertIn(result[5], {'*', '#', '•', '×'})

    def test_mask_phone_is_deterministic_but_content_dependent(self):
        result_a = mask_phone('+15550100000')
        result_b = mask_phone('+12222333333')
        self.assertEqual(result_a, mask_phone('+15550100000'))
        self.assertNotEqual(result_a, result_b)

    def test_mask_phone_handles_non_11_digit(self):
        self.assertEqual(mask_phone(''), '')
        self.assertEqual(mask_phone(None), '')

    def test_mask_phone_does_not_expose_original_digits_in_masked_section(self):
        result = mask_phone('+15550100000')
        masked_section = result[5:11]
        self.assertNotEqual(masked_section, '550100')
        self.assertTrue(any(ch in masked_section for ch in ('*', '#', '•', '×')))
