from django.contrib.admin import AdminSite

from cms.rbac import can_access_django_admin


class CmsAdminSite(AdminSite):
    site_header = 'TSP Couture CMS'
    site_title = 'TSP Couture — Atelier Dashboard'
    index_title = 'Atelier Dashboard'

    def has_permission(self, request):
        return (
            request.user.is_authenticated
            and request.user.is_active
            and can_access_django_admin(request.user)
        )


cms_admin_site = CmsAdminSite(name='cms_admin')
