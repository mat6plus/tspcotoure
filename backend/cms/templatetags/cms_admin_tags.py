from django import template

from cms.rbac import role_label, role_slug, role_summary


register = template.Library()


@register.filter
def cms_role_for(user):
    return role_label(user)


@register.filter
def cms_role_slug_for(user):
    return role_slug(user)


@register.filter
def cms_role_summary_for(user):
    return role_summary(user)
