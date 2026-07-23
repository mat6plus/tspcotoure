from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import EmailMultiAlternatives, send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    BespokeRequestStatusForm,
    BespokeSilhouetteForm,
    CMSAdminLoginForm,
    CMSUserForm,
    CMSEditUserForm,
    CMSUserPasswordForm,
    FabricSwatchForm,
    GarmentForm,
    SiteConfigurationForm,
    TestimonialForm,
)
from .masking import mask_email, mask_phone
from .models import (
    BespokeRequest,
    BespokeRequestStatusHistory,
    BespokeSilhouette,
    FabricSwatch,
    Garment,
    SiteConfiguration,
    Testimonial,
)
from .rbac import (
    CMS_ADMIN_GROUP,
    CMS_DESIGNER_GROUP,
    CMS_GROUPS,
    CMS_SUPERVISOR_GROUP,
    can_assign_request,
    can_delete_cms_content,
    can_edit_internal_notes,
    can_manage_cms_content,
    can_manage_cms_users,
    can_manage_site_configuration,
    can_send_completion_email,
    can_update_request_progress,
    can_view_full_client_pii,
    ensure_cms_groups,
    get_group,
    is_cms_admin,
    is_cms_designer,
    is_cms_supervisor,
    visible_bespoke_requests,
)


ROLE_TO_GROUP = {
    'admin': CMS_ADMIN_GROUP,
    'supervisor': CMS_SUPERVISOR_GROUP,
    'designer': CMS_DESIGNER_GROUP,
}


def _cms_required(user):
    return bool(user and user.is_authenticated and user.is_active and (
        is_cms_admin(user) or is_cms_supervisor(user) or is_cms_designer(user)
    ))


def _paginate(queryset, request, default_per_page='10'):
    per_page_options = ['5', '10', '25', '50']
    per_page = request.GET.get('per_page', default_per_page)
    if per_page not in per_page_options:
        per_page = default_per_page

    paginator = Paginator(queryset, int(per_page))
    page_number = request.GET.get('page', '1')
    try:
        return paginator.page(page_number), per_page
    except PageNotAnInteger:
        return paginator.page(1), per_page
    except EmptyPage:
        return paginator.page(paginator.num_pages), per_page


def _status_counts(queryset):
    return {
        s[0]: {
            'label': s[1],
            'count': queryset.filter(status=s[0]).count(),
        }
        for s in BespokeRequest.STATUS_CHOICES
    }


def _record_status_history(request_obj, old_status, new_status, user, note='', source='cms_admin'):
    if old_status == new_status:
        return
    BespokeRequestStatusHistory.objects.create(
        request=request_obj,
        old_status=old_status,
        new_status=new_status,
        changed_by=user,
        note=note,
        source=source,
    )


def _send_completion_email(obj):
    subject = 'Your TSP Couture Bespoke Order is Ready'
    text_body = render_to_string('cms/emails/order_completed_customer.txt', {'request': obj})
    html_body = render_to_string('cms/emails/order_completed_customer.html', {'request': obj})
    msg = EmailMultiAlternatives(subject, text_body, None, [obj.email])
    msg.attach_alternative(html_body, 'text/html')
    msg.send(fail_silently=True)


def _send_status_email(obj, status):
    status_map = {
        'in_progress': {
            'subject': 'Your TSP Couture Order is Now In Progress',
            'txt': 'cms/emails/order_in_progress_customer.txt',
            'html': 'cms/emails/order_in_progress_customer.html',
        },
        'ready_for_review': {
            'subject': 'Your TSP Couture Order is Ready for Review',
            'txt': 'cms/emails/order_ready_for_review_customer.txt',
            'html': 'cms/emails/order_ready_for_review_customer.html',
        },
        'cancelled': {
            'subject': 'Your TSP Couture Order Status Update',
            'txt': 'cms/emails/order_cancelled_customer.txt',
            'html': 'cms/emails/order_cancelled_customer.html',
        },
    }
    if status not in status_map:
        return
    cfg = status_map[status]
    text_body = render_to_string(cfg['txt'], {'request': obj})
    html_body = render_to_string(cfg['html'], {'request': obj})
    msg = EmailMultiAlternatives(cfg['subject'], text_body, None, [obj.email])
    msg.attach_alternative(html_body, 'text/html')
    msg.send(fail_silently=True)


def _mask_contact_for_user(user, *objects):
    if can_view_full_client_pii(user):
        return
    for obj in objects:
        if hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
            for item in obj:
                if hasattr(item, 'email'):
                    item.email = mask_email(item.email)
                if hasattr(item, 'phone'):
                    item.phone = mask_phone(item.phone)
        elif hasattr(obj, 'email'):
            obj.email = mask_email(obj.email)
        if hasattr(obj, 'phone'):
            obj.phone = mask_phone(obj.phone)


def _set_user_cms_role(user, role):
    ensure_cms_groups()
    user.groups.remove(*CMS_GROUPS)
    user.groups.add(get_group(ROLE_TO_GROUP[role]))
    user.is_staff = True
    user.is_superuser = False
    user.save(update_fields=['is_staff', 'is_superuser'])


def _active_admin_count_excluding(user_pk=None):
    queryset = get_user_model().objects.filter(
        is_active=True,
        groups__name=CMS_ADMIN_GROUP,
    ).distinct()
    if user_pk is not None:
        queryset = queryset.exclude(pk=user_pk)
    return queryset.count()


def _last_active_admin_error(target_user, action):
    if is_cms_admin(target_user) and _active_admin_count_excluding(target_user.pk) == 0:
        return f'Cannot {action}; at least one active CMS Admin must remain.'
    return None


def _role_choices_for_template():
    return [
        ('admin', 'CMS Admin'),
        ('supervisor', 'Supervisor / Lead Designer'),
        ('designer', 'Fashion Designer / Atelier Designer'),
    ]


def login_view(request):
    if request.user.is_authenticated and _cms_required(request.user):
        return redirect('cms-admin:dashboard')

    form = CMSAdminLoginForm()
    error = None

    if request.GET.get('logged_out') == '1':
        messages.info(request, 'You have been successfully logged out. See you soon!')

    if request.method == 'POST':
        form = CMSAdminLoginForm(request.POST)
        if form.is_valid():
            ensure_cms_groups()
            user = form.cleaned_data['user']
            login(request, user)
            next_url = request.GET.get('next', 'cms-admin:dashboard')
            return redirect(next_url)
        error = 'Invalid username, password, or CMS role access.'

    return render(request, 'cms_admin/login.html', {
        'form': form,
        'error': error,
    })


def logout_view(request):
    logout(request)
    return redirect('/cms-admin/login/?logged_out=1')


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
def dashboard(request):
    user = request.user
    requests = visible_bespoke_requests(user)
    total_requests = requests.count()
    new_requests = requests.filter(status='new').count()
    in_progress = requests.filter(status='in_progress').count()
    ready_for_review = requests.filter(status='ready_for_review').count()
    completed = requests.filter(status='completed').count()
    cancelled = requests.filter(status='cancelled').count()

    recent_requests = requests.select_related('assigned_to').order_by('-created_at')[:5]
    _mask_contact_for_user(user, recent_requests)

    status_counts = {
        s: requests.filter(status=s).count()
        for s, _ in BespokeRequest.STATUS_CHOICES
    }

    content_context = {}
    if can_manage_cms_content(user):
        content_context.update({
            'total_garments': Garment.objects.count(),
            'published_garments': Garment.objects.filter(is_published=True).count(),
            'total_testimonials': Testimonial.objects.count(),
            'published_testimonials': Testimonial.objects.filter(is_published=True).count(),
            'total_silhouettes': BespokeSilhouette.objects.count(),
            'published_silhouettes': BespokeSilhouette.objects.filter(is_published=True).count(),
            'total_swatches': FabricSwatch.objects.count(),
            'published_swatches': FabricSwatch.objects.filter(is_published=True).count(),
        })

    team_context = {}
    if can_manage_cms_users(user):
        team_context['active_cms_users'] = get_user_model().objects.filter(
            is_active=True,
            groups__name__in=CMS_GROUPS,
        ).distinct().count()

    return render(request, 'cms_admin/dashboard.html', {
        'total_requests': total_requests,
        'new_requests': new_requests,
        'in_progress': in_progress,
        'ready_for_review': ready_for_review,
        'completed': completed,
        'cancelled': cancelled,
        'recent_requests': recent_requests,
        'status_counts': status_counts,
        'now': timezone.now(),
        **content_context,
        **team_context,
    })


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
def bespoke_request_list(request):
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '').strip()

    requests = visible_bespoke_requests(request.user)

    if status_filter in dict(BespokeRequest.STATUS_CHOICES):
        requests = requests.filter(status=status_filter)

    if search_query:
        if can_view_full_client_pii(request.user):
            requests = requests.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(garment_type__icontains=search_query)
            )
        else:
            requests = requests.filter(
                Q(name__icontains=search_query) |
                Q(garment_type__icontains=search_query) |
                Q(fabrics__icontains=search_query) |
                Q(color_notes__icontains=search_query) |
                Q(inspiration_notes__icontains=search_query) |
                Q(fit_notes__icontains=search_query)
            )

    requests = requests.order_by('-created_at')
    page_obj, per_page = _paginate(requests, request)
    status_counts = _status_counts(requests)
    total_count = requests.count()

    _mask_contact_for_user(request.user, page_obj)

    return render(request, 'cms_admin/bespoke_list.html', {
        'requests': page_obj,
        'status_counts': status_counts,
        'current_status': status_filter,
        'search_query': search_query,
        'total_count': total_count,
        'per_page': per_page,
        'cms_can_view_full_client_pii': can_view_full_client_pii(request.user),
    })


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
def bespoke_request_detail(request, pk):
    req = get_object_or_404(visible_bespoke_requests(request.user).select_related('assigned_to'), pk=pk)
    _mask_contact_for_user(request.user, req)

    if not can_update_request_progress(request.user):
        return HttpResponseForbidden('You do not have permission to update this request.')

    form = BespokeRequestStatusForm(instance=req, user=request.user)
    if not can_edit_internal_notes(request.user):
        del form.fields['admin_notes']
    if not can_assign_request(request.user):
        del form.fields['assigned_to']

    if request.method == 'POST':
        form = BespokeRequestStatusForm(request.POST, instance=req, user=request.user)
        if not can_edit_internal_notes(request.user):
            del form.fields['admin_notes']
        if not can_assign_request(request.user):
            del form.fields['assigned_to']

        if form.is_valid():
            old_status = req.status
            send_completion_email = form.cleaned_data.get('send_completion_email', False)
            notify_in_progress = form.cleaned_data.get('notify_in_progress', False)
            notify_ready_for_review = form.cleaned_data.get('notify_ready_for_review', False)
            notify_cancelled = form.cleaned_data.get('notify_cancelled', False)
            form.save()
            history_note = req.work_notes.strip() if req.work_notes else ''

            if send_completion_email and can_send_completion_email(request.user) and req.status == 'completed':
                _send_completion_email(req)
                if old_status == req.status:
                    BespokeRequestStatusHistory.objects.create(
                        request=req,
                        old_status=req.status,
                        new_status=req.status,
                        changed_by=request.user,
                        note='Completion email sent to client.',
                        source='cms_admin',
                    )
                else:
                    history_note = f'{history_note}\n\nCompletion email sent to client.'.strip()

            status_email_map = {
                'in_progress': (notify_in_progress, 'In Progress email sent to client.'),
                'ready_for_review': (notify_ready_for_review, 'Ready for Review email sent to client.'),
                'cancelled': (notify_cancelled, 'Cancellation email sent to client.'),
            }
            if req.status in status_email_map and can_send_completion_email(request.user):
                should_send, email_note = status_email_map[req.status]
                if should_send:
                    _send_status_email(req, req.status)
                    history_note = f'{history_note}\n\n{email_note}'.strip()

            if old_status != req.status:
                _record_status_history(
                    req,
                    old_status,
                    req.status,
                    request.user,
                    note=history_note,
                    source='cms_admin',
                )
            if (send_completion_email and req.status == 'completed') or \
               (notify_in_progress and req.status == 'in_progress') or \
               (notify_ready_for_review and req.status == 'ready_for_review') or \
               (notify_cancelled and req.status == 'cancelled'):
                messages.success(request, 'Request status updated successfully. Customer notification email sent.')
            else:
                messages.success(request, 'Request status updated successfully.')
            return redirect('cms-admin:bespoke_detail', pk=pk)

    return render(request, 'cms_admin/bespoke_detail.html', {
        'bespoke_request': req,
        'form': form,
        'cms_can_view_full_client_pii': can_view_full_client_pii(request.user),
        'cms_can_edit_internal_notes': can_edit_internal_notes(request.user),
        'cms_can_assign_requests': can_assign_request(request.user),
        'status_history': req.status_history.select_related('changed_by').order_by('-created_at'),
        'status_labels': {s: label for s, label in BespokeRequest.STATUS_CHOICES},
    })


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
def garment_list(request):
    if not can_manage_cms_content(request.user):
        return HttpResponseForbidden('You do not have permission to manage garments.')

    garments = Garment.objects.all()
    total_garments = garments.count()
    published_garments = Garment.objects.filter(is_published=True).count()
    draft_garments = Garment.objects.filter(is_published=False).count()
    featured_garments = Garment.objects.filter(is_featured=True).count()
    page_obj, per_page = _paginate(garments, request)

    return render(request, 'cms_admin/garment_list.html', {
        'garments': page_obj,
        'per_page': per_page,
        'total_garments': total_garments,
        'published_garments': published_garments,
        'draft_garments': draft_garments,
        'featured_garments': featured_garments,
    })


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
def garment_create(request):
    if not can_manage_cms_content(request.user):
        return HttpResponseForbidden('You do not have permission to manage garments.')

    form = GarmentForm()
    if request.method == 'POST':
        form = GarmentForm(request.POST, request.FILES)
        if form.is_valid():
            garment = form.save()
            messages.success(request, f'“{garment.title}” has been added to the garment collection.')
            return redirect('cms-admin:garment_list')

    return render(request, 'cms_admin/garment_form.html', {
        'form': form,
        'is_edit': False,
    })


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
def garment_edit(request, pk):
    if not can_manage_cms_content(request.user):
        return HttpResponseForbidden('You do not have permission to manage garments.')

    garment = get_object_or_404(Garment, pk=pk)
    form = GarmentForm(instance=garment)
    if request.method == 'POST':
        form = GarmentForm(request.POST, request.FILES, instance=garment)
        if form.is_valid():
            form.save()
            messages.success(request, f'“{garment.title}” has been updated successfully.')
            return redirect('cms-admin:garment_list')

    return render(request, 'cms_admin/garment_form.html', {
        'form': form,
        'is_edit': True,
        'garment': garment,
    })


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
@require_POST
def garment_delete(request, pk):
    if not can_delete_cms_content(request.user):
        messages.error(request, 'Only CMS Admins can delete garments.')
        return redirect('cms-admin:garment_list')

    garment = get_object_or_404(Garment, pk=pk)
    name = garment.title
    garment.delete()
    messages.success(request, f'“{name}” has been removed from the garment collection.')
    return redirect('cms-admin:garment_list')


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
def testimonial_list(request):
    if not can_manage_cms_content(request.user):
        return HttpResponseForbidden('You do not have permission to manage testimonials.')

    testimonials = Testimonial.objects.all()
    total_testimonials = testimonials.count()
    published_testimonials = Testimonial.objects.filter(is_published=True).count()
    draft_testimonials = Testimonial.objects.filter(is_published=False).count()
    page_obj, per_page = _paginate(testimonials, request)

    return render(request, 'cms_admin/testimonial_list.html', {
        'testimonials': page_obj,
        'per_page': per_page,
        'total_testimonials': total_testimonials,
        'published_testimonials': published_testimonials,
        'draft_testimonials': draft_testimonials,
    })


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
def testimonial_create(request):
    if not can_manage_cms_content(request.user):
        return HttpResponseForbidden('You do not have permission to manage testimonials.')

    form = TestimonialForm()
    if request.method == 'POST':
        form = TestimonialForm(request.POST)
        if form.is_valid():
            t = form.save()
            messages.success(request, f'Testimonial from “{t.author_name}” has been added.')
            return redirect('cms-admin:testimonial_list')

    return render(request, 'cms_admin/testimonial_form.html', {
        'form': form,
        'is_edit': False,
    })


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
def testimonial_edit(request, pk):
    if not can_manage_cms_content(request.user):
        return HttpResponseForbidden('You do not have permission to manage testimonials.')

    testimonial = get_object_or_404(Testimonial, pk=pk)
    form = TestimonialForm(instance=testimonial)
    if request.method == 'POST':
        form = TestimonialForm(request.POST, instance=testimonial)
        if form.is_valid():
            form.save()
            messages.success(request, f'Testimonial from “{testimonial.author_name}” has been updated.')
            return redirect('cms-admin:testimonial_list')

    return render(request, 'cms_admin/testimonial_form.html', {
        'form': form,
        'is_edit': True,
        'testimonial': testimonial,
    })


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
@require_POST
def testimonial_delete(request, pk):
    if not can_delete_cms_content(request.user):
        messages.error(request, 'Only CMS Admins can delete testimonials.')
        return redirect('cms-admin:testimonial_list')

    testimonial = get_object_or_404(Testimonial, pk=pk)
    name = testimonial.author_name
    testimonial.delete()
    messages.success(request, f'Testimonial from “{name}” has been removed.')
    return redirect('cms-admin:testimonial_list')


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
def silhouette_list(request):
    if not can_manage_cms_content(request.user):
        return HttpResponseForbidden('You do not have permission to manage silhouettes.')

    silhouettes = BespokeSilhouette.objects.all()
    total_silhouettes = silhouettes.count()
    published_silhouettes = BespokeSilhouette.objects.filter(is_published=True).count()
    custom_vision_silhouettes = BespokeSilhouette.objects.filter(is_custom_vision=True).count()
    page_obj, per_page = _paginate(silhouettes, request)

    return render(request, 'cms_admin/silhouette_list.html', {
        'silhouettes': page_obj,
        'per_page': per_page,
        'total_silhouettes': total_silhouettes,
        'published_silhouettes': published_silhouettes,
        'custom_vision_silhouettes': custom_vision_silhouettes,
    })


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
def silhouette_create(request):
    if not can_manage_cms_content(request.user):
        return HttpResponseForbidden('You do not have permission to manage silhouettes.')

    form = BespokeSilhouetteForm()
    if request.method == 'POST':
        form = BespokeSilhouetteForm(request.POST, request.FILES)
        if form.is_valid():
            s = form.save()
            messages.success(request, f'Silhouette “{s.name}” has been added.')
            return redirect('cms-admin:silhouette_list')
    return render(request, 'cms_admin/silhouette_form.html', {
        'form': form, 'is_edit': False,
    })


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
def silhouette_edit(request, pk):
    if not can_manage_cms_content(request.user):
        return HttpResponseForbidden('You do not have permission to manage silhouettes.')

    silhouette = get_object_or_404(BespokeSilhouette, pk=pk)
    form = BespokeSilhouetteForm(instance=silhouette)
    if request.method == 'POST':
        form = BespokeSilhouetteForm(request.POST, request.FILES, instance=silhouette)
        if form.is_valid():
            form.save()
            messages.success(request, f'Silhouette “{silhouette.name}” has been updated.')
            return redirect('cms-admin:silhouette_list')
    return render(request, 'cms_admin/silhouette_form.html', {
        'form': form, 'is_edit': True, 'silhouette': silhouette,
    })


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
@require_POST
def silhouette_delete(request, pk):
    if not can_delete_cms_content(request.user):
        messages.error(request, 'Only CMS Admins can delete silhouettes.')
        return redirect('cms-admin:silhouette_list')

    silhouette = get_object_or_404(BespokeSilhouette, pk=pk)
    name = silhouette.name
    silhouette.delete()
    messages.success(request, f'Silhouette “{name}” has been removed.')
    return redirect('cms-admin:silhouette_list')


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
def swatch_list(request):
    if not can_manage_cms_content(request.user):
        return HttpResponseForbidden('You do not have permission to manage fabric swatches.')

    swatches = FabricSwatch.objects.all()
    total_swatches = swatches.count()
    published_swatches = FabricSwatch.objects.filter(is_published=True).count()
    hidden_swatches = FabricSwatch.objects.filter(is_published=False).count()
    page_obj, per_page = _paginate(swatches, request)

    return render(request, 'cms_admin/swatch_list.html', {
        'swatches': page_obj,
        'per_page': per_page,
        'total_swatches': total_swatches,
        'published_swatches': published_swatches,
        'hidden_swatches': hidden_swatches,
    })


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
def swatch_create(request):
    if not can_manage_cms_content(request.user):
        return HttpResponseForbidden('You do not have permission to manage fabric swatches.')

    form = FabricSwatchForm()
    if request.method == 'POST':
        form = FabricSwatchForm(request.POST, request.FILES)
        if form.is_valid():
            s = form.save()
            messages.success(request, f'Fabric swatch “{s.name}” has been added.')
            return redirect('cms-admin:swatch_list')
    return render(request, 'cms_admin/swatch_form.html', {
        'form': form, 'is_edit': False,
    })


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
def swatch_edit(request, pk):
    if not can_manage_cms_content(request.user):
        return HttpResponseForbidden('You do not have permission to manage fabric swatches.')

    swatch = get_object_or_404(FabricSwatch, pk=pk)
    form = FabricSwatchForm(instance=swatch)
    if request.method == 'POST':
        form = FabricSwatchForm(request.POST, request.FILES, instance=swatch)
        if form.is_valid():
            form.save()
            messages.success(request, f'Fabric swatch “{swatch.name}” has been updated.')
            return redirect('cms-admin:swatch_list')
    return render(request, 'cms_admin/swatch_form.html', {
        'form': form, 'is_edit': True, 'swatch': swatch,
    })


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
@require_POST
def swatch_delete(request, pk):
    if not can_delete_cms_content(request.user):
        messages.error(request, 'Only CMS Admins can delete fabric swatches.')
        return redirect('cms-admin:swatch_list')

    swatch = get_object_or_404(FabricSwatch, pk=pk)
    name = swatch.name
    swatch.delete()
    messages.success(request, f'Fabric swatch “{name}” has been removed.')
    return redirect('cms-admin:swatch_list')


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
def site_configuration(request):
    if not can_manage_site_configuration(request.user):
        return HttpResponseForbidden('You do not have permission to manage site configuration.')

    cfg = SiteConfiguration.get_solo()
    form = SiteConfigurationForm(instance=cfg)
    if request.method == 'POST':
        form = SiteConfigurationForm(request.POST, instance=cfg)
        if form.is_valid():
            form.save()
            messages.success(request, 'Site configuration has been saved successfully.')
            return redirect('cms-admin:site_configuration')
    return render(request, 'cms_admin/site_configuration.html', {
        'form': form,
        'cfg': cfg,
    })


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
def team_list(request):
    if not can_manage_cms_users(request.user):
        return HttpResponseForbidden('You do not have permission to manage CMS users.')

    users = get_user_model().objects.filter(is_staff=True).prefetch_related('groups').order_by('is_active', 'username')
    return render(request, 'cms_admin/team_list.html', {
        'users': users,
        'role_choices': _role_choices_for_template(),
    })


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
def team_create(request):
    if not can_manage_cms_users(request.user):
        return HttpResponseForbidden('You do not have permission to manage CMS users.')

    form = CMSUserForm()
    if request.method == 'POST':
        form = CMSUserForm(request.POST)
        if form.is_valid():
            User = get_user_model()
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['temporary_password'],
                first_name=form.cleaned_data['full_name'],
                is_staff=True,
                is_active=form.cleaned_data['is_active'],
            )
            _set_user_cms_role(user, form.cleaned_data['role'])
            messages.success(request, f'CMS user “{user.get_username()}” has been created.')
            return redirect('cms-admin:team_list')

    return render(request, 'cms_admin/team_form.html', {
        'form': form,
        'is_edit': False,
        'role_choices': _role_choices_for_template(),
    })


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
def team_edit(request, pk):
    if not can_manage_cms_users(request.user):
        return HttpResponseForbidden('You do not have permission to manage CMS users.')

    user = get_object_or_404(get_user_model().objects.filter(is_staff=True), pk=pk)
    if user.is_superuser:
        messages.error(request, 'Superusers must be managed through Django authentication controls.')
        return redirect('cms-admin:team_list')

    form = CMSEditUserForm(user=user, initial={
        'full_name': user.get_full_name() or user.get_username(),
        'email': user.email,
        'role': 'admin' if is_cms_admin(user) else 'supervisor' if is_cms_supervisor(user) else 'designer',
        'is_active': user.is_active,
    })

    if request.method == 'POST':
        form = CMSEditUserForm(request.POST, user=user)
        if form.is_valid():
            last_admin_error = _last_active_admin_error(
                user,
                'deactivate this CMS Admin' if not form.cleaned_data['is_active'] else 'remove the last CMS Admin role',
            )
            if last_admin_error:
                messages.error(request, last_admin_error)
                return render(request, 'cms_admin/team_form.html', {
                    'form': form,
                    'is_edit': True,
                    'target_user': user,
                    'role_choices': _role_choices_for_template(),
                })

            user.first_name = form.cleaned_data['full_name']
            user.email = form.cleaned_data['email']
            user.is_active = form.cleaned_data['is_active']
            user.save(update_fields=['first_name', 'email', 'is_active'])
            _set_user_cms_role(user, form.cleaned_data['role'])
            messages.success(request, f'CMS user “{user.get_username()}” has been updated.')
            return redirect('cms-admin:team_list')

    return render(request, 'cms_admin/team_form.html', {
        'form': form,
        'is_edit': True,
        'target_user': user,
        'role_choices': _role_choices_for_template(),
    })


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
@require_POST
def team_toggle_active(request, pk):
    if not can_manage_cms_users(request.user):
        return HttpResponseForbidden('You do not have permission to manage CMS users.')

    user = get_object_or_404(get_user_model().objects.filter(is_staff=True), pk=pk)
    if user.pk == request.user.pk:
        messages.error(request, 'You cannot deactivate your own CMS account from this page.')
        return redirect('cms-admin:team_list')
    if user.is_superuser:
        messages.error(request, 'Superusers must be managed through Django authentication controls.')
        return redirect('cms-admin:team_list')
    if not user.is_active and is_cms_admin(user) and _active_admin_count_excluding(user.pk) == 0:
        messages.error(request, 'Cannot deactivate this CMS Admin; at least one active CMS Admin must remain.')
        return redirect('cms-admin:team_list')

    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    action = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'CMS user “{user.get_username()}” has been {action}.')
    return redirect('cms-admin:team_list')


@login_required(login_url='cms-admin:login')
@user_passes_test(_cms_required, login_url='cms-admin:login')
def team_password(request, pk):
    if not can_manage_cms_users(request.user):
        return HttpResponseForbidden('You do not have permission to manage CMS users.')

    user = get_object_or_404(get_user_model().objects.filter(is_staff=True), pk=pk)
    if user.is_superuser:
        messages.error(request, 'Superuser passwords must be changed through Django authentication controls.')
        return redirect('cms-admin:team_list')

    form = CMSUserPasswordForm()
    if request.method == 'POST':
        form = CMSUserPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password'])
            user.save(update_fields=['password'])
            messages.success(request, f'Password for “{user.get_username()}” has been changed.')
            return redirect('cms-admin:team_list')

    return render(request, 'cms_admin/team_password.html', {
        'form': form,
        'target_user': user,
    })
