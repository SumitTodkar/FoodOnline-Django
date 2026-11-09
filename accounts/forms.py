from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm
)

from .models import Address, Profile, phone_validator

User = get_user_model()


class BootstrapFormMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            widget = field.widget

            if isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                css_class = 'form-check-input'
            elif isinstance(widget, forms.Select):
                css_class = 'form-select'
            else:
                css_class = 'form-control'

            widget.attrs['class'] = css_class


class RegistrationForm(BootstrapFormMixin, UserCreationForm):

    email = forms.EmailField(required=True)

    phone = forms.CharField(
        max_length=15,
        validators=[phone_validator]
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    field_order = [
        'first_name',
        'last_name',
        'username',
        'email',
        'phone',
        'password1',
        'password2'
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'An account with this email already exists.'
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data['phone']
            profile.save()

        return user


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    pass


class UserUpdateForm(BootstrapFormMixin, forms.ModelForm):

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        if User.objects.filter(
            email__iexact=email
        ).exclude(pk=self.instance.pk).exists():

            raise forms.ValidationError(
                'Another account already uses this email address.'
            )

        return email


class ProfileForm(BootstrapFormMixin, forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('phone',)


class AddressForm(BootstrapFormMixin, forms.ModelForm):

    class Meta:
        model = Address
        fields = (
            'label',
            'full_name',
            'phone',
            'line1',
            'line2',
            'landmark',
            'city',
            'state',
            'pincode',
            'is_default'
        )


class BootstrapPasswordChangeForm(
    BootstrapFormMixin,
    PasswordChangeForm
):
    pass