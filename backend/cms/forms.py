from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _

from .models import Garment, BespokeRequest, Testimonial, BespokeSilhouette, FabricSwatch, SiteConfiguration
from .rbac import CMS_DESIGNER_GROUP, allowed_statuses_for_user, is_cms_admin, is_cms_supervisor, is_cms_user


_INPUT = (
    'w-full px-4 py-3 bg-transparent border-b-2 border-[#55433d] text-[#1b1c1c] '
    'text-base font-[Inter] focus:outline-none focus:border-[#914325] transition-colors'
)
_TEXTAREA = (
    'w-full px-4 py-3 bg-transparent border-2 border-[#e4e2e1] text-[#1b1c1c] '
    'text-base font-[Inter] rounded-lg focus:outline-none focus:border-[#914325] '
    'transition-colors resize-vertical min-h-[100px]'
)
_SELECT = (
    'w-full px-4 py-3 bg-[#f6f3f2] border-2 border-[#e4e2e1] text-[#1b1c1c] '
    'text-base font-[Inter] rounded-lg focus:outline-none focus:border-[#914325] transition-colors'
)
_FILE = (
    'w-full px-4 py-3 bg-[#f6f3f2] border-2 border-dashed border-[#e4e2e1] '
    'text-[#55433d] text-base font-[Inter] rounded-lg cursor-pointer '
    'focus:outline-none focus:border-[#914325] transition-colors file:mr-4 '
    'file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm '
    'file:font-[Inter] file:font-semibold file:bg-[#914325] file:text-white hover:file:bg-[#783114]'
)
_CHECKBOX = 'h-5 w-5 rounded border-[#e4e2e1] text-[#914325] focus:ring-[#914325] cursor-pointer'
_NUMBER = (
    'w-full px-4 py-3 bg-transparent border-b-2 border-[#55433d] text-[#1b1c1c] '
    'text-base font-[Inter] focus:outline-none focus:border-[#914325] transition-colors'
)


class CMSAdminLoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-transparent border-b-2 border-[#55433d] text-[#1b1c1c] '
                     'text-base font-[Inter] focus:outline-none focus:border-[#914325] transition-colors',
            'placeholder': 'Username',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 bg-transparent border-b-2 border-[#55433d] text-[#1b1c1c] '
                     'text-base font-[Inter] focus:outline-none focus:border-[#914325] transition-colors',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError('Invalid username or password.')
            if not user.is_active or not is_cms_user(user):
                raise forms.ValidationError('You do not have access to the TSP Couture CMS admin.')
            cleaned_data['user'] = user
        return cleaned_data


class GarmentForm(forms.ModelForm):
    class Meta:
        model = Garment
        fields = [
            'title', 'description', 'category', 'image',
            'is_featured', 'is_published', 'sort_order',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-transparent border-b-2 border-[#55433d] text-[#1b1c1c] '
                         'text-base font-[Inter] focus:outline-none focus:border-[#914325] transition-colors',
                'placeholder': 'Garment Title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-transparent border-2 border-[#e4e2e1] text-[#1b1c1c] '
                         'text-base font-[Inter] rounded-lg focus:outline-none focus:border-[#914325] '
                         'transition-colors resize-vertical min-h-[100px]',
                'placeholder': 'Short description for alt text and captions',
                'rows': 4,
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-[#f6f3f2] border-2 border-[#e4e2e1] text-[#1b1c1c] '
                         'text-base font-[Inter] rounded-lg focus:outline-none focus:border-[#914325] '
                         'transition-colors',
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 bg-[#f6f3f2] border-2 border-dashed border-[#e4e2e1] '
                         'text-[#55433d] text-base font-[Inter] rounded-lg cursor-pointer '
                         'focus:outline-none focus:border-[#914325] transition-colors file:mr-4 '
                         'file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm '
                         'file:font-[Inter] file:font-semibold file:bg-[#914325] file:text-white '
                         'hover:file:bg-[#783114]',
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 rounded border-[#e4e2e1] text-[#914325] '
                         'focus:ring-[#914325] cursor-pointer',
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 rounded border-[#e4e2e1] text-[#914325] '
                         'focus:ring-[#914325] cursor-pointer',
            }),
            'sort_order': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-transparent border-b-2 border-[#55433d] text-[#1b1c1c] '
                         'text-base font-[Inter] focus:outline-none focus:border-[#914325] '
                         'transition-colors',
                'placeholder': '0',
                'min': 0,
            }),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError('Title is required.')
        return title

    def clean_sort_order(self):
        value = self.cleaned_data.get('sort_order', 0)
        if value < 0:
            raise forms.ValidationError('Sort order must be a positive number.')
        return value


class BespokeRequestStatusForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        queryset = get_user_model().objects.filter(
            is_active=True,
            groups__name=CMS_DESIGNER_GROUP,
        ).order_by('first_name', 'last_name', 'username')
        if self.instance.assigned_to_id:
            queryset = queryset | get_user_model().objects.filter(pk=self.instance.assigned_to_id)
        self.fields['assigned_to'].queryset = queryset
        self.fields['assigned_to'].empty_label = 'Unassigned'
        self.fields['assigned_to'].widget.attrs.update({
            'class': _SELECT,
        })
        if user and not is_cms_admin(user) and not is_cms_supervisor(user):
            self.fields['status'].choices = [
                choice for choice in self.fields['status'].choices
                if choice[0] in allowed_statuses_for_user(user)
            ]
        elif user and (is_cms_admin(user) or is_cms_supervisor(user)):
            self.fields['send_completion_email'] = forms.BooleanField(
                required=False,
                label='Send customer completion email when marking completed',
                widget=forms.CheckboxInput(attrs={'class': _CHECKBOX}),
            )
            self.fields['notify_in_progress'] = forms.BooleanField(
                required=False,
                label='Notify customer that work is now in progress',
                widget=forms.CheckboxInput(attrs={'class': _CHECKBOX}),
            )
            self.fields['notify_ready_for_review'] = forms.BooleanField(
                required=False,
                label='Notify customer that the garment is ready for review',
                widget=forms.CheckboxInput(attrs={'class': _CHECKBOX}),
            )
            self.fields['notify_cancelled'] = forms.BooleanField(
                required=False,
                label='Notify customer that this order has been cancelled',
                widget=forms.CheckboxInput(attrs={'class': _CHECKBOX}),
            )

    def clean_assigned_to(self):
        assigned_to = self.cleaned_data.get('assigned_to')
        if 'assigned_to' not in self.data and self.instance.assigned_to_id:
            return self.instance.assigned_to
        return assigned_to

    def clean_status(self):
        status = self.cleaned_data.get('status')
        if not status:
            return status
        old_status = self.instance.status if self.instance.pk else 'new'
        if old_status != status:
            from .rbac import is_valid_status_transition
            if not is_valid_status_transition(self.user, old_status, status):
                raise forms.ValidationError(
                    'Your role is not allowed to move this request to that status.'
                )
        return status

    class Meta:
        model = BespokeRequest
        fields = ['status', 'admin_notes', 'work_notes', 'assigned_to']
        widgets = {
            'status': forms.Select(attrs={
                'class': _SELECT,
            }),
            'admin_notes': forms.Textarea(attrs={
                'class': _TEXTAREA,
                'placeholder': 'Sensitive internal notes visible only to Admins and Supervisors...',
                'rows': 5,
            }),
            'work_notes': forms.Textarea(attrs={
                'class': _TEXTAREA,
                'placeholder': 'Shared atelier progress notes...',
                'rows': 5,
            }),
            'assigned_to': forms.Select(attrs={
                'class': _SELECT,
            }),
        }


class CMSUserForm(forms.Form):
    full_name = forms.CharField(max_length=200, required=True)
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[
            ('admin', 'CMS Admin'),
            ('supervisor', 'Supervisor / Lead Designer'),
            ('designer', 'Fashion Designer / Atelier Designer'),
        ],
        required=True,
    )
    temporary_password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=12,
        required=True,
    )
    is_active = forms.BooleanField(required=False, initial=True)

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        User = get_user_model()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('A user with this username already exists.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('A user with this email address already exists.')
        return email

    def clean_temporary_password(self):
        password = self.cleaned_data.get('temporary_password')
        if password and len(password) < 12:
            raise forms.ValidationError('Temporary password must be at least 12 characters.')
        return password


class CMSEditUserForm(forms.Form):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    full_name = forms.CharField(max_length=200, required=True)
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[
            ('admin', 'CMS Admin'),
            ('supervisor', 'Supervisor / Lead Designer'),
            ('designer', 'Fashion Designer / Atelier Designer'),
        ],
        required=True,
    )
    is_active = forms.BooleanField(required=False)

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        User = get_user_model()
        if self.user and User.objects.exclude(pk=self.user.pk).filter(email__iexact=email).exists():
            raise forms.ValidationError('A user with this email address already exists.')
        return email


class CMSUserPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=12,
        required=True,
    )

    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        if password and len(password) < 12:
            raise forms.ValidationError('Password must be at least 12 characters.')
        return password


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['author_name', 'author_location', 'text', 'is_published', 'sort_order']
        widgets = {
            'author_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-transparent border-b-2 border-[#55433d] text-[#1b1c1c] '
                         'text-base font-[Inter] focus:outline-none focus:border-[#914325] transition-colors',
                'placeholder': 'Author Name',
            }),
            'author_location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-transparent border-b-2 border-[#55433d] text-[#1b1c1c] '
                         'text-base font-[Inter] focus:outline-none focus:border-[#914325] transition-colors',
                'placeholder': 'e.g. New York',
            }),
            'text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-transparent border-2 border-[#e4e2e1] text-[#1b1c1c] '
                         'text-base font-[Inter] rounded-lg focus:outline-none focus:border-[#914325] '
                         'transition-colors resize-vertical min-h-[120px]',
                'placeholder': 'Testimonial text...',
                'rows': 5,
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 rounded border-[#e4e2e1] text-[#914325] '
                         'focus:ring-[#914325] cursor-pointer',
            }),
            'sort_order': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-transparent border-b-2 border-[#55433d] text-[#1b1c1c] '
                         'text-base font-[Inter] focus:outline-none focus:border-[#914325] transition-colors',
                'placeholder': '0',
                'min': 0,
            }),
        }

    def clean_author_name(self):
        name = self.cleaned_data.get('author_name', '').strip()
        if not name:
            raise forms.ValidationError('Author name is required.')
        return name


class BespokeSilhouetteForm(forms.ModelForm):
    class Meta:
        model = BespokeSilhouette
        fields = ['name', 'label', 'image', 'is_custom_vision', 'is_published', 'sort_order']
        widgets = {
            'name': forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'e.g. Royal Indigo Agbada'}),
            'label': forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Short card label, e.g. Royal Agbada'}),
            'image': forms.FileInput(attrs={'class': _FILE}),
            'is_custom_vision': forms.CheckboxInput(attrs={'class': _CHECKBOX}),
            'is_published': forms.CheckboxInput(attrs={'class': _CHECKBOX}),
            'sort_order': forms.NumberInput(attrs={'class': _NUMBER, 'placeholder': '0', 'min': 0}),
        }

    def clean_name(self):
        v = self.cleaned_data.get('name', '').strip()
        if not v:
            raise forms.ValidationError('Silhouette name is required.')
        return v

    def clean_label(self):
        v = self.cleaned_data.get('label', '').strip()
        if not v:
            raise forms.ValidationError('Display label is required.')
        return v


class FabricSwatchForm(forms.ModelForm):
    class Meta:
        model = FabricSwatch
        fields = ['name', 'color_hex', 'texture_css', 'image', 'is_published', 'sort_order']
        widgets = {
            'name': forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'e.g. Heavy Linen'}),
            'color_hex': forms.TextInput(attrs={
                'class': _INPUT,
                'placeholder': '#e0d6c8',
                'type': 'color',
                'style': 'height:48px;padding:4px 8px;',
            }),
            'texture_css': forms.Textarea(attrs={
                'class': _TEXTAREA,
                'placeholder': 'Optional: CSS for overlay div, e.g. background-image:repeating-linear-gradient(...);opacity:0.2;',
                'rows': 3,
            }),
            'image': forms.FileInput(attrs={'class': _FILE}),
            'is_published': forms.CheckboxInput(attrs={'class': _CHECKBOX}),
            'sort_order': forms.NumberInput(attrs={'class': _NUMBER, 'placeholder': '0', 'min': 0}),
        }

    def clean_name(self):
        v = self.cleaned_data.get('name', '').strip()
        if not v:
            raise forms.ValidationError('Fabric name is required.')
        return v

    def clean_color_hex(self):
        v = self.cleaned_data.get('color_hex', '').strip()
        if v and not v.startswith('#'):
            v = '#' + v
        return v


class SiteConfigurationForm(forms.ModelForm):
    class Meta:
        model = SiteConfiguration
        fields = [
            'contact_email', 'whatsapp_number',
            'instagram_url', 'facebook_url', 'twitter_url', 'pinterest_url',
            'hero_tagline', 'hero_subtext',
            'footer_address', 'footer_copyright',
            'delivery_lead_time',
        ]
        widgets = {
            'contact_email': forms.EmailInput(attrs={'class': _INPUT, 'placeholder': 'hello@romcouture.com'}),
            'whatsapp_number': forms.TextInput(attrs={'class': _INPUT, 'placeholder': '+2348012345678'}),
            'instagram_url': forms.URLInput(attrs={'class': _INPUT, 'placeholder': 'https://instagram.com/romcouture'}),
            'facebook_url': forms.URLInput(attrs={'class': _INPUT, 'placeholder': 'https://facebook.com/romcouture'}),
            'twitter_url': forms.URLInput(attrs={'class': _INPUT, 'placeholder': 'https://x.com/romcouture'}),
            'pinterest_url': forms.URLInput(attrs={'class': _INPUT, 'placeholder': 'https://pinterest.com/romcouture'}),
            'hero_tagline': forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Short headline for the homepage hero'}),
            'hero_subtext': forms.Textarea(attrs={'class': _TEXTAREA, 'placeholder': 'Supporting paragraph beneath the tagline', 'rows': 3}),
            'footer_address': forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Studio address shown in footer'}),
            'footer_copyright': forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Leave blank to use default copyright'}),
            'delivery_lead_time': forms.TextInput(attrs={'class': _INPUT, 'placeholder': '4–6 weeks'}),
        }
