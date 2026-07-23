from .rbac import cms_context


def cms_admin(request):
    if not request.user or not request.user.is_authenticated:
        return {}
    return cms_context(request.user)
