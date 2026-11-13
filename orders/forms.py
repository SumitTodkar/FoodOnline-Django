from django import forms

from accounts.forms import BootstrapFormMixin
from accounts.models import Address, phone_validator, pincode_validator

from .models import Order

REQUIRED_WHEN_NEW_ADDRESS = ('full_name', 'phone', 'address_line1', 'city', 'state', 'pincode')


class CheckoutForm(BootstrapFormMixin, forms.Form):
    """Delivery details and payment method. Use a saved address or type a new one."""

    address = forms.ModelChoiceField(
        queryset=Address.objects.none(), required=False, empty_label='Enter a new address',
        label='Saved addresses',
    )
    full_name = forms.CharField(max_length=120, required=False)
    phone = forms.CharField(max_length=15, required=False, validators=[phone_validator])
    email = forms.EmailField(required=False)
    address_line1 = forms.CharField(max_length=200, required=False, label='Address line 1')
    address_line2 = forms.CharField(max_length=200, required=False, label='Address line 2')
    landmark = forms.CharField(max_length=120, required=False)
    city = forms.CharField(max_length=80, required=False)
    state = forms.CharField(max_length=80, required=False)
    pincode = forms.CharField(max_length=6, required=False, label='PIN code', validators=[pincode_validator])
    notes = forms.CharField(
        max_length=300, required=False, label='Delivery instructions',
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'e.g. Ring the bell twice, leave at the door'}),
    )
    save_address = forms.BooleanField(required=False, label='Save this address for next time')
    payment_method = forms.ChoiceField(
        choices=Order.PaymentMethod.choices, initial=Order.PaymentMethod.COD, widget=forms.RadioSelect,
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only the customer's own addresses can ever be selected.
        self.fields['address'].queryset = Address.objects.filter(user=user)

    def clean(self):
        cleaned = super().clean()
        address = cleaned.get('address')
        if address:
            cleaned.update({
                'full_name': address.full_name,
                'phone': address.phone,
                'address_line1': address.line1,
                'address_line2': address.line2,
                'landmark': address.landmark,
                'city': address.city,
                'state': address.state,
                'pincode': address.pincode,
            })
        else:
            for name in REQUIRED_WHEN_NEW_ADDRESS:
                if not cleaned.get(name) and name not in self.errors:
                    self.add_error(name, 'This field is required.')
        return cleaned
