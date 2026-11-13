from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import (
    AddressForm,
    BootstrapPasswordChangeForm,
    LoginForm,
    ProfileForm,
    RegistrationForm,
    UserUpdateForm,
)
from .models import Address, Profile
User = get_user_model()


def _safe_next(request):
    """Return the next URL only if it belongs to this website."""

    target = (
        request.POST.get('next')
        or request.GET.get('next')
        or ''
    )

    if target and url_has_allowed_host_and_scheme(
        target,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return target

    return ''

def register(request):

    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':

        form = RegistrationForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            messages.success(
                request,
                f'Welcome to FoodOnline, {user.first_name}! Your account is ready.'
            )

            return redirect(
                _safe_next(request) or 'core:home'
            )

        messages.error(
            request,
            'Please correct the errors below.'
        )

    else:
        form = RegistrationForm()

    return render(
        request,
        'accounts/registration.html',
        {
            'form': form,
            'next': _safe_next(request)
        }
    )

class CustomLoginView(LoginView):

    template_name = 'accounts/login.html'

    authentication_form = LoginForm

    redirect_authenticated_user = True

    def form_valid(self, form):

        user = form.get_user()

        messages.success(
            self.request,
            f'Welcome back, {user.first_name or user.username}!'
        )

        return super().form_valid(form)
    

@login_required
def profile(request):

    user = User.objects.get(pk=request.user.pk)

    profile_obj, _ = Profile.objects.get_or_create(
        user=user
    )

    if request.method == 'POST':

        user_form = UserUpdateForm(
            request.POST,
            instance=user
        )

        profile_form = ProfileForm(
            request.POST,
            instance=profile_obj
        )

        if user_form.is_valid() and profile_form.is_valid():

            user_form.save()
            profile_form.save()

            messages.success(
                request,
                'Your personal information has been updated.'
            )

            return redirect('accounts:profile')

        messages.error(
            request,
            'Please correct the errors below.'
        )

    else:

        user_form = UserUpdateForm(instance=user)

        profile_form = ProfileForm(instance=profile_obj)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'addresses': request.user.addresses.all()[:3],
        'address_count': request.user.addresses.count(),
        'order_count': request.user.orders.count(),
    }

    return render(
        request,
        'accounts/profile.html',
        context
    )



class ChangePasswordView(
    SuccessMessageMixin,
    PasswordChangeView
):

    template_name = 'accounts/password_change.html'

    form_class = BootstrapPasswordChangeForm

    success_url = reverse_lazy('accounts:profile')

    success_message = 'Your password was changed successfully.'


@login_required
def address_list(request):

    return render(
        request,
        'accounts/address_list.html',
        {
            'addresses': request.user.addresses.all()
        }
    )


@login_required
def address_create(request):

    form = AddressForm(
        request.POST or None,
        initial={
            'full_name': request.user.get_full_name()
        }
    )

    if request.method == 'POST' and form.is_valid():

        address = form.save(commit=False)

        address.user = request.user

        address.save()

        messages.success(request, 'Address saved.')

        return redirect(
            _safe_next(request) or 'accounts:address_list'
        )

    return render(
        request,
        'accounts/address_form.html',
        {
            'form': form,
            'title': 'Add a new address'
        }
    )


@login_required
def address_update(request, pk):

    address = get_object_or_404(
        Address,
        pk=pk,
        user=request.user
    )

    form = AddressForm(
        request.POST or None,
        instance=address
    )

    if request.method == 'POST' and form.is_valid():

        form.save()

        messages.success(request, 'Address updated.')

        return redirect('accounts:address_list')

    return render(
        request,
        'accounts/address_form.html',
        {
            'form': form,
            'title': 'Edit address'
        }
    )


@login_required
@require_POST
def address_delete(request, pk):
    address = get_object_or_404(
        Address,
        pk=pk,
        user=request.user
    )

    was_default = address.is_default
    address.delete()

    if was_default:
        next_address = Address.objects.filter(
            user=request.user
        ).first()

        if next_address:
            next_address.is_default = True
            next_address.save()

    messages.success(request, 'Address deleted successfully.')

    return redirect('accounts:address_list')



@login_required
@require_POST
def address_set_default(request, pk):

    address = get_object_or_404(
        Address,
        pk=pk,
        user=request.user
    )

    address.is_default = True

    address.save()

    messages.success(
        request,
        'Default address updated.'
    )

    return redirect('accounts:address_list')



